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

# def Similarity(movieId1, movieId2):
#     a = movies.iloc[movieId1]
#     b = movies.iloc[movieId2]
    
#     genresA = a['binary_genres']
#     genresB = b['binary_genres']
    
#     genreDistance = spatial.distance.cosine(genresA, genresB)
    
#     castA = a['binary_cast']
#     castB = b['binary_cast']
#     castDistance = spatial.distance.cosine(castA, castB)
    
#     directA = a['binary_director']
#     directB = b['binary_director']
#     directDistance = spatial.distance.cosine(directA, directB)
    
#     wordsA = a['binary_words']
#     wordsB = b['binary_words']
#     wordsDistance = spatial.distance.cosine(wordsA, wordsB)
    
#     return genreDistance + directDistance + castDistance + wordsDistance


# def recommend_movie(name):
#     new_movie = movies[movies['original_title'].str.contains(name)].iloc[0].to_frame().T
    
#     print('Selected Movie: ', new_movie.original_title.values[0])
    
#     def getNeighbors(baseMovie, K):
#         distances = []


#         for index, movie in movies.iterrows():
#             if movie['new_id'] != baseMovie['new_id'].values[0].astype(int):
#                 dist = Similarity(baseMovie['new_id'].values[0], movie['new_id'])
#                 distances.append((movie['new_id'], dist))
#         distances.sort(key=operator.itemgetter(1))
#         neighbors = []

#         for x in range(min(K, len(distances))):
#             neighbors.append(distances[x])
#         return neighbors
    
#     K = 10
#     neighbors = getNeighbors(new_movie, K)
#     data = []

#     for neighbor in neighbors:
#         m = {
#             "title" : str(movies.iloc[neighbor[0]][1]),
#             "genres" : str(movies.iloc[neighbor[0]][2]).strip('[]').replace(' ', ''),
#             "rating" : str(movies.iloc[neighbor[0]][4])
#         }
#         data.append(m)
#         # print(
#         # str(movies.iloc[neighbor[0]][1]) +
#         # " | Genres: " +
#         # str(movies.iloc[neighbor[0]][2]).strip('[]').replace(' ', '') +
#         # " | Rating: " +
#         # str(movies.iloc[neighbor[0]][4]))

#     return data


# class Recommend(APIView):
#     def get(self, request, movie_title):
#         res = recommend_movie(movie_title)
#         return Response(res)
    


    

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
    def get(self, request, movie_title):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, 'recommend_movie.csv')
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