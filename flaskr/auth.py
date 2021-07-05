import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, close_db

import re

from flask_mail import Mail, Message

from itsdangerous.url_safe import URLSafeTimedSerializer

import os

SALT = 'dev'


def isalnum(s):
    alnumReg = re.compile(r'^[a-zA-Z0-9]+$')
    return alnumReg.match(s) is not None

def pass_vali(s):
    vali=re.compile(r'\A(?=.*?[a-z])(?=.*?[A-Z])(?=.*?\d)[a-zA-Z\d]{5,100}\Z')
    return vali.match(s) is not None

def create_token(user_id, secret_key, salt):
    ''' user_idからtokenを生成
    '''
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(user_id, salt=salt)

def load_token(token, secret_key, salt):
    ''' tokenからuser_idとtimeを取得
    '''
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.loads(token, salt=salt, max_age=600)



bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        fit_id = request.form['fit_id'].lower()
        username = request.form['username']
        password = request.form['password']
        password_c = request.form['password_c']
        gender = request.form['RadioGender']
        age = request.form['age']

        db = get_db()
        error = None

        try:
            age = int(age)
        except:
            error = '年齢は半角数字のみで入力してください。'

        if not username:
            error = 'ユーザー名を入力してください。'
        elif not password:
            error = 'パスワードを入力してください。'
        elif not fit_id:
            error = '学籍番号を入力してください。'

        # 学籍番号の存在確認
        db.execute("SELECT * FROM users WHERE fit_id = %s", (fit_id,))
        info = db.fetchone()
        if info is not None:
            error = '学籍番号: {}はすでにアカウントが存在します。'.format(fit_id)

        # 学籍番号の形式の判定
        if len(fit_id) != 7:
            error = '正しい形式で学籍番号を入力してください。'

        if not (password == password_c):
            error = 'パスワードが一致していません。'

        if not isalnum(fit_id):
            error = '学籍番号は半角英数字で入力してください。'
        if not pass_vali(password):
            error = 'パスワード脆弱です。'

        if error is None:
            db.execute(
                'INSERT INTO users (i_o, fit_id, username, password, gender, age) VALUES (%s, %s, %s, %s, %s, %s)',
                (1, fit_id, username, generate_password_hash(password), gender, age)
            )
            g.conn.commit()
            close_db()
            flash('アカウントの作成に成功しました。', "alert alert-success")
            return redirect(url_for('auth.login'))

        flash(error, "alert alert-danger")
        close_db()
    return render_template('auth/register.html')

@bp.route('/register_guest', methods=('GET', 'POST'))
def register_guest():
    fit_id = ''
    if request.method == 'POST':
        fit_id = request.form['fit_id'].lower()
        username = request.form['username']
        password = request.form['password']
        password_c = request.form['password_c']
        gender = request.form['RadioGender']
        age = request.form['age']

        db = get_db()
        error = None

        try:
            age = int(age)
        except:
            error = '年齢は半角数字のみで入力してください。'

        if not username:
            error = 'ユーザー名を入力してください。'
        elif not password:
            error = 'パスワードを入力してください。'

        if not (password == password_c):
            error = 'パスワードが一致していません。'

        if not pass_vali(password):
            error = 'パスワード脆弱です。'

        if error is None:
            db.execute(
                'INSERT INTO users (i_o, fit_id, username, password, gender, age) VALUES (%s, %s, %s, %s, %s, %s)',
                (0, fit_id, username, generate_password_hash(password), gender, age)
            )
            g.conn.commit()
            close_db()
            flash('アカウントの作成に成功しました。', "alert alert-success")
            return redirect(url_for('auth.login'))

        flash(error, "alert alert-danger")
        close_db()
    else:
        conn = get_db()
        conn.execute('SELECT fit_id FROM users WHERE i_o = %s ORDER BY id desc', (0,))
        u = conn.fetchone()
        if u is None:
            fit_id = '0000001'
        else:
            u = str(int(u[0])+1)
            for i in range((7-len(u))):
                fit_id += '0'
            fit_id += u
        close_db()
    return render_template('auth/register_guest.html', f_i = fit_id)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        fit_id = request.form['fit_id'].lower()
        password = request.form['password']
        db = get_db()
        error = None
        user = None
        db.execute("SELECT * FROM users WHERE fit_id = %s", (fit_id,))
        user = db.fetchone()
        if user is None:
            error = 'このユーザー名は存在しません。'
        elif not check_password_hash(user['password'], password):
            error = 'パスワードが正しくありません。'

        if error is None:
            #user = user.fetchone().description
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            flash('ログインしました。', "alert alert-success")
            cur = get_db()
            cur.execute('SELECT * FROM users WHERE id = %s', (user['id'],))
            g.user = cur.fetchone()
            close_db()
            return redirect(url_for('upload.index'))

        flash(error, "alert alert-danger")
        close_db()
    return render_template('auth/login.html')

# TODO: メールでのパスワード再設定の処理の記述
@bp.route('/forget_pass')
def forget_pass():
    return render_template('auth/forget_pass.html')

@bp.route('/send_mail_test', methods=['GET', 'POST'])
def send_mail_test():
    if request.method == 'POST':
        email = request.form['email']
        if not email:
            flash('メールアドレスが入力されていません。', "alert alert-danger")
            return redirect(url_for('auth.forget_pass'))
        token = create_token(email, current_app.config['SECRET_KEY'], SALT)
        url = url_for('auth.new_pass', token=token, _external=True)
        mail = Mail(current_app)
        msg = Message('パスワードの再設定', recipients=[email])
        msg.body = ('''以下のリンクから、再設定のページへとんで、再設定を行ってください。\n
                    ( * リンクの有効期限は10分です。)\n
                    {}'''.format(url))
        msg.html = ('''<h1>パスワードの再設定</h1>
                    <p>以下のリンクから、再設定のページへとんで、再設定を行ってください。<br />
                    ( <b>* リンクの有効期限は10分です。</b>)<br />
                    <a href="{}">{}</a></p>'''.format(url, url))
        mail.send(msg)
        flash('メールを送信しました。', "alert alert-success")
        return redirect(url_for('upload.index'))
    else:
        flash('エラーが発生しました。', "alert alert-danger")
        return redirect(url_for('auth.forget_pass'))
    return

@bp.route('/new_pass', methods=["GET", "POST"])
def new_pass():
    if request.method == 'POST':
        username = request.form['username']
        fit_id = request.form['fit_id']
        password = request.form['password']
        password_c = request.form['password_c']
        db = get_db()
        error = None

        if not username:
            error = 'ユーザー名を入力してください。'
        elif not password:
            error = 'パスワードを入力してください。'
        elif not fit_id:
            error = '学籍番号を入力してください。'
        # 学籍番号の形式の判定
        if len(fit_id) != 7:
            error = '正しい形式で学籍番号を入力してください。'
        if not (password == password_c):
            error = 'パスワードが一致していません。'

        if not isalnum(fit_id):
            error = '学籍番号は半角英数字で入力してください。'

        if not pass_vali(password):
            error = 'パスワード脆弱です。'

        db.execute("SELECT * FROM users WHERE fit_id = %s AND username = %s", (fit_id,username,))
        info = db.fetchone()
        if info is None:
            error = '登録した氏名と学籍番号が一致しません。'

        if error is None:
            db.execute('UPDATE users SET password = %s WHERE fit_id = %s', (generate_password_hash(password), fit_id))
            g.conn.commit()
            close_db()
            flash('パスワードを再設定しました。', "alert alert-success")
            return redirect(url_for('auth.login'))
        flash(error, "alert alert-danger")
        close_db()
    return render_template('auth/new_pass.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        cur = get_db()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        g.user = cur.fetchone()
        close_db()

@bp.route('/logout')
def logout():
    session.clear()
    flash('ログアウトしました。', "alert alert-success")
    return redirect(url_for('upload.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
