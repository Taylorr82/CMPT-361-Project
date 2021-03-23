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

        uname = input("Enter your username: ")
        passwrd = input("Enter your password: ")

        

        #print(self.receiveMessageASCII(2048))
        #uname = input()
        #self.sendMessageASCII(uname)

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
        pass

    def viewInbox(self):
        pass;        

    def viewEmail(self):
        pass

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