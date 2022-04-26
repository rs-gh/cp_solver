from abc import ABC, abstractmethod
from itertools import product, repeat
from collections import defaultdict
from variable import Variable
from constant import Constant
from utils import (
    isolate_var_from_exp1_and_rearrange_exp2,
    print_expression_tree
)
from status import FAILURE


class Constraint(ABC):
    def __init__(self, comparison, lhs, rhs):
        self.comparison = comparison
        self.lhs = lhs
        self.rhs = rhs
        self.variables = lhs.variables.union(rhs.variables)

    
    def get_heuristic_domains(self, state):
        lhs_min_value = self.lhs.get_min_value(state)
        lhs_max_value = self.lhs.get_max_value(state)
        rhs_min_value = self.rhs.get_min_value(state)
        rhs_max_value = self.rhs.get_max_value(state)
        heuristic_lhs_domain = set(range(lhs_min_value, lhs_max_value + 1))
        heuristic_rhs_domain = set(range(rhs_min_value, rhs_max_value + 1))
        return heuristic_lhs_domain, heuristic_rhs_domain
    

    def get_operation_variable_pairs(self):
        lhs_vars = list(zip(repeat("lhs", len(self.lhs.variables)), self.lhs.variables))
        rhs_vars = list(zip(repeat("rhs", len(self.rhs.variables)), self.rhs.variables))
        return lhs_vars + rhs_vars


    @abstractmethod
    def is_feasible(self, state):
        pass


    @abstractmethod
    def prune(self, state):
        pass


class NotEqualConstraint(Constraint):
    def __init__(self, lhs, rhs):
        super().__init__(lambda x, y: x != y, lhs, rhs)
    

    def get_feasible_domain(self, state):
        heuristic_lhs_domain, heuristic_rhs_domain = self.get_heuristic_domains(state)
        return heuristic_lhs_domain.union(heuristic_rhs_domain)


    def is_feasible(self, state):
        feasible_domain = self.get_feasible_domain(state)
        if len(feasible_domain) > 1:
            return True
        else:
            return False
    

    def prune(self, state):
        is_any_variable_state_changed = False if len(self.variables) > 0 else True

        for op, var in self.get_operation_variable_pairs():
            if op == "lhs":
                _, rearranged_exp = isolate_var_from_exp1_and_rearrange_exp2(var, self.lhs, self.rhs)
            else:
                _, rearranged_exp = isolate_var_from_exp1_and_rearrange_exp2(var, self.rhs, self.lhs)
            
            rearranged_exp.solve(state)
            confirmed_value = rearranged_exp.try_get_confirmed_value(state)
            if confirmed_value is not None:
                is_variable_state_changed = var.try_filter_variable_domain(
                    state,
                    lambda var_value, bound: var_value != bound,
                    confirmed_value
                )

                if is_variable_state_changed == FAILURE:
                    return FAILURE
    
                is_any_variable_state_changed |=  is_variable_state_changed
        
        return is_any_variable_state_changed


class EqualityConstraint(Constraint):
    def __init__(self, lhs, rhs):
        super().__init__(lambda x, y: x == y, lhs, rhs)


    def get_feasible_domain(self, state):
        heuristic_lhs_domain, heuristic_rhs_domain = self.get_heuristic_domains(state)
        return heuristic_lhs_domain.intersection(heuristic_rhs_domain)


    def is_feasible(self, state):
        feasible_domain = self.get_feasible_domain(state)
        if len(feasible_domain) >= 1:
            return True
        else:
            return False
    

    def prune(self, state):
        is_any_variable_state_changed = False if len(self.variables) > 0 else True
        
        feasible_domain = self.get_feasible_domain(state)
        lower_bound =  Constant(min(feasible_domain))
        upper_bound = Constant(max(feasible_domain))

        lhs_lower_constraint = LessThanEqualConstraint(lower_bound, self.lhs)
        lhs_upper_constraint = LessThanEqualConstraint(self.lhs, upper_bound)
        rhs_lower_constraint = LessThanEqualConstraint(lower_bound, self.rhs)
        rhs_upper_constraint = LessThanEqualConstraint(self.rhs, upper_bound)
        constraints = (lhs_lower_constraint, lhs_upper_constraint, rhs_lower_constraint, rhs_upper_constraint)
        
        for constraint in constraints:
            is_variable_state_changed = constraint.prune(state)

            if is_variable_state_changed == FAILURE:
                return FAILURE

            is_any_variable_state_changed |= is_variable_state_changed
        
        return is_any_variable_state_changed


class LessThanEqualConstraint(Constraint):
    def __init__(self, lhs, rhs):
        super().__init__(lambda x, y: x <= y, lhs, rhs)


    def is_feasible(self, state):
        if self.lhs.get_min_value(state) > self.rhs.get_max_value(state):
            return False
        else:
            return True
    

    def prune(self, state):
        is_any_variable_state_changed = False if len(self.variables) > 0 else True

        for op, var in self.get_operation_variable_pairs():
            if op == "lhs":
                _, rearranged_exp = isolate_var_from_exp1_and_rearrange_exp2(var, self.lhs, self.rhs)
                is_variable_state_changed = var.try_filter_variable_domain(
                    state,
                    lambda var_value, bound: var_value <= bound,
                    rearranged_exp.get_max_value(state)
                )
            else:
                _, rearranged_exp = isolate_var_from_exp1_and_rearrange_exp2(var, self.rhs, self.lhs)
                is_variable_state_changed = var.try_filter_variable_domain(
                    state,
                    lambda var_value, bound: var_value >= bound,
                    rearranged_exp.get_min_value(state)
                )
            
            if is_variable_state_changed == FAILURE:
                return FAILURE

            is_any_variable_state_changed |= is_variable_state_changed

        return is_any_variable_state_changed
