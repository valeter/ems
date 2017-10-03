#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import logging

from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager


class DBService:
    def __init__(self, dbconfig):
        self.dbconfig = dbconfig
        self.db = SimpleConnectionPool(
            minconn=self.dbconfig['minconn'], 
            maxconn=self.dbconfig['maxconn'],
            database=self.dbconfig['dbname'], 
            user=self.dbconfig['username'], 
            host=self.dbconfig['host'], 
            port=self.dbconfig['port'], 
            password=self.dbconfig['password'])

    @contextmanager
    def get_cursor(self):
        con = self.db.getconn()
        try:
            yield con.cursor()
            con.commit()
        finally:
            self.db.putconn(con)

    def update(self, sql):
        with self.get_cursor() as cursor:
            logging.debug(u'Executing sql: [{0}]'.format(sql.strip()))
            cursor.execute(sql)

    def query(self, sql, rowCallback):
        with self.get_cursor() as cursor:
            logging.debug(u'Executing sql: [{0}]'.format(sql.strip()))
            cursor.execute(sql) 
            for row in cursor:
                rowCallback(row)

    def query_single(self, sql):
        with self.get_cursor() as cursor:
            logging.debug(u'Executing sql: [{0}]'.format(sql.strip()))
            cursor.execute(sql) 
            yield cursor.fetchone()