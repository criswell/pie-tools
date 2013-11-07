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

node_root = "%s/_content/pages/node" % pie_dir
post_root = "%s/_content/posts" % pie_dir

mkdir_p(node_root)

time_format = '%Y-%m-%d %H:%M'

def make_page(e):
    header = []
    body = e.body
    header.append('title: %s' % e.title)
    header.append('date: %s' % time.strftime(time_format, time.localtime(e.created)))
    if not e.terms is None:
        #import pdb; pdb.set_trace()
        header.append('tags: [ %s ]' % ', '.join(e.terms))

    return "---\n" + "\n".join(header) + "\n---\n" + body

for e in d.get_nodes():
    page = make_page(e).encode('utf-8')
    print("Processing: %s -> '%s'" % (e.nid, e.title))
    # First, the obvious ones... node/N
    node_path = "%s/%s.html" % (node_root, e.nid)
    with open(node_path, "w", encoding="utf-8") as f:
        f.write(page)
    # Next, if it has a pretty URL
    if e.url is not None:
        url_path = "%s/_content/%s" % (pie_dir, e.url)
        (head, tail) = os.path.split(url_path)
        mkdir_p(head)
        with open("%s.html", "w", encoding="utf-8") as f:
            f.write(page)
    # Finally, if it was a blog post, put in posts
    if e.type == "blog":
        year = time.strftime("%Y", time.localtime(e.created))
        month = time.strftime("%m", time.localtime(e.created))
        day = time.strftime("%d", time.localtime(e.created))
        blog_root = "%s/%s/%s" % (post_root, year, month)
        mkdir_p(blog_root)
        blog_file = "%s/%s_post.html" % (blog_root, day)
        with open(blog_file, "w", encoding="utf-8") as f:
            f.write(page)
