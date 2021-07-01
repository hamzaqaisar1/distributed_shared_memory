"""
Implement a node class that runs and subscribtes to the network by importing the claasses 
of Arbiter and Memory Manager both of which are responsible for different part of the
task in order to test whether or not the whole process is working correctly. This class
will be used in the file __init__.py within the same folder
"""
import random
import string

from varname import varname, nameof

from Client import Client

class Sim_Process:
    def __init__(self,process_id,commands):
        self.client = Client()
        self.process_id = process_id
        self.commands = commands
        self.shared_vars_names = []
        self.read_replicated_vars = []
        self.write_access_vars = []

    def run(self):
        letters = string.ascii_lowercase
        print("The available variables of the process " + str(self.process_id) +\
                " is: " + str(self.client.metadata) )
        
        while self.commands > 0:
            sentinel = random.randint(1,7)
            sample_var = None
            if sentinel == 1 or sentinel == 5:
                if random.randint(0,1):
                    sample_var = random.randint(1,10)
                else:
                    sample_var =  ''.join(random.choice(letters) for i in range(10))


            if sentinel == 1:
                curr_var_name = "sample_var_" + str(self.commands)
                if self.client.set_as_shared(curr_var_name,sample_var):
                    self.shared_vars_names.append(curr_var_name)
                    print("Added variable: " + curr_var_name + ", With name: " + str(sample_var))
                    print("The client shared vars are: " + self.client.client_shared_vars)

            elif sentinel == 2:
                var_name_removed = self.shared_vars_names[random.randint(0,len(self.shared_vars_names) - 1)]
                if self.client.remove_shared_status(var_name_removed):
                    self.shared_vars_names.remove(var_name_removed)
                    print("Removed variable: " + curr_var_name + ", With name: " + str(sample_var))
                    print("The client shared vars are: " + self.client.client_shared_vars)
            elif sentinel == 3:
                if self.client.metadata:
                    print(self.client.metadata)
                    target_node_id = input("Enter the node id you want to fetch variable of: ")
                    target_var_name = input("Enter the name of the variable: ")
                    if self.client.get_var(target_node_id,target_var_name):
                        fetched_var = self.client.read_replicated_vars[target_node_id][target_var_name]
                        self.read_replicated_vars.append(fetched_var)
                        print("Successfully fetched variable: " + target_var_name +\
                            " with value: " + str(fetched_var.get_value()) )
                    else:
                        print("Failed to fetch variable")
                else:
                    print("No variables have been shared")
            elif sentinel == 4:
                print(self.client.get_all_shared_var())
            elif sentinel == 5:
                if self.client.metadata and self.read_replicated_vars != []:
                    print(self.client.metadata)
                    write_access_var = self.read_replicated_vars[random.randint(0,len(self.read_replicated_vars) - 1)]

                    if self.client.get_write_access(write_access_var):
                        fetched_var = self.client.read_replicated_vars[str(write_access_var.get_node_id())][str(write_access_var.get_var_name())]
                        print("Successfully fetched variable for read access: " + fetched_var.get_var_name() +\
                            " with value: " + str(fetched_var.get_value) )
                    else:
                        print("Failed to fetch variable")
                else:
                    print("No variables have been shared")
            elif sentinel == 6:
                if self.client.metadata and self.read_replicated_vars != []:
                    print(self.client.metadata)
                    write_access_var = self.read_replicated_vars[random.randint(0,len(self.read_replicated_vars) - 1)]

                    if self.client.check_write_access(write_access_var):
                        print("Variable: " + fetched_var.get_var_name() +\
                            " with value: " + str(fetched_var.get_value) + " is write accessible")
                    else:
                        print("Failed to fetch variable")
                else:
                    print("No variables have been shared")
            elif sentinel == 7:
                if  self.write_access_vars != []:
                    write_access_var = self.write_access_vars[random.randint(0,len(self.write_access_vars) - 1)]

                    if self.client.revoke_write_access(write_access_var):
                        fetched_var = self.client.read_replicated_vars[str(write_access_var.get_node_id())][str(write_access_var.get_var_name())]
                        print("Successfully revoked read access for variable: " + fetched_var.get_var_name() +\
                            " with value: " + str(fetched_var.get_value) )
                    else:
                        print("Failed to fetch variable")
                else:
                    print("No variables have been shared")

