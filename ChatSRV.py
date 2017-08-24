__author__ = 'Trishma'


from threading import *
from socket import *
from datetime import *

# Static Variables
server_address = 'localhost'
server_port = 13375
female = ['f', 'F', 'Female', 'female']
male = ['m', 'M', 'Male', 'male']
udp_sock = socket(AF_INET, SOCK_DGRAM)
s = socket(AF_INET, SOCK_STREAM)

# Dynamic
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
            females.append(self)
            user_females.append(self.username)
            sendata = ','.join(user_males)
            udp_sock.sendto(sendata.encode(), self.client_udp)
            print('sent males')
            for mu in males:
                if mu is not None:
                    sendata = '/add ' + self.username
                    mu.socket.send(sendata.encode())
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
        else:
            print('You\'re neither male nor female, apparently')
        super().__init__()
        self.start()

    def run(self):
        invalid = '/invalid '
        confirmation = '/confirm '
        connect = '[' + str(datetime.now())[:-7] + ']' + self.username + ' has connected!\n'
        with open('Output.txt', 'a') as text_file:
            text_file.write(connect)
        print(self.username, 'has connected!')
        while True:
            try:
                rcvd = self.socket.recv(4096).decode()
                msg = '<' + self.username + '> ' + rcvd
                print(msg)
                msg_write = '[' + str(datetime.now())[:-7] + ']' + msg + '\n'
                with open('Output.txt', 'a') as text_file:
                    text_file.write(msg_write)

                # Processing the client answer (command [and optional list])
                if '/msg ' == rcvd[:5]:
                    lst, message = rcvd[5:].split(' ', 1)
                    lst = lst.split(',')
                    # works up to here
                    if self in males:
                        if not females:
                            femoff = 'No female users are online'
                            self.socket.send(femoff.encode())
                        else:
                            for fu in females:
                                for l in lst:
                                    if fu.username == l:
                                        sendata = '<' + self.username + '> ' + message
                                        fu.socket.send(sendata.encode())
                                        confirmation += ', ' + l
                                        break
                            for l in lst:
                                if l not in usernames:
                                    invalid += ', ' + l
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
                                    print(l)
                                    print(usernames)
                                    invalid += ', ' + l

                    print(invalid, confirmation)
                    if invalid is not '/invalid ':
                        self.socket.send(invalid.encode())
                    elif confirmation is not '/confirm ':
                        self.socket.send(confirmation.encode())

                elif '/msgall ' == rcvd[:8]:
                    print('he sent a /msgall command')
                    message = rcvd[8:]
                    if self in males:
                        if not females:
                            femoff = 'No female users are online'
                            self.socket.send(femoff.encode())
                        else:
                            for fu in females:
                                sendata = '<' + self.username + '> ' + message
                                fu.socket.send(sendata.encode())
                            sendata = 'Message sent to all female users'
                            self.socket.send(sendata.encode())
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
            except ValueError:
                print('Client thread \'', self.username, ' has input in an invalid format')
                err = 'Invalid input!'
                self.socket.send(err.encode())
            except IOError:
                clients.remove(self)
                if self.sex in male:
                    user_males.remove(self.username)
                    males.remove(self)
                    for fu in females:
                        if fu is not None:
                            remove = '/remove ' + self.username
                            fu.socket.send(remove.encode())
                elif self.sex in female:
                    user_females.remove(self.username)
                    females.remove(self)
                    for mu in males:
                        if mu is not None:
                            remove = '/remove ' + self.username
                            mu.socket.send(remove.encode())
                else:
                    print('hermafrodit')
                print('Client', self.username, 'has disconnected')
                dc_write = '[' + str(datetime.now())[:-7] + ']' \
                           + 'Client \'' + self.username + '\' has disconnected \n'
                with open('Output.txt', 'a') as text_file:
                    text_file.write(dc_write)
                break
while True:
    try:
        client_sock, client_addr = s.accept()
        rcv = client_sock.recv(4096).decode()
        client_name, client_sex, client_udp_addr, client_udp_port = rcv.split(',')
        CLThread(client_sock, client_addr, client_name, client_sex, client_udp_addr, client_udp_port)
    except:
        print('neko ode')