#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pymongo
import mongoParseQuery

class dbMongoDB():

    def __init__(self, host='127.0.0.1', port=27017):
        try:
            self.db = MongoClient(host=host, port=port).wren
        except Exception as e:
            print e

    def initdb(self):
        return

    def regcond(self, cond_id, key, cond):
        self.db[self.__TAB_KEY_MAP].find({'key': key})
        self.c.execute('select key_id from tab_key_map where key = ?', (key,))
        res = self.c.fetchone()
        if res == None:
            print 'no such key in tab_key_map, %s' % (key)
            return None
        key_id = res[0]
        self.c.execute('select cond_id from tab_cond where key_id = ? and cond = ?', (key_id, cond))
        if self.c.fetchone() != None:
            print '%s is already registered with %s for %s' % (cond, cond_id, key)
            return None
        self.c.execute('insert into tab_cond values (?, ?, ?)', (cond_id, key_id, cond))
        self.db.commit()

    def docond(self, cond_id):
        self.c.execute('select key_id, cond from tab_cond where cond_id = ?', (cond_id,))
        res = self.c.fetchone()
        if res == None:
            print 'no such cond_id %s' % (cond_id)
            return []
        key_id = res[0]
        cond = eval(res[1]) # XXX need to be revied.
        return self.select_direct(key_id, cond, 10)

    def makekey(self, key, key_id):
        self.c.execute('select key from tab_key_map where key = ?', (key,))
        if self.c.fetchone() != None:
            print '%s is already registered with %s' % (key, key_id)
            return
        self.c.execute('insert into tab_key_map values (?, ?)', (key_id, key))
        arg = 'create table %s (time text, value text)' % (key_id,)
        self.c.execute(arg)
        self.db.commit()

    def insert(self, key, ts, value):
        self.c.execute('select key_id from tab_key_map where key = ?', (key,))
        res = self.c.fetchone()
        if res == None:
            print 'no such key in tab_key_map %s' % (key,)
            return None
        key_id = res[0]
        arg = 'insert into %s (time, value) values (?, ?)' % (key_id,)
        self.c.execute(arg, (ts, value))
        self.db.commit()

    #
    # @return list of values
    #
    def select(self, key, cond, cursor_size):
        self.c.execute('select key_id from tab_key_map where key = ?', (key,))
        res = self.c.fetchone()
        if res == None:
            print 'no such key in tab_key_map %s' % (key)
            return []
        key_id = res[0]
        return self.select_direct(key_id, cond, cursor_size)

    #
    # @return the latest record
    #
    def select_latest(self, key_id):
        arg = 'select time, value from %s order by time desc limit 1' % (key_id,)
        self.c.execute(arg)
        return self.c.fetchmany()

    #
    # @note the memory allocation issue needs to be considered
    #
    def select_direct(self, key_id, cond, cursor_size):
        m = mongoParseQuery.mongoParseQuery()
        arg = 'select time, value from %s where %s' % (key_id, m.parse_cond(cond))
        self.c.execute(arg)
        return self.c.fetchmany(size=cursor_size)

