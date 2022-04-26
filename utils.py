from copy import deepcopy
from variable import Variable
from constant import Constant
from operation import Add, Multiply, Inverse, Negative


def print_expression_tree(exp, state, level):
    name_or_value = ""
    if isinstance(exp, Variable):
        name_or_value = exp.name + " " + str(exp.get_current_value(state))
    elif isinstance(exp, Constant):
        name_or_value = exp.value
    print("-" * level, type(exp), name_or_value)
    for op in exp.operands:
        print_expression_tree(op, state, level+1)


def get_operands_without_variable(exp, var):
    return (op for op in exp.operands if var != op and var not in op.variables)


def move_operand_from_exp1_to_exp2(exp1_op, exp1, exp2):
    if isinstance(exp1, Add):
        exp2_op = Negative(exp1_op)
        exp2 = Add(exp2) if type(exp2) != type(exp1) else exp2
    elif isinstance(exp1, Multiply):
        exp2_op = Inverse(exp1_op)
        exp2 = Multiply(exp2) if type(exp2) != type(exp1) else exp2
    elif isinstance(exp1, Negative):
        exp2_op = exp1_op.operands[0]
        exp2 = Negative(exp2) if type(exp2) != type(exp1) else exp2
    elif isinstance(exp1, Inverse):
        exp2_op = exp1_op.operands[0]
        exp2 = Inverse(exp2) if type(exp2) != type(exp1) else exp2           
    
    exp1.operands.remove(exp1_op)
    exp2.operands.append(exp2_op)

    if len(exp1.operands) == 1:
        exp1 = exp1.operands[0]

    return exp1, exp2


def is_variable_at_root(root, var):
    if root == var:
        return True
    return False


def isolate_var_from_exp1_and_rearrange_exp2(var, exp1, exp2):
    root = deepcopy(exp1)
    new_exp = deepcopy(exp2)
    while not is_variable_at_root(root, var):
        for op in get_operands_without_variable(root, var):
            root, new_exp = move_operand_from_exp1_to_exp2(op, root, new_exp)
    return root, new_exp
