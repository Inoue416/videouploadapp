import click
from flask import current_app, g
from flask.cli import with_appcontext
import psycopg2
from psycopg2.extras import DictCursor


def get_db():
    if 'conn' not in g:
        g.conn = psycopg2.connect(
            database='d7u0nfp69rado0',
            user='csxvjmyqhnxgmw',
            password='9a2194e3c025af1532adf82b3ad4d5aec4b9e9bd561954d87b8aef52fe4b5a7d',
            host='ec2-3-89-0-52.compute-1.amazonaws.com',
            port='5432'
        )
        g.cur = g.conn.cursor(cursor_factory=DictCursor)
    return g.cur

def close_db(e=None):
    db_conn = g.pop('conn', None)
    db_cur = g.pop('cur', None)
    if db_conn is not None:
        db_conn.close()
    if db_cur is not None:
        db_cur.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))
    g.conn.commit()

@click.command('setting-data')
@with_appcontext
def setting_data_command():
    file = open(file='text_data/tweet.txt', mode='r', encoding='utf_8')
    dic = {}
    i=0
    for f in file:
        dic['t_v{}'.format(i)] = [f.replace('\n', '')]
        i+=1

    file.close()
    file = open(file='text_data/tweet_kana.txt', mode='r', encoding='utf_8')
    i = 0
    for f in file:
        dic['t_v{}'.format(i)].append(f.replace('\n', ''))
        dic['t_v{}'.format(i)].append(0)
        i+=1
    file.close()
    cur = get_db()
    for k, v in dic.items():
        cur.execute(
            'INSERT INTO tweets (file_id, file_title, kana, num, created) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (k, v[0], v[1], v[2])
        )
    g.conn.commit()

    file = open(file='text_data/ita.txt', mode='r', encoding='utf_8')
    dic = {}
    i=0
    for f in file:
        dic['i_v{}'.format(i)] = [f.replace('\n', '')]
        i+=1

    file.close()
    file = open(file='text_data/ita_kana.txt', mode='r', encoding='utf_8')
    i = 0
    for f in file:
        dic['i_v{}'.format(i)].append(f.replace('\n', ''))
        dic['i_v{}'.format(i)].append(0)
        i+=1
    file.close()
    cur = get_db()
    for k, v in dic.items():
        cur.execute(
            'INSERT INTO itas (file_id, file_title, kana, num, created) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)',
            (k, v[0], v[1], v[2])
        )
    g.conn.commit()
    close_db()
    click.echo('Setting data complete.')


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(setting_data_command)
