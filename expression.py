from abc import ABC, abstractmethod
from itertools import product


class Expression(ABC):
    def __init__(self, *operands):
        self.operands = list(operands) if len(operands) > 0 else list()


    @property
    def variables(self):
        return self.get_variables_in_expression()


    @abstractmethod
    def solve(self, state):
        pass
    

    @abstractmethod
    def get_max_value(self, state):
        pass
    
    
    @abstractmethod
    def get_min_value(self, state):
        pass

    
    @abstractmethod
    def try_get_confirmed_value(self, state):
        pass
    
    
    @abstractmethod
    def get_variables_in_expression(exp):
        pass
