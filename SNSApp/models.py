from flask import abort
import pymysql
from util.DB import DB
import uuid

#初回起動時にコネクションプールを作成して接続を作成
db_pool = DB.init_db_pool()

#ユーザークラス
class Users:
    @classmethod
    #DBに新たにデータを追加
    def create(cls, user_name, email_address, password):
        user_id = uuid.uuid4().hex #uuid4でuser_idを生成して16進数文字列化
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO Users (id, user_name, email_address, password) VALUES (%s, %s, %s, %s);"
                cur.execute(sql, (user_id, user_name, email_address, password))
                conn.commit()
                return user_id
            
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)

        finally:
            db_pool.release(conn)
    
    
    #DB内をEmail_addressで検索
    @classmethod
    def find_by_email(cls, email_address):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM Users WHERE email_address = %s;"
                cur.execute(sql, (email_address,))
                user = cur.fetchone() 
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)

