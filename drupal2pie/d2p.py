#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Tool to convert drupal dumps into piecrust
"""

import sys
import os.path
import os
import errno
import time

from drupal import Drupal

if len(sys.argv) < 3:
    print("usage: drupal_dump.py sqlite.db piecrust/path/")
    sys.exit(1)

db = os.path.abspath(sys.argv[1])
pie_dir = os.path.abspath(sys.argv[2])

d = Drupal(db)

def mkdir_p(path):
    '''
    Does the equivalent of a 'mkdir -p' (Linux) on both platforms.
    '''
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass

mkdir_p("%s/_content/pages/node" % pie_dir)
mkdir_p("%s/_content/posts" % pie_dir)

def make_page(e):
    header = []
    body = e.body
    header.append('title: %s' % e.title)
    header.append('date: %s' % time.strftime(time_format, e.created))
    if not e.terms is None:
        header.append('tags: [ %s ]' % ', '.join(e.terms))

    return "---\n" + "\n".join(header) + "\n---\n" + body


time_format = '%Y-%m-%d %H:%M'

for e in get_nodes:
    print(make_page(e))