from _thread import *
import socket
import threading
import json
import sys
from Shared_Var import Shared_Var
import time
from config import *


"""
The client side is the part of the network that requests and subscribes to the network
and uses the DSM functionality. This class will provide the functionality that will help
the user to just create this class and be able so subscribe directly to the DSM. This
class will use both the Aribter and Memory Manager class so as to allow the subscribing
to the network and specifying what to share and what to access in tandem with the other
two classes.
"""

class Client:
    def __init__(self):
        """
        Metadata structure : {node_id: [variable_names]}
        Read Replicated Vars structure: {node_id: {variable_names : Shared_Var}}
        Client Shared Vars structure: {var_name: Shared_Var...}
        """
        self.client_sock = None
        self.listen_sock = None
        self.write_lock = threading.Lock()   
        self._node_id = self.subscribe()
        print("The id received is: ",self._node_id)
        time.sleep(100)
        self.get_all_shared_var()
        self.client_shared_vars = {}
        self.read_replicated_vars = {}
        self.listen_thread = threading.Thread(target=self.__listen)
        self.listen_thread.start()

    def subscribe(self):
        self.client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_addr = (IP,ARBITER_CLIENT_PORT)
        try:
            self.client_sock.connect(server_addr)
        except socket.error as e:
            print(str(e))
            
        self.__send_message(str.encode(self.__create_message(0)))
        recv_data = None
        recv_data = self.client_sock.recv(BUFFER_SIZE)

        print(recv_data)
        if not recv_data:
           print("Unable to connect")

        
        node_id = self.__parse_response(recv_data)
        return node_id

    def __threaded_client_listen(self,server_conn):
        while True:
            request = server_conn.recv(BUFFER_SIZE)
            if not request:
                break
            self.__parse_incoming_request(request)

    def __listen(self):
        self.listen_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.listen_sock.bind((IP,CLIENT_PORT))
        except socket.error as e:
            print(str(e))

        self.listen_sock.listen(10)

        while True:
            server, address = self.listen_sock.accept()
            start_new_thread(self.__threaded_client_listen,(server, ))

    def __send_message(self,encoded_message):
        self.client_sock.send(encoded_message)

    def __parse_response(self,message):
        response = message.decode('utf-8')
        response = response.split('|')
        msg_type = int(response[0])
        if msg_type == -1:
            print(response[1])
            del self
        elif msg_type == 0:
            return int(response[1])
        elif msg_type == 1 or msg_type == 2 or msg_type == 5  or msg_type == 7:
            if self._node_id == int(response[1]):
                return self._node_id
            
            return None
        elif msg_type == 3:
            if self._node_id == int(response[1]):
                var_value = json.load(response[2])
                return var_value
            
            return None
        elif msg_type == 4:
            if response[2] == '':
                print("No vairables have been shared")
                return None
            else:    
                return json.load(response[2])
        elif msg_type == 6:
            if self._node_id == int(response[1]):
                var_value = int(response[2])
                return bool(var_value)
            
            return None
             
            

    def __parse_incoming_request(self,message):
        request = message.decode('utf-8')
        request = request.split('|')
        msg_type = int(request[0])
        if msg_type == -1:
            print(request[1])
            del self
        elif msg_type == 0:
            if self._node_id == int(request[1]):
                self.__halt_read(int(request[2]),request[3])
            else:
                return
        elif msg_type == 1:
            if self._node_id == int(request[1]):
                self.__update_metadata(request[2])
            else:
                return

    # When another client requests write access to a variable read replicated by this one
    def __halt_read(self,target_node_id,var_name):
        if target_node_id in self.read_replicated_vars and var_name in self.read_replicated_vars[target_node_id]:
            self.read_replicated_vars[target_node_id].pop(var_name)

    def __update_metadata(self,json_string):
        self.write_lock.acquire()
        self.metadata = json.load(json_string)
        self.write_lock.release()

    def __create_message(self,message_id,args=None):
        message = None
        if message_id == 0:
            message = "0"
        elif message_id == 1:
            message = "1|{}|{}".format(str(args._node_id),json.dumps({'var_name': args['var_name'],'value':args['value']}))
        elif message_id == 2:
            message = "2|{}|{}".format(str(args._node_id),str(args.var_name))
        elif message_id == 3:
            message = "3|{}|{}|{}".format(str(args._node_id),str(args.traget_node_id),str(args.var_name))
        elif message_id == 4:
            message = "4|{}".format(str(args._node_id))
        elif message_id == 5:
            message = "5|{}|{}|{}".format(str(args._node_id),str(args.traget_node_id),str(args.var_name))
        elif message_id == 6:
            message = "6|{}|{}|{}".format(str(args._node_id),str(args.traget_node_id),str(args.var_name))
        elif message_id == 7:
            message = "7|{}|{}|{}".format(str(args._node_id),str(args.traget_node_id),str(args.var_name))
        
        return message

    def set_as_shared(self,var_name,value):
        self.__send_message(self.__create_message(1,{'node_id':self._node_id,'var_name':var_name,'value':value}))
        recv_data = self.client_sock.recv(BUFFER_SIZE)
        if not recv_data:
           print("Unable to connect")

        node_id = self.__parse_response(recv_data)
        if node_id != None:
            self.client_shared_vars[var_name] = Shared_Var(var_name,value,self._node_id)
            return True
        else:
            return None

    def remove_shared_status(self,var_name):
        self.__send_message(self.__create_message(2,{'node_id':self._node_id,'var_name':var_name}))
        recv_data = self.client_sock.recv(BUFFER_SIZE)
        if not recv_data:
           print("Unable to connect")

        node_id = self.__parse_response(recv_data)
        if node_id != None:
            self.client_shared_vars.pop(var_name)
            return True
        else:
            return False


    def get_var(self,target_node_id,var_name):
        """
        This method gets a single variable from the ones that have been shared to the 
        server for reading
        """
        self.__send_message(self.__create_message(3,{'node_id':self._node_id,'target_node_id':target_node_id,'var_name':var_name}))
        recv_data = self.client_sock.recv(BUFFER_SIZE)
        if not recv_data:
           print("Unable to connect")
           return False

        var_value = self.__parse_response(recv_data)
        if var_name in var_value:
            self.read_replicated_vars[str(target_node_id)][var_name]  = Shared_Var(var_name,var_value,target_node_id)
            return True
        else:
            return False

    def get_write_access(self,shared_var):
        """
        This method gets the variable from the server to allow the node to be able to 
        change it for at the server level
        """
        self.__send_message(self.__create_message(5,{'node_id':self._node_id,'target_node_id':shared_var.node_id,'var_name':shared_var.var_name}))
        recv_data = None
        while not recv_data:
            recv_data = self.client_sock.recv(BUFFER_SIZE)

        node_id = self.__parse_response(recv_data)
        if node_id != None:
            self.read_replicated_vars[str(shared_var.target_node_id)][shared_var.var_name].set_can_write(self._node_id,True)


    def revoke_write_access(self,shared_var):
        self.__send_message(self.__create_message(6,{'node_id':self._node_id,'target_node_id':shared_var.node_id,'var_name':shared_var.var_name}))
        recv_data = self.client_sock.recv(BUFFER_SIZE)
        if not recv_data:
           print("Unable to connect")

        node_id = self.__parse_response(recv_data)
        if node_id != None:
            self.read_replicated_vars[str(shared_var.node_id)][shared_var.var_name].set_can_write(self._node_id,False)




    def get_all_shared_var(self):
        """

        """
        self.__send_message(str.encode(self.__create_message(4,args={'node_id':self._node_id})))
        recv_data = self.client_sock.recv(BUFFER_SIZE)

        if not recv_data:
           print("Unable to connect")
           return False

        
        self.metadata = self.__parse_response(recv_data)


    def check_write_access(self,shared_var):
        """
        Checks the memory manager to make sure that the variable has read access
        """
        self.__send_message(self.__create_message(5,{'node_id':self._node_id,'target_node_id':shared_var.node_id,'var_name':shared_var.var_name}))
        recv_data = None
        while not recv_data:
            recv_data = self.client_sock.recv(BUFFER_SIZE)

        is_avail = self.__parse_response(recv_data)
        if is_avail != None:
            return is_avail

if __name__ == "__main__":
    my_client = Client()