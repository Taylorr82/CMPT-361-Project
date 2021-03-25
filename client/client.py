# CMPT361 - Project
# MacEwan University
# Authors: Robert Taylor, Jayden Laturnus, Braden Simmons

import sys
import socket
import json
import time

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA

class Client:
    # Initialize operating system requirements
    # Requirements: Create socket
    def __init__(self):
        self._serverName = "127.0.0.1"
        self._serverPort = 13000

        self._serverCipher = None
        self._clientCipher = None
        self._symkey = None
        self._symCipher = None

        self._clientSocket = None

        self._userName = ""

        try:
            # Get a socket from the operating system
            self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error as e:
            print('Error in client socket creation:',e)
            sys.exit(1)

        try:
            k = open("server_public.pem", "rb")
            key = RSA.importKey(k.read())
            self._serverCipher = PKCS1_OAEP.new(key)
            k.close()

        except:
            print("Couldn't read server key")
            sys.exit(1)

    # Ask user for server name and then connect to the server
    # Handles user input and sending input to the server
    def start(self):
        self._serverName = input("Enter the server name or IP address: ")

    
        self._userName = input("Enter your username: ")
        password = input("Enter your password: ")
        try:
            k = open("{}_private.pem".format(self._userName), "rb")
            key = RSA.importKey(k.read())
            self._clientCipher = PKCS1_OAEP.new(key)
            k.close()
        except:
            print("Couldn't open client private key")
            sys.exit(1)

        try:
            #Client connect with the server
            self._clientSocket.connect((self._serverName,self._serverPort))
        
        except socket.error as e:
            print('An error occured: ', e)
            self._clientSocket.close()
            sys.exit(1)

        try:
            d = dict()
            d["username"] = self._userName
            d["password"] = password
            message = json.dumps(d)

            # encrypt username and password then send
            enc_message = self._serverCipher.encrypt(message.encode("ascii"))

            self._clientSocket.send(enc_message)

            # receive symmetric key
            ekey = self._clientSocket.recv(2048)
            try: # if it can decode ascii it's clearly not a key
                ekey = ekey.decode('ascii')
                print(ekey)
                self.terminate()
            except:
                pass
        
            self._symkey = self._clientCipher.decrypt(ekey)
            self._symCipher = AES.new(self._symkey, AES.MODE_ECB)

            self.sendMessageASCII("OK")

            # Enter option loop
            while 1:
                message = self.receiveMessageASCII(2048)

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
            self._clientSocket.close()
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
            # Receive OK from server after

            # Send the email to the server
            self.sendMessageASCII(email)
            #self._clientSocket.sendall(email.encode("ascii"))
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
        email = "From: " + self._userName + "\nTo: " + to + "\nTitle: " + title + "\nContent Length: " + str(len(message))\
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
                self._clientSocket.sendall(email.encode('ascii'))
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
        ct_bytes = self._symCipher.encrypt(pad(message.encode('ascii'),16))
        self._clientSocket.send(ct_bytes)

    # recieve a message and decode as ascii up to size
    def receiveMessageASCII(self, size):
        enc_message = self._clientSocket.recv(size)
        padded_message = self._symCipher.decrypt(enc_message)
        #Remove padding
        encoded_message = unpad(padded_message,16)
        return encoded_message.decode('ascii')

    # wraps Socket.sendall() with encryption
    def sendall(self, message):
        enc_message = self._symCipher.encrypt(pad(message.encode('ascii'), 16))
        self._clientSocket.sendall(enc_message)

    # terminate client protocol
    # Exits upon socket closure
    def terminate(self):
        print("Connection Terminated")
        self._clientSocket.close()
        sys.exit(1)


def main():
    c = Client()
    c.start()

main()