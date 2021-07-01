
class Shared_Var():
    """
    docstring
    """
    def __init__(self,var_name,value,node_id):
        """
        docstring
        """
        self._var_name = var_name
        self._value = value
        self._can_write = False
        self._node_id = node_id
        

    def get_node_id(self):
        return self._node_id
        
    def get_var_name(self):
        """
        docstring
        """
        return self._var_name
    
    def get_value(self):
        """
        docstring
        """
        return self._value

    def get_can_write(self):
        """
        docstring
        """
        return self._can_write

    def set_value(self,value):
        """
        docstring
        """
        self._value = value      
    
    def set_can_write(self,node_id,can_write):
        self._can_write = can_write