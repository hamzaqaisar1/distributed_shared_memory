from _thread import *
import socket
import threading
import json
import sys
import random

from Shared_Var import Shared_Var
from config import *

"""
Implement the server side of the algorithm with the responsibility of managing 
incoming requests from the server and storing it on nodes according to an algorithm 
and passing the message to other clients that the data is available to be read
"""

class Server:
    def __init__(self):
        """
        var_data structure : {node_id: [Shared_Var]}
        """
        self.write_lock = threading.Lock()
        self.var_data = {}
        self.listen_server_sock = None
        self.listen_arbiter_sock = None
        self._server_id = self.subscribe()
        self.server_list = []
        self.listen_arbiter_thread = threading.Thread(target=self.__listen_server)

    def __listen_server(self):
        """
        docstring
        """
        self.client_listen_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.client_listen_sock.bind(IP,SERVER_PORT)
        except socket.error as e:
            print(str(e))

        self.client_listen_sock.listen(1)

        while True:
            arbiter, arbiter_address = self.client_listen_sock.accept()
            start_new_thread(self.__threaded_server_listen,(arbiter,arbiter_address ))

    def __threaded_server_listen(self,arbiter_conn,arbiter_address):
        while True:
            request = arbiter_address.recv(BUFFER_SIZE)
            if not request:
                break
            if not self.__parse_incoming_client_request(request,arbiter_address):
                self.send_request_to_client("-1|Unable to send request to server",client_address)

    
    def subscribe(self):
        self.client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_addr = (IP,ARBITER_PORT)
        try:
            self.client_sock.connect(server_addr)
        except socket.error as e:
            print(str(e))
            
        self.__send_message(str.encode(self.__create_message(0)))

        recv_data = self.client_sock.recv(BUFFER_SIZE)

        if not recv_data:
           print("Unable to connect")

        
        node_id = self.__parse_response(recv_data)
        return node_id
    