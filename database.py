import psycopg2
import hashlib
import base64
from Crypto.Cipher import AES
from config import settings



def connection():
    return psycopg2.connect(host=settings.POSTGRES_HOST, port=settings.POSTGRES_PORT, database=settings.POSTGRES_DB, user=settings.POSTGRES_USER, password=AES.new(hashlib.sha256(base64.b64decode(settings.POSTGRES_SECRET_KEY)).digest(), AES.MODE_CBC, base64.b64decode(settings.POSTGRES_PASSWORD)[:AES.block_size]).decrypt(base64.b64decode(settings.POSTGRES_PASSWORD)[AES.block_size:]).rstrip(b"\0").decode())
