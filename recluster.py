from sklearn.cluster import DBSCAN
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
from kneed import KneeLocator
import seaborn as sns
import joblib
import pymongo
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

    ####################################################

    X = X.dropna()
    X = X.reset_index(drop=True)

    first_col_name = X.columns[0]

    for i in X:
        if isinstance(X[i][0], str):

            if ',' in X[i][0]:
                X[i] = X[i].str.split(r"\s*,\s*", regex=True)
                x = X.explode(i)
                X = (
                    pd.concat(
                        [X.set_index(first_col_name), pd.crosstab(x[first_col_name], x[i])], axis=1
                    )
                    .reset_index()
                    .drop(columns=i)
                )

    for i in X:
        # print(X[i][3])
        if isinstance(X[i][3], str):

            # print("YES")
            X[i] = pd.Categorical(X[i])
            X[i] = X[i].cat.codes

    ####################################################

    print(X)

    # scaler = StandardScaler()
    # X = scaler.fit_transform(X)
    # print(X)
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
    cluster_data = {"entity_name": entity_name, "cluster_file_name": filename,"cluster_type": "kmeans","clusters": cluster_map}
    print(cluster_data)
    db['clusters'].update_one({'entity_name': entity_name}, {'$set': cluster_data}, upsert=True)
    return cluster_data


