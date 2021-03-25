# CMPT361 - Project
# MacEwan University
# Authors: Robert Taylor, Jayden Laturnus, Braden Simmons

import sys
import socket
import json
import datetime
import glob
import os

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA


class server:
    serverPort = 13000

    clientConnectionSocket = None
    clientAddr = None

    """ Dictionary is formatted as follows: {"client{}": password}"""
    database = None

    serverSocket = None

    privateCipher = None

    publicCipher = None

    symkey = None

    # initialize operating system requirements
    # Requirements: bind socket,
    # does not start listening on the socket
    def __init__(self):

        try:
            # create socket
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        except socket.error as e:
            print('Error in server socket creation: ', e)
            sys.exit(1)
        
        # bind port to socket
        try:
            self.serverSocket.bind(('', self.serverPort))
        except socket.error as e:
            print('Error in server socket binding: ', e)
            sys.exit(1)

        try:
            k = open("server_private.pem", "rb")
            key = RSA.importKey(k.read())
            self.privateCipher = PKCS1_OAEP.new(key)
            k.close()
        except:
            print("Couldn't open server private key")
            sys.exit(1)

        try:
            k = open("server_public.pem", "rb")
            key = RSA.importKey(k.read())
            self.publicCipher = PKCS1_OAEP.new(key)
            k.close()
        except:
            print("Couldn't open server public key")
            sys.exit(1)

        try:
            d = open("user_pass.json", 'r')
            self.database = json.loads(d.read())
            d.close()
        except:
            print("Couldn't open user_pass.json")
            sys.exit(1)
    
    # starts listening on the socket and handles input from client
    def start(self):
        while 1:
            try:
                self.waitForConnection()
                
                pid = os.fork()
                if pid == 0:
                    self.handleConnection()

            # these exceptions kept getting thrown when the
            # client experienced its own error. simply terminate
            # the client is one of them is thrown
            except BrokenPipeError:
                self.terminateClient()

            except ConnectionResetError:
                self.terminateClient()

    def handleConnection(self):
        optionsMessage = "\nSelect the operation:\n1) Create and send an email\n2) Display the inbox list\n3) Display the email contents\n4) Terminate the connection\n\nChoice: "

        # Assign the client username to access the email directories
        cl = json.loads((self.privateCipher.decrypt(self.clientConnectionSocket.recv(2048))).decode('ascii'))
        user = cl["username"]
        password = cl["password"]

        if (user in self.database) and (password == self.database[user]):
            try:
                client_pub = open("{}_public.pem".format(user), 'r')
                cipher = PKCS1_OAEP.new(RSA.import_key(client_pub.read()))
            except:
                print("Failed to open public key")
                sys.exit(1)
    
            self.symkey = get_random_bytes(16)
            self.symCipher = AES.new(self.symkey, AES.MODE_ECB)
            self.clientConnectionSocket.send(cipher.encrypt(self.symkey))
        else:
            self.clientConnectionSocket.send("Invalid username or password").encode('ascii')
            sys.exit(0)

        message = self.receiveMessageASCII(2048)

        if message != "OK":
            self.terminateClient()
            sys.exit(1)
        
        self.sendMessageASCII(optionsMessage)

        while 1:

            message = self.receiveMessageASCII(2048)

            if not message.isdigit():
                self.sendMessageASCII("Error: not a number\n\n" + optionsMessage)
                continue
            
            message = int(message)

            if message == 1:
                self.sendEmail()

            elif message == 2:
                self.viewInbox()
                continue

            elif message == 3:
                self.viewEmail(optionsMessage)
                continue

            elif message == 4:
                self.terminateClient()
                break
                
            else:
                print(message)
                self.sendMessageASCII("Invalid Option\n" + optionsMessage)
                continue
            
            self.sendMessageASCII(optionsMessage)


        os._exit(0)

    #Process the email sent by the client
    def sendEmail(self):
        self.sendMessageASCII("Send the email")

        #get size from client
        size = self.receiveMessageASCII(2048)

        if("Invalid File!" in size or "Message is too long!" in size):
            print("Invalid Message!")

        else:
            #create the email
            message = self.createMessage(size)
            emailSplit = message.split("\n")

            #who is the message from
            emailFromSplit = emailSplit[0].split()
            emailFrom = emailFromSplit[1]

            #Content
            emailContent = emailSplit[len(emailSplit) - 1]

            #the title of the email
            emailTitleSplit = emailSplit[2].split()
            emailTitle = emailTitleSplit[1]

            if(len(emailTitle) > 100 or len(emailContent) > 1000000):
                print("Invalid Message!")

            else:
                #who is the email for
                to = emailSplit[1].split()
                names = ""
                if(len(to) > 1):
                    if(";" in to[1]):
                        names = to[1].split(";")
                    else:
                        names = [to[1]]
                else:
                    names = " "

                flag = 0
                for name in names:
                    if name.lower() == "client1" or name.lower() == "client2" or name.lower() == "client3" or name.lower() == "client4" or name.lower() == "client5":
                        if(flag == 0):
                            #print the message that the email was recieved
                            self.createReceiveMessage(emailFrom, names, len(emailContent))
                            flag = 1

                        #insert date and time into the email
                        self.getDateAndTime(emailSplit)

                        temp = ""
                        fileName = emailFrom + "_" + emailTitle + ".txt"
                        cwd = os.getcwd()
                        for globName in glob.glob(cwd + "/*"):
                            if name.lower() in globName:
                                path = os.path.join(globName, fileName)
                                f = open(path, "w")
                                for elem in emailSplit:
                                    temp += elem + "\n"
                                f.write(temp)
                                f.close()
                    else:
                        print(name + " is an invalid recipient!")
                        

    def viewInbox(self):
        message = "{:<15} {:<15} {:<30} {:<15}".format("Index", "From", "DateTime", "Title")

        emails = self.buildEmailList()
        sortedEmails = self.sortEmails(emails)

        for i, email in enumerate(sortedEmails):
            message = "{}\n{:<15} {:<15} {:<30} {:<15}".format(message, str(i+1), str(email["From"]), str(email["DateTime"]), str(email["Title"]))

        self.sendMessageASCII(message)

    def viewEmail(self, optionsMessage):
        self.sendMessageASCII("Enter the email index you wish to view: ")
        message = self.receiveMessageASCII(2048)

        if not message.isdigit():
            self.sendMessageASCII("Error: Not an Index.")
            return

        index = int(message)
        emails = self.buildEmailList()
        sortedEmails = self.sortEmails(emails)

        if index < 1 or index > len(sortedEmails):
            self.sendMessageASCII("Error: Index Out of Range.")
            return

        email = sortedEmails[index-1]["FileName"]

        with open(email, "r") as e:
            contents = ''.join(e.readlines())
            self.sendMessageASCII("\n" + contents + "\n")

    def sortEmails(self, emails):
        emailContents = []

        for email in emails:
            with open (email, "r") as e:
                entry = {}
                lines = e.readlines()
                # Assign file values
                entry["From"] = lines[0].split(':')[1].strip()
                entry["DateTime"] = ''.join(lines[2].split(':')[1:]).strip()
                entry["Title"] = lines[3].split(':')[1].strip()
                entry["FileName"] = email
                emailContents.append(entry)

        return sorted(emailContents, key=lambda k: k['DateTime'])

    def buildEmailList(self):
        emails = []

        for f in os.listdir(self._client):
            if f.endswith(".txt"):
                emails.append(os.path.join(self._client, f))

        return emails

    #create the confirmation message that the email was recieved
    def createReceiveMessage(self, sender, to, size):
        m = "An email from " + sender + " is sent to "
        for i in range(len(to)):
            if(i == len(to) - 1):
                m += to[i]
            else:
                m += to[i] + ";"
        m += " has a content length of " + str(size) + ".\n"
        print(m)

    #Get date and time and insert into list
    def getDateAndTime(self, emailList):
        dateAndTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        time = "Time and Date: " + str(dateAndTime)
        emailList.insert(2, time)

    #Create email based on client messages
    def createMessage(self, size):
        message = ""
        email = self.receiveMessageASCII(2048)
        message += email
        total = sys.getsizeof(email)
        while total < int(size):
            total += sys.getsizeof(email)
            email = self.receiveMessageASCII(2048)
            message += email
        return message

    # Terminate client connection
    def terminateClient(self):
        self.clientConnectionSocket.close()

    # blocks waiting for client to connect
    def waitForConnection(self):
        self.serverSocket.listen(0)
        self.clientConnectionSocket, self.clientAddr = self.serverSocket.accept()

    # Send a message to connected client encoded as ascii
    def sendMessageASCII(self, message):
        ct_bytes = self.symCipher.encrypt(pad(message.encode('ascii'),16))
        self.clientConnectionSocket.send(ct_bytes)

    # recieve a message and decode as ascii up to size
    def receiveMessageASCII(self, size):
        enc_message = self.clientConnectionSocket.recv(size)
        padded_message = self.symCipher.decrypt(enc_message)
        #Remove padding
        encoded_message = unpad(padded_message,16)
        return encoded_message.decode('ascii')

def main():
    s = server()
    s.start()

main()