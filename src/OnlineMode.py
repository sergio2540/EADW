from os import system
import platform
from time import sleep

print("Loading data. Please wait...")
from BasicProcessing import *

professor1 = "Pavel Calado"
professor2 = "Mario Gaspar da Silva"
student1= "Sergio Alves"
student2= "Bruno Braga"


def printLinuxLogo():
    print(u"""                  .88888888:. 
                88888888.88888. 
              .8888888888888888. 
              888888888888888888 
              88' _`88'_  `88888 
              88 88 88 88  88888 
              88_88_::_88_:88888 
              88:::,::,:::::8888 
              88`:::::::::'`8888                    Movie recommendation system by: %s
             .88  `::::'    8:88.                                                   %s
            8888            `8:888. 
          .8888'             `888888. 
         .8888:..  .::.  ...:'8888888:. 
        .8888.'     :'     `'::`88:88888            Professors: %s 
       .8888        '         `.888:8888.                       %s 
      888:8         .           888:88888 
    .888:88        .:           888:88888: 
    8888888.       ::           88:888888 
    `.::.888.      ::          .88888888 
   .::::::.888.    ::         :::`8888'.:. 
  ::::::::::.888   '         .:::::::::::: 
  ::::::::::::.8    '      .:8::::::::::::. 
 .::::::::::::::.        .:888::::::::::::: 
 :::::::::::::::88:.__..:88888:::::::::::' 
  `'.:::::::::::88888888888.88:::::::::' 
        `':::_:' -- '' -'-' `':_::::'` """ % (student1, student2, professor1, professor2))
    print("\n")

def printWindowsLogo():
    print(u"""           ,-~и^  ^и-,           _,
           /          / ;^-._...,и/
          /          / /         /
         /          / /         /
        /          / /         /  Movie recommendation system by: %s
       /,.-:''-,_ / /         /                                   %s
       _,.-:--._ ^ ^:-._ __../    Professors: %s
     /^         / /и:.._и__.;                 %s
    /          / /      ^  /
   /          / /         /
  /          / /         /
 /_,.--:^-._/ /         /
^            ^ии-.___.:^  """ % (student1, student2, professor1, professor2))
    print("\n")

def linuxOnlineMode():
  while True:
    system("clear")
    printLinuxLogo()
    user = raw_input("Username:",)
    if not user.isdigit():
        continue
    if not users.has_key(int(user)):
       print("Invalid user. Please retry") 
       continue
    break
 
  loggedUser = users[int(user)]
  while True:
    system("clear")
    printLinuxLogo()
    print("1)Suggested movies")
    print("2)Rate movie")
    option = raw_input("Enter option:")
    if not option.isdigit():
        print("Invalid option(must be 1 or 2)")
        continue
    integerOption = int(option)
    if int(option) == 1:
           print("Suggested movies")
           loggedUser.preference.findMovies()
           loggedUser.preference.printSuggestedMovies()
           raw_input("Continue?",)
    elif int(option) == 2:
            print("Rate movie")
    else: 
          print("Option not in range. Must be 1 or 2.") 

def windowsOnlineMode():
  while True:
    system("cls")
    printWindowsLogo()
    user = raw_input("Username:",)
    if not user.isdigit():
        continue
    if not users.has_key(int(user)):
       print("Invalid user. Please retry") 
       continue
    break

  loggedUser = users[int(user)]

  while True:
    system("cls")
    printWindowsLogo()
    print("1)Suggested movies")
    print("2)Rate movie")
    option = raw_input("Enter option:")
    if not option.isdigit():
        print("Invalid option(must be 1 or 2)")
        continue
    integerOption = int(option)
    if int(option) == 1:
           print("Suggested movies")
           loggedUser.preference.findMovies()
           loggedUser.preference.printSuggestedMovies()
           raw_input("Continue?",)
    elif int(option) == 2:
            print("Rate movie")
    else: 
          print("Option not in range. Must be 1 or 2.") 


operatingSystem = platform.system()


if operatingSystem == "Windows":
    print "Starting Windows online mode. Please wait",
    for i in range(0,3):
        print ".",
        sleep(2)
    windowsOnlineMode()
elif operatingSystem == "Linux":
    print "Starting Linux online mode.Please wait",
    for i in range(0,3):
        print ".",
        sleep(2)
    linuxOnlineMode()
else: print("Unknown OS.")

