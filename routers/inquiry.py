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
    prefix='/inquiry',
    tags=['inquiry']
)


class TranNo(BaseModel):
    joborderno: str
    invoiceno: str
    orno: str


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.post('/master', status_code=status.HTTP_200_OK)
def protected(tranno: TranNo, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectmaster(par_json => %(par_json)s);", {"par_json": tranno.json()})
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret












