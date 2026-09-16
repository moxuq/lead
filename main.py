from fastapi import FastAPI

from .routers import (
    accounts,
    tasks,
    leads,
    stats,
    error
)

app = FastAPI(title="Lead", version="1.0.0")
app.include_router(accounts.accounts_router)
app.include_router(tasks.tasks_router)
app.include_router(leads.leads_router)
app.include_router(stats.stats_router)
app.include_router(error.errors_router)
