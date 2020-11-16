#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import contextmanager

import pymysql
from pymysql import MySQLError
from pymysql.cursors import DictCursor


class MysqlHelper:
    def __init__(self, host, database, user, password, port=3306, charset='utf8'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.charset = charset

        self._conn = self._get_conn()

    def _get_conn(self):
        config = {
            "host": self.host,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "port": self.port,
            "charset": self.charset

        }
        return pymysql.connect(**config)

    def query_one(self, query, args=None):
        cursor = self._conn.cursor(DictCursor)
        with cursor:
            cursor.execute(query, args)
            return cursor.fetchone()

    def query_all(self, query, args=None):
        cursor = self._conn.cursor(DictCursor)
        with cursor:
            cursor.execute(query, args)
            return cursor.fetchall()

    def execute(self, query: str, args=None):
        cursor = self._conn.cursor(DictCursor)
        with cursor:
            cursor.execute(query, args)
            return cursor.rowcount

    def execute_many(self, query, args):
        """[执行多条sql]

        Args:
            query (str): [要执行的sql]
            args (list): [参数序列]

        Returns:
            int: [受影响的行数（如果有）]
        """
        cursor = self._conn.cursor(DictCursor)
        with cursor:
            cursor.executemany(query, args)
            return cursor.rowcount

    @contextmanager
    def auto_commit(self):
        """
        with self.auto_commit():
            self.query()
        """
        try:
            yield
            self._conn.commit()
        except MySQLError as e:
            self._conn.rollback()
            raise e


if __name__ == '__main__':
    mysql_helper = MysqlHelper(host="192.168.2.129", database="prosee_web2",
                               user="prosee_dev", password="prosee_dev")
    query = "SELECT * from `schema` WHERE group_id=%s"
    args = ["1326393933848252416"]
    result = mysql_helper.query_one(query, args)
    print(result)
