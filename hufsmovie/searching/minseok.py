from django.shortcuts import render
import pandas as pd
import numpy as np
import json
from rest_framework.response import Response
from rest_framework.views import APIView
from scipy import spatial
import operator
import csv
import os
import gc

class Test(APIView):
    def get(self, request, movie_title):
        gc.collect()
        current_directory = os.path.dirname(__file__)  # 파일이 있는 스크립트의 디렉토리

        # 데이터 파일의 상대 경로

        # 상대 경로를 절대 경로로 변환
        absolute_path = os.path.join(current_directory, 'tmdb_5000_movies.csv')

        movies = pd.read_csv(os.path.join(current_directory, 'tmdb_5000_movies.csv'))
        credits = pd.read_csv(os.path.join(current_directory, 'tmdb_5000_credits.csv'))



        movies['genres'] = movies['genres'].apply(json.loads)
        for index, row in movies.iterrows():
            genre_list = [genre['name'] for genre in row['genres']]
            movies.at[index, 'genres'] = str(genre_list)



        movies['keywords'] = movies['keywords'].apply(json.loads)
        for index, row in movies.iterrows():
            keywords_list = [keywords['name'] for keywords in row['keywords']]
            movies.at[index, 'keywords'] = str(keywords_list)





        credits['cast'] = credits['cast'].apply(json.loads)
        for index, row in credits.iterrows():
            cast_list = [cast['name'] for cast in row['cast']]
            credits.at[index, 'cast'] = str(cast_list)



        credits['crew'] = credits['crew'].apply(json.loads)
        def get_directors(x):
            directors = [crew['name'] for crew in x if crew['job'] == 'Director']
            return directors
        credits['crew'] = credits['crew'].apply(get_directors)
        credits.rename(columns={'crew':'director'},inplace=True)




        movies = movies.merge(credits,left_on='id',right_on='movie_id',how='left')
        movies = movies[['id','original_title','genres','cast','vote_average','director','keywords']]




        new_id = list(range(0,movies.shape[0]))
        movies['new_id'] = new_id
        movies = movies[['new_id','original_title','genres','cast','vote_average','director','keywords']]




        movies['genres'] = movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
        movies['genres'] = movies['genres'].str.split(',')




        for i,j in zip(movies['genres'],movies.index):
            list2=[]
            list2=i
            list2.sort()
            movies.loc[j,'genres'] = str(list2)
        movies['genres'] = movies['genres'].str.strip('[]').str.replace(' ','').str.replace("'",'')
        movies['genres'] = movies['genres'].str.split(',')




        genreList = []
        for index, row in movies.iterrows():
            genres = row["genres"]
            
            for genre in genres:
                if genre not in genreList:
                    genreList.append(genre)




        def binary(genre_list):
            binaryList = []
            
            for genre in genreList:
                if genre in genre_list:
                    binaryList.append(1)
                else:
                    binaryList.append(0)
            
            return binaryList




        movies['binary_genres'] = movies['genres'].apply(lambda x: binary(x))






        def xstr(s):
            if s is None:
                return ''
            return str(s)
        movies['director'] = movies['director'].apply(xstr)



        directorList=[]
        for i in movies['director']:
            if i not in directorList:
                directorList.append(i)




        def binary(director_list):
            binaryList = []  
            for direct in directorList:
                if direct in director_list:
                    binaryList.append(1)
                else:
                    binaryList.append(0)
            return binaryList


        movies['binary_director'] = movies['director'].apply(lambda x: binary(x))



        movies['cast'] = movies['cast'].str.strip('[]').str.replace(' ','').str.replace("'",'').str.replace('"','')
        movies['cast'] = movies['cast'].str.split(',')




        movies['cast'] = movies['cast'].apply(lambda x: sorted(x[:4]))
        movies['cast'] = movies['cast'].apply(lambda x: ','.join(x))




        castList = []
        for index, row in movies.iterrows():
            cast = row["cast"]
            
            for i in cast:
                if i not in castList:
                    castList.append(i)



        def binary(cast_list):
            binaryList = []
            
            for genre in castList:
                if genre in cast_list:
                    binaryList.append(1)
                else:
                    binaryList.append(0)
            
            return binaryList



        movies['binary_cast'] = movies['cast'].apply(lambda x: binary(x))



        movies['keywords'] = (
            movies['keywords']
            .str.strip('[]')
            .str.replace(' ', '')
            .str.replace("'", '')
            .str.replace('"', '')
        )
        movies['keywords'] = movies['keywords'].str.split(',')



        words_list = []
        for index, row in movies.iterrows():
            genres = row["keywords"]
            
            for genre in genres:
                if genre not in words_list:
                    words_list.append(genre)



        def binary(words):
            binaryList = []
            for genre in words_list:
                if genre in words:
                    binaryList.append(1)
                else:
                    binaryList.append(0)
            return binaryList



        movies['binary_words'] = movies['keywords'].apply(lambda x: binary(x))



        movies = movies[(movies['vote_average']!=0)]
        movies = movies[movies['director']!='']



        movies['new_id']= range(movies.shape[0])



        from scipy import spatial

        def Similarity(movieId1, movieId2):
            a = movies.iloc[movieId1]
            b = movies.iloc[movieId2]
            
            genresA = a['binary_genres']
            genresB = b['binary_genres']
            
            genreDistance = spatial.distance.cosine(genresA, genresB)
            
            castA = a['binary_cast']
            castB = b['binary_cast']
            castDistance = spatial.distance.cosine(castA, castB)
            
            directA = a['binary_director']
            directB = b['binary_director']
            directDistance = spatial.distance.cosine(directA, directB)
            
            wordsA = a['binary_words']
            wordsB = b['binary_words']
            wordsDistance = spatial.distance.cosine(directA, directB)
            
            return genreDistance + directDistance + castDistance + wordsDistance



        import operator

        def recommend_movie(name):
            new_movie = movies[movies['original_title'].str.contains(name)].iloc[0].to_frame().T
            
            print('Selected Movie: ', new_movie.original_title.values[0])
            
            def getNeighbors(baseMovie, K):
                distances = []

                for index, movie in movies.iterrows():
                    if movie['new_id'] != baseMovie['new_id'].values[0].astype(int):
                        dist = Similarity(baseMovie['new_id'].values[0], movie['new_id'])
                        distances.append((movie['new_id'], dist))

                distances.sort(key=operator.itemgetter(1))
                neighbors = []

                for x in range(min(K, len(distances))):
                    neighbors.append(distances[x])

                return neighbors
            
            K = 10
            neighbors = getNeighbors(new_movie, K)
            
            data = []

            for neighbor in neighbors:
                m = {
                    "title" : str(movies.iloc[neighbor[0]][1]),
                    "genres" : str(movies.iloc[neighbor[0]][2]).strip('[]').replace(' ', ''),
                    "rating" : str(movies.iloc[neighbor[0]][4])
                }
                data.append(m)
                # print(
                # str(movies.iloc[neighbor[0]][1]) +
                # " | Genres: " +
                # str(movies.iloc[neighbor[0]][2]).strip('[]').replace(' ', '') +
                # " | Rating: " +
                # str(movies.iloc[neighbor[0]][4]))

            return data

            


        res = {
            "data" : recommend_movie(movie_title)
        }
        return Response(res)