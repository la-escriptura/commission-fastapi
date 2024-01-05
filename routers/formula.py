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
    prefix='/formula',
    tags=['formula']
)


def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()


@router.get('/all', status_code=status.HTTP_200_OK)
def protected(user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectformula();")
    ret = Response(content=json.dumps(cursor.fetchall(), default=str), media_type='application/json')
    cursor.close()
    return ret












