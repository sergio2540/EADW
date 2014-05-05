from DataTypes import Preference

class User:

    def __init__(self,user_id, age, gender, occupation,zip_code, movies):
        self.user_id = int(user_id)
        self.age = int(age)
        self.gender = gender
        self.occupation = occupation
        self.zip_code = zip_code
        self.preference = Preference.Preference(movies)
    
    def __str__(self):
        return "id : %d age: %d gender: %s occupation %s zip code: %s" % (self.user_id,self.age, self.gender, self.occupation, self.zip_code)

    

   
