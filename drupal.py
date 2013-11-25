#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import itertools

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
        self.parent = None
        self.child = None
        self.prev = None
        self.next = None

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
        self._conn.text_factory = lambda x : str(x, 'gbk', 'ignore')
        c = self._conn.cursor()
        self._urls = {}
        for row in c.execute("select * from url_alias"):
            nid = int(row[1].split('/')[1])
            self._urls[nid] = row[2]
        self.lookup_books = {}
        self._books = self.get_books()

    def _gen_entry(self, row):
        c = self._conn.cursor()
        c2 = self._conn.cursor()
        user = c.execute("select name from users where uid = %s" % row[4]).fetchall()
        node = c.execute("select * from node_revisions where vid = %s" % row[1]).fetchall()[0]
        terms = []
        for elem in c2.execute("select * from term_node where nid=%s" % row[0]):
            t = c.execute("select name from term_data where tid=%s" % elem[1]).fetchone()[0]
            terms.append(t)
        url = None
        if row[0] in self._urls:
            url = self._urls[row[0]]
        return Entry(row, user, node, terms, url)

    def get_node(self, nid):
        """
        """
        c = self._conn.cursor()
        r = c.execute("select * from node where nid=%s" % nid).fetchall()
        if len(r) == 1:
            return self._gen_entry(r[0])
        else:
            return None

    def get_nodes(self):
        """
        """
        c = self._conn.cursor()
        c2 = self._conn.cursor()
        c3 = self._conn.cursor()
        for row in c.execute("select * from node order by nid"):
            e = self._gen_entry(row)
            if e.type == 'book':
                if e.nid in self._books:
                    e.children = []
                    for b in self._books[e.nid]:
                        e.children.append(self.get_node(b))
                elif e.nid in self.lookup_books:
                    e.parent = self.get_node(self.lookup_books[e.nid])
                    i = self._books[e.parent.nid].index(e.nid)
                    if i > 0:
                        e.prev = self.get_node(self._books[e.parent.nid][i-1])
                    if i < len(self._books[e.parent.nid])-1:
                        e.next = self.get_node(self._books[e.parent.nid][i+1])
            yield e

    def get_books(self):
        c = self._conn.cursor()
        b = {}
        # first, get all the roots
        for row in c.execute("select * from book where parent=0"):
            nid = row[1]
            b[nid] = [[] for i in range(35)]
        # Next, get all the children
        for row in c.execute("select * from book where parent!=0"):
            nid = row[1]
            parent = row[2]
            weight = row[3]
            if parent in b:
                b[parent][weight+15].append(nid)
                self.lookup_books[nid] = parent

        # Now, clean up the Nones
        for k, v in b.items():
            b[k] = [i for i in itertools.chain.from_iterable(v)]

        #import pdb; pdb.set_trace()
        return b
