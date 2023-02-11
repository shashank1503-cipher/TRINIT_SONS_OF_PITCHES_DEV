from fastapi import APIRouter
import pymongo
from fastapi import  HTTPException,Request
import pandas as pd
router = APIRouter()

MONGO_URI = 'mongodb+srv://trinit:trinit123@trinit.hqhhlhx.mongodb.net/test'
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['cluster_db']


@router.post("/add_data")
async def add_data_to_cluster(req:Request):
    data = await req.json()
    entity_name = data['entity_name']
    data = data['data']
    fetch_data = db[entity_name].find_one({})
    keys = fetch_data.keys()
    keys = [key for key in keys if key not in ['_id','Labels']]
    new_data = {}
    for key in keys:
        new_data[key] = data[key]
    df = pd.DataFrame(new_data,index=[0])
    cluster = add_data_to_cluster(entity_name,df)
    db[entity_name].insert_one(data)
    return {"cluster": cluster}
@router.get("/get_cluster_data/{entity_name}")
async def get_data_from_cluster(req:Request):
    entity_name = req.path_params['entity_name']
    fetch_data = db["clusters"].find_one({'entity_name': entity_name})
    fetch_data.pop('_id')
    return fetch_data