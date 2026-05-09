from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import User, Thread, Post, Comment, Reaction #クラス名は仮、追加機能時（Tweetなど）追加

#定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

csrf = CSRFProtect(app)


# ログインページ表示
@app.route('/', methods = ['GET'])
def login_view():
    if session.get('user_id') is not None:
        return redirect(url_for('threads_view')) #threads関数未作成
    return render_template('auth/login.html') #login画面へ

#ログイン処理
@app.route('/login', methods = ['POST'])
def login_process():
    email_address = request.form.get('email_address')
    password = request.form.get('password')

    # emailまたはpasswordに入力されていないとき
    if email_address == "" or password == "":
        flash('メールアドレスorパスワードが空です', 'error')
    else:
        #Usersテーブルをemailで検索、データがあった場合のエラー処理
        user = User.find_by_email(email_address) #models.py内の関数未設定
        if user is None:
            flash('メールアドレスまたはパスワードが違います', 'error')
        else:
            hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashPassword != user["password"]:
                #辞書機能でuserとpasswordの組み合わせを確認、合致しない場合エラー処理
                flash('メールアドレスまたはパスワードが違います', 'error')
            else:
                #辞書機能でuserとpasswordの組み合わせが合致する場合ログイン処理
                session['user_id'] = user['id']
                return redirect(url_for('threads_view'))
    return redirect(url_for('login_view'))

#ログアウト処理
@app.route('/logout', methods = ['POST']) 
def logout():
    session.clear()
    return redirect(url_for('login_view'))

#サインアップ画面の表示
@app.route('/signup', methods = ['GET']) 
def signup_view():
    if session.get('user_id') is not None:
        return redirect(url_for('threads_view'))

    return render_template('auth/signup.html')
    

#サインアップ処理
@app.route('/signup', methods = ['POST'])
def signup_process():
    user_name = request.form.get('user_name')
    email_address = request.form.get('email_address')
    password = request.form.get('password')
    password_confirmation = request.form.get('password_confirmation')

    #空チェック
    if not user_name or not email_address or not password or not password_confirmation:
        flash('入力されていない項目があります', 'error')
        return redirect(url_for('signup_view'))

    #メール形式のチェック
    if not re.match(EMAIL_PATTERN, email_address):
        flash('メールアドレスの形式になっていません', 'error')
        return redirect(url_for('signup_view'))
    
    #passwordとpasswors_confirmationの一致確認
    if password != password_confirmation:
        flash('入力したパスワードが確認用パスワードと一致しません', 'error')
        return redirect(url_for('signup_view'))
    
    #重複登録確認
    if User.find_by_email(email_address) is not None:
        flash('すでにユーザー登録済みです', 'error')
        return redirect(url_for('signup_view'))    

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() #sha356で良い？

    user_id = User.create(user_name, email_address, hashed_password) ##models.py内の関数未設定
    session['user_id'] = user_id

    return redirect(url_for('threads_view'))


#スレッド一覧画面の表示
@app.route("/threads", methods=["GET"])
def threads_view():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        threads = Thread.get_all()
        for thread in threads:
            thread["created_at"] = thread["created_at"].strftime("%Y/%m/%d %H:%M")
            thread["user_name"] = User.get_name_by_id(thread["user_id"])
            #最新3件のポストを表示
            posts = Post.get_few(thread["id"])
            #リアクション数を表示
            reaction_counts = Reaction.count(thread["id"])
            #コメント数を表示
            comment_counts = Comment.count(thread["id"])
        return render_template("/thread/thread_time_line.html", threads = threads, posts = posts, reaction_counts = reaction_counts, comment_counts = comment_counts)
    
#スレッド作成画面の表示
@app.route("/threads/new", methods=["GET"])
def new_thread_view():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        return render_template("/thread/new.html")

#スレッド作成処理
@app.route("/threads", methods=["POST"])
def create_thread():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        title = request.form.get("title", "").strip()
        image = request.form.get("", "")
        theme_id = request.form.get("theme", "")
        if title == "":
            flash("タイトルが空です", "error")
        elif theme_id == "":
            flash("趣旨を選んでください", "error")
        else:
            thread_id = uuid.uuid4().bytes
            Thread.create(thread_id, user_id, title, image, theme_id)
            flash("スレッドを作成しました", "success")
            return redirect(url_for("user_threads_view"))

#スレッド詳細画面の表示
@app.route("/threads/<uuid:thread_id>", methods=["GET"])
def thread_detail_view(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        #スレッドを表示
        thread = Thread.find_by_id(thread_id)
        if thread is None:
            abort(404)
        thread["created_at"] = thread["created_at"].strftime("%Y/%m/%d %H:%M")
        #リアクション数を表示
        reaction_counts = Reaction.count(thread_id)
        #コメント数を表示
        comment_counts = Comment.count(thread_id)
        #ポストを表示
        posts = Post.get_all(thread_id)
        for post in posts:
            post["created_at"] = post["created_at"].strftime("%Y/%m/%d %H:%M")
        return render_template("thread/thread_detail.html", thread = thread, reaction_counts = reaction_counts, comment_counts = comment_counts, posts = posts)

#スレッド削除処理
@app.route("/threads/<uuid:thread_id>/delete", methods=["POST"])
def delete_thread(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        thread = Thread.find_by_id(thread_id)
        if thread is None:
            abort(404)
        #自分のスレッドのみ削除可能
        elif thread["user_id"] != user_id:
            flash("このスレッドを削除することはできません", "error")
            return redirect(url_for("thread_detail_view"))
        else:
            Thread.delete(thread_id)
            flash("スレッドを削除しました", "success")
            return redirect(url_for("user_threads_view"))


#コメント一覧ページ表示
@app.route("/threads/<uuid:thread_id>/comments", methods=["GET"])
def comments_view(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        #スレッドを表示
        thread = Thread.find_by_id(thread_id)
        if thread is None:
            abort(404)
        thread["created_at"] = thread["created_at"].strftime("%Y/%m/%d %H:%M")
        #リアクション数を表示
        reacition_counts = Reaction.count(thread_id)
        #コメント数を表示
        comments_counts = Comment.count(thread_id)
        #コメントを表示
        comments = Comment.get_all(thread_id)
        for comment in comments:
            comment["created_at"] = comment["created_at"].strftime("%Y/%m/%d %H:%M")
            comment["user_name"] = User.get_name_by_id(comment["user_id"])
        return render_template("/", thread = thread, reacition_counts = reacition_counts, comments_counts = comments_counts, comments = comments)

#コメント投稿画面の表示
@app.route("/threads/<uuid:thread_id>/comments/new", methods=["GET"])
def new_comment_view(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        thread = Thread.find_by_id(thread_id)
        if thread is None:
            abort (404)
        else:
            return render_template("/")

#コメント投稿処理
@app.route("/threads/<uuid:thread_id>/comments/new", methods=["POST"])
def create_comment(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        content = request.form.get("content", "").strip()
        if content == "":
            flash("コメントが空です", "error")
        else:
            comment_id = uuid.uuid4().bytes
            Comment.create(comment_id, user_id, thread_id, content)
            flash("コメントを投稿しました", "error")
            return redirect(url_for("comments_view", thread_id = thread_id))

#コメント削除処理
@app.route("/threads/<uuid:thread_id>/comments/<uuid:comment_id/delete", methods=["POST"])
def delete_comment(thread_id, comment_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login_view"))
    else:
        comment = Comment.find_by_id(comment_id)
        if comment is None:
            abort(404)
        elif comment["user_id"] != user_id:
            flash("このコメントを削除することはできません", "error")
            return redirect(url_for("comments_view", thread_id = thread_id))
        else:
            Comment.delete(comment_id)
            flash("コメントを削除しました", "success")
            return redirect(url_for("comments_view", thread_id = thread_id))















































#ポスト作成処理
@app.route("/threads/<uuid:thread_id>/posts", methods = ["POST"]) 
def create_post(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('login_view'))
    content = request.form.get("post", "").strip()
    image = request.form.get("") #imageをどう書くか？
    count = request.form.get("count", "").strip()
    rep = request.form.get("rep", "").strip()
  

    if content == "":
        flash("トレーニング記録を入力してください", "error")
        return redirect(url_for("thread_detail_view"))
    elif count == "":
        flash("トレーニング回数を入力してください", "error")
        return redirect(url_for('', thread_id = thread_id)) 
    else:
        post_id = uuid.uuid4().bytes
        Post.create(post_id, user_id, thread_id, content, image, count, rep)
        flash("トレーニング記録を作成しました", "success")
        return redirect(url_for("thread_detail_view", thread_id = thread_id))
    
#ポスト削除処理
@app.route("/threads/<uuid:thread_id>/posts/<uuid:post_id>/delete", methods = ["POST"])
def post_delete(post_id, thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('login_view'))
    
    post = Post.find_by_id(post_id)

    if post is None:
        flash("トレーニング記録がありません", "error")
        return redirect(url_for("thread_detail_view", thread_id = thread_id))
    
    if post['user_id'] != user_id:
        flash("このトレーニング記録は削除できません", "error")
        return redirect(url_for("thread_detail_view", thread_id = thread_id))
    
    Post.delete(post_id)
    flash("トレーニング記録が削除されました", "success")
    return redirect(url_for("thread_detail_view", thread_id = thread_id))

#ポスト一覧表示機能⇒thread詳細表示機能にpost表示を含めている

#リアクション送信機能
@app.route("/threads/<uuid:thread_id>", methods = ["POST"])
def create_reaction(thread_id):
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for('login_view'))
    
    reaction_id = request.form.get("reaction") #HTML変数確認

    if reaction_id == "":
        flash("リアクション内容がありません", "error")
        return redirect(url_for("thread_detail_view", thread_id = thread_id))
    
    #すでに送信済みのリアクションかを確認
    existing_reaction = Reaction.find_same_reaction(user_id, thread_id, reaction_id)

    if existing_reaction is None:
        #初めてリアクションを送る場合
        Reaction.create(user_id, thread_id, reaction_id)
        flash('リアクションを送信しました', 'success')
        return redirect(url_for("thread_detail_view", thread_id = thread_id))

    #すでに同一リアクションを送っている場合はDBをUPDATEする
    else:
        Reaction.update(user_id, thread_id, reaction_id)
        flash("リアクションを送信しました", "success")
        return redirect(url_for("thread_detail_view", thread_id = thread_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
