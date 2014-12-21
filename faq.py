#!/usr/bin/env python

import praw
import pickle
import sys

import requests

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import numpy as np
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import linear_kernel

from sklearn.cluster import KMeans 
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn import decomposition

import pprint
import argparse

corpus = []

def fetchFromFileAndSave(f, url):
    comments = fetchFromUrl(url)
    saveToFile(f, comments)
    return comments

def saveToFile(f,comments):
    pickle.dump( comments, open(f, "wb"))

def fetchFromFile(f):

    comments = pickle.load(open(f, 'r'))
    return comments
    pass

def fetchFromUrl(url):
    r  = praw.Reddit(user_agent='example')
    amy = None
    try:
        amy = r.get_submission(url)
    except (requests.exceptions.MissingSchema):
        print "%s is not a valid schema" % (url)
        sys.exit()
    except (requests.exceptions.ConnectionError):
        print "%s couldn't be connected " % (url)
        sys.exit()
    except (requests.exceptions.InvalidURL):
        print "Invalid URL"
        sys.exit()
    except (requests.exceptions.HTTPError):
        print "Couldn't find %s" % (url)
        sys.exit()

    if amy is None:
        print "Unknown error with URL fetching!"
        sys.exit()

    print "Starting to download all comments for this submission (takes time)"
    amy.replace_more_comments(limit=None, threshold=0)

    comments = []
    for c in amy.comments:
        if c.parent_id.find(amy.id) == -1:
            continue
        if type(c) == praw.objects.MoreComments:
            continue
        a = ' '.join(c.body.splitlines())
        comments.append(a)

    return comments
    pass

def dbscan_(X):
    sys.stdout.write("Preparing to create DBSCAN...")
    sys.stdout.flush()
    km = DBSCAN(eps=.1, min_samples=1)
    sys.stdout.write("done!\n")

    sys.stdout.write("Running fit()...")
    sys.stdout.flush()
    km.fit(X)
    sys.stdout.write("done!\n")

    res = {}
    for i in range(len(corpus)):
        label = km.labels_[i] 
        if res.has_key(label):
            if corpus[i] not in res[label]:
                res[label].append(corpus[i])
        else:
            res[label] = []
            res[label].append(corpus[i])

    for i in res.keys():
        if len(res[i]) > 1:
            pprint.pprint(res[i])

def nmf_(X):
    
    sys.stdout.write("Preparing to run NMF ... ")
    sys.stdout.flush()
    X[X < 0] = 0.0
    km = decomposition.NMF(n_components=10, random_state=1)
    sys.stdout.write("done!\n")

    sys.stdout.write("Running fit()...")
    sys.stdout.flush()
    km.fit(X)
    sys.stdout.write("done!\n")

    feature_names = vectorizer.get_feature_names()

    for topic_idx, topic in enumerate(km.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print()

n_samples = 2000
n_features = 1000
n_topics = 10
n_top_words = 20

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Download and find duplicate questions for .')

    parser.add_argument('-n', metavar='m_ngram', type=str, nargs='?', help="Maximum n-gran number")
    parser.add_argument('-u', metavar='url', type=str, nargs='?', help="URL to fetch comments from")
    parser.add_argument('-f', metavar='f', type=str, nargs='?', help="Pickle File to fetch list of comments from")
    parser.add_argument('-F', metavar='F', type=str, nargs='*', help="Use NMF")

    args = parser.parse_args()

    print args

    m_ngram = 4

    comments = []
    sys.stdout.write("Preparing to collect stopwords...")
    sys.stdout.flush()
    stop = set(stopwords.words('english'))
    sys.stdout.write("done!\n")

    sys.stdout.write("Preparing to collect data from source...")
    sys.stdout.flush()
    if args.f is not None and args.u is not None:
        comments = fetchFromFileAndSave(args.f, args.u)
    elif args.f is not None:
        comments = fetchFromFile(args.f)
    elif args.u is not None:
        comments = fetchFromUrl(args.u)
    
    if args.n is not None:
        m_ngram =  int(args.n)

    sys.stdout.write("done!\n")

    sys.stdout.write("Preparing to collect comments...")
    sys.stdout.flush()
    for c in comments:
        a = ' '.join(c.splitlines())
        tok = word_tokenize(a)
        tok_stopped = []
        stopped = []

        for word in tok:
            if word not in stop:
                tok_stopped.append(word)

        corpus.append(a)
    sys.stdout.write("done!\n")


    sys.stdout.write("Preparing to create TFIDF vector...")
    sys.stdout.flush()
    vectorizer = TfidfVectorizer(ngram_range=(2,m_ngram), 
                                 stop_words='english',
                                 max_df=0.95,
                                 min_df=2,
                                 max_features=1000)
    tfidf = vectorizer.fit_transform(corpus)
    tfidf = tfidf * tfidf.T
    sys.stdout.write("done!\n")

    sys.stdout.write("Preparing to scale date...")
    sys.stdout.flush()
    X = StandardScaler().fit_transform(tfidf.todense())
    sys.stdout.write("done!\n")

    if args.F is None:
        dbscan_(X)
    else:
        nmf_(X)

