from sklearn.cluster import DBSCAN
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import NearestNeighbors
from kneed import KneeLocator
import seaborn as sns
import joblib
import pymongo
import json
from sklearn.cluster import KMeans

MONGO_URI = 'mongodb+srv://trinit:trinit123@trinit.hqhhlhx.mongodb.net/test'
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['cluster_db']


def recluster(entity_name):
    fetch_data = db[entity_name].find({})
    data = []
    for row in fetch_data:
        row.pop('_id')
        data.append(row)
    df = pd.DataFrame(data)
    df.drop(['clustering_status'], axis=1, inplace=True)
    X = df.drop(['Labels'], axis=1)
    km = joblib.load('kmeans_mall_customers.sav')
    clusters = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i).fit(X)
        clusters.append(km.inertia_)
        

    kl = KneeLocator(range(1,11), clusters, curve='convex', direction='decreasing')
    n_clusters = kl.knee
    km5 = KMeans(n_clusters=n_clusters).fit(X)
    X['Labels'] = km5.labels_
    clusters = X['Labels'].unique()
    cluster_map = {}
    for cluster in clusters:
        cluster_map[str(cluster)] = X[X['Labels'] == cluster].drop('Labels', axis=1).mean().to_dict()
        
    filename = 'kmeans_'+entity_name+'.sav'
    joblib.dump(km5, filename)
    cluster_data = {"entity_name": "mall_customers", "cluster_file_name": filename,"cluster_type": "kmeans","clusters": cluster_map}
    db['clusters'].update_one({'entity_name': entity_name}, {'$set': cluster_data}, upsert=True)
    return cluster_data