from collections import defaultdict
from copy import copy, deepcopy
from status import SUCCESS, FAILURE


class Model:
    def __init__(self):
        self.variables = set()
        self.constraints = set()
        self.variable_constraint_map = defaultdict(set)
        self.superset_state = None
    

    def add_constraints(self, *constraints):
        for constraint in constraints:
            if any(var not in self.variables for var in constraint.variables):
                raise Exception("All variables need to be added to model first")
            for var in constraint.variables:
                self.variable_constraint_map[var].add(constraint)
            self.constraints.add(constraint)
    

    def add_variables(self, *variables):
        for var in variables:
            self.variables.add(var)

    
    def init_constraint_execution_stack(self):
        return list(constraint for constraint in self.constraints)
    

    def init_executed_constraints(self):
        return set()
    

    def check_init_superset_state(self, init_state):
        if self.superset_state is None:
            self.superset_state = init_state
    

    def remove_infeasible_values_from_superset_state(self, constraint, state):
        confirmed_value_variables = (var for var in constraint.variables if var.try_get_confirmed_value(state) is not None)
        # keep state only for the confirmed_value_variables
        # use superset_state for all the other variables
        # then check if feasible
        # if not feasible, remove this var/value combo from superset_state
        for var in confirmed_value_variables:
            var_check_state = deepcopy(self.superset_state)
            confirmed_domain = var.get_domain(state)
            var.set_domain(var_check_state, confirmed_domain)
            
            if not constraint.is_feasible(var_check_state):
                var.remove_from_domain(self.superset_state, confirmed_domain)


    def sync_with_superset_state(self, state):
        for var in self.variables:
            superset_domain = var.get_domain(self.superset_state)
            state_domain = var.get_domain(state)
            var.set_domain(state, state_domain.intersection(superset_domain))
        return state


    def is_every_constraint_executed(self, executed_constraints):
        return self.constraints == executed_constraints


    def get_most_constrained_variable(self, state):
        most_constrained_unconfirmed_variable = None
        min_domain_size = float("inf")

        for var in self.variables:
            confirmed_value = var.try_get_confirmed_value(state)
            if confirmed_value is None:
                domain = var.get_domain(state)
                domain_size = len(domain)
                if domain_size < min_domain_size:
                    most_constrained_unconfirmed_variable = var
                    min_domain_size = domain_size
        
        return most_constrained_unconfirmed_variable

    
    def propagate(self, state):
        new_state = deepcopy(state)
        constraint_execution_stack = self.init_constraint_execution_stack()
        executed_constraints = self.init_executed_constraints()
        
        while True:
            constraint = constraint_execution_stack.pop()
            
            if not constraint.is_feasible(new_state):
                self.remove_infeasible_values_from_superset_state(constraint, new_state)
                return FAILURE, None

            is_variable_domain_changed = constraint.prune(new_state)

            if is_variable_domain_changed == FAILURE:
                return FAILURE, None

            elif is_variable_domain_changed:  # TODO: only do this for variables with changed domains
                executed_constraints = self.init_executed_constraints()
                for var in constraint.variables:
                    for var_constraint in self.variable_constraint_map[var]:
                        constraint_execution_stack.append(var_constraint)
            
            else:
                executed_constraints.add(constraint)

            if self.is_every_constraint_executed(executed_constraints):
                break

            elif len(constraint_execution_stack) == 0:
                constraint_execution_stack = self.init_constraint_execution_stack()
        
        return SUCCESS, new_state


    def solve(self, state):
        self.check_init_superset_state(state)

        state = self.sync_with_superset_state(state)
        result, state = self.propagate(state)
        
        if result == FAILURE:
            return FAILURE, None

        if all(var.try_get_confirmed_value(state) is not None for var in self.variables):
            return SUCCESS, state
        
        decision_var = self.get_most_constrained_variable(state)

        for decision_value in decision_var.get_domain(state):
            child_state = deepcopy(state)
    
            # make decision on a variable by picking a value for it        
            decision_var.set_domain(child_state, {decision_value})
            child_result, child_state = self.solve(child_state)
            
            if child_result == SUCCESS:
                return SUCCESS, child_state
        
        return FAILURE, None
