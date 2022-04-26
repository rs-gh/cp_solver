from expression import Expression
from variable_store import VariableStore
from status import FAILURE


class Variable(Expression):
    def __init__(self, name, current_value=None):
        self.name = name
        super().__init__()


    # Don't need to create deep copies of variables
    def __deepcopy__(self, memo):
        return self 


    def get_domain(self, state):
        return state.get_domain(self.name)
    

    def set_domain(self, state, new_domain):
        state.set_domain(self.name, new_domain)
    

    def set_domain(self, state, new_domain):
        state.set_domain(self.name, new_domain)


    def add_to_domain(self, state, add_values):
        old_domain = self.get_domain(state)
        new_domain = old_domain.union(add_values)
        self.set_domain(state, new_domain)


    def remove_from_domain(self, state, remove_values):
        new_domain = set(value for value in self.get_domain(state) if value not in remove_values)
        if len(new_domain) == 0:
            return FAILURE
        self.set_domain(state, new_domain)

  
    def get_current_value(self, state):
        return state.get_current_value(self.name)


    def set_current_value(self, state, value):
        state.set_current_value(self.name, value)


    def solve(self, state):
        confirmed_value = self.try_get_confirmed_value(state)
        return confirmed_value if confirmed_value is not None else self.get_current_value(state)
    

    def get_max_value(self, state):
        return max(self.get_domain(state)) 
    

    def get_min_value(self, state):
        return min(self.get_domain(state))
    

    def try_get_confirmed_value(self, state):
        return state.try_get_confirmed_value(self.name)
    
    
    def set_max_value(self, state):
        self.set_current_value(state, self.get_max_value(state))
    

    def set_min_value(self, state):
        self.set_current_value(state, self.get_min_value(state))
    

    def get_variables_in_expression(self):
        variables = set()
        variables.add(self)
        return variables
    

    def try_filter_variable_domain(self, state, comparison, bound):
        new_domain = set(value for value in self.get_domain(state) if comparison(value, bound))
        if len(new_domain) == 0:
            return FAILURE
        is_domain_changed = not(self.get_domain(state) == new_domain)
        self.set_domain(state, new_domain)
        return is_domain_changed
