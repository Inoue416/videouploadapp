from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, make_response, jsonify
)
import werkzeug

from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db, close_db
import os
import re
from datetime import datetime
from flaskr.googleAPI.upload_googledrive import upload_drive

from flask_bootstrap import Bootstrap
from flask_paginate import Pagination, get_page_parameter

bp = Blueprint('upload', __name__)
danger = "alert alert-danger"
success = "alert alert-success"


@bp.route('/')
def index():
    return render_template('upload/index.html')

@bp.route('/introduction')
def introduction():
    return render_template('upload/introduction.html')

@bp.route('/tweet_list')
@login_required
def tweet_list():
    #if g.user:
    filter = False
    db = get_db()
    #アップロード状況を取得
    db.execute('SELECT file_id FROM posts WHERE author_id = %s', (session.get('user_id'),))
    uploaded = db.fetchall()
    # ビデオデータベース情報を取得
    data = db.execute('SELECT * FROM tweets ORDER BY id')
    data = db.fetchall()

    # フィルタ処理
    if len(uploaded) >= len(data):
        filter = True
    max_age = 60 * 60 * 24
    expires = int(datetime.now().timestamp()) + max_age
    i = 0
    for u in uploaded:
        for d in data:
            if u[0] == d[1]:
                data.remove(d)

    # ページネーション
    page_disp_msg = '表示範囲 <b>{start}件 - {end}件 </b> 合計：<b>{total}</b>件'
    page = request.args.get(get_page_parameter(), type=int, default=1)
    da = data[(page - 1)*10: page*10]
    pagination = Pagination(page=page, total=len(data), search=False, per_page=10, css_framework='bootstrap4',display_msg=page_disp_msg)
    resp = make_response(render_template('upload/tweet_list.html', data=da, filter=filter, pagination=pagination))
    resp.set_cookie(key='user_id', value=str(session.get('user_id')), max_age=max_age, path=request.path,
    expires=expires, httponly=True, secure=False)
    close_db()
    """else:
        resp = make_response(redirect(url_for('upload.index')))"""
    return resp

@bp.route('/ita_list')
@login_required
def ita_list():
    #if g.user:
    filter = False
    db = get_db()
    #アップロード状況を取得
    db.execute('SELECT file_id FROM posts WHERE author_id = %s', (session.get('user_id'),))
    uploaded = db.fetchall()
    # ビデオデータベース情報を取得
    data = db.execute('SELECT * FROM itas ORDER BY id')
    data = db.fetchall()

    # フィルタ処理
    if len(uploaded) >= len(data):
        filter = True
    max_age = 60 * 60 * 24
    expires = int(datetime.now().timestamp()) + max_age
    i = 0
    for u in uploaded:
        for d in data:
            if u[0] == d[1]:
                data.remove(d)

    # ページネーション
    page_disp_msg = '表示範囲 <b>{start}件 - {end}件 </b> 合計：<b>{total}</b>件'
    page = request.args.get(get_page_parameter(), type=int, default=1)
    da = data[(page - 1)*10: page*10]
    pagination = Pagination(page=page, total=len(data), search=False, per_page=10, css_framework='bootstrap4',display_msg=page_disp_msg)
    resp = make_response(render_template('upload/ita_list.html', data=da, filter=filter, pagination=pagination))
    resp.set_cookie(key='user_id', value=str(session.get('user_id')), max_age=max_age, path=request.path,
    expires=expires, httponly=True, secure=False)
    close_db()
    """else:
        resp = make_response(redirect(url_for('upload.index')))"""
    return resp

@bp.route('/upload_tweet/<file_id>')
@login_required
def upload_tweet(file_id):
    #if g.user:
    if file_id == None:
        return redirect(url_for('upload.index'))
    cur = get_db()
    cur.execute('SELECT * FROM tweets WHERE file_id = %s', (file_id,))
    data = cur.fetchone()
    close_db()
    resp = make_response(render_template('upload/upload_tweet.html', file_id=file_id, data=data))
    """else:
        resp = make_response(redirect(url_for('upload.index')))"""
    return resp

@bp.route('/upload_ita/<file_id>')
@login_required
def upload_ita(file_id):
    #if g.user:
    if file_id == None:
        return redirect(url_for('upload.index'))
    cur = get_db()
    cur.execute('SELECT * FROM itas WHERE file_id = %s', (file_id,))
    data = cur.fetchone()
    close_db()
    resp = make_response(render_template('upload/upload_ita.html', file_id=file_id, data=data))
    """else:
        resp = make_response(redirect(url_for('upload.index')))"""
    return resp


@bp.route('/save_tweet/<file_id>', methods=['POST'])
@login_required
def save_tweet(file_id):
    if 'video' not in request.files:
        flash('ファイルが選択されていません。', danger)
        resp = make_response(redirect(url_for('upload.upload_tweet', file_id=file_id)))
    else:
        UPLOAD_PATH = 'flaskr/video'
        db = get_db()
        db.execute('SELECT * FROM tweets WHERE file_id = %s', (file_id,))
        # 動画のデータベース情報を獲得
        data = db.fetchone()
        v_num = data['num']
        video = request.files['video']

        db.execute('SELECT gender, age FROM users WHERE id = %s', (session.get('user_id'),))
        u_data = db.fetchone()
        gender = u_data['gender']
        age = u_data['age']

        exd = re.findall(r'\.\w*', video.filename)
        filename = UPLOAD_PATH + (('/{}_{}{}').format(file_id, v_num, exd[0]))
        videoname = (('{}_{}{}').format(file_id, v_num, exd[0]))
        video.save(os.path.join(UPLOAD_PATH, videoname))

        db.execute('INSERT INTO posts (author_id, file_id, gender, age, created) VALUES(%s,%s,%s,%s,CURRENT_TIMESTAMP)', (session.get('user_id'), file_id, gender, age))
        g.conn.commit()
        upload_drive(foldername=file_id, videopath=filename, videoname=videoname)
        v_num += 1
        db.execute('UPDATE tweets SET num = %s, created = CURRENT_TIMESTAMP WHERE file_id = %s', (v_num, file_id))
        g.conn.commit()
        flash('アップロードしました。ありがとうございます。', success)
        close_db()
        resp = make_response(redirect(url_for('upload.index')))
    return resp

@bp.route('/save_ita/<file_id>', methods=['POST'])
@login_required
def save_ita(file_id):
    if 'video' not in request.files:
        flash('ファイルが選択されていません。', danger)
        resp = make_response(redirect(url_for('upload.upload_ita', file_id=file_id)))
    else:
        UPLOAD_PATH = 'flaskr/video'
        db = get_db()
        db.execute('SELECT * FROM itas WHERE file_id = %s', (file_id,))
        # 動画のデータベース情報を獲得
        data = db.fetchone()
        v_num = data['num']
        video = request.files['video']

        db.execute('SELECT gender, age FROM users WHERE id = %s', (session.get('user_id'),))
        u_data = db.fetchone()
        gender = u_data['gender']
        age = u_data['age']

        exd = re.findall(r'\.\w*', video.filename)
        filename = UPLOAD_PATH + (('/{}_{}{}').format(file_id, v_num, exd[0]))
        videoname = (('{}_{}{}').format(file_id, v_num, exd[0]))
        video.save(os.path.join(UPLOAD_PATH, videoname))

        db.execute('INSERT INTO posts (author_id, file_id, gender, age, created) VALUES(%s,%s,%s,%sCURRENT_TIMESTAMP)', (session.get('user_id'), file_id, gender, age))
        g.conn.commit()
        upload_drive(foldername=file_id, videopath=filename, videoname=videoname)
        v_num += 1
        db.execute('UPDATE itas SET num = %s, created = CURRENT_TIMESTAMP WHERE file_id = %s', (v_num, file_id))
        g.conn.commit()
        flash('アップロードしました。ありがとうございます。', success)
        close_db()
        resp = make_response(redirect(url_for('upload.index')))
    return resp
