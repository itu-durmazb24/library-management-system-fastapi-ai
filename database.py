import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
sifre = os.getenv("SIFRE")

mydb = psycopg2.connect(
    host="localhost",
    port=1234,
    database="kutuphane_db",
    user="postgres",
    password=sifre
)