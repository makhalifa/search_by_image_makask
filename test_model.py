# Import RecommendationSystem class from model/main.py
from model.model import RecommendationSystem
import numpy as np
import pickle
import json

products = [None] * 2000
# feature_list_test = np.array(pickle.load(open('embeddings.pkl', 'rb')))
# Array of images from images folder
# rec = RecommendationSystem(None, None)
# for i in range(0, 2000):
#     image = f"images/{i}.jpg"
#     formated_data = np.array(rec.feature_extraction(image))
#     formated_list = formated_data.tolist()
#     docImg = {  "_id": i, "image": image, "formated_img": formated_list }
#     products[i] = docImg

# products = np.array(products)
# products = products.tolist()
# print(products)
# np.savetxt('output.txt', products, fmt='%d')
    


# jsonString = json.dumps(products)
# jsonFile = open("data.json", "w")
# jsonFile.write(jsonString)
# jsonFile.close()

products = np.array(json.load(open('data.json', 'rb')))
formated_data = []
filenames = []
for p in products:
    formated_data.append(p["formated_img"])
    filenames.append(p["image"])

rec = RecommendationSystem(formated_data, filenames)

# filenames_test = np.array(images)
# print(filenames_test)
# formated_data = rec.feature_extraction("images/0.jpg")
# print(formated_data)
res = rec.recommender("images/0.jpg", 5)
print(res)
