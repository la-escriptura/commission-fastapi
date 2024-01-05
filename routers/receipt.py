import sys
import json

import psycopg2.extras
from typing import List
from datetime import timedelta, datetime

from starlette import status
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from pydantic import BaseModel
from database import connection
from routers.auth import get_current_user

router = APIRouter(
    prefix='/receipt',
    tags=['receipt']
)


class Account(BaseModel):
    invoice: str
    rebate: float
    retention: float
    penalty: float
    govshare: float
    withheld0: float
    withheld1: float
    withheld2: float

class Receipt(BaseModel):
    OR: str
    isEditReceipt: bool
    dt: str
    invoices: list[Account]


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.get('/invoices', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectinvoices();")

    custid = 0
    custname = ""
    customers = {}
    invoices = []
    rows = []
    row = cursor.fetchone()
    while row:
        custid = row["custid"]
        custname = row["custname"]
        invoices.append(dict(list(row.items())[2:]))
        row = cursor.fetchone()
        if ((not row) or (custid != row["custid"])):
            customers["custname"] = custname
            customers["invoices"] = invoices
            rows.append(customers)
            customers = {}
            invoices = []

    ret = Response(content=json.dumps(rows, default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/redoreceipts', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectredoreceipts();")

    receiptid = 0
    orno = ""
    dateor = ""
    custname = ""
    receipts = {}
    invoices = []
    rows = []
    row = cursor.fetchone()
    while row:
        receiptid = row["receiptid"]
        orno = row["orno"]
        dateor = row["dateor"]
        custname = row["custname"]
        invoices.append(dict(list(row.items())[4:]))
        row = cursor.fetchone()
        if ((not row) or (receiptid != row["receiptid"])):
            receipts["receiptid"] = receiptid
            receipts["orno"] = orno
            receipts["dateor"] = dateor
            receipts["custname"] = custname
            receipts["invoices"] = invoices
            rows.append(receipts)
            receipts = {}
            invoices = []

    ret = Response(content=json.dumps(rows, default=str), media_type='application/json')
    cursor.close()
    return ret


@router.post('/transaction', status_code=status.HTTP_201_CREATED)
def protected(receipt: Receipt, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    try:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute("CALL com.usp_insertreceipt (par_json => %(par_json)s, par_userid => %(par_userid)s);", {"par_json": receipt.json(), "par_userid": user_id})
        conn.commit()
        cursor.close()
        return Response(content=json.dumps({"Success": True}, default=str), media_type='application/json')
    except Exception as e:
        # ex_type, ex_value, ex_traceback = sys.exc_info()
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e).split('\n')[0])
        return Response(content=json.dumps({"Success": False, "Error": str(e).split('\n')[0]}, default=str), media_type='application/json')












