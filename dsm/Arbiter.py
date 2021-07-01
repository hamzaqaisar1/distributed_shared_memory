from _thread import *
import socket
import threading
import json
import sys
import random
from Shared_Var import Shared_Var
from config import *

"""
The clients will communicate with the arbiter which will be the bottleneck in the communication
with the distributed shared memory. The arbiter will pass on the query to the distributed 
network or will deal with it on its own based on the type of the message that it gets.
"""

class Arbiter:

    def __init__(self):
        """
        connected_clients structure : {node_id: address,...}
        possible_new_clients structure: [address,...]
        possible_new_clients: {address,...}
        """
        self.client_listen_sock = None
        self.server_listen_sock = None
        self.connected_clients = {}
        self.connected_servers = []
        self.possible_new_clients = []
        self.write_lock = threading.Lock()
        self.client_listen_thread = threading.Thread(target=self.__listen_client)
        self.client_listen_thread.start()
        # self.server_listen_thread = threading.Thread(target=self.__listen_server)
        # self.server_listen_thread.start()


    def __listen_client(self):
        """
        docstring
        """
        self.client_listen_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.client_listen_sock.bind((IP,ARBITER_CLIENT_PORT))
        except socket.error as e:
            print(str(e))

        self.client_listen_sock.listen(CLIENTS_LIMIT)

        while True:
            client, address = self.client_listen_sock.accept()
            start_new_thread(self.__threaded_client_listen,(client,address ))

    def __threaded_client_listen(self,client_conn,client_address):
        request = None
        while not request:
            request = client_conn.recv(BUFFER_SIZE)
            if not request:
                break
            if not self.__parse_incoming_client_request(client_conn,request,client_address):
                self.send_request_to_client("-1|Unable to send request to server",client_address)

    def __listen_server(self):
        """
        docstring
        """
        self.server_listen_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.server_listen_sock.bind((IP,ARBITER_SERVER_PORT))
        except socket.error as e:
            print(str(e))

        self.server_listen_sock.listen(SERVERS_LIMIT)

        while True:
            server, address = self.server_listen_sock.accept()
            start_new_thread(self.__threaded_server_listen,(server,address ))


    def __threaded_server_listen(self,server_conn,server_address):
        while True:
            request = server_conn.recv(BUFFER_SIZE)
            if not request:
                break
            if self.__parse_incoming_server_request(request):
                self.send_request_to_server("-1|Unable to send request to server",server_addr=server_address)

   
    # Basic Communication Methods
    def send_request_to_client(self,request,client_conn,address):
        """
        docstring
        """
        try:
            client_conn.send(str.encode(request))
            return True
        except socket.error as e:
            print(str(e))
            return False
        

    def send_request_to_server(self,request,server_addr=None):
        """
        docstring
        """
        new_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:

            serv_addr = None
            serv_index = None
            if server_addr == None:
                for index,server in enumerate(self.connected_servers):
                    if server['toggle'] == 0:
                        serv_addr = server['address']
                        serv_index = index
                        break
                    else:
                        server['toggle'] = 0
            else:
                serv_addr = server_addr
                serv_index = self.connected_servers.index(server_addr)

            if serv_addr:
                self.write_lock.acquire()
                self.connected_servers[serv_index]['toggle'] = 1
                new_socket.connect(serv_addr)
                new_socket.send(str.encode(request))
                new_socket.close()
                self.write_lock.release()
            else:
                return False
            return True
        except socket.error as e:
            print(str(e))
            return False
        
        

    def create_message(self,parameter_list):
        """
        docstring
        """
        pass

    def __parse_incoming_client_request(self,client_conn,request,client_address):
        """
        docstring
        """
        request = request.decode('utf-8')
        request = request.split('|')
        msg_type = int(request[0])
        if msg_type == 0:
            self.write_lock.acquire()
            self.possible_new_clients.append(client_address)
            request.append(str(len(self.connected_clients) + 1))
            if not self.send_request_to_client('|'.join(request),client_conn,client_address):
                print("Unable tosend request to the server")
                return False
            client_conn.close()
            self.connected_clients[str(len(self.connected_clients) + 1)] = client_address
            self.write_lock.release()            
        else:
            self.send_request_to_server('|'.join(request))
        return True

        
    def __parse_incoming_server_request(self,request):
        """
        docstring
        """
        request = request.decode('utf-8')
        request = request.split('|')
        msg_type = int(request[0])
        if msg_type == -1:
            self.write_lock.acquire()
            try:
                index_of_element = self.possible_new_clients.index((request[1],int(request[2])))
                if not self.send_request_to_client('|'.join(request),self.possible_new_clients[index_of_element]):
                    print("Unable to send request to the client")
                    self.write_lock.release()            
                    return False
                self.possible_new_clients.remove(index_of_element)
            except ValueError:
                print("Unable to send request to the client")
                self.write_lock.release()            
                return False
            return True
        elif msg_type == 0:
            self.write_lock.acquire()
            try:
                index_of_element = self.possible_new_clients.index((request[2],int(request[3])))
                if not self.send_request_to_client('0|{}'.format(request[1]),self.possible_new_clients[index_of_element]):
                    print("Unable to send request to the client")
                    self.possible_new_clients.remove(index_of_element)
                    self.write_lock.release()            
                    return False
                self.connected_clients[request[1]] = (request[2],int(request[3]))
                self.possible_new_clients.remove(index_of_element)
            except ValueError:
                print("Unable to send request to the client")
                self.write_lock.release()            
                return False
            return True
        else:
            if request[1] in self.connected_clients.keys() and \
                self.send_request_to_client('|'.join(request),self.connected_clients[request[1]]):
                return True
            else:
                print("Unable to send request to the client")
                return False

if __name__ == "__main__":
    my_arbiter = Arbiter()