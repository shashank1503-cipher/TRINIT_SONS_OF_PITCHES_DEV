import joblib
import pandas as pd
from bson.objectid import ObjectId
import pymongo

MONGO_URI = 'mongodb+srv://trinit:trinit123@trinit.hqhhlhx.mongodb.net/test'
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['cluster_db']

def add_data_to_cluster(entity_name,data):
    fetch_cluster = db['clusters'].find_one({'entity_name': entity_name})
    cluster_file_name = fetch_cluster['cluster_file_name']
    cluster_model = joblib.load(cluster_file_name)
    new_data_cluster = cluster_model.predict(data)
    return new_data_cluster[0]

keys = ["Age","Income","Score"]
data = {}
for key in keys:
    data[key] = int(input(f"Enter {key}: "))
print(data)
df = pd.DataFrame(data,index=[0])
# df.drop("CustomerID",axis=1,inplace=True)
# df.drop("Gender",axis=1,inplace=True)
cluster = add_data_to_cluster("mall_customers",df)
print(cluster)