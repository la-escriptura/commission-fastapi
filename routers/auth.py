import json

import psycopg2.extras
import base64
from typing import List
from datetime import timedelta
from starlette import status
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from passlib.context import CryptContext
from pydantic import BaseModel
from redis import Redis
from database import connection
from config import settings

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


class Settings(BaseModel):
    authjwt_secret_key: str = base64.b64decode(settings.JWT_SECRET_KEY).decode('utf-8')
    authjwt_public_key: str = base64.b64decode(settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(settings.JWT_PRIVATE_KEY).decode('utf-8')
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_encode_issuer: str = settings.JWT_ENCODE_ISSUER
    authjwt_decode_issuer: str = settings.JWT_DECODE_ISSUER
    authjwt_access_token_expires: int = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
    authjwt_refresh_token_expires: int = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
    authjwt_denylist_enabled: bool = settings.JWT_DENYLIST_ENABLED
    authjwt_denylist_token_checks: set = set(settings.JWT_DENYLIST_TOKEN_CHECKS.split(','))


class User(BaseModel):
    email: str
    password: str


class Password(BaseModel):
    oldpassword: str
    newpassword: str


redis_conn = Redis(host='localhost', port=6379, db=0, decode_responses=True)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = connection()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(email: str, password: str, conn):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM com.ufn_selectuserbyemail(%(par_email)s);", {"par_email": email})
    resultSet = cursor.fetchone()
    cursor.close()

    if not resultSet:
        return False
    if not bcrypt_context.verify(password, resultSet['passwordhash']):
        return False
    return resultSet


async def get_current_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        return current_user
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


@AuthJWT.load_config
def get_config():
    return Settings()


# Create our function to check if a token has been revoked. In this simple
# case, we will just store the tokens jti (unique identifier) in redis.
# This function will return the revoked status of a token. If a token exists
# in redis and value is true, token has been revoked
@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'


@router.post('/login', status_code=status.HTTP_200_OK)
def login(user: User, Authorize: AuthJWT = Depends(), conn = Depends(get_db)):
    userAuth = authenticate_user(user.email, user.password, conn)

    if not userAuth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    access_token = Authorize.create_access_token(subject=userAuth['userid'])
    refresh_token = Authorize.create_refresh_token(subject=userAuth['userid'])
    return {
        "first_name": userAuth['first_name'],
        "rolename": userAuth['rolename'],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expires": settings.JWT_ACCESS_TOKEN_EXPIRES
    }


@router.post('/changepassword', status_code=status.HTTP_200_OK)
def changepassword(password: Password, user_id: str = Depends(get_current_user), conn = Depends(get_db)):
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM com.ufn_selectuserbyid(%(par_userid)s);", {"par_userid": user_id})
        resultSet = cursor.fetchone()

        if not resultSet:
            raise Exception("Could not validate user.")
        if not bcrypt_context.verify(password.oldpassword, resultSet['passwordhash']):
            raise Exception("Could not validate user.")

        cursor.execute("CALL com.usp_updateuser (par_userid => %(par_userid)s, par_newpasswordhash => %(par_newpasswordhash)s);", {"par_userid": user_id, "par_newpasswordhash": bcrypt_context.hash(password.newpassword)})
        conn.commit()
        cursor.close()
        return Response(content=json.dumps({"Success": True}, default=str), media_type='application/json')
    except Exception as e:
        # ex_type, ex_value, ex_traceback = sys.exc_info()
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e).split('\n')[0])
        return Response(content=json.dumps({"Success": False, "Error": str(e).split('\n')[0]}, default=str), media_type='application/json')


@router.post('/refresh', status_code=status.HTTP_200_OK)
def refresh(Authorize: AuthJWT = Depends()):
    try:
        """
        The jwt_refresh_token_required() function insures a valid refresh
        token is present in the request before running any code below that function.
        we can use the get_jwt_subject() function to get the subject of the refresh
        token, and use the create_access_token() function again to make a new access token
        """
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()

        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        jti = Authorize.get_raw_jwt()['jti']
        redis_conn.setex(jti, timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES), 'true')

        new_access_token = Authorize.create_access_token(subject=current_user)
        new_refresh_token = Authorize.create_refresh_token(subject=current_user)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_expires": settings.JWT_ACCESS_TOKEN_EXPIRES
        }
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')



