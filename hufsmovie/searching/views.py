from django.shortcuts import render
import pandas as pd
import numpy as np
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from scipy import spatial
import os

# Create your views here.
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'new_movie_list.csv')

movies = pd.read_csv(file_path)
    

class Search(APIView):
    def post(self, request):
        text = request.data['text']
        selected_movies = movies[movies['original_title'].str.contains(text, case=False)]
        title_list = selected_movies['original_title'].tolist()
        res = {
            "data" : title_list
        }
        return Response(res)
    

class Recommend(APIView):
    def post(self, request, movie_title):
        type = request.data['recommend_type']

        if type == "include":
            script_dir = os.path.dirname(__file__)
            file_path = os.path.join(script_dir, 'recommend_movie.csv')
            rec_movie = pd.read_csv(file_path)
        else:
            script_dir = os.path.dirname(__file__)
            file_path = os.path.join(script_dir, 'recommend_movie_director-cast제거.csv')
            rec_movie = pd.read_csv(file_path)


        aa = rec_movie[rec_movie['movie_name'] == movie_title]['recommend_movie'].values[0]

        lines = aa.splitlines()

        del lines[0]
        del lines[0]

        data = []

        for line in lines:
            str = line.split('|')
            genres = str[1].replace("Genres: ", "").replace("'", "").strip().split(',')
            genres_str = ""
            for g in genres:
                genres_str += g
                genres_str += ", "


            m = {
                "title" : str[0].strip(),
                "genres" : genres_str[:-2],
                "rating" : str[2].replace("Rating: ", "").strip()
            }
            data.append(m)

            if len(data) >= 6:
                break

        res = {
            "data" : data
        }


        return Response(res)