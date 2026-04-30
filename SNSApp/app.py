from flask import Flask, request, redirect, render_template, session, flash, abort, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import hashlib
import uuid
import re
import os


# 定数定義
EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
SESSION_DAYS = 30

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', uuid.uuid4().hex)
app.permanent_session_lifetime = timedelta(days=SESSION_DAYS)

csrf = CSRFProtect(app)

@app.route('/threads', methods=['GET'])
def timeline():
    threads = [
        {
            "username": "田中 太郎",
            "title": "5月中は毎日スクワット30回",
            "created_at": "一週間前",
            "exercises": [
                {"count": 5, "sets": 3, "comment": "膝が痛かった"},
                {"count": 10,  "sets": 3, "comment": ""},
                {"count": 10, "sets": 2, "comment": "きつかった！"},
            ],
            "reaction_type": "あきらめるな",
            "reaction_count": 24,
            "comments_count": 5,
        },
        {
            "username": "山田 花子",
            "title": "3か月連続で毎日上体起こし20回",
            "created_at": "2時間前",
            "exercises": [
                {"count": 5,  "sets": 4, "comment": "できた"},
                {"count": 10, "sets": 2, "comment": "調子よかった"},
                {"count": 5, "sets": 2, "comment": "調子が悪かった"},
            ],
            "reaction_type": "すごい！",
            "reaction_count": 10,
            "comments_count": 2,
        },
    ]
    return render_template("thread/thread_time_line.html", threads=threads)

if __name__ == '__main__':
    app.run()
    app.run(host="0.0.0.0", debug=True)