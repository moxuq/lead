import asyncio
import re
import random
import pandas as pd
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import phonenumbers

# --- КОНФИГУРАЦИЯ ---
# Домены, наличие которых означает, что у бизнеса НЕТ корпоративного сайта
BLACKLIST_DOMAINS = [
    'vk.com', 'ok.ru', 'facebook.com', 't.me', 'wa.me', 'telegram.me',
    'taplink.cc', 'taplink.ru', 'mssg.me', 'linktr.ee', 'beacons.ai',
    'instagram.com', 'youtube.com', 'tiktok.com', 'avito.ru'
]

# Регулярные выражения
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+?\d[\d \-\(\)]{8,15}\d')
DOMAIN_REGEX = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+(?:ru|com|net|org|рф|kz|by)\b')
MESSENGER_REGEX = re.compile(r'(?:t\.me|wa\.me|telegram\.me)/([a-zA-Z0-9_]+)')

async def setup_browser(proxy: str = None):
    """Инициализация браузера с анти-детект настройками."""
    launch_args = [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage'
    ]
    
    proxy_settings = {"server": proxy} if proxy else None
    
    browser = await async_playwright().start()
    browser = await browser.chromium.launch(
        headless=False, # Для отладки False, в проде лучше True + stealth
        args=launch_args,
        proxy=proxy_settings
    )
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    
    # Скрываем признак автоматизации (navigator.webdriver)
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)
    return browser, context

async def parse_profile(context, username: str):
    """Основная логика парсинга одного профиля."""
    page = await context.new_page()
    url = f"https://www.instagram.com/{username}/"
    
    try:
        # Рандомная задержка для эмуляции человека
        await asyncio.sleep(random.uniform(2.0, 5.0))
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(3.0, 6.0))
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        data = {
            "username": username,
            "url": url,
            "name": "",
            "category": "",
            "bio": "",
            "has_corporate_site": False,
            "site_url": "",
            "phone": "",
            "email": "",
            "whatsapp": "",
            "address": "",
            "subscribers": "",
            "has_ru_com_in_bio": False
        }
        
        # 1. Сбор базовой инфы через meta-теги (самый стабильный метод, не зависит от классов React)
        meta_desc = soup.find("meta", property="og:description")
        if meta_desc and meta_desc.get("content"):
            desc = meta_desc["content"]
            # Пример: "10K Followers, 500 Following, 120 Posts - Name (@username) on Instagram"
            subs_match = re.search(r'([\d,.]+[KMB]?) Followers', desc, re.IGNORECASE)
            if subs_match: data["subscribers"] = subs_match.group(1)
            
            name_match = re.search(r' - (.*?) \(@', desc)
            if name_match: data["name"] = name_match.group(1)

        # 2. Парсинг Bio и ссылок через BS4
        header = soup.find("header")
        if header:
            # Ищем блок с био (обычно это span с переносами строк)
            spans = header.find_all("span")
            bio_text = " ".join([s.get_text(strip=True) for s in spans if len(s.get_text(strip=True)) > 10])
            data["bio"] = bio_text
            
            # Проверка описания на .ru/.com
            if DOMAIN_REGEX.search(bio_text):
                data["has_ru_com_in_bio"] = True
                
            # Поиск мессенджеров в био
            tg_wa_match = MESSENGER_REGEX.search(bio_text)
            if tg_wa_match:
                data["whatsapp"] = tg_wa_match.group(0)

        # 3. Детекция внешнего сайта (Фильтр "Нет сайта")
        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            if "l.instagram.com" in href:
                # Распаковываем редирект Инстаграма
                parsed = urlparse(href)
                query = parse_qs(parsed.query)
                if "u" in query:
                    actual_url = query["u"][0]
                    domain = urlparse(actual_url).netloc.replace("www.", "").lower()
                    
                    if not any(bl in domain for bl in BLACKLIST_DOMAINS):
                        data["has_corporate_site"] = True
                        data["site_url"] = actual_url
                        break
            elif href.startswith("http") and "instagram.com" not in href:
                domain = urlparse(href).netloc.replace("www.", "").lower()
                if not any(bl in domain for bl in BLACKLIST_DOMAINS):
                    data["has_corporate_site"] = True
                    data["site_url"] = href
                    break

        # 4. Извлечение контактов из Bio (Regex)
        if data["bio"]:
            emails = EMAIL_REGEX.findall(data["bio"])
            if emails: data["email"] = emails[0]
                
            phones = PHONE_REGEX.findall(data["bio"])
            if phones:
                for p in phones:
                    try:
                        parsed_phone = phonenumbers.parse(p, "RU")
                        if phonenumbers.is_valid_number(parsed_phone):
                            data["phone"] = p
                            break
                    except:
                        data["phone"] = p

        # 5. Клики по кнопкам "Email" / "Позвонить" (если есть бизнес-кнопки)
        # В React-верстке кнопки часто имеют специфические классы, поэтому ищем по тексту
        buttons = soup.find_all(["button", "div"], role="button")
        for btn in buttons:
            btn_text = btn.get_text(strip=True).lower()
            if "email" in btn_text or "электронная почта" in btn_text:
                try:
                    await page.click(f'button:has-text("{btn.get_text(strip=True)}")')
                    await asyncio.sleep(1.5)
                    # Ищем появившийся mailto:
                    mailto = await page.query_selector('a[href^="mailto:"]')
                    if mailto: data["email"] = (await mailto.get_attribute("href")).replace("mailto:", "")
                except: pass
            elif "позвонить" in btn_text or "call" in btn_text:
                try:
                    await page.click(f'button:has-text("{btn.get_text(strip=True)}")')
                    await asyncio.sleep(1.5)
                    tel = await page.query_selector('a[href^="tel:"]')
                    if tel: data["phone"] = (await tel.get_attribute("href")).replace("tel:", "")
                except: pass

        # Если есть корпоративный сайт - возвращаем None (согласно ТЗ, фильтруем)
        if data["has_corporate_site"]:
            return None

        return data

    except Exception as e:
        print(f"Ошибка парсинга {username}: {e}")
        return None
    finally:
        await page.close()

async def export_to_excel(data_list, filename="leads.xlsx"):
    """Экспорт в Excel согласно ТЗ."""
    df = pd.DataFrame(data_list)
    cols = ["username", "name", "category", "bio", "phone", "email", "whatsapp", "address", "subscribers", "url"]
    for c in cols:
        if c not in df.columns: df[c] = ""
    df = df[cols]
    df.to_excel(filename, index=False)
    print(f"✅ Успешно сохранено в {filename}")

# --- ПРИМЕР ЗАПУСКА ---
async def main():
    # Прокси нужно брать резидентные или мобильные (например, proxy6.net, spaceproxy)
    proxy = "http://user:pass@ip:port" 
    
    browser, context = await setup_browser(proxy=None) # Для теста без прокси
    
    # Пример списка для парсинга
    targets = ["durov", "some_local_cafe"] 
    results = []
    
    for target in targets:
        res = await parse_profile(context, target)
        if res:
            results.append(res)
            
    await context.close()
    await browser.close()
    
    if results:
        await export_to_excel(results)

if __name__ == "__main__":
    asyncio.run(main())