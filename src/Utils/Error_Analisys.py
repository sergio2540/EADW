

class Error_Analisys:
    n_corrects = 0
    accum_error = 0
    count_error = 0
    
    def collect(self, teste_r, predicted_r):
        
                error = abs(teste_r - predicted_r)
                
                if round(error) == 0:
                    self.n_corrects += 1
               
                    
                self.accum_error += error
                self.count_error += 1
                
                return error
            
                    
    def getNCorrects(self):
        return self.n_corrects
    
    def getAccumError(self):
        return self.accum_error
    
    def getCountError(self):
        return self.count_error
    
    def getMeanAbsoluteError(self):
        return self.accum_error/self.count_error
    
    
