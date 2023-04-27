#----------------------------------------------------------------------------
# Created By  : Eashan Sapre
# Collaborators: es4069, ks4065
# Created Date: 25/03/2023
# version ='1.0'
# ---------------------------------------------------------------------------
__author__ = "Eashan Sapre"
__email__ = "es4069@columbia.edu"
__version__ = "1.0"

import sys
import socket
import threading
import os
import pickle
from util import EXIT,REQUEST,BUFFER_SIZE,FORMAT,REGISTERED,REGISTRATION,CLONE,UTF,ACK,TABLE_UPDATE,TABLE,SERVER,CLIENT,SET_DIR,OFFER,REQUEST_FILE,ONLINE,OFFLINE,DEREG,ERROR
from tabulate import tabulate

class Server():
    '''
    Server Class (UDP)
    '''
    def __init__(self,port):
        self.port = port
        self.dir = None
        self.registered = []
        self.table = []
        self.u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.accept_connections()

    def accept_connections(self):
        '''Start server and accept new connections'''
        ip = socket.gethostbyname(socket.gethostname())
        port = int(self.port) 
        print('Running on IP:'+ip)
        print('Running on port:'+str(port))        
        self.u.bind((ip,port))
        threading.Thread(target=self.handle_client,args=()).start()

    def handle_client(self):
        '''Handle client side
           REGISTRATION functionality
           Accept FILES functionality
           Table Updates
           DEREGISTRATION functionalit
        '''
        while(1):
            try:
                data, addr = self.u.recvfrom(BUFFER_SIZE)

                if data.decode() == REGISTRATION:
                    data, addr = self.u.recvfrom(BUFFER_SIZE)
                    data = data.decode()
                    if any(data in i for i in self.registered):
                        self.u.sendto(CLONE.encode(),addr)
                        continue
                    else:
                        self.registered.append([data,addr[0],addr[1],ONLINE])
                        print('client registered: {}'.format(data))
                        self.u.sendto(REGISTERED.encode(),addr)
                        self.u.sendto(pickle.dumps(self.table),addr)
                        continue
                
                if data.decode() == OFFER:
                    print('new file offereing recieved')
                    self.u.sendto(ACK.encode(),addr)
                    print('ack sent')
                    file_names, addr = self.u.recvfrom(BUFFER_SIZE)
                    name, addr = self.u.recvfrom(BUFFER_SIZE)
                    tcp_port, addr = self.u.recvfrom(BUFFER_SIZE)

                    print('filename recieved. Updating table')
                    file_names = pickle.loads(file_names)
                    for file_name in file_names:
                        if (file_name,name.decode(),addr[0],int(tcp_port)) not in self.table:
                            self.table.append((file_name,name.decode(),addr[0],int(tcp_port)))
                        else:
                            continue
                    print('Table Updated')
                    for i in self.registered:
                        if i[3]==ONLINE:
                            flag_ack = False
                            for _ in range(2):
                                if flag_ack:
                                    break
                                self.u.sendto(TABLE_UPDATE.encode(),(i[1],int(i[2])))
                                self.u.sendto(pickle.dumps(self.table),(i[1],int(i[2])))
                                self.u.settimeout(.5)
                                try:
                                    data, addr = self.u.recvfrom(BUFFER_SIZE)
                                    print(data)
                                    if data.decode() == ACK:
                                        print('ACK recieved by server')
                                        flag_ack=True
                                except socket.timeout:
                                    print('No ACK from client {}'.format(i[0]))
                                    continue
                    print(self.table)
                    continue
                if data.decode()==DEREG:
                    # self.u.sendto(ACK.encode(),addr)
                    name, addr = self.u.recvfrom(BUFFER_SIZE)
                    for i in self.registered:
                        if i[0]==name.decode() and i[1]==addr[0] and int(i[2])==int(addr[1]):
                            i[3]=OFFLINE
                            print('Successfully Deregistered {}'.format(i[0]))
                            row = 0
                            while row < len(self.table):
                                if i[0] in self.table[row]:
                                    self.table.pop(row)
                                else:
                                    row+=1
                    for i in range(len(self.registered)):
                                if self.registered[i][3]==ONLINE:
                                    flag_ack = False
                                    for _ in range(2):
                                        if flag_ack:
                                            break
                                        self.u.sendto(TABLE_UPDATE.encode(),(self.registered[i][1],int(self.registered[i][2])))
                                        self.u.sendto(pickle.dumps(self.table),(self.registered[i][1],int(self.registered[i][2])))
                                        self.u.settimeout(5)
                                        try:
                                            data, addr = self.u.recvfrom(BUFFER_SIZE)
                                            print(data)
                                            if data.decode() == ACK:
                                                print('ACK recieved by server')
                                                flag_ack=True
                                        except socket.timeout:
                                            print('No ACK from client {}'.format(self.registered[i][0]))
                                            continue
                    print(self.table)
                    continue

                    continue
            except socket.timeout:
                continue


class Client():
    '''
    Client Class (TCP & UDP)
    '''
    def __init__(self,name,server_ip,server_port,client_udp_port,client_tcp_port):
        self.name = name
        self.server_ip = server_ip
        self.server_port= server_port
        self.client_udp_port = client_udp_port
        self.client_tcp_port = client_tcp_port
        self.s =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.t =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.u =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.temp = []
        self.dir = None
        self.table = []
        self.registration()

    def registration(self):
        '''Registration module on initialization'''
        self.u.sendto(REGISTRATION.encode(), (self.server_ip,int(self.server_port)))
        self.u.sendto(self.name.encode(), (self.server_ip,int(self.server_port)))
        try:
            val, addr = self.u.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print('Server is not available')
            return

        if val.decode()==CLONE:
            print(">>> Client already present with same nickname. Register with different user")
            return
        if val.decode()==REGISTERED:
            print('>>> Welcome, You are registered.')
            table, addr = self.u.recvfrom(BUFFER_SIZE)
            self.table = pickle.loads(table)
            print('>>> Client Table Updated')
            for i in range(len(self.table)):
                print(self.table[i])
        threading.Thread(target=self.listen,args=()).start()
        threading.Thread(target=self.handle,args=()).start()
        threading.Thread(target=self.accept,args=()).start()

    def accept(self):
        ip = socket.gethostbyname(socket.gethostname())
        self.s.bind((ip,int(self.client_tcp_port)))
        self.s.listen(100)

        while 1:
            c, addr = self.s.accept()
            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    def handle_client(self,c,addr):
        message = c.recv(1024).decode()
        if message==REQUEST_FILE:
            print('>>> Accepting connection request from {}'.format(addr))
            c.send(ACK.encode())
            data = c.recv(1024).decode()
            print('>>> Transferring file '.format(data))
            try:
                if data != '':
                        file = open(os.path.join(self.dir,data),'rb')
                        data = file.read(1024)
                        while data:
                            c.send(data)
                            data = file.read(1024)
                        c.shutdown(socket.SHUT_RDWR)
                        c.close()
                        print('>>>file transferred successfully!')
                        print('>>>Connection closed!')


            except:
                print('Error in file transfer')
                c.send(ERROR.encode())
                c.shutdown(socket.SHUT_RDWR)
                c.close()

            print('>>>')

    def listen(self):
        '''fetch table updates'''
        while True:
            try:
                data, addr = self.u.recvfrom(BUFFER_SIZE)
                if data.decode()==TABLE_UPDATE:
                    table, addr = self.u.recvfrom(BUFFER_SIZE)
                    # print(' table  update recieved by client')
                    self.table = pickle.loads(table)
                    self.u.sendto(ACK.encode(),(self.server_ip,int(self.server_port)))
                    print('client table update recieved')
                    print('>>>')
            except socket.timeout:
                continue


    def handle(self):
        ''' handle Client side commands, FILE OFFERING, SETTING DIRECTORY '''
        while(1):
            a = input('>>>')
            # if self.table!=self.temp:
            #     print('>>> Table update recieved')       
            #     self.temp = self.table.copy() 
            #     continue  

            a = a.split()
            if a[0]==SET_DIR and len(a)==2:
                try:
                    if os.path.exists(a[1]):
                        print(">>> Successfully set <{}> as the directory for searching offered files.".format(a[1]))
                        self.dir = a[1]
                        continue
                    else:
                        print(">>> setdir failed: <{}> does not exist.".format(a[1]))
                        continue
                except:
                    print(">>> invalid request")
                    continue
            if a[0]==OFFER and len(a)>=2:
                # print('inoffer')
                if  self.dir is None:
                    print(">>> directory not set, please set the directory")
                    continue
                self.u.sendto(OFFER.encode(),(self.server_ip,int(self.server_port)))
                # message, addr = self.u.recvfrom(BUFFER_SIZE)
                # print(message.decode())
                # if message.decode()==ACK:
                #         print(">>> Offer Message received by Server.")
                self.u.sendto(pickle.dumps(a[1:]),(self.server_ip,int(self.server_port)))

                self.u.sendto(self.name.encode(),(self.server_ip,int(self.server_port)))
                self.u.sendto(self.client_tcp_port.encode(),(self.server_ip,int(self.server_port)))
                print(">>> nickname details sent")

                continue
                # except socket.timeout:
                #         print('>>> No ACK from Server, please try again later')
            if a[0]==TABLE and len(a)==1:
                header = ['FILENAME','OWNER','IP ADDRESS','TCP PORT']
                if self.table:
                    print(tabulate(self.table, headers=header, tablefmt='grid'))
                    continue
                else:
                    print(">>> No files available for download at the moment.")
                    continue
            if a[0]==REQUEST:
                flag = False
                if len(a)==3:
                    for i in self.table:
                        if i[0]==a[1] and i[1]==a[2]:
                            target_ip= i[2]
                            target_port= i[3]
                            self.t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.t.connect((target_ip,int(target_port)))
                            self.t.send(REQUEST_FILE.encode())
                            message = self.t.recv(BUFFER_SIZE).decode()
                            if message == ACK:
                                self.t.send(a[1].encode())

                                print(">>> Connection with client {} established.".format(a[2]))
                                print(">>> Downloading {}.".format(a[1]))
                                if os.path.exists(a[1]): os.remove(a[1])
                                data = self.t.recv(1024)
                                if data == ERROR:
                                    print('>>> Error in receiving file. Pls try again later..')
                                    continue
                                if data is not None:

                                    with open(a[1],'wb') as file:
                                            # print('infile')
                                            while 1:
                                                # print('in while')
                                                if not data:
                                                    # print('here')
                                                    break
                                                file.write(data)
                                                data = self.t.recv(1024)

                                                # print('after write')
                                print('>>> {} Successfully Downloaded.'.format(a[1]))
                                self.t.close()
                                print('>>> Connection with Client {} Closed.'.format(a[2]))
                                flag=True
                if flag!=True:
                    print(">>> Invalid request")
                continue
            if a[0]==DEREG and len(a)==2:
                self.u.sendto(a[0].encode(),(self.server_ip,int(self.server_port)))
                try:
                    # data, addr = self.u.recvfrom(BUFFER_SIZE)
                    # if data.decode()==ACK:
                        self.u.sendto(a[1].encode(),(self.server_ip,int(self.server_port)))
                        print('Name has been sent for dereg')
                        print(">>> you are offline. Bye")
                        continue
                except socket.timeout:
                    print('>>> No ACK from server please try again later.')
                    continue
            if a[0]== EXIT:
                self.t.close()
                self.u.close()
                self.s.close()
                return
            else:
                print(">>> invalid command")
            
if __name__ == "__main__":
   if sys.argv[1]==SERVER:
        server = Server(sys.argv[2])

   elif sys.argv[1]== CLIENT and len(sys.argv)==7:
        client = Client(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])

   else:
       print('>>> invalid command')
       exit


#----------------------------------------------/-\--------------------------------------------------------------------------------------------