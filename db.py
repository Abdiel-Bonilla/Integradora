import psycopg2
from psycopg2 import pool

#crear pool de connecion
connection_pool=pool.SimpleConnectionPool(
    1,20,
    database= "spvtcd",
    user="postgres",
    password="Kokies13",
    host="localhost",
    port="5432"
)

def conectar():
    return connection_pool.getconn()

def desconectar(conn):
    connection_pool.putconn(conn)

