# coding=utf8

""" Load legacy Drupal data into virgin models 
"""

import sys
import os
import os.path

# Bootstrap Django
def relpath(p):
    return os.path.join(os.path.dirname(__file__), p)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path = sys.path[:1] + ['./'] + sys.path[1:]
sys.path = sys.path[:1] + [relpath('../..')] + sys.path[1:]

from content.models import Page, Tag
from vocabulary.models import Vocabulary, Concept
from django.template.defaultfilters import truncatewords
import MySQLdb
import settings

# mysql -u root -p -f -h localhost drupal_db < drupal_db.sql
conn = MySQLdb.connect(
        host   = settings.DB_HOST,
        user   = settings.DATABASES['default']['USER'],
        passwd = settings.DATABASES['default']['PASSWORD'],
        db     = 'ns'
    )

c = conn.cursor()

def query(sql):
    return c.execute(sql)

def load_vocabs(conn):
    query('SELECT vid, name, description FROM vocabulary')
    for v in c.fetchall():
        v = Vocabulary(
            id=v[0],
            title=v[1],
            description=v[2]
        )
        print('Vocab: %s - %s' % (v[0], v[1]))
        v.save()
        query('SELECT tid, name, description FROM term_data WHERE vid = %s' % v.id)
        for term in c.fetchall():
            query('SELECT guid FROM term_note WHERE termid = %s LIMIT 1' % term[0])
            guid = c.fetchone()
            concept = Concept(
                id=term[0],
                node_id=guid[0],
                vocabulary=v,
                name=term[1],
                description=term[2]
            )
            print('        Concept: %s - %s' % (term[0], term[1]))
            concept.save()

def load_tags(page_id):
    query('SELECT DISTINCT tid, nid FROM term_node')
    
    for t in c.fetchall:
        tag = Tag(
            concept_id=t[0],
            page_id=page_id
        )
        tag.save()

def load_pages(conn):
    query('SELECT * FROM node WHERE type="page"') # page, nid ~ page.id
    for node in c.fetchall():
        query('SELECT title, body, teaser, timestamp FROM node_revisions WHERE nid = %s ORDER BY vid DESC LIMIT 1' % node[0])
        rev = c.fetchone()
        try:
            page = Page(
                id=node[0],
                title=rev[0],
                body=unicode(rev[1]),
                teaser=unicode(rev[2]),
                #updated_at=updated_at,
                #created_at=created_at
            )
            page.save()
        except:
            print('Unicode trouble with nid: %s' % node[0])
            pass

def drop_empty_tables(conn):
    query('SHOW TABLES')
    for table in c.fetchall():    
        query('SELECT * FROM %s' % table[0])
        if c.rowcount == 0:
            query('DROP TABLE %s' % table[0])

def count_tag_frequency(conn):
    # select all terms used for tagging
    query('SELECT DISTINCT tid FROM term_node')
    for t in c.fetchall():
        tid = int(t[0])
        # select all nodes for this tag in their latest revision
        query('SELECT COUNT(DISTINCT nid) FROM term_node WHERE tid=%d ORDER BY vid' % tid)
        count = c.fetchone()[0]
        def _get(tid, fid):
            query('SELECT VALUE FROM taxonomy_extension_value WHERE tid=%s and fid=%s' % (tid, fid))
            try:
                return c.fetchone()[0]
            except:
                print('c')
                pass
        term_node_id  = _get(tid, 6)
        vocab_node_id = _get(tid, 1)
        try:
            vocab = Vocabulary.objects.get(node_id=vocab_node_id)
            concept = Concept.objects.get(node_id=term_node_id, vocabulary=vocab)
            concept.count = count
            print('%s - %s in %s' % (count, concept.name, vocab_node_id))
            concept.save()
        except:
            print('Something went wrong, vocabulary or concept DoesNotExist')
            pass

count_tag_frequency(conn)
#drop_empty_tables(conn)
#load_pages(conn)
#load_vocabs(conn)
#load_tags(conn)