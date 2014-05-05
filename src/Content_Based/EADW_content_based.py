# -*- coding: UTF-8 -*-
from __future__ import division
import operator
from sys import stdin

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.qparser import *

from DataTypes import *
from ImdbProcessor import *

import os
import math
from __builtin__ import sum, max


class Content_Based:
    
   
    
    def createIndex(self):
        schema = Schema(title=TEXT(stored=True),id = NUMERIC(stored=True), content=TEXT(stored=True))
        ix = create_in("indexes/", schema)
        writer = ix.writer()
    
        #adicionar dados de sinopses,realizadores,actores
        for i in range(1,1683):
            dataFilePath = "./DB/ProcessedDB//%s.txt" % str(i)
            dbfile = open(dataFilePath,'r')
            fileContent = dbfile.read()
            #docTitleDec = fileContent.split(" ")[0].decode('utf8')
            contentDec = fileContent.decode('utf8')
            writer.add_document(id=i,content=contentDec)
        writer.commit()
    
    def __init__(self,data,users,movies):
        
        self.MIN_RATING=1
        self.MAX_RATING=5
        self.ERROR_MINIMIZER=3
        
        load_missing_files(movies)
        #load_corrected_files(movies)
        #process_URLS(movies)
 
        #getMissing(movies)
        #getCorrected(movies)
        processDb()
        self.createIndex()
        self.movies = movies
        self.data = data

    def getAverageBasedOnGenres(self,movie):
        
        movies = self.movies
        
        #MovieId->Number of genres that match the evaluated movie.
        similarMoviesAndSimilarity = {}
        #Every Avg of every movie
        everyAvg = {}
        evaluatedMovieGenres = movies[movie].id_String_Genres
        
        #Calculate most similar and get every avg of movies.
        for movieIdent, movie in movies.iteritems():
            currentMovieGenres = movie.id_String_Genres
            similarMoviesAndSimilarity[movieIdent] = len(evaluatedMovieGenres.intersect(currentMovieGenres))
            everyAvg[movieIdent] = movie.votes_sum / movie.votes_num
            
            
         
    
        ##get the maximum genre similarity
        maxSimilarity = max(similarMoviesAndSimilarity.values())
        mostSimilar = set()
    
        #Get ids of most similar
        for movieIdent, similarity in similarMoviesAndSimilarity.iteritems():
            if similarity == maxSimilarity:
                mostSimilar[movieIdent].add(movieIdent)
        
    
        totalAvg = 0
        totalCounted = 0
        for movieIdent in mostSimilar:
            #movieAvg = everyAvg[movieIdent]['Avg']
            movieAvg = everyAvg[movieIdent]
            if movieAvg > 0:
                #totalAvg += everyAvg[movieIdent]['Avg']
                totalAvg += everyAvg[movieIdent]
                totalCounted += 1
                
        if totalAvg != 0:
                return totalAvg/totalCounted
        
        totalAvg = 0
        totalCounted = 0
        for movieIdent, score in everyAvg.iteritems():
            #movieAvg = everyAvg[movieIdent]['Avg']
            #movieAvg = everyAvg[movieIdent]
            if score > 0:
                #totalAvg += everyAvg[movieIdent]['Avg']
                totalAvg += score
                totalCounted += 1
    
        if totalAvg > 0:
            return totalAvg/totalCounted
        return self.ERROR_MINIMIZER

 
    ##used to calculate pearson correlation between users.receives two user ids
    def calculatePearsonCorrelation(self,userA, userB):
        
        data_set = self.data
        
        dividend = 0
        tempLeftDivisor = 0
        tempRightDivisor = 0
        
        #print("User values for votes: %s" % data_set[userA].values())
        avgUser = data_set.getMeanUser(userA)
        avgCompUser = data_set.getMeanUser(userB)
    
        userWatchedMovies = set(data_set.getMoviesRatedBy(userA))
        compareUserWatchedMovies = set(data_set.getMoviesRatedBy(userB))
        
        commonMovies = userWatchedMovies.intersection(compareUserWatchedMovies)
        
        
        for movie in commonMovies:
            
            a = data_set.getRating(userA,movie) - avgUser
            b = data_set.getRating(userB,movie)-avgCompUser
            
            dividend += a*b
            
            tempLeftDivisor += a**2
            tempRightDivisor += b**2
               
        divisor = math.sqrt(tempLeftDivisor)*math.sqrt(tempRightDivisor)
        
        
        if divisor == 0:
            return 0
        
        similarity = dividend / divisor
        return similarity

    ##similarUsersIdsPearson->dictionary that maps user to similarity to cyrrentUserId
    def calculatePrediction(self,currentUserId,similarUsersIdsPearson,evaluatedMovie):
        data_set = self.data
        
        dividend = 0
        divisor = 0
        for userId, similarity in similarUsersIdsPearson.iteritems():
            #print("Similarity:%f" % similarity)
            if similarity <= 0:
                continue
            avgUser = data_set.getMeanUser(userId)
            # print("AvgUser:%f" % avgUser)
            dividend += similarity*(data_set.getRating(userId,evaluatedMovie) - avgUser)
            # print("Dividend:%f" % dividend)
            divisor += similarity
            # print("Divisor:%f" % divisor)
            
        avgEvaluatingUser = data_set.getMeanUser(currentUserId) 
        
        #print("AvgEvaluatingUser:%f" % avgEvaluatingUser)
        if divisor == 0:
            return avgEvaluatingUser
        if avgEvaluatingUser + (dividend/divisor) < self.MIN_RATING:##################################################
            return self.MIN_RATING
        if avgEvaluatingUser + (dividend/divisor) > self.MAX_RATING:
            return self.MAX_RATING
        #print("Rating:%f" %(avgEvaluatingUser + (dividend/divisor)))
        return avgEvaluatingUser + (dividend/divisor)
  
  
  
    def getSimilars(self,evaluatedMovieId):
        ##Search whoosh index.
        ix = open_dir("./indexes/")
        similarMovies = {}
        with ix.searcher() as searcher:
            content = searcher.document(id=evaluatedMovieId)
            query = QueryParser("content", ix.schema, group=OrGroup).parse(content['content'])#####group???
            results = searcher.search(query, limit=25)
            for i, r in enumerate(results):
                if r['id'] != evaluatedMovieId: 
                    similarMovies[r['id']] = results.score(i)
        return similarMovies



    #####################
    #Evaluation steps:
    #1)Check if we voted for this movie. If we did, we return that result
    #2)Using BM-25 similarity and whoosh indexing, we get the most similar movies to the one we are rating (similarity regarding content).
    #3)We check if we saw the similar movies.
        #3.1)If we saw some of those movies,we return a prediction which is the average of the ratings given by us to those movies.
    #4)We check if the most similar movies have been watched by others and we create an association between movies and users who watched them, calculating
        #similarities between users.
    #5)Now, we calculate a prediction bases on the similarities calculated previously.
        #5.1)If we find a movie that has not been watched by anyone, we use movies that are genre similar to the one we are evaluating and the user
        #has watched.
            #5.1.1)If the user hasn't watched any movie at all, we give the imdb rating as a prediction since we know nothing about this user.(era fixe tirar conclusoes daqui)
        #5.2)We use the similarities between users to calculate predictions. We exclude negative similarities.
    #####################


    def evaluate(self,userEvaluating , evaluatedMovieId):
        
        data_set = self.data
        #print("Movie name:%s genres:%s" %(movies[evaluatedMovieId].title,movies[evaluatedMovieId].genreStringRep()))
    
        ##Check if we voted.
        if data_set.isInMatrix(userEvaluating,evaluatedMovieId):
            return data_set.getRating(userEvaluating, evaluatedMovieId)
    
        ##Search whoosh index.
       
        
        similarMovies = self.getSimilars(evaluatedMovieId)
        
        #print userEvaluating
        #print evaluatedMovieId
        
        print("Evaluated Movie:%s genres:%s" %(self.movies[evaluatedMovieId].title,self.movies[evaluatedMovieId].genreStringRep()))
        
        #print("Found:%d similar movies" % len(similarMovies))
        #for movieId, score in similarMovies.iteritems():
        #    print("Founded Score %s Movie:%s genres:%s" %(score, self.movies[movieId].title,self.movies[movieId].genreStringRep()))
    
          
        ##we will keep only the movies that are most similar in genre. this allows us to extend the search from 10 to 100.
        movieSimilarity = {}
        for movieId in similarMovies.keys():
            movieSimilarity[movieId] = len(set(self.movies[movieId].id_String_Genres.keys()).intersection(set(self.movies[evaluatedMovieId].id_String_Genres.keys())))
    
        ##get the maximum genre similarity
        maxSimilarity = max(movieSimilarity.values())
        mostSimilar = {}
    
        for movieId, similarity in movieSimilarity.iteritems():
            if similarity == maxSimilarity:
                mostSimilar[movieId] = similarMovies[movieId]
        
        mostSimilarMovies = set(mostSimilar.keys())
        
        movies = set(data_set.getMoviesRatedBy(userEvaluating))
        
        commonMovies = mostSimilarMovies.intersection(movies)
    
        #print("Most similar:%d" % len(mostSimilar))
        for movieId in mostSimilarMovies:
            print("Movie id: %d" % movieId)
    
        ##check if the most similar movies have been watched.
        commonMoviesNumber = len(commonMovies)
        if commonMoviesNumber == 0:
            print("Hasn't seen similar movies.")
        else: 
            #print("We have seen the similar movies")
            ##if we saw the common movies, we return a rating that is the average of the most similar regarding genres
            #print "Media dos filmes mais comuns que eu vi"
            totalRating = 0
            for movieId in commonMovies:
                totalRating += data_set.getRating(userEvaluating, movieId)
            #return round(totalRating/commonMoviesNumber
            return totalRating/commonMoviesNumber
    
        
        ##we search for users who watched those similar movies. 
        similarMoviesAndWatchers = {}
        for movieId, score in mostSimilar.iteritems():
            similarMoviesAndWatchers[movieId] = {'score':0, 'users':{}}
            similarMoviesAndWatchers[movieId]['score'] = score
    
            ##we create an association (movieId, ('score'(whoosho score), 'users':(userId,similarity to evaluator)))
            for userId in data_set.getUsersThatRate(movieId):
                
                #We check if the user has seen movies similar to ours
                #if ratedByUser.has_key(evaluatedMovieId):
                #if ratedByUser.has_key(movieId):
                
                    userWatchedMovies = set(data_set.getMoviesRatedBy(userEvaluating))
                    compareUserWatchedMovies = set(data_set.getMoviesRatedBy(userId))
    
                    commonMovies = compareUserWatchedMovies.intersection(userWatchedMovies)
    
                    ##to find similarity between users we must check if the users have seen the same movies or a set of common movies.
                    if len(commonMovies) == 0:
                        #print("The users have no movies watched in common. Zero similarity.")
                        similarMoviesAndWatchers[movieId]['users'][userId] = 0
                        continue
                 
                    ###Pearson correlation. How similar are the users
                    similarMoviesAndWatchers[movieId]['users'][userId]=self.calculatePearsonCorrelation(userEvaluating, userId)
        
        #Now we calculate the predictions for every similar movies based on previous calculated similarities between users.
        similarMoviesAndPredictions = {}
        for movieId, scoreUsers in similarMoviesAndWatchers.iteritems():
            similarMoviesAndPredictions[movieId] = {}
            similarMoviesAndPredictions[movieId]['score'] = scoreUsers['score']
    
            #No one has seen this movie.
            if len(similarMoviesAndWatchers[movieId]['users']) == 0:
                #print("The movie with id:%d title:%s wasn't watched by anyone." % (movieId, movies[movieId].title))
    
              
                #We look for movies that are similar in genres to this movie and do an average of the ratings(the movies must have 
                #been watched by the user).
                #We check if the user has voted on any movie.
                
                if len(data_set.getMoviesRatedBy(userEvaluating)) == 0:
                    #print("User hasn't voted yet.IMDB rating used")
                    if imdbRating.has_key(movieId):
                        #Imdb rating 1 a 10
                        similarMoviesAndPredictions[movieId]['prediction'] = 5*imdbRating[movieId]/10
                        
                    else:
                        similarMoviesAndPredictions[movieId]['prediction'] = self.getAverageBasedOnGenres(movieId) ##dar 0 se imdb nao tiver votaçao?---_------>se calhar deveriamos atribuir 5??
                    
                    continue
                
                ##we look for movies voted by the user that match the most the genres of the one to be evaluated movie.
                watchedMovieSimilarity = {}
                
                for watchedMovieId in data_set.getMoviesRatedBy(userEvaluating):
                    watchedMovieGenres = set(self.movies[watchedMovieId].id_String_Genres.keys())
                    evaluatedMovieGenres = set(self.movies[evaluatedMovieId].id_String_Genres.keys())
                    watchedMovieSimilarity[watchedMovieId] = len(watchedMovieGenres.intersection(evaluatedMovieGenres))
                
                
                maxWatchedSimilarity = max(watchedMovieSimilarity.values())
                #mostSimilarAndWatched = {}
                
                
                #Now we calculate an average for the most similar movies and give it as our estimate.
                totalRating = 0
                similarities = 0
                for similarMovieId, similarity in watchedMovieSimilarity.iteritems():
                    if similarity == maxWatchedSimilarity:
                            totalRating += data_set.getRating(userEvaluating,similarMovieId)
                            similarities += 1
                
                similarMoviesAndPredictions[movieId]['prediction'] =  totalRating/similarities
                
                
            #Some users watched this movie. we predict based on their similarities with this user.
            #print("Prediction based on similarity")
            #similarMoviesAndPredictions[movieId]['prediction'] = calculatePrediction(userEvaluating,similarMoviesAndWatchers[movieId]['users'],evaluatedMovieId)
            similarMoviesAndPredictions[movieId]['prediction'] = self.calculatePrediction(userEvaluating,similarMoviesAndWatchers[movieId]['users'],movieId)
             
        #print("These are the suggestions for each similar movie.")   
        totalRatings = 0
        notZeroCount = 0
        print(similarMoviesAndPredictions)
        for movieId, scorePrediction in similarMoviesAndPredictions.iteritems():
            #print("Score prediction:%f" % scorePrediction['prediction'])
            if scorePrediction['prediction'] > 0:
                totalRatings += scorePrediction['prediction']
                notZeroCount += 1
        
        print("Prediction based on similarity")
        #return round(totalRatings/ notZeroCount)
        return totalRatings/ notZeroCount
    