"""
    Client program for CMPT361 File server

    Handles sending commands and data to the file server

    Author: Robert Taylor
"""

import sys
import socket
import json
import time

class client:
    serverName = "127.0.0.1"
    serverPort = 13000

    clientSocket = None

    connected = False

    # Initialize operating system requirements
    # Requirements: Create socket
    def __init__(self):

        try:
            # Get a socket from the operating system
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as e:
            print('Error in client socket creation:',e)
            sys.exit(1)

        self.uname = input("Enter your username: ")
        self.passwrd = input("Enter your password: ")   

    # Ask user for server name and then connect to the server
    # Handles user input and sending input to the server
    def start(self):
        self.serverName = input("Enter the server name or IP address: ")

        try:
            #Client connect with the server
            self.clientSocket.connect((self.serverName,self.serverPort))
            connected = True
        
        except socket.error as e:
            print('An error occured:',e)
            self.clientSocket.close()
            sys.exit(1)

        while connected:
            try:
                message = self.receiveMessageASCII(2048)
                print(message)
                if "Terminated" in message:
                    self.terminate()

                option = input()

                while (len(option) == 0) or (not option.isdigit()):
                    print("invalid option. Please try again: ")
                    option=input()

                self.sendMessageASCII(option)

                option = int(option)

                if option == 1:
                    self.sendEmail()
                    continue

                elif option == 2:
                    self.viewInbox()

                elif option == 3:
                    self.viewEmail()

                elif option == 4:
                    self.terminate()

                else:
                    continue

            except socket.error:
                print("unknown socket error")
                self.clientSocket.close()
                sys.exit(1)

    def sendEmail(self):
        m = self.receiveMessageASCII(2048)
        to = input("Enter destinations (separated by ;): ")
        title = self.getTitle()
        choice = self.getChoice()
        if(choice.strip().lower() == "n"):
            message = self.getMessage()
            email = self.createEmail(to, title, message)

            #send the size of the email to the server
            size = sys.getsizeof(email)
            self.sendMessageASCII(str(size))

            #send the email to the server
            self.clientSocket.sendall(email)
            #self.sendSegments(size, email)
            
        else:
            self.readFile(to, title)
            

    def viewInbox(self):
        pass;        

    def viewEmail(self):
        pass

    #Create the email that will be sent to the server
    def createEmail(self, to, title, message):
        email = "From: " + self.uname + "\nTo: " + to + "\nTitle: " + title + "\nContent Length: " + str(len(message))\
            + "\nContent: \n" + message
        return email

    #send the contents to the server
    def sendSegments(self, size, contents):
        total = 0
        while total < size:
            s = self.clientSocket.send(contents.encode("ascii"))
            total += s

    #Get the title of the email
    def getTitle(self):
        title = input("Enter title: ")
        while len(title) > 100:
            title = input("Too many characters! Enter title: ")
        return title

    #send a message based on a file
    def readFile(self, to, title):
        filename = input("Enter filename: ")
        filename = filename.strip()
        try:
            f = open(filename, "r")
            message = f.read()
            if(len(message) > 1000000):
                f.close()
                print("Message is too long!\n")
            else:
                email = self.createEmail(to, title, message)
                f.close()

                #send the size of the email to the server
                size = sys.getsizeof(email)
                self.sendMessageASCII(str(size))

                #send the email to the server
                self.clientSocket.sendall(email)
                #self.sendSegments(size, email)

        except FileNotFoundError:
                print("File does not exist")

    #Get the choice of message
    def getChoice(self):
        choice = input("Would you like to load the contents from a file (Y/N): ")
        while choice.lower() != "y" and choice.lower() != "n":
            choice = input("Would you like to load the contents from a file (Y/N): ")
        return choice

    #Get the message
    def getMessage(self):
        message = input("Enter message contents: ")
        while len(message) > 1000000:
            message = input("Too many characters! Enter message contents: ")
        return message

    # Send a message to connected server encoded as ascii
    def sendMessageASCII(self, message):
        self.clientSocket.send(message.encode("ascii"))

    # Receive a message with length up to size
    def receiveMessageASCII(self, size):
        return self.clientSocket.recv(size).decode('ascii')

    # terminate client protocol
    # Exits upon socket closure
    def terminate(self):
        print("Connection Terminated")
        self.clientSocket.close()
        sys.exit(1)


def main():
    c = client()
    c.start()

main()