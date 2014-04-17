import argparse

class ArgParser:
    
    #########################################
    ######          PARSING             #####
    #########################################
    
    parser = argparse.ArgumentParser(description='Recommend Movies.')
    parser.add_argument('--online', type=bool, default=False,
                       help='prompt interactive console (Default=False)')
    parser.add_argument('--training',default="./ml-100k/u.data",
                       help='path to batch training file(Default=./ml-100k/u.data)')
    parser.add_argument('--test',
                       help='path to batch test file')
    
    
    def parse(self):
        return self.parser.parse_args()