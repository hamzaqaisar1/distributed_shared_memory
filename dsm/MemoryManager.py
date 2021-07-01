"""
The aim of this class is it works in tandem with the arbiter and manages the memory
and the variable that one of the node has accessed and they will be accessed with 
the help of this class along with maintaining read replication and other 
synchronization based problems
"""

class MemoryManager:

    def __init__(self):
        self.shared_vars = {}

    def store_shared_var(self, shared_var):
        """
        """
        pass

    def remove_var(self,shared_var):
        """
        """
        pass

    def grant_write_acess(self,shared_var):
        """
        This will allow the user to change the variable and also contact the arbiter to
        send the changes when done
        """
        pass