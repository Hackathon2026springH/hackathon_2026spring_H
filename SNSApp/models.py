from flask import abort
import pymysql
from util.DB import DB
import uuid

#初回起動時にコネクションプールを作成して接続を作成
db_pool = DB.init_db_pool()

#ユーザークラス
class User:
    @classmethod
    #DBに新たにデータを追加
    def create(cls, user_name, email_address, password):
        user_id = uuid.uuid4().bytes #uuid4でuser_idを生成してバイナリ形式に変換
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

#Threadクラス
class Thread:
    @classmethod
    def get_all(cls):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM threads ORDER BY created_at DESC;"
                cur.execute(sql)
                threads = cur.fetchall()
            return threads
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
        
    @classmethod
    def create(cls, thread_id, user_id, title, image, theme_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO threads (id, user_id, title, image, thme_id) VALUE (%s, %s, %s, %s, %s);"
                cur.execute(sql, (thread_id, user_id, title, image, theme_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

class Post:
    @classmethod
    def create(cls, use_id, thread_id, content, image, number, rep):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO Posts(id, user_id, thread_id, content, image, count, rep) VALUE (%S, %S, %S, %S, %S, %S, %S);"
                cur.execute(sql,(post_id, user_id, thread_id, content, image, count, rep))
                conn.commit()
        except pymysql.Error as {e}:
            print(f"エラーが発生しています：{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FORM Posts WHERE ID = %s"
                cur.execute(sql, (post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f"トレーニング記録がありません：{e}")
        finally:
            db_pool.release(conn)
    
    @classmethod
    def delete(cls, post_id):
        conn =db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                #DBにはdeleted_atカラム未設定
                sql = "UPDATE Posts SET deleted_at = NOW() WHERE id = %s;"
                #直接データを削除する場合
                # sql = "DELETE FROM Posts WHERE id = %s;"
                cur.execute(sql, (post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f"トレーニング記録がありません：{e}")
        finally:
            db_pool.release(conn)
    
                  


