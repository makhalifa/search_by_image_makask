from typing import Union
import numpy as np
import pickle
import tensorflow
import cv2
import io
from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm


class RecommendationSystem:

    def __init__(self, feature_list: np.array, filenames: list[str]) -> None:
        """Class for the recommendation system

        Args:
            feature_list (np.array): features list of the data set
            filenames (list[str]): file names paths of the data set
        """
        self.model = ResNet50(weights='imagenet', include_top=False,
                              input_shape=(224, 224, 3))
        self.model.trainable = False

        self.model = tensorflow.keras.Sequential([
            self.model,
            GlobalMaxPooling2D()
        ])
        self.feature_list = feature_list
        self.filenames = filenames

    def feature_extraction(self, img_obj: Union[str, bytes]) -> np.array:
        """Used to preprocess the images, you can use it to convert the image to the model data

        Args:
            img_path (str): The path you want to test the model with

        Returns:
            np.array: the model data
        """
        if type(img_obj) == bytes:
            img = Image.open(io.BytesIO(img_obj)).convert().resize(
                (224, 224), resample=Image.Resampling.NEAREST)
            # img = image.smart_resize(img, (224, 224))
        elif type(img_obj) == str:
            img = image.load_img(img_obj, target_size=(224, 224))
        else:
            assert False, "Unreachable"
        img_array = image.img_to_array(img)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img_array)
        result = self.model.predict(preprocessed_img).flatten()
        normalized_result = result / norm(result)
        print(img)
        return normalized_result

    def __recommend(self, features: np.array, n: int) -> np.ndarray:
        """Makes a recommendation based on the data proved

        Args:
            features (np.array): the features of the test image
            n (int): the number of recommendations you want

        Returns:
            np.ndarray: a list of the recommendations indices
        """
        neighbors = NearestNeighbors(
            n_neighbors=n, algorithm='brute', metric='euclidean')
        neighbors.fit(self.feature_list)

        _, indices = neighbors.kneighbors([features])

        return indices

    def recommender(self, uploaded_file_path: str, n: int) -> list[str]:
        """Process the data and gives the recommendations back

        Args:
            uploaded_file_path (str): the path to the image you want to test for
            n (int): the number of recommendations you want

        Returns:
            list[str]: list of file paths of the recommendation
        """
        # feature extract
        features = self.feature_extraction(uploaded_file_path)
        # recommendation
        indices = self.__recommend(features, n)
        res_names = []
        for i in indices[0]:
            res_names.append(self.filenames[i])
        return res_names


if __name__ == '__main__':
    feature_list_test = np.array(pickle.load(open('embeddings.pkl', 'rb')))
    filenames_test = pickle.load(open('filenames.pkl', 'rb'))
    rec = RecommendationSystem(feature_list_test, filenames_test)
    with open("test_data/images.jpeg", "rb") as f:
        image_bytes = f.read()
    res = rec.recommender("test_data/images.jpeg", 5)
    res2 = rec.recommender(image_bytes, 5)
    print(res)
    print(res2)
