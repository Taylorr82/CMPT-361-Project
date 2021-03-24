# CMPT361 - Project
# MacEwan University
# Authors: Robert Taylor, Jayden Laturnus, Braden Simmons

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

        # Added username here
        self._username = ""

    # Ask user for server name and then connect to the server
    # Handles user input and sending input to the server
    def start(self):
        self.serverName = input("Enter the server name or IP address: ")

        try:
            #Client connect with the server
            self.clientSocket.connect((self.serverName,self.serverPort))
            connected = True
        
        except socket.error as e:
            print('An error occured: ', e)
            self.clientSocket.close()
            sys.exit(1)

        try:
            # Username chain
            message = self.receiveMessageASCII(2048)
            self._username = input(message)
            self.sendMessageASCII(self._username)
            # Password chain
            message = self.receiveMessageASCII(2048)
            password = input(message)
            self.sendMessageASCII(password)

            # Enter option loop
            while connected:
                message = self.receiveMessageASCII(2048)

                if "Invalid username or password.\nTerminating.\n" in message:
                    self.terminate()

                option = input(message)

                while (len(option) == 0) or (not option.isdigit()):
                    option = input("Invalid option. Please try again: ")

                self.sendMessageASCII(option)

                option = int(option)

                if option == 1:
                    self.sendEmail()
                    continue

                elif option == 2:
                    self.viewInbox()
                    continue

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

            # Send the size of the email to the server
            size = sys.getsizeof(email)
            self.sendMessageASCII(str(size))

            # Send the email to the server
            self.clientSocket.sendall(email.encode("ascii"))
            print("The message is sent to the server\n")
            
        else:
            self.readFile(to, title)

    def viewInbox(self):
        message = self.receiveMessageASCII(2048)
        print(message)
        self.sendMessageASCII("OK")

    def viewEmail(self):
        message = self.receiveMessageASCII(2048)
        index = input(message)
        self.sendMessageASCII(str(index))
        # Receive email contents
        message = self.receiveMessageASCII(2048)
        print(message)
        self.sendMessageASCII("OK")

    #Create the email that will be sent to the server
    def createEmail(self, to, title, message):
        email = "From: " + self._username + "\nTo: " + to + "\nTitle: " + title + "\nContent Length: " + str(len(message))\
            + "\nContent: \n" + message
        return email

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
                print("Message is too long!\n")
                self.sendMessageASCII("Message is too long!")
                f.close()

            else:
                email = self.createEmail(to, title, message)
                # Send the size of the email to the server
                size = sys.getsizeof(email)
                self.sendMessageASCII(str(size))

                # Send the email to the server
                self.clientSocket.sendall(email.encode('ascii'))
                f.close()
                print("The message is sent to the server\n")

        except FileNotFoundError:
            print("File does not exist.")
            self.sendMessageASCII("Invalid File!")

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