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
    prefix='/report',
    tags=['report']
)


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.get('/salesmonth', status_code=status.HTTP_200_OK)
def protected(truncmonth: str, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectsales(par_truncmonth => %(par_truncmonth)s) ORDER BY \"Date\", \"JO\";", {"par_truncmonth": truncmonth})
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/salesyear', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.vw_salesyear;")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/soa', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectsoa();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/commcollect', status_code=status.HTTP_200_OK)
def protected(truncmonth: str, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectcommcollect(par_truncmonth => %(par_truncmonth)s);", {"par_truncmonth": truncmonth})
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/corpcomm', status_code=status.HTTP_200_OK)
def protected(truncmonth: str, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectcorpcomm(par_truncmonth => %(par_truncmonth)s);", {"par_truncmonth": truncmonth})
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret


@router.get('/salesrepcomm', status_code=status.HTTP_200_OK)
def protected(truncmonth: str, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectsalesrepcomm(par_truncmonth => %(par_truncmonth)s);", {"par_truncmonth": truncmonth})
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret












