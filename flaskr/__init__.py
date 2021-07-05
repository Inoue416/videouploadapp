import os

from flask import Flask

from datetime import timedelta

from flask_mail import Mail


import sys
sys.path.append(os.path.join('..'))



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        #SECRET_KEY='dev',
        DATABASE=os.environ.get(('DATABASE_URL') or 'postgres://inoueyuya:127.0.0.1:5000/flaskr')
        #DATABASE=os.environ.get('postgres://inoueyuya:127.0.0.1:5000/flaskr')
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # セッションの有効期限設定
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30)

    # アップロードファイルの最大サイズの制限(1GB未満だけ許可)
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

    # mailの設定
    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'apikey'
    app.config['MAIL_PASSWORD'] = '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'
    app.config['MAIL_DEFAULT_SENDER'] = 's18f1005@bene.fit.ac.jp'

    # database
    from . import db
    db.init_app(app)

    # auth
    from . import auth
    app.register_blueprint(auth.bp)

    # upload
    from . import upload
    app.register_blueprint(upload.bp)
    app.add_url_rule('/', endpoint='index')
    return app
