from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, ForeignKey
from datetime import datetime
from enum import Enum
from typing import Text

from .database import Base

class AccountStatuses(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    BAN = "banned"
    REQ_2FA = "2fa_required"

class TasksTypes(Enum):
    LOCATION = "location"
    HASHTAG = "hashtag"
    COMPETITOR_FOLLOWERS = "competitor_followers"
    
class TasksStatuses(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    
class ParseStatus(Enum):
    PENDING = "pending"
    PARSED = "parsed"
    ERROR = "error"

class LeadsNoSiteReason(Enum):
    EMPTY_BIO = "empty_bio"
    MESSENGER_ONLY = "messenger_only"
    SOCIAL_ONLY = "social_only"
    AGGREGATOR = "aggregator"
    
class TypeContacts(Enum):
    PHONE = "phone"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TG = "telegram"
    WEBSITE = "website"

class SourceContacts(Enum):
    BIO = "bio"
    BUTTON = "button"
    LOCATION = "location"
    PROFILE_LINK = "profile_link"

class ErrorType(Enum):
    CAPTCHA = "captcha"
    BAN = "ban"
    TIMEOUT = "timeout"
    SELECTOR_MISSING = "selector_missing"
    LOGIN_FAILED = "login_failed"

class AccountPool(Base):
    __tablename__ = "accounts_pool"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    proxy_url: Mapped[str] = mapped_column()
    status: Mapped[AccountStatuses] = mapped_column(nullable=False, default=AccountStatuses.AVAILABLE)
    last_used_at: Mapped[datetime] = mapped_column(DateTime)
    profiles_parsed_count: Mapped[int] = mapped_column(nullable=False, default=0)

class SearchTask(Base):
    __tablename__ = "search_tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[TasksTypes] = mapped_column()
    query: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column()
    status: Mapped[TasksStatuses] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
class RawProfile(Base):
    __tablename__ = "raw_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    url: Mapped[str] = mapped_column(nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("search_tasks.id"))
    parsed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    parse_status: Mapped[ParseStatus] = mapped_column()
    
class Lead(Base):
    __tablename__ = "leads"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("raw_profiles.id"), unique=True)
    name: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)
    bio_text: Mapped[Text] = mapped_column(nullable=True)
    is_business_account: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    followers_count: Mapped[int] = mapped_column(default=0)
    has_website: Mapped[bool] = mapped_column(nullable=False)
    no_site_reason: Mapped[LeadsNoSiteReason] = mapped_column()
    address: Mapped[str] = mapped_column(nullable=True)
    parsed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
class Contact(Base):
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"))
    type: Mapped[TypeContacts] = mapped_column()
    value: Mapped[str] = mapped_column(nullable=False)
    source: Mapped[SourceContacts] = mapped_column()
    is_valid: Mapped[bool] = mapped_column(default=True)
    
class ErrorLog(Base):
    __tablename__ = "error_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts_pool.id"), nullable=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("raw_profiles.id"), nullable=True)
    error_type: Mapped[TypeError] = mapped_column()
    message: Mapped[Text] = mapped_column(nullable=False)
    stack_trace: Mapped[Text] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())