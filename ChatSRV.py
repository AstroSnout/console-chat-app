__author__ = 'Trishma'


from threading import *
from socket import *
from datetime import *

# Static
server_address = 'localhost'
server_port = 13375
female = ['f', 'F', 'Female', 'female']
male = ['m', 'M', 'Male', 'male']
udp_sock = socket(AF_INET, SOCK_DGRAM)
s = socket(AF_INET, SOCK_STREAM)

# Vars
females = []
males = []
usernames = []
user_males = []
user_females = []
clients = []


s.bind((server_address, server_port))
s.listen(5)
print('Server is ready to accept new connections')


# Server thread for each client ------------------------------------------
class CLThread (Thread):
    def __init__(self, cl_sock, cl_addr, cl_name, cl_sex, cl_udp_addr, cl_udp_port):
        self.socket = cl_sock
        self.address = cl_addr
        self.username = cl_name
        self.sex = cl_sex
        self.client_udp = (cl_udp_addr, int(cl_udp_port))

        clients.append(self)
        usernames.append(self.username)

        if cl_sex in female:
            # Add thread to list of females
            females.append(self)
            # Add username to list of female usernames
            user_females.append(self.username)
            # Send the list of males to this client
            sendata = ','.join(user_males)
            udp_sock.sendto(sendata.encode(), self.client_udp)
            print('sent males')
            # Send other males that a new female joined
            for mu in males:
                if mu is not None:
                    sendata = '/add ' + self.username
                    mu.socket.send(sendata.encode())
        # Works the same as the "if cl_sex in female:" block
        elif cl_sex in male:
            males.append(self)
            user_males.append(self.username)
            sendata = ','.join(user_females)
            udp_sock.sendto(sendata.encode(), self.client_udp)
            print('sent females')
            for fu in females:
                if fu is not None:
                    sendata = '/add ' + self.username
                    fu.socket.send(sendata.encode())
        # Redundant else statement
        else:
            print('You\'re neither male nor female, apparently')
        # Calls the constructor of super class (Thread)
        super().__init__()
        self.start()

    # Is called by self.start()
    def run(self):
        # String formating
        connect = '[' + str(datetime.now())[:-7] + ']' + self.username + ' has connected!\n'
        # Writes a newly connected user (this user) to a log file "Output.txt"
        with open('Output.txt', 'a') as text_file:
            text_file.write(connect)
        print(self.username, 'has connected!')

        while True:
            invalid = '/invalid '
            confirmation = '/confirm '
            try:
                rcvd = self.socket.recv(4096).decode()
                msg = '<' + self.username + '> ' + rcvd
                print(msg)
                msg_write = '[' + str(datetime.now())[:-7] + ']' + msg + '\n'
                with open('Output.txt', 'a') as text_file:
                    text_file.write(msg_write)
                # Processing the client answer (command [and optional list])
                # Command /msg user1,user2 message
                if '/msg ' == rcvd[:5]:
                    # Splits the data on the 2nd space
                    lst, message = rcvd[5:].split(' ', 1)
                    # Splits the users string into a list
                    lst = lst.split(',')
                    # Checks if user (this user) is a male
                    if self in males:
                        # Checks if females list is empty
                        if not females:
                            # Sends the appropriate message to user (this user)
                            femoff = 'No female users are online'
                            self.socket.send(femoff.encode())
                        else:
                            # Looks for a female user that is also within the users list that the client sent
                            for fu in females:
                                for l in lst:
                                    if fu.username == l:
                                        # Sends the message to the specified user
                                        sendata = '<' + self.username + '> ' + message
                                        fu.socket.send(sendata.encode())
                                        # Making of the confirmation that we send to the user (this user)
                                        # So that he knows who the messages were sent too
                                        confirmation += ', ' + l
                                        break
                            # Checks if the specified users are online
                            for l in lst:
                                if l not in usernames:
                                    invalid += ', ' + l
                    # Works the same as "if self in males:" block
                    elif self in females:
                        if not males:
                            maloff = 'No male users are online'
                            self.socket.send(maloff.encode())
                        else:
                            for mu in males:
                                for l in lst:
                                    if mu.username == l:
                                        sendata = '<' + self.username + '> ' + message
                                        mu.socket.send(sendata.encode())
                                        confirmation += ', ' + l
                                        break
                            for l in lst:
                                if l not in usernames:
                                    invalid += ', ' + l

                    print(invalid, confirmation)
                    if invalid is not '/invalid ':
                        self.socket.send(invalid.encode())
                    elif confirmation is not '/confirm ':
                        self.socket.send(confirmation.encode())
                # Command /msgall that sends a message to all opposite sex users
                elif '/msgall ' == rcvd[:8]:
                    print('he sent a /msgall command')  # Debug
                    # Sloppy way of splitting a string
                    message = rcvd[8:]
                    if self in males:
                        # Checks if females list is empty
                        if not females:
                            femoff = 'No female users are online'
                            self.socket.send(femoff.encode())
                        else:
                            # Sends the message to all female user
                            for fu in females:
                                sendata = '<' + self.username + '> ' + message
                                fu.socket.send(sendata.encode())
                            # Returns a confirmation that it indeed sent the message to all female users
                            sendata = 'Message sent to all female users'
                            self.socket.send(sendata.encode())
                    # Works the same as "if self in males:" block
                    if self in females:
                        if not males:
                            maloff = 'No female users are online'
                            self.socket.send(maloff.encode())
                        else:
                            for mu in males:
                                sendata = '<' + self.username + '> ' + message
                                mu.socket.send(sendata.encode())
                            sendata = 'Message sent to all male users'
                            self.socket.send(sendata.encode())

            # Error handling ---------------------------------------------
            # Basically catches an error and returns a message to the user (this user)
            except ValueError:
                print('Client thread \'', self.username, ' has input in an invalid format')
                err = 'Invalid input!'
                self.socket.send(err.encode())
            except IOError:
                # Removes this thread from clients
                clients.remove(self)
                if self.sex in male:
                    # Removes this user's username
                    user_males.remove(self.username)
                    # Removes this thread from male clients
                    males.remove(self)
                    for fu in females:
                        # Sends a command to all females to remove user (this user)
                        # from their local lists
                        if fu is not None:
                            remove = '/remove ' + self.username
                            fu.socket.send(remove.encode())
                # Works the same as "if self.sex in male:" block
                elif self.sex in female:
                    user_females.remove(self.username)
                    females.remove(self)
                    for mu in males:
                        if mu is not None:
                            remove = '/remove ' + self.username
                            mu.socket.send(remove.encode())
                # Redundant else statement
                else:
                    print('hermafrodit')

                print('Client', self.username, 'has disconnected')
                # Prepares a string
                dc_write = '[' + str(datetime.now())[:-7] + ']' \
                           + 'Client \'' + self.username + '\' has disconnected \n'
                # Writes the disconnected user to the log file
                with open('Output.txt', 'a') as text_file:
                    text_file.write(dc_write)
                break


# Main loop
while True:
    try:
        # Accepts a connection
        client_sock, client_addr = s.accept()
        # Receives client info
        rcv = client_sock.recv(4096).decode()
        # Splits client info
        client_name, client_sex, client_udp_addr, client_udp_port = rcv.split(',')
        # Initializes an object
        CLThread(client_sock, client_addr, client_name, client_sex, client_udp_addr, client_udp_port)
    except:
        print('Someone disconnected!')