import os
import pymysql
from dbutils.pooled_db import PooledDB

class _Pool:
    def __init__(self, pool):
        self._pool = pool

    def get_conn(self):
        return self._pool.connection()

    def release(self, conn):
        conn.close()

class DB:
    @classmethod
    def init_db_pool(cls):
        pool = PooledDB(
            creator=pymysql,
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE'),
            maxconnections=10,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return _Pool(pool)