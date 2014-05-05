from DataTypes import *


#########################################
######        LOAD DA DATA          #####
#########################################

class Loader:
    
    
    def __init__(self):
        self.users = {}
        self.movies = {}
        self.data = None
        
    
    def load_movies(self, movies_path):
        
        def binaryToGenres(binary_String):
            
            genres_Dict = {18:"unknown", 17:"Action" , 16:"Adventure", 15:"Animation", 14: "Children's", 13:"Comedy",12:"Crime", 11:"Documentary", 10:"Drama", 9:"Fantasy",8:"Film-Noir",
          7:"Horror", 6:"Musical", 5:"Mystery", 4:"Romance", 3:"Sci-Fi", 2:"Thriller", 1:"War", 0:"Western"}

            
            parsed_String = binary_String.replace('|', '')
            idStringAssociation = {} # idStringAssociation[id_de_genero] = string_de_genero 
            
            for index in range(19):
                bin = parsed_String[index]
                if bin == "1":
                    idStringAssociation[18-index] = genres_Dict[18-index]
            
            return idStringAssociation
        
        
        
        with open(movies_path) as u_item_file:
            
            u_items = u_item_file.readlines()
        
            for item in u_items:
                (movie_id, title, release_date, video_release_date, imdb_url, genres ) = item.split("|",5)
                new_Movie = Movie(movie_id,title,release_date,video_release_date,imdb_url, genres)
                new_Movie.id_String_Genres = binaryToGenres(genres)
                self.movies[int(movie_id)] = new_Movie
                
    def load_users(self, users_path):
        with open(users_path) as u_user_file:
        
            u_users = u_user_file.readlines()
    
            for user in u_users:
                (user_id, age, gender, occupation,zip_code) = user.split("|")
                self.users[int(user_id)] = User(user_id,age,gender,occupation,zip_code,self.movies)
                
    
    def load_data(self, data_path):
        
        with open(data_path) as u_data_file:
            
            u_datas = u_data_file.readlines()
            dataSet = Data(943, 1682,len(u_datas))
            # from u.info
            # 943 users
            # 1682 items
            # 100000 ratings
              
            for data in u_datas:
                (user_id, movie_id, rating, timestamp) = data.split("\t")   
                dataSet.setRating(user_id, movie_id, rating)
            
            dataSet.finalize()   
        
        self.data = dataSet
            
    
    def load(self, data_path):
        
        l = Loader()
        l.load_movies("./ml-100k/u.item")
        l.load_users("./ml-100k/u.user")
        l.load_data(data_path)
        return l