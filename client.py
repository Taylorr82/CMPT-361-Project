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
                    self.sendInfo()
                    continue

                elif option == 2:
                    self.uploadFile()

                elif option==3:
                    self.terminate()

                else:
                    continue

            except socket.error:
                print("unknown socket error")
                self.clientSocket.close()
                sys.exit(1)

    # Upload file Protocol
    # Receive and print prompt for name, send name and size of file. 
    # Receive "OK {size}" from server and then upload file
    def uploadFile(self):
        done = False
        print(self.receiveMessageASCII(2048))
        fname = input()
        while not done:
            try:
                upload_f = open(fname,"rb")
                done = True
            except:
                print("invalid file. please try again: ")

        # find the end of the file
        upload_f.seek(0,2)

        #get the size of the file
        size = upload_f.tell()

        # return to the beginning to send file
        upload_f.seek(0,0)
        self.sendMessageASCII("{}\n{}".format(fname,size))

        ack = self.receiveMessageASCII(2048)
        print(ack)
        if "OK" in ack:
            sentData = 0
            try:
                while sentData != size:
                    data = upload_f.read(2048)
                    sentData += len(data)
                    self.clientSocket.send(data)
            except:
                print("Error uploading file.")
                sys.exit(1)

        print("Upload process complete.")
    
    # get metadata protocol
    # Client is only responsible for printing what the server sends
    def sendInfo(self):
        print(self.receiveMessageASCII(2048))
        

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