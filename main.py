from a2wsgi import ASGIMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, joborder, invoice, receipt, report, inquiry, formula, utility
from config import settings

app = FastAPI()
wsgi_app = ASGIMiddleware(app)

origins = [settings.CLIENT_ORIGIN]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(joborder.router)
app.include_router(invoice.router)
app.include_router(receipt.router)
app.include_router(report.router)
app.include_router(inquiry.router)
app.include_router(formula.router)
app.include_router(utility.router)