#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

class Entry(object):
    def __init__(self, row, user, node, terms, url):
        self.nid = row[0]
        self.vid = row[1]
        self.type = row[2]
        self.title = row[3]
        self.user = user[0]
        self.created = row[6]
        self.updated = row[7]
        self.body = node[4]
        self.teaser = node[5]
        self.format = node[8]
        self.terms = terms
        self.url = url

class Drupal(object):
    """
    """

    def __init__(self, dbfile):
        """
        Initializes the drupal sqlite connection. Assumes dbfile is a
        filename to an sqlite3 DB file representation of a Drupal DB.
        """
        self._dbfn = dbfile
        self._conn = sqlite3.connect(dbfile)
        c = self._conn.cursor()
        self._urls = {}
        for row in c.execute("select * from url_alias"):
            nid = int(row[1].split('/')[1])
            self._urls[nid] = row[2]

    def get_nodes(self):
        """
        """
        c = self._conn.cursor()
        c2 = self._conn.cursor()
        c3 = self._conn.cursor()
        for row in c.execute("select * from node order by nid"):
            user = c2.execute("select name from users where uid = %s" % row[4])
            node = c2.execute("select * from node_revisions where vid = %s" % row[1])
            terms = []
            for elem in c3.execute("select * from term_node where nid=%s" % row[0]):
                t = c2.execute("select name from term_data where tid=%s" % elem[1])
                terms.append(t)
            url = None
            if self._urls.has_key(row[0]):
                url = self._urls[row[0]]

            yield Entry(row, user, node, terms, url)