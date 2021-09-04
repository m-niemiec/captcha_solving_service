import os
import sqlite3


def clean_up():
    if os.path.exists('test.db'):
        os.remove('test.db')


def create_test_tables():
    # Make sure that 'test.db' does not exist, if so - delete it.
    clean_up()

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('CREATE TABLE user (id INTEGER PRIMARY KEY, credit_balance int, username text, email text, '
              'password text, time_updated text, time_created text)')
