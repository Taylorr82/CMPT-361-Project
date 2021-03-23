"""
    Server program for CMPT361 file server

    Stores a database of files upploaded by client program
    Database and files are preserved after server program quits

    Author: Robert Taylor
"""

import sys
import socket
import json
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class server:
    serverPort = 13000

    clientConnected = False
    clientConnectionSocket = None
    clientAddr = None

    """ Dictionary is formatted as follows: {"filename": {"size":size, "time":time}}"""
    database = None

    databaseFile = None

    serverSocket = None

    # initialize operating system requirements
    # Requirements: bind socket,
    # does not start listening on the socket
    def __init__(self):

        try:
            self.databaseFile = open("Database.json", "r+")
            self.database = json.load(self.databaseFile)

        
        except Exception as e: 
            print(e)
            print("Error opening Database.json")
            print("Assuming database empty. Continuing with new one")
            self.database = dict()
            try:
                self.databaseFile.close()
            except:
                pass

            privateKeyLen = 256
            privateKey = get_random_bytes(int(privateKeyLen/8))
            cipherPrivate = AES.new(privateKey, AES.MODE_ECB)
            private = open("server_public.pem", "w")
            private.write(cipherPrivate)
            private.close()

            publicKeyLen = 256
            publicKey = get_random_bytes(int(publicKeyLen/8))
            cipherPublic = AES.new(publicKey, AES.MODE_ECB)
            public = open("server_public.pem", "w")
            public.write(cipherPublic)
            public.close()
        

        try:
            # create socket
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as e:
            print('Error in server socket creation:',e)
            sys.exit(1)
        
        # bind port to socket
        try:
            self.serverSocket.bind(('', self.serverPort))
        except socket.error as e:
            print('Error in server socket binding:',e)
            sys.exit(1)
    
    # starts listening on the socket and handles input from client
    def start(self):
        optionsmessage = "\n\nPlease select the operation:\n1) view uploaded files' information\n2) Upload a file\n3) Terminate the connection\nChoice: "
        while 1:
            try:
                self.waitForConnection()
                self.sendMessageASCII("Welcome to our system.\nEnter your username: ")
                uname = self.receiveMessageASCII(2048)
                if uname != "user1":
                    self.sendMessageASCII("Incorrect username. Connection Terminated.")
                    self.terminateClient()
                    continue
                
                self.sendMessageASCII(optionsmessage)

                while self.clientConnected:

                    message = self.receiveMessageASCII(2048)
                    if not message.isdigit():
                        self.sendMessageASCII("Error: not a number\n\n"+optionsmessage)
                        continue
                    
                    message = int(message)

                    if message == 1:
                        self.sendEmail()

                    elif message == 2:
                        self.viewInbox()

                    elif message == 3:
                        self.viewEmail()

                    elif message == 4:
                        self.terminateClient()
                        continue
                        
                    else:
                        self.sendMessageASCII("Invalid Option\n"+optionsmessage)
                        continue

                    self.sendMessageASCII(optionsmessage)

            # these exceptions kept getting thrown when the
            # client experienced its own error. simply terminate
            # the client is one of them is thrown
            except BrokenPipeError:
                self.terminateClient()

            except ConnectionResetError:
                self.terminateClient()

    def sendEmail(self):
        pass

    def viewInbox(self):
        pass

    def viewEmail(self):
        pass

    # Terminate client connection
    def terminateClient(self):
        self.clientConnectionSocket.close()
        self.clientConnected = False

    # blocks waiting for client to connect
    def waitForConnection(self):
        self.serverSocket.listen(0)
        self.clientConnectionSocket, self.clientAddr = self.serverSocket.accept()
        self.clientConnected = True

    #send a message to the client encoded as ascii
    def sendMessageASCII(self, message):
        self.clientConnectionSocket.send(message.encode("ascii"))

    # recieve a message and decode as ascii up to size
    def receiveMessageASCII(self, size):
        return self.clientConnectionSocket.recv(size).decode('ascii')

def main():
    s = server()
    s.start()

main()