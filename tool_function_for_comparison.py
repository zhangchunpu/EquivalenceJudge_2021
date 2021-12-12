import sympy as sy
def _eq_reduction(equation):
    left_side = equation.args[0].factor()
    right_side = equation.args[1].factor()
    if (left_side.is_Mul) and (right_side.is_Mul):
        term_shared = set(left_side.args) ^ set(right_side.args)
        i = 1
        for term in term_shared:
            i *= term
        if term_shared:
            left_side = left_side/i
            right_side = right_side/i
            return sy.Eq(left_side, right_side)
        else:
            return equation
    else:
        return equation
def _eq_transform(eq_group_one, eq_group_two):
    def eq_do_same_cal(equation_one, equation_two):
        if equation_one.free_symbols != equation_two.free_symbols:
            return False
        else:
            if equation_one == equation_two:
                return True
            else:
                for var in equation_one.free_symbols:
                    try:
                        eq_one_solution = sy.solve(equation_one.expand(), var)[0]
                        eq_two_solution = sy.solve(equation_two.expand(), var)[0]
                        q = sy.simplify(eq_one_solution/eq_two_solution)
                        if int(q) == 1:
                            return True
                        else:
                            continue
                    except:
                        continue
                return False
    for equation_i in eq_group_one:
        for equation_j in eq_group_two:
            is_same = eq_do_same_cal(equation_i, equation_j)
            if is_same:
                index = eq_group_two.index(equation_j)
                eq_group_two[index] = equation_i
            else:
                continue
    return eq_group_one, eq_group_two
def __term_separate(eq_group):
    lst = []
    for equation in eq_group:
        lst.append([equation.args[0], equation.args[1]])
    return lst
def _info_complement(eq_group):
    term_lst = __term_separate(eq_group)
    other_term_lst = term_lst.copy()
    for eq_term_lst_i in term_lst:
        other_term_lst.remove(eq_term_lst_i)
        left_side = eq_term_lst_i[0]
        right_side = eq_term_lst_i[1]
        for eq_term_lst_j in other_term_lst:
            if left_side == eq_term_lst_j[0]:
                new_eq = sy.Eq(right_side, eq_term_lst_j[1])
                if not new_eq in eq_group:
                    eq_group.append(new_eq)
            elif left_side == eq_term_lst_j[1]:
                new_eq = sy.Eq(right_side, eq_term_lst_j[0])
                if not new_eq in eq_group:
                    eq_group.append(new_eq)
            elif right_side == eq_term_lst_j[0]:
                new_eq = sy.Eq(left_side, eq_term_lst_j[1])
                if not new_eq in eq_group:
                    eq_group.append(new_eq)
            elif right_side == eq_term_lst_j[1]:
                new_eq = sy.Eq(left_side, eq_term_lst_j[0])
                if not new_eq in eq_group:
                    eq_group.append(new_eq)
    return eq_group