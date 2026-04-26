from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os

from models import User, Thread, Post, Coomment, Reaction #クラス名は仮、追加機能時（Tweetなど）追加

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
        return redirect(url_for('threads')) #threads関数未作成
    return render_template('auth/login.html') #login画面へ

#ログイン処理
@app.route('/login', methods = ['POST'])
def login_process():
    email = request.form.get('email')
    password = request.form.get('password')

    # emailまたはpasswordに入力されていないとき
    if email == "" or password == "":
        flash('メールアドレスorパスワードが空です', 'error')
    else:
        #Userテーブルをemailで検索、データがあった場合のエラー処理
        user = User.find_by_email(email) #models.py未設定
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
                return redirect(url_for('threads'))
        return redirect(url_for('login_view'))

#ログアウト処理
@app.route('/logout', methods = ['POST']) #POSTメソッドの指定は不要？
def logout():
    session.clear()
    return redirect(url_for('login_view'))
