 # -*- coding: UTF-8 -*-
from __future__ import division
from sets import Set
import operator

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.qparser import *

from BasicProcessing import *
from Imdb import *

import os
import math
from __builtin__ import sum, max

processDb()

def createIndex():
    schema = Schema(title=TEXT(stored=True),id = NUMERIC(stored=True), content=TEXT(stored=True))
    ix = create_in("indexes/imdbIndex", schema)
    writer = ix.writer()

#adicionar dados de sinopses,realizadores,actores
    for i in range(1,1683):
        dataFilePath = "./DB/ProcessedDB//%s.txt" % str(i)
        dbfile = open(dataFilePath,'r')
        fileContent = dbfile.read()
        #print("%d" % numericId)
        docTitleDec = fileContent.split("\n")[0].decode('utf-8')
        contentDec = fileContent.decode('utf-8')
        writer.add_document(title=docTitleDec, id=i,content=contentDec)
    writer.commit()

#processDb()
#print(imdbRating)
##############adicionar dados de sinopses,realizadores,actores
createIndex()
 
##used to calculate pearson correlation between users.receives two user ids
def calculatePearsonCorrelation(userA, userB):
    dividend = 0
    tempLeftDivisor = 0
    tempRightDivisor = 0
    divisor = 0
    #print("User values for votes: %s" % data_set[userA].values())
    avgUser = sum(data_set[userA].values())/len(data_set[userA])
    avgCompUser = sum(data_set[userB].values())/len(data_set[userB])

    userWatchedMovies = data_set[userA]
    compareUserWatchedMovies = data_set[userB]
    commonMovies = Set(userWatchedMovies.keys()).intersection(Set(compareUserWatchedMovies.keys()))
    

    for movie in commonMovies:
           dividend += (userWatchedMovies[movie]-avgUser)*(compareUserWatchedMovies[movie]-avgCompUser)
           tempLeftDivisor += (userWatchedMovies[movie]-avgUser)**2
           tempRightDivisor += (compareUserWatchedMovies[movie]-avgCompUser)**2
           
    divisor = math.sqrt(tempLeftDivisor)*math.sqrt(tempRightDivisor)
    
    #Duvida?????
    if divisor == 0:
        return 0
    
    similarity = dividend / divisor
    return similarity

##similarUsersIdsPearson->dictionary that maps user to similarity to cyrrentUserId
def calculatePrediction(currentUserId,similarUsersIdsPearson,movieId):

    dividend = 0
    divisor = 0
    for userId, similarity in similarUsersIdsPearson.iteritems():
        #print("Similarity:%f" % similarity)
        if similarity < 0:
            continue
        dividend += similarity*(data_set[userId][movieId]-(sum(data_set[userId].values())/len(data_set[userId])))
        divisor += similarity
    avgUser = sum(data_set[currentUserId].values())/len(data_set[currentUserId])
    
    if divisor == 0:
        return 0
    
    return avgUser + (dividend/divisor)
  

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
def evaluate(userEvaluating , evaluatedMovieId):
            
    #print("Movie name:%s genres:%s" %(movies[evaluatedMovieId].title,movies[evaluatedMovieId].genreStringRep()))

    ##Check if we voted.
    if data_set[userEvaluating].has_key(evaluatedMovieId):
        return data_set[userEvaluating][evaluatedMovieId]

    ##Search whoosh index.
    ix = open_dir("./indexes/imdbIndex")
    similarMovies = {}
    with ix.searcher() as searcher:
        content = searcher.document(id=evaluatedMovieId)
        query = QueryParser("content", ix.schema, group=OrGroup).parse(content['content'])#####group???
        results = searcher.search(query, limit=10)
        for i, r in enumerate(results):
            if r['id'] != evaluatedMovieId: 
                similarMovies[r['id']] = results.score(i)

    #print("Found:%d similar movies" % len(similarMovies))
    #for movieId, score in similarMovies.iteritems():
        #print("Movie name:%s genres:%s" %(movies[movieId].title,movies[movieId].genreStringRep()))

      
    ##we will keep only the movies that are most similar in genre. this allows us to extend the search from 10 to 100.
    movieSimilarity = {}
    for movieId in similarMovies.keys():
        movieSimilarity[movieId] = len(Set(movies[movieId].id_String_Genres.keys()).intersection(Set(movies[evaluatedMovieId].id_String_Genres.keys())))

    ##get the maximum genre similarity
    maxSimilarity = max(movieSimilarity.values())
    mostSimilar = {}

    for movieId, similarity in movieSimilarity.iteritems():
         if similarity == maxSimilarity:
             mostSimilar[movieId] = similarMovies[movieId]
    
    mostSimilarKeys = Set(mostSimilar.keys())
    dataKeys = Set(data_set[userEvaluating].keys())
    commonKeys = mostSimilarKeys.intersection(dataKeys)

    #print("Most similar:%d" % len(mostSimilar))
    #for movieId in mostSimilarKeys:
        #print("Movie name:%s genres:%s" %(movies[movieId].title,movies[movieId].genreStringRep()))

    ##check if the most similar movies have been watched.
    commonKeysNo = len(commonKeys)
    if commonKeysNo == 0:
        print("Hasn't seen similar movies.")
    else: 
        #print("We have seen the similar movies")
        ##if we saw the common movies, we return a rating that is the average of the most similar regarding genres
        print "Media dos filmes mais comuns que eu vi"
        totalRating = 0
        for movieId in commonKeys:
            totalRating += data_set[userEvaluating][movieId]
        return totalRating/len(commonKeys)
    
    
    
    ##agora vamos buscar utilizadores que tenham visto o filme--->sergio fez isto
    ## userSimilarityDict = {}
    ## for userId, movies in data_set.iteritems():
    ##     if movieId in movies.keys():
    ##         userSimilarityDict[userId] = calculatePearsonCorrelation(user, userId)
    ##  if len(userSimilarityDict) != 0:
    ##       return calculatePrediction(user, userId)

    
    ##we search for users who watched those similar movies. 
    similarMoviesAndWatchers = {}
    for movieId, score in mostSimilar.iteritems():
        similarMoviesAndWatchers[movieId] = {'score':0, 'users':{}}
        similarMoviesAndWatchers[movieId]['score'] = score

        ##we create an association (movieId, ('score'(whoosho score), 'users':(userId,similarity to evaluator)))
        for userId, ratedByUser in data_set.iteritems():
            if ratedByUser.has_key(evaluatedMovieId):
                userWatchedMovies = data_set[userEvaluating]
                compareUserWatchedMovies = data_set[userId]

                commonMovies = Set(compareUserWatchedMovies.keys()).intersection(Set(userWatchedMovies.keys()))

                ##to find similarity between users we must check if the users have seen the same movies or a set of common movies.
                if len(commonMovies) == 0:
                    #print("The users have no movies watched in common. Zero similarity.")
                    similarMoviesAndWatchers[movieId]['users'][userId] = 0
                    continue
             
                ###Pearson correlation. How similar are the users
                similarMoviesAndWatchers[movieId]['users'][userId]=calculatePearsonCorrelation(userEvaluating, userId)
    
    #Now we calculate the predictions for every similar movies based on prrevious calculated similarities between users.
    similarMoviesAndPredictions = {}
    for movieId, scoreUsers in similarMoviesAndWatchers.iteritems():
        similarMoviesAndPredictions[movieId] = {}
        similarMoviesAndPredictions[movieId]['score'] = scoreUsers['score']

        #No one has seen this movie.
        if len(similarMoviesAndWatchers[movieId]['users']) == 0:
             #print("The movie with id:%d title:%s wasn't watched by anyone." % (movieId, movies[movieId].title))

          
            #We look for movies that are similar in genres tho this movie and do an average of the ratings.
             if not data_set.has_key(userEvaluating) or len(data_set[userEvaluating]) == 0:
                 print("User hasn't votted yet.\nIMDB rating used")
                 if imdbRating.has_key(movieId):
                     #Imdb rating 1 a 10
                     similarMoviesAndPredictions[movieId]['prediction'] = 5*imdbRating[movieId]/10
                 else:
                     similarMoviesAndPredictions[movieId]['prediction'] = 0 ##dar 0 se imdb nao tiver votaçao?---_------>se calhar deveriamos atribuir 5??

             ##we look for movies voted by the user that match the most the genres of the to be evaluated movie.
             watchedMovieSimilarity = {}
             for watchedMovieId in data_set[userEvaluating].keys():
                watchedMovieGenres = Set(movies[watchedMovieId].id_String_Genres.keys())
                evaluatedMovieGenres = Set(movies[evaluatedMovieId].id_String_Genres.keys())
                watchedMovieSimilarity[watchedMovieId] = len(watchedMovieGenres.intersection(evaluatedMovieGenres))
            
             
             maxWatchedSimilarity = max(watchedMovieSimilarity.values())
             #mostSimilarAndWatched = {}

             #Now we calculate an average for the most similar movies and give it as our estimate.
             totalRating = 0
             similarities = 0
             for similarMovieId, similarity in watchedMovieSimilarity.iteritems():
                if similarity == maxWatchedSimilarity:
                        totalRating += data_set[userEvaluating][similarMovieId]
                        similarities += 1
             similarMoviesAndPredictions[movieId]['prediction'] =  totalRating/similarities
            
            
        #Some users watched this movie. we predict based on their similarities with this user.
        #print("Prediction based on similarity")
        similarMoviesAndPredictions[movieId]['prediction'] = calculatePrediction(userEvaluating,similarMoviesAndWatchers[movieId]['users'],evaluatedMovieId)

         
    #print("These are the suggestions for each similar movie.")   
    totalRatings = 0
    notZero = 0
    for movieId, scorePrediction in similarMoviesAndPredictions.iteritems():
        print("Score prediction:%f" % scorePrediction['prediction'])
        if scorePrediction['prediction'] != 0:
            totalRatings += scorePrediction['prediction']
            notZero += 1
    
    print("Prediction based on similarity")
    return totalRatings/ notZero





#print(evaluate(30,500))


#print(evaluate(193,6))# a maior parte dos filmes parecidos não foram vistos. os restantes não foram vistos em comum com o users
#print(evaluate(193,30))
   # similarUsers = []
   # for id, user in users.iteritems():
     #   if (Set(user.preference.genre_Preference_Dict.keys()).intersection(Set(users[user].preference.genre_Preference_Dict.keys())) != 0):
     #       similarUsers[id] = 0 #este dicionario vai conter os valores de semelhanca entre 

#ix = open_dir("indexdir")
#list = []
#with ix.searcher() as searcher:
 #      query = QueryParser("content", ix.schema, group=OrGroup).parse(expression)
  #     results = searcher.search(query, limit=100)
   #    for r in results:
    #        print r
     #  print "Number of results:", results.scored_length()
                
       






