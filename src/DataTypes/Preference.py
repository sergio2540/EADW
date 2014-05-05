from __future__ import division

class Preference:
    def __init__(self, movies):
        self.genre_Preference_Dict = {} #mapeamento de id de genero para genero string
        self.preference_Frequency = {} #mapeamento de id de genero para numero de vezes que ocorre
        self.relative_Frequency = {}
        self.suggestions_And_Scores = {}#ids of movies and scores
        self.total_Added_Types = 0
        self.movies = movies
    

    def updateRelativeFrequency(self):
        for id,times in self.preference_Frequency.iteritems():
                 self.relative_Frequency[id] = times / self.total_Added_Types 
       

    def addPreferences(self, new_Preferences):
         self.total_Added_Types += len(new_Preferences) #adicionar por cada genero mais um.
         self.genre_Preference_Dict.update(new_Preferences)

         #print(self.total_Added_Types)
         for id in new_Preferences.keys():
             if not self.preference_Frequency.has_key(id):
                self.preference_Frequency[id] = 0       #primeira vez que tipo e observado
             pref_Frequency_Updated = (self.preference_Frequency[id] + 1) #buscar valor antigo de preferencia para o tipo e adicionar um pois temos mais uma ocorrencia
             self.preference_Frequency[id] =  pref_Frequency_Updated #actualizar o valor
             #self.relative_Frequency[id] =  (pref_Frequency_Updated / self.total_Added_Types) #recalcular a frequencia relativa
             self.updateRelativeFrequency() 
             #print("Type:%s Freq:%f" % (id,self.relative_Frequency[id]))



    def findMovies(self):

         for movie_Id, movie_Obj in self.movies.iteritems():
              retString = ""

              for type_Id in movie_Obj.id_String_Genres.keys():

                 if(type_Id in self.genre_Preference_Dict.keys()):

                    if not self.suggestions_And_Scores.has_key(movie_Id):
                        self.suggestions_And_Scores[movie_Id] = 0
                    self.suggestions_And_Scores[movie_Id] += self.relative_Frequency[type_Id]

    #file = open("Sorted.txt", 'w')
    def printSuggestedMovies(self):
        sorted_Suggestions = sorted(self.suggestions_And_Scores, key=self.suggestions_And_Scores.__getitem__,reverse=True)
        for sorted_Id  in sorted_Suggestions:
            print("Movie:%s Rating:%f" %(self.movies[sorted_Id].title, self.suggestions_And_Scores[sorted_Id]))
        sorted_Suggestions = sorted([(v,k) for k,v in self.suggestions_And_Scores.items()],reverse=True)
        for sorted_Tuple  in sorted_Suggestions:
            parString = "Movie:%s Rating:%f Genres:%s\n" %(self.movies[sorted_Tuple[1]].title, sorted_Tuple[0], self.movies[sorted_Tuple[1]].genreStringRep())
            print("Movie:%s Rating:%f" %(self.movies[sorted_Tuple[1]].title, sorted_Tuple[0]))
            file.write(parString)
    #file.close()