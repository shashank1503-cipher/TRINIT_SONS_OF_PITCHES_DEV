import pymongo
import recluster

MONGO_URI = 'mongodb+srv://trinit:trinit123@trinit.hqhhlhx.mongodb.net/test'
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['cluster_db']


fetch_entities = db.list_collection_names()

need_for_clustering = []
for entity in fetch_entities:
    if entity == 'clusters':
        continue
    fetch_clustering_status = db[entity].find_one({'clustering_status': False})
    if fetch_clustering_status:
        need_for_clustering.append(entity)

for entity in need_for_clustering:
    recluster.recluster(entity)