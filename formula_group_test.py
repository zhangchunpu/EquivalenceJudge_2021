import sympy as sy
import os
import copy

from EquivalenceJudge.tool_function_for_comparison import _info_complement


class EquationGroup:

    def __init__(self, equation_list):
        # 連立方程式は等式から構成されることを想定する
        self._equation_list = self.eq_group_init(equation_list)
        self._var_set = self.get_var_set()
        self._degree_of_freedom = self.get_degree_of_freedom()
        self._var_equation_dict = self.get_var_for_equation()
        self._parameter = self.find_parameter()

    def get_degree_of_freedom(self):
        return len(self._var_set)-len(self._equation_list)

    def get_var_set(self):
        var_set = set()
        for formula in self._equation_list:
            # 等式も通の数式もfree_symbolsメソッドがあります
            var_set = var_set.union(formula.free_symbols)
        return var_set

    def get_var_for_equation(self):
        dict = {}
        for equation in self:
            dict[equation] = equation.free_symbols
        return dict

    # 等式の中の項をリストに入れて返す, 使い方はこれから考えましょう、必要なのかどうかすらまだ分からない
    def seperate_cal_term(self):
        cal_term_dic = {}
        for equation in self:
            lst = []
            formula_tuple = equation.args
            for formula in formula_tuple:
                if formula.args:
                    for term in formula.args:
                        lst.append(term)
                else:
                    lst.append(formula)
            cal_term_dic[equation] = lst
        return cal_term_dic

    def find_parameter(self):  # 複数の式に登場した変数については消去する、関数名は考え直す必要がある
        var_in_more_than_one_equation = []
        for var in self._var_set:
            number_of_equation_var_in = 0
            for equation in self._equation_list:
                lst = equation.free_symbols
                if var in lst:
                    number_of_equation_var_in += 1

            if number_of_equation_var_in > 1:
                var_in_more_than_one_equation.append(var)

        return var_in_more_than_one_equation

    def __getitem__(self, index):
        return self._equation_list[index]

    def __eq__(self, other):
        if self._degree_of_freedom != other._degree_of_freedom:
            return False
        else:
            return self.compare(self=self, other=other)

    @property
    def equation_list(self):
        return self._equation_list

    @property
    def degree_of_freedom(self):
        return self._degree_of_freedom

    @property
    def var_set(self):
        return self._var_set

    @property
    def var_equation_dict(self):
        return self._var_equation_dict

    @property
    def parameter(self):
        return self._parameter

    @classmethod
    def eq_group_init(cls, equation_list, is_first_loop=True):
        if is_first_loop is True:
            for formula in equation_list:
                if not formula.is_Equality:
                    raise Exception(
                        'formula list must be consisted of equations')
        for formula_i in equation_list:
            a = equation_list.index(formula_i) + 1
            b = len(equation_list)
            for i in range(a, b):
                formula_j = equation_list[i]
                do_same_cal = cls.eq_do_same_cal(formula_i, formula_j)
                if do_same_cal:
                    equation_list.remove(formula_i)
                    is_first_loop = False
                    return cls.eq_group_init(equation_list, is_first_loop)
                else:
                    continue
            continue
        return equation_list

    @classmethod
    def reduce_the_number_of_equation(cls, parameter_list, equation_list,
                                      target=None):

        def index_of_equation_with_parameter(parameter_list, equation_list):
            dict = {}
            for param in parameter_list:
                dict[param] = []
                for equation in equation_list:
                    if param in equation.free_symbols:
                        dict[param].append(equation_list.index(equation))
            return dict

        if not parameter_list:
            return equation_list

        else:
            parameter_info_dict = index_of_equation_with_parameter(
                parameter_list=parameter_list,
                equation_list=equation_list)
            equation_list_copy = equation_list.copy()

            if not target:
                return equation_list

            else:
                for target_var in target:
                    if target_var in parameter_info_dict:
                        param_solution = []
                        for index in parameter_info_dict[target_var]:
                            try:
                                solution = sy.solve(equation_list[index],
                                                    target_var)
                                # solutionは複数ある場合がある、なのでlist
                                if len(solution) == 1:
                                    param_solution.append(solution[0])
                                else:
                                    raise Exception(
                                        'dont try to solve a multivalued function')

                                equation_list_copy.remove(equation_list[index])

                            except:
                                raise Exception(
                                    'this function cant be solved by sympy')

                        if len(param_solution) == 2:
                            new_eq = sy.Eq(param_solution[0], param_solution[1])
                            equation_list_copy.append(new_eq)

                        else:  # パラメータが二つ以上の数式に現れた場合
                            for i in range(len(param_solution) - 1):
                                new_eq = sy.Eq(param_solution[i],
                                               param_solution[i + 1])
                                equation_list_copy.append(new_eq)

                        target.remove(target_var)
                        break

                    else:
                        continue

            parameter_list = cls(equation_list_copy).parameter
            return cls.reduce_the_number_of_equation(
                parameter_list=parameter_list,
                equation_list=equation_list_copy,
                target=target)

    @classmethod
    def compare(cls, self, other):

        self_parameter = self._parameter.copy()
        other_parameter = other.parameter.copy()
        # いらないかも
        self_parameter.sort(key=str)
        other_parameter.sort(key=str)

        target_var_self = set()
        target_var_other = set()

        if self._var_set > other.var_set:
            target_var_self = self._var_set - other.var_set
        elif other.var_set > self._var_set:
            target_var_other = other.var_set - self._var_set
        else:
            var_shared = self._var_set & other.var_set
            target_var_self = self._var_set - var_shared
            target_var_other = other.var_set - var_shared

        # 片方の数式群にしか含まれない変数は消去可能なものでなければいけません、
        # でないとこの二つの数式群は異なる計算をすることになります。
        # parameter: 群内共有変数
        parameter_not_include_target_var = \
            target_var_self > set(self._parameter) or \
            target_var_other > set(other.parameter)
        if parameter_not_include_target_var:
            return False

        # 消去の対象となる変数がいずれの数式群にも含まれない。
        if (not target_var_self) and (not target_var_other):
            cwd = os.getcwd()
            is_same = cls.has_same_meaning(self._equation_list,
                                           other.equation_list)
            if is_same:
                with open(cwd + '/equation_one_final_latex.txt', 'w') as f:
                    for eq_ in self._equation_list:
                        f.write(sy.latex(eq_) + '\n')
                with open(cwd + '/equation_two_final_latex.txt', 'w') as f:
                    for eq_ in other.equation_list:
                        f.write(sy.latex(eq_) + '\n')
                # 最終形態のsympyオブジェクトをファイルに書き込む
                self_equation_list = copy.deepcopy(self._equation_list)
                other_equation_list = copy.deepcopy(other.equation_list)
                with open(cwd + '/equation_one_final_latex.txt', 'w') as f:
                    for eq in self_equation_list:
                        f.write(sy.latex(eq) + '\n')
                with open(cwd + '/equation_two_final_latex.txt', 'w') as f:
                    for eq in other_equation_list:
                        f.write(sy.latex(eq) + '\n')
                return True

            else:
                target = list(set(self_parameter) & set(other_parameter))
                if not target:
                    self_eq_lst = self._equation_list
                    other_eq_lst = other.equation_list
                    new_self_eq = _info_complement(self_eq_lst)
                    new_other_eq = _info_complement(other_eq_lst)
                    return cls.compare(cls(new_self_eq), cls(new_other_eq))
                else:
                    self_eq_lst_no_param = self.reduce_the_number_of_equation(
                        parameter_list=self_parameter,
                        equation_list=self._equation_list,
                        target=target.copy())
                    other_eq_lst_no_param = self.reduce_the_number_of_equation(
                        parameter_list=other_parameter,
                        equation_list=other.equation_list,
                        target=target.copy())
                    # 数式の最終形態をファイルの書き込む
                    with open(cwd + '/equation_one_final_latex.txt', 'w') as f:
                        for eq in self_eq_lst_no_param:
                            f.write(sy.latex(eq) + '\n')
                    with open(cwd + '/equation_two_final_latex.txt', 'w') as f:
                        for eq in other_eq_lst_no_param:
                            f.write(sy.latex(eq) + '\n')

                    return cls.has_same_meaning(self_eq_lst_no_param,
                                                other_eq_lst_no_param)

        else:
            self_eq_lst_no_param = self.reduce_the_number_of_equation(
                parameter_list=self_parameter,
                equation_list=self._equation_list,
                target=target_var_self)
            other_eq_lst_no_param = self.reduce_the_number_of_equation(
                parameter_list=other_parameter,
                equation_list=other.equation_list,
                target=target_var_other)
            return cls.compare(cls(self_eq_lst_no_param),
                               cls(other_eq_lst_no_param))

    @classmethod
    def has_same_meaning(cls, equation_lst_self, equation_lst_other):

        for equation_i in equation_lst_other:
            has_same_eq_in_self = False
            for equation_j in equation_lst_self:
                is_same_equation = cls.eq_do_same_cal(equation_i, equation_j)
                if is_same_equation:
                    has_same_eq_in_self = True
                    break
                else:
                    continue
            if has_same_eq_in_self:
                continue
            else:
                return False
        return True

    @classmethod
    def eq_do_same_cal(cls, equation_one, equation_two):
        if equation_one.free_symbols != equation_two.free_symbols:
            return False
        else:
            if equation_one == equation_two:
                return True
            else:
                for var in equation_one.free_symbols:
                    try:
                        eq_one_solution = sy.solve(equation_one.expand(), var)[
                            0]
                        eq_two_solution = sy.solve(equation_two.expand(), var)[
                            0]
                        q = sy.simplify(eq_one_solution / eq_two_solution)
                        if int(q) == 1:
                            return True
                        else:
                            continue
                    except:
                        continue
                return False
