from fastapi import FastAPI, File, UploadFile 
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from model.model import RecommendationSystem
# from model.main import RecommendationSystem
import numpy as np
import json
# MongoDB
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
# # Url to the image
# import urllib.request
from io import BytesIO
from PIL import Image

import imghdr

from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.applications.vgg16 import preprocess_input

import datetime
import os


products = np.array(json.load(open('product_thumbnail.json', 'rb')))
formated_data = []
product_id = []
for p in products:
    formated_data.append(p["formated_img"])
    product_id.append(p["_id"])

def pipeline(res):
    return [
    {'$match' : { '_id': { '$in': res } }},
    {
        '$lookup': {
            'from': 'colors', 
            'localField': '_id', 
            'foreignField': 'product', 
            'as': 'color'
        }
    }, {
        '$lookup': {
            'from': 'reviews', 
            'localField': 'reviews', 
            'foreignField': '_id', 
            'as': 'reviews'
        }
    }, {
        '$project': {
            '_id': 1, 
            'seller': 1, 
            'title': 1, 
            'category': 1, 
            'subcategory': 1, 
            'color': '$color.color', 
            'images': {
                '$first': '$color.images'
            }, 
            'price': {
                '$toDouble': {
                    '$first': '$color.price'
                }
            }, 
            'discount': {
                '$first': '$color.discount'
            }, 
            'n': {
                '$size': '$reviews'
            }, 
            'rating': {
                '$cond': {
                    'if': {
                        '$eq': [
                            {
                                '$size': '$reviews'
                            }, 0
                        ]
                    }, 
                    'then': 0, 
                    'else': {
                        '$divide': [
                            {
                                '$sum': '$reviews.rating'
                            }, {
                                '$size': '$reviews'
                            }
                        ]
                    }
                }
            }, 
            'createdAt': 1
        }
    }
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


mongo_uri = "mongodb+srv://makask:makask@cluster0.tbjzwli.mongodb.net/makask?retryWrites=true&w=majority"
# Connect to the MongoDB instance
try:
    client = MongoClient("mongodb+srv://makask:makask@cluster0.tbjzwli.mongodb.net/makask?retryWrites=true&w=majority")
except ConnectionFailure as e:
    print("Could not connect to MongoDB:", e)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test_db")
async def test_db():
    ids=[ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    documents = client.makask.products.find({"_id": {"$in": ids}})
    return {"message": list(documents)}

@app.post("/test")
async def test(file: bytes = File(...)):
    print(file)
    return {"message": "done ✅"}

@app.post("/recommend")
async def recommend(file:bytes = File(...), n:int = 5):
    extension = imghdr.what(None, file)
    print(extension)
    img = Image.open(BytesIO(file))
    print(file)
    # Make class instance
    rec = RecommendationSystem(formated_data, product_id)
    # # Recommend n images based on the image provided
    res = rec.recommender(img, n)
    
    documents = client.makask.products.find({"_id": {"$in": res}})
    
    return list(documents)

@app.post("/recommend/v2")
async def recommend(file:bytes = File(...), n:int = 5):
    extension = imghdr.what(None, file)
    img = Image.open(BytesIO(file))
    # save the image in its original format
    filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.' + extension
    img.save(filename)
    # image preprocessing

    # Make class instance
    rec = RecommendationSystem(formated_data, product_id)
    # # Recommend n images based on the image provided
    res = rec.recommender(filename, n)
    
    if os.path.exists(filename):
        os.remove(filename)

    # documents = client.makask.products.find({"_id": {"$in": res}})
    documents = client.makask.products.aggregate(pipeline(res))

    return list(documents)

# uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)