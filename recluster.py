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
MONGO_URI = 'mongodb+srv://trinit:trinit123@trinit.hqhhlhx.mongodb.net/test'
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['cluster_db']

# Load the customer data
df = pd.read_csv("Mall_Customers.csv")

df.rename(index=str, columns={'Annual_Income_(k$)': 'Income',
                              'Spending_Score': 'Score'}, inplace=True)

X = df.drop(['CustomerID', 'Gender'], axis=1)
from sklearn.cluster import KMeans

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
    
filename = 'kmeans_mall_customers.sav'
joblib.dump(km5, filename)

# data_in_json = X.to_json(orient='records')
# data_in_json = json.loads(data_in_json)
# db["mall_customers"].insert_many(data_in_json)   
cluster_data = {"entity_name": "mall_customers", "cluster_file_name": filename,"cluster_type": "kmeans","clusters": cluster_map}
print(cluster_data)
db["clusters"].insert_one(cluster_data)