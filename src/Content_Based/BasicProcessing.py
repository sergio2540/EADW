class Preference:
    def __init__(self):
        self.genre_Preference_Dict = {} #mapeamento de id de genero para genero string
        self.preference_Frequency = {} #mapeamento de id de genero para numero de vezes que ocorre
        self.relative_Frequency = {}
        self.suggestions_And_Scores = {}#ids of movies and scores
        self.total_Added_Types = 0
    

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

         for movie_Id, movie_Obj in movies.iteritems():
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
            print("Movie:%s Rating:%f" %(movies[sorted_Id].title, self.suggestions_And_Scores[sorted_Id]))
        sorted_Suggestions = sorted([(v,k) for k,v in self.suggestions_And_Scores.items()],reverse=True)
        for sorted_Tuple  in sorted_Suggestions:
            parString = "Movie:%s Rating:%f Genres:%s\n" %(movies[sorted_Tuple[1]].title, sorted_Tuple[0], movies[sorted_Tuple[1]].genreStringRep())
            print("Movie:%s Rating:%f" %(movies[sorted_Tuple[1]].title, sorted_Tuple[0]))
            file.write(parString)
    #file.close()

  


def binaryToGenres(binary_String):
        parsed_String = binary_String.replace('|', '')
        idStringAssociation = {} # idStringAssociation[id_de_genero] = string_de_genero 
        for index in range(19):
            bin = parsed_String[index]
            if bin == "1":
                idStringAssociation[18-index] = genres_Dict[18-index]
        return idStringAssociation


#########################################
######          USERS               #####
#########################################

users = {}


class User:

    def __init__(self,user_id, age, gender, occupation,zip_code):
        self.user_id = int(user_id)
        self.age = int(age)
        self.gender = gender
        self.occupation = occupation
        self.zip_code = zip_code
        self.preference = Preference()
    
    def __str__(self):
        return "id : %d age: %d gender: %s occupation %s zip code: %s" % (self.user_id,self.age, self.gender, self.occupation, self.zip_code)

    


with open('ml-100k/u.user') as u_user_file:
    
    u_users = u_user_file.readlines()

    for user in u_users:
        (user_id, age, gender, occupation,zip_code) = user.split("|")
        users[int(user_id)] = User(user_id,age,gender,occupation,zip_code)



#########################################
######          MOVIES              #####
#########################################
movies = {}
genres_Dict = {18:"unknown", 17:"Action" , 16:"Adventure", 15:"Animation", 14: "Children's", 13:"Comedy",12:"Crime", 11:"Documentary", 10:"Drama", 9:"Fantasy",8:"Film-Noir",
          7:"Horror", 6:"Musical", 5:"Mystery", 4:"Romance", 3:"Sci-Fi", 2:"Thriller", 1:"War", 0:"Western"}

class Movie:

    def __init__(self,movie_id,title,release_date,video_release_date,imdb_url,genres):
        self.movie_id = int(movie_id)
        self.title = title
        self.release_date = release_date
        self.video_release_date = video_release_date
        self.imdb_url = imdb_url
        self.genres = genres
        self.id_String_Genres = {}
        self.user_votes = {}
        self.votes_sum = 0
        self.votes_num = 0

    
    def __str__(self):
        return "Movie id : %d Title: %s Release: %s Video Release %s IMDB URL: %s Genres %s"  % (self.movie_id,self.title, self.release_date, self.video_release_date, self.imdb_url,self.genres)

    def genreStringRep(self):
        repString = ""
        for genre_Id, genre_String in self.id_String_Genres.iteritems():
            repString += (genre_String + "|")
        return repString

with open('ml-100k/u.item') as u_item_file:
    
    u_items = u_item_file.readlines()

    for item in u_items:
        (movie_id, title, release_date, video_release_date, imdb_url, genres ) = item.split("|",5)
        new_Movie = Movie(movie_id,title,release_date,video_release_date,imdb_url, genres)
        new_Movie.id_String_Genres = binaryToGenres(genres)
        movies[int(movie_id)] = new_Movie


data_set = {}


with open('ml-100k/u1.base') as u_data_file:
    
    u_datas = u_data_file.readlines()

    for data in u_datas:
        (user_id, movie_id, rating, timestamp) = data.split("\t")
        
	if int(user_id) not in data_set.keys():
            data_set[int(user_id)] = {}
	#alterado        
	users[int(user_id)].preference.addPreferences(movies[int(movie_id)].id_String_Genres)
        
	data_set[int(user_id)][int(movie_id)] = float(rating)
    evaluated_movie = movies[int(movie_id)]
    evaluated_movie.user_votes[int(user_id)] = float(rating)
    evaluated_movie.votes_sum += float(rating)
    evaluated_movie.votes_num += 1

#file = open("sorteddata.txt", 'w+')
#sortedDataByUser = sorted([(k,v) for k,v in data_set.iteritems()])
#for sortedTuple in sortedDataByUser:
   #sortedByMovieId =  sorted([(k,v) for k,v in data_set[sortedTuple[0]].iteritems()])
   #for sortedT in sortedByMovieId:
       #parSt = "User:%s     MovieId:%s     Rating:%s\n" % (sortedTuple[0], sortedT[0], sortedT[1])
       #file.write(parSt)
 
#file.close()

genres = {}
with open('ml-100k/u.genre') as u_genre_file:
    
    u_genres = u_genre_file.read()

    for g in u_genres.splitlines():
        if g == "":
            break
        (genre, genre_id) = g.split("|")
        genres[genre_id] = genre

    
#for id,obj in users.iteritems():
 #       for genr,rat in obj.preference.relative_Frequency.iteritems():
  #          print("Genre:%s Rating:%f" % (genr, rat))

#for user_Id, data_D in data_set.iteritems():
   # if user_Id == "36":
   #     for movie_Id in sorted([(int(k),v) for k,v in data_D.iteritems()]):
    #        print("Movie:%s Rating:%s Genres:%s" % (movie_Id[0], movie_Id[1], movies[str(movie_Id[0])].genreStringRep()))
#print("==============================================================================")


#file = open("Suggestions.txt",'w')
#for user_Id,user_Obj in users.iteritems():
 #   if user_Id == 197:
  #   #print("User:%d" % user_Id)
   #  users[user_Id].preference.findMovies()
    # users[user_Id].preference.printSuggestedMovies()
#print("==============================================================================")

#file.close()
