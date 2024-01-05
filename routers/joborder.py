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
    prefix='/joborder',
    tags=['joborder']
)


class SalesRep(BaseModel):
	agent: str
	rate: float

class JobOrder(BaseModel):
    jobOrder: str
    isEditJobOrder: bool
    orderRef: str
    dt: str
    customerName: str
    isNewCustomerName: bool
    formTitle: str
    quantity: int
    unitMeasure: str
    materialCost: float
    processCost: float
    otherCost: float
    totalTransfer: float
    sellingPrice: float
    docStamps: float
    discount: float
    shippingHandling: float
    callable: float
    accountManager: str
    salesReps: list[SalesRep]


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.get('/redojoborders', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectredojoborders();")

    joborderid = 0
    joborderno = ""
    orderref = ""
    dt = ""
    custid = 0
    formtitle = ""
    quantity = 0
    unitmeasure = ""
    materialcost = 0
    processcost = 0
    othercost = 0
    totaltransfer = 0
    sellingprice = 0
    docstamps = 0
    discount = 0
    shippingHandling = 0
    callable = 0
    accountmanager = 0
    redojoborders = {}
    salesreps = []
    rows = []
    row = cursor.fetchone()
    while row:
        joborderid = row["joborderid"]
        joborderno = row["joborderno"]
        orderref = row["orderref"]
        dt = row["dt"]
        custid = row["custid"]
        formtitle = row["formtitle"]
        quantity = row["quantity"]
        unitmeasure = row["unitmeasure"]
        materialcost = row["materialcost"]
        processcost = row["processcost"]
        othercost = row["othercost"]
        totaltransfer = row["totaltransfer"]
        sellingprice = row["sellingprice"]
        docstamps = row["docstamps"]
        discount = row["discount"]
        shippingHandling = row["shippingHandling"]
        callable = row["callable"]
        accountmanager = row["accountmanager"]
        sr = dict(list(row.items())[18:])
        if (sr['agent'] is not None):
            salesreps.append(sr)
        row = cursor.fetchone()
        if ((not row) or (joborderid != row["joborderid"])):
            redojoborders["joborderid"] = joborderid
            redojoborders["joborderno"] = joborderno
            redojoborders["orderref"] = orderref
            redojoborders["dt"] = dt
            redojoborders["custid"] = custid
            redojoborders["formtitle"] = formtitle
            redojoborders["quantity"] = quantity
            redojoborders["unitmeasure"] = unitmeasure
            redojoborders["materialcost"] = materialcost
            redojoborders["processcost"] = processcost
            redojoborders["othercost"] = othercost
            redojoborders["totaltransfer"] = totaltransfer
            redojoborders["sellingprice"] = sellingprice
            redojoborders["docstamps"] = docstamps
            redojoborders["discount"] = discount
            redojoborders["shippingHandling"] = shippingHandling
            redojoborders["callable"] = callable
            redojoborders["accountmanager"] = accountmanager
            redojoborders["salesreps"] = salesreps
            rows.append(redojoborders)
            redojoborders = {}
            salesreps = []

    ret = Response(content=json.dumps(rows, default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/unitmeasures', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectunitmeasures();")

    rows = []
    for row in cursor.fetchall():
        col = list(row.items())[0][1]
        # col = dict(list(row.items())[:])
        rows.append(col)

    ret = Response(content=json.dumps(rows, default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/customers', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectcustomers();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/agents', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectagents();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.post('/transaction', status_code=status.HTTP_201_CREATED)
def protected(jobOrder: JobOrder, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    try:
        cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cursor.execute("CALL com.usp_insertjoborder (par_json => %(par_json)s, par_userid => %(par_userid)s);", {"par_json": jobOrder.json(), "par_userid": user_id})
        conn.commit()
        cursor.close()
        return Response(content=json.dumps({"Success": True}, default=str), media_type='application/json')
    except Exception as e:
        # ex_type, ex_value, ex_traceback = sys.exc_info()
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e).split('\n')[0])
        return Response(content=json.dumps({"Success": False, "Error": str(e).split('\n')[0]}, default=str), media_type='application/json')












