from collections import defaultdict, namedtuple


_Variable = namedtuple("_Variable", ["domain", "current_value"])


class VariableStore:
    def __init__(self):
        self.store = defaultdict(_Variable)
    

    def is_duplicate_name(self, name):
        return name in self.store.keys()
    

    def add_to_variable_store(self, name, domain, current_value=None):
        assert not self.is_duplicate_name(name), "Duplicate variable name for {}".format(name)
        if current_value is None:
            current_value = min(domain)
        self.store[name] = _Variable(domain, current_value)
    

    def get_domain(self, name):
        return self.store[name].domain

    
    def set_domain(self, name, new_domain):
        self.store[name] = self.store[name]._replace(domain=new_domain)
        if self.get_current_value(name) not in self.get_domain(name):
            self.set_current_value(name, self.get_default_value(name))
    
    
    def get_default_value(self, name):
        return min(self.get_domain(name))


    def get_current_value(self, name):
        return self.store[name].current_value
    

    def set_current_value(self, name, value):
        assert value in self.store[name].domain, "Value {} not in domain for {}".format(value, name)
        self.store[name] = self.store[name]._replace(current_value=value)
    

    def try_get_confirmed_value(self, name):
        if len(self.store[name].domain) == 1:
            confirmed_value = min(self.store[name].domain)
            self.store[name] = self.store[name]._replace(current_value=confirmed_value)
        else:
            confirmed_value = None
        return confirmed_value
