# -*-coding:utf8-*-

__author__ = "Neyanbbhin"

import threading
import logging
import MySQLdb
from functools import wraps

engine = None


class Row(dict):

    def __init__(self, dict):
        pass

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(name)


class DBInitializeError(Exception):
    pass


class _Engine(object):

    def __init__(self, connect):
        # connect is a _mysql.connection object
        self._connect = connect

    def connect(self):
        return self._connect()


class _Connection(object):

    '''
    Lazy Connection
    '''

    def __init__(self):
        self.connection = None

    def cursor(self):
        if not self.connection:
            connection = engine.connect()
            self.connection = connection
            logging.info("New connection %s" % hex(id(connection)))
            return self.connection.cursor()
        return self.connection.cursor()

    def commit(self):
        logging.info("Commited")
        self.connection.commit()

    def rollback(self):
        logging.error("Database updated failed, rolled back!")
        self.connection.rollback()

    def close(self):
        if self.connection:
            connection = self.connection
            logging.info("Connection %s closed!" % hex(id(connection)))
            connection.close()
            self.connection = None


class _DbCtx(threading.local):

    '''
    持有数据库连接对象的Thread.local对象,包含很多相互不共享数据的数据库连接对象
    '''

    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        self.connection = _Connection()
        logging.info("Initialize a lazy connection in local thread %s"
                     % hex(id(self.connection)))
        # Initialize transactions count
        self.transactions = 0

    def cleanup(self):
        logging.info("Close connection %s in local thread "
                     % hex(id(self.connection)))
        self.connection.close()
        self.connection = None


# global _DBCtx instance
_db_ctx = _DbCtx()


class _ConnectionCtx(object):

    '''
    数据库连接上下文(connection context manage)
    '''

    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


def connection():
    return _ConnectionCtx()


def with_connection(func):
    @wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper


class _TransactionCtx(object):

    '''
    数据库事务上下文
    '''

    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        logging.info(
            'begin transaction...'
            if _db_ctx.transactions == 1 else
            'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.connection.close()

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            _db_ctx.connection.rollback()
            logging.error("Commit on connection %s failed"
                          % hex(id(_db_ctx.connection)))

    def rollback(self):
        global _db_ctx
        _db_ctx.connection.rollback()


def transaction():
    return _TransactionCtx()


def with_transaction(func):
    @wraps(func)
    def _wraper(*args, **kw):
        with _TransactionCtx():
            return func(*args, **kw)
    return _wraper


@with_connection
def print_all():
    global _db_ctx
    _db_ctx.connection.connect()
    for user in _db_ctx.connection.connection.query("SELECT * FROM users"):
        print user


@with_connection
def _select(sql, first, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace("?", "%s")
    logging.info("Going to executing SQL:%s, Args:%s" % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        logging.info("Executing SQL:%s" % sql)
        cursor.execute(sql, args)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
        if first:
            row = cursor.fetchone()
            values = list(row)
            return dict(zip(columns, values))
        res = []
        for item in cursor.fetchall():
            values = [x for x in item]
            res.append(dict(zip(columns, values)))
        return res

    except:
        return {}
    finally:
        if cursor:
            cursor.close()


@with_connection
def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace("?", "%s")
    logging.info("Going to execute SQL:%s, Args:%s" % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if _db_ctx.transactions == 0:
            _db_ctx.connection.commit()
        return cursor.rowcount
        # return the coutn of row which is affected by execute
    finally:
        if cursor:
            cursor.close()


# get a list of result
def select(sql, *args):
    return _select(sql, False, *args)


# get one of the first colomn of reuslt
def select_one(sql, args):
    return _select(sql, True, *args)


def update(sql, *args):
    return _update(sql, *args)


def insert(sql, *args):
    return _update(sql, *args)


def delete(sql, *args):
    return _update(sql, *args)


def create_engine(host, port, username, password, db):
    global engine
    params = dict(host=host, port=port, user=username,
                  passwd=password, db=db)
    engine = _Engine(lambda: MySQLdb.connect(**params))
    logging.info("Create engine with params: \n%s" % params)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s: %(message)s'
                        )
    create_engine("localhost", 3306, "root", "", "testdb")
    sql = "delete from users where id=?"
    delete(sql, 4)
