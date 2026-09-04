from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./instalead.db"
    INSTAGRAM_BASE_URL: str = "https://www.instagram.com"
    HEADLESS: bool = False
    MIN_DELAY_BETWEEN_REQUESTS: int = 5
    MAX_DELAY_BETWEEN_REQUESTS: int = 15
    MIN_SCROLL_DELAY: int = 2
    MAX_SCROLL_DELAY: int = 6
    LOGIN_TIMEOUT_SECONDS: int = 30
    PAGE_LOAD_TIMEOUT_SECONDS: int = 20
    MAX_PROFILES_PER_HOUR: int = 60
    USER_AGENTS_FILE: str = "config/user_agents.txt"
    BLACKLIST_DOMAINS: list[str] = ['vk.com', 'ok.ru', 't.me', 'wa.me', 'taplink.cc', 'mssg.me', 'linktr.ee', 'instagram.com']
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )