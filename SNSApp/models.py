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
                sql = "INSERT INTO users (id, user_name, email_address, password) VALUES (%s, %s, %s, %s);"
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
                sql = "SELECT * FROM users WHERE email_address = %s;"
                cur.execute(sql, (email_address,))
                user = cur.fetchone() 
            return user
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
            abort(500)
        finally:
            db_pool.release(conn)


    @classmethod
    def get_name_by_id(cls, user_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT user_name FROM users WHERE id=%s;"
                cur.execute(sql, (user_id,))
                user = cur.fetchone()
            return user
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
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
                sql = "SELECT * FROM threads WHERE deleted_at IS NULL ORDER BY created_at DESC;"
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
                cur.execute(sql, (thread_id, user_id, title, image, theme_id))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def find_by_id(cls, thread_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM threads WHERE id=%s AND deleted_at IS NULL;"
                cur.execute(sql, (thread_id,))
                thread = cur.fetchone()
            return thread
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, thread_id):
        conn =db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE threads SET deleted_at = NOW() WHERE id=%s;"
                cur.execute(sql, (thread_id,))
                cur.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)


#Postクラス
class Post:
    @classmethod
    def get_all(cls, thread_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM posts WHERE id=%s AND deleted_at IS NULL ORDER BY created_at DESC;"
                cur.execute(sql, (thread_id,))
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def get_few(cls, thread_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM posts WHERE id=%s AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 3;"
                cur.execute(sql, (thread_id,))
                posts = cur.fetchall()
            return posts
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    #ポストidでの検索
    def find_by_id(cls, post_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM Posts WHERE id = %s AND deleted_at IS NULL"
                cur.execute(sql, (post_id,))
                post = cur.fetchone()
            return post
        except pymysql.Error as e:
            print(f"エラーが発生しています：{e}")
        finally:
            db_pool.release(conn)

    #ポスト作成
    @classmethod
    def create(cls, post_id, user_id, thread_id, content, image, count, rep):
        post_id = uuid.uuid4().bytes #uuid4でpost_idを生成してバイナリ形式に変換
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO posts(id, user_id, thread_id, content, image, count, rep) VALUE (%S, %S, %S, %S, %S, %S, %S);"
                cur.execute(sql,(post_id, user_id, thread_id, content, image, count, rep))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています：{e}")
            abort(500)
        finally:
            db_pool.release(conn) 

    
    #ポスト削除機能
    @classmethod
    def delete(cls, post_id):
        conn =db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE posts SET deleted_at = NOW() WHERE id = %s;"
                cur.execute(sql, (post_id,))
                conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています：{e}")
        finally:
            db_pool.release(conn)

#Reactionクラス
class Reaction:
    @classmethod
    def find_same_reaction(cls, user_id, thread_id, reaction_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM thread_reactions WHERE user_id = %s AND thread_id = %s AND reaction_id = %s"
                cur.execute(sql, (user_id, thread_id, reaction_id))
                reaction = cur.fetchone()
            return reaction
        except pymysql.Error as e:
            print(f'エラーが発生しています：{e}')
        finally:
            db_pool.release(conn)

    @classmethod
    def create(cls, user_id, thread_id, reaction_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO Thread_reactions(user_id, thread_id, reaction_id) VALUES(%s, %s, %s);" #reaction_countカラムへの入力は不要？
                cur.execute(sql, (user_id, thread_id, reaction_id))
                conn.commit()
                #reaction_idはAuto_increment
        except pymysql.Error as e:
            print(f"エラーが発生しています：{e}")
        finally:
            db_pool.release(conn)

    @classmethod
    def update(cls, user_id, thread_id, reaction_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                #リアクション上限到達確認
                sql = "SELECT reaction_count FROM thread_reactions WHERE user_id = %s AND thread_id = %s AND reaction_id = %s"
                cur.execute(sql, (user_id, thread_id, reaction_id))
                row = cur.fetchone()
                if row is None:
                    print(f"該当するリアクションがありません")
                    return
                
                current_reaction_count = row [0]

                if current_reaction_count >= 100:
                    print("リアクション数が上限に達しています")
                    return
                #reaction_countに+1する
                else:
                    sql = "UPDATE thread_reactions SET reaction_count = reaction_count + 1 WHERE user_id = %s AND thread_id = %s AND reaction_id = %s" #default設定が必要？
                    cur.execute(sql, (user_id, thread_id, reaction_id))             
                    conn.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています：{e}")
        finally:
            db_pool.release(conn)
        
    @classmethod
    def count(cls, thread_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT reaction_id, reaction_name, SUM(reaction_count) FROM thread_reactions INNER JOIN reactions ON thread_reactions.reaction_id = reactions.id WHERE thread_id=%s GROUP BY reaction_id;"
                cur.execute(sql, (thread_id,))
                reaction_counts = cur.fetchall()
            return reaction_counts
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)


#Commentクラス
class Comment:
    @classmethod
    def get_all(cls, thread_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT * FROM comments WHERE thread_id=%s AND deleted_at IS NULL ORDER BY created_at DESC;"
                cur.execute(sql, (thread_id,))
                comments = cur.fetchall()
            return comments
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)
    
    @classmethod
    def count(cls, thread_id):
        conn =db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "SELECT COUNT(id) FROM comments WHERE thread_id=%s AND deleted_at IS NULL;"
                cur.execute(sql, (thread_id,))
                comment_counts = cur.fetchone()
            return comment_counts
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def create(cls, comment_id, user_id, thread_id, content):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "INSERT INTO comments (id, user_id, thread_id, content) VALUE (%s, %s, %s, %s);"
                cur.execute(sql, (comment_id, user_id, thread_id, content))
                cur.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)

    @classmethod
    def delete(cls, comment_id):
        conn = db_pool.get_conn()
        try:
            with conn.cursor() as cur:
                sql = "UPDATE comments SET deleted_at = NOW() WHERE id=%s;"
                cur.execute(sql, (comment_id,))
                cur.commit()
        except pymysql.Error as e:
            print(f"エラーが発生しています:{e}")
            abort(500)
        finally:
            db_pool.release(conn)