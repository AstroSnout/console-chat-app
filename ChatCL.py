__author__ = 'Trishma'


from threading import *
from socket import *
from time import sleep
import sys

# Two TCP sockets? - one for commands, the other for messages


# Static variables
SRV_ADDRESS = 'localhost'
SRV_PORT = 13375
VALID_SEX = ['m', 'M', 'Male', 'male', 'f', 'F', 'Female', 'female']
INVALID_USERNAME = [',', ' ', ';', '\\']
VALID = True
OPP_OFFLINE = True


online_users = []

# Listener
class Listen(Thread):
    def __init__(self, lis_s):
        super().__init__()
        self.socket = lis_s
        self.start()
        print('Listening...')


    def run(self):
        while True:
            try:
                rcv = self.socket.recv(4096).decode()
                if '/invalid ' in rcv[:9]:
                    print('Message not sent to: ' + rcv[11:])
                elif '/confirm ' in rcv[:9]:
                    print('Message sent to: ' + rcv[11:])
                elif '/rip ' in rcv[:5]:
                    print(rcv[5:])
                elif '/remove ' in rcv[:8]:
                    online_users.remove(rcv[8:])
                    print('User', rcv[8:], ' has disconnected')
                elif '/add ' in rcv[:5]:
                    online_users.append(rcv[5:])
                    print('User', rcv[5:], 'has connected')
                else:
                    print(rcv)

            except:
                print('Disconnected from the server')
                break


# Connection method
def connect(server_address, server_port):
    while True:
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((server_address, server_port))
            udp_sock = socket(AF_INET, SOCK_DGRAM)
            udp_sock.bind((server_address, 0))
            print('Connected!')
            listenClass = Listen(sock)
            return sock, udp_sock, listenClass
        except:
            print('Failed to connect. Retrying in 5 seconds...')
            sleep(5)

# Username
while True:
    USERNAME = input('Input your username: ')
    if USERNAME is '':
        print('Invalid input! You have to enter something...')
        continue
    for u in USERNAME:
        if u in INVALID_USERNAME:
            print('Invalid input! Characters ', INVALID_USERNAME, 'are not allowed!')
            VALID = False
            break
        else:
            VALID = True
    if VALID:
        break

# Sex
while True:
    SEX = input('Input your sex : ')
    if SEX in VALID_SEX:
        break
    else:
        print('Invalid input! Allowed inputs are: \n', VALID_SEX)

# Connection
s, udp_sock, listenClass = connect(SRV_ADDRESS, SRV_PORT)


# Send Username and Sex
tup = udp_sock.getsockname()
HOST = tup[0]
PORT = tup[1]
USER_SEX_UDP = USERNAME + ',' + SEX + ',' + str(HOST) + ',' + str(PORT)
s.send(USER_SEX_UDP.encode())
received_users = udp_sock.recv(4096).decode()
online_users = received_users.split(',')
print('Input format is: \'/msg user1,user2 your message here\' '
      'or \'/msgall your message here\'')
print('For a list of available commands use \'/help\'.')

# Main loop
while True:
    text = input()
    if text == '/list':
        print('Opposite sex currently online: ', online_users)
    elif text == '/help':
        print('/msg [users] message ; /msgall message ; /list ; /help ; /quit')
    elif text == '/quit':
        s.close()
        break
    else:
        try:
            s.send(text.encode())
        except:
            print('Failed to send the message to the server')