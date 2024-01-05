import sys
import json

from typing import List
from datetime import timedelta, datetime

from starlette import status
from fastapi import APIRouter, HTTPException, Depends, Request, Response

router = APIRouter(
    prefix='/utility',
    tags=['utility']
)


@router.get('/servertimestamp', status_code=status.HTTP_200_OK)
def protected():
    ret = Response(content=json.dumps(datetime.today(), default=str), media_type='application/json')
    return ret












