import os
import pymysql
from pymysqlpool.pool import pool

class DB:
    @classmethod
    def init_db_pool(cls):
        pool = pool(
            host = os.getenv('DB_HOST'), #データベースホスト
            user = os.getenv('DB_USER'), #データベースユーザー
            password = os.getenv('DB_PASSWORD'), #データベースパスワード
            database = os.getenv('DB_DATABASE'),
            max_size = 10, #仮設定
            charset = "utf8mb4", #文字コード
            cursorclass = pymysql.cursors.DictCursor　#カーソルクラス
            autocommit = True
        )

        pool.init()
        return pool