from expression import Expression


class Constant(Expression):
    def __init__(self, value):
        self.value = value
        super().__init__()

    
    def solve(self, state):
        return self.value
    

    def get_max_value(self, state):
        return self.value
    

    def get_min_value(self, state):
        return self.value

    
    def try_get_confirmed_value(self, state):
        return self.value
    

    def get_variables_in_expression(self):
        return set()
