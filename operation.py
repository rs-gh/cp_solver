from abc import ABC, abstractmethod
from functools import reduce
from expression import Expression
from variable import Variable
from constant import Constant


class Operation(Expression):
    def __init__(self, operation, *operands):
        self.operation = operation
        super().__init__(*operands)


    def _binary_operation_solve(self, state):
        return reduce(
            lambda x, y: self.operation(x, y),
            (op.solve(state) for op in self.operands)
        )


    def _unary_operation_solve(self, state):
        operand = self.operands[0]
        return self.operation(operand.solve(state))


    def _set_variables_for_max_absolute_value(self, state):
        for op in self.operands:
            if isinstance(op, Variable):
                op.set_max_value(state)
            elif isinstance(op, Constant):  # TODO: when constant is < 0, need to flip
                continue
            else:
                op.get_max_value(state, False)
    
    
    def _set_variables_for_min_absolute_value(self, state):
        for op in self.operands:
            if isinstance(op, Variable):
                op.set_min_value(state)
            elif isinstance(op, Constant):  # TODO: when constant is < 0, need to flip
                continue
            else:
                op.get_min_value(state, False)


    def get_variables_in_expression(self):
        variables = set()
        for op in self.operands:
            variables = variables.union(op.variables)
        return variables
    
    
    @abstractmethod
    def solve(self, state):
        pass


    @abstractmethod
    def get_max_value(self, state, solve=True):
        pass

    
    @abstractmethod
    def get_min_value(self, state, solve=True):
        pass
    

    def try_get_confirmed_value(self, state):
        if all(op.try_get_confirmed_value(state) is not None for op in self.operands):
            return self.solve(state)
        else:
            return False


class Add(Operation):
    def __init__(self, *operands):
        super().__init__(lambda x, y: x + y, *operands)
    

    def solve(self, state):
        return self._binary_operation_solve(state)


    def get_max_value(self, state, solve=True):
        self._set_variables_for_max_absolute_value(state)
        if solve:
            return self.solve(state)
    
    
    def get_min_value(self, state, solve=True):
        self._set_variables_for_min_absolute_value(state)
        if solve:
            return self.solve(state)


class Multiply(Operation):
    def __init__(self, *operands):
        super().__init__(lambda x, y: x * y, *operands)


    def solve(self, state):
        return self._binary_operation_solve(state)


    def get_max_value(self, state, solve=True):
        self._set_variables_for_max_absolute_value(state)
        if solve:
            return self.solve(state)
    
    
    def get_min_value(self, state, solve=True):
        self._set_variables_for_min_absolute_value(state)
        if solve:
            return self.solve(state)


class Negative(Operation):
    def __init__(self, operand):
        super().__init__(lambda x: -1.0 * x, operand)
    

    def solve(self, state):
        return self._unary_operation_solve(state)


    def get_max_value(self, state, solve=True):
        self._set_variables_for_min_absolute_value(state)
        if solve:
            return self.solve(state)


    def get_min_value(self, state, solve=True):
        self._set_variables_for_max_absolute_value(state)
        if solve:
            return self.solve(state)


class Inverse(Operation):
    def __init__(self, operand):
        super().__init__(lambda x: 1.0 / x, operand)


    def solve(self, state):
        return self._unary_operation_solve(state)


    def get_max_value(self, state, solve=True):
        self._set_variables_for_min_absolute_value(state)
        if solve:
            return self.solve(state)


    def get_min_value(self, state, solve=True):
        self._set_variables_for_max_absolute_value(state)
        if solve:
            return self.solve(state)
