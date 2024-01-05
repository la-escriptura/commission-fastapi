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
    prefix='/invoice',
    tags=['invoice']
)


class Invoice(BaseModel):
    invoice: str
    isEditInvoice: bool
    jobOrderNo: str
    dt: str
    qtyinvoice: int
    deliveryReceipt: str


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.get('/joborders', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectjoborders();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/redoinvoices', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectredoinvoices();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.post('/transaction', status_code=status.HTTP_201_CREATED)
def protected(invoice: Invoice, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    try:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute("CALL com.usp_insertinvoice (par_json => %(par_json)s, par_userid => %(par_userid)s);", {"par_json": invoice.json(), "par_userid": user_id})
        conn.commit()
        cursor.close()
        return Response(content=json.dumps({"Success": True}, default=str), media_type='application/json')
    except Exception as e:
        # ex_type, ex_value, ex_traceback = sys.exc_info()
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e).split('\n')[0])
        return Response(content=json.dumps({"Success": False, "Error": str(e).split('\n')[0]}, default=str), media_type='application/json')












