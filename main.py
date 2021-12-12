import sys
import os

cwd = os.getcwd()
sys.path.append(cwd)

from EquivalenceJudge.mathml_to_eq_group import mathml_to_eq_group

if __name__ == '__main__':

    eq_group_one_path = '../test_data/test_data_equation/' + 'equation_group_29.html'
    eq_group_two_path = '../test_data/test_data_equation/' + 'equation_group_30.html'

    #同義性判定を行う
    eq_group_obj_1, eq_group_obj_2 = mathml_to_eq_group(eq_group_one_path, eq_group_two_path)
    is_same = eq_group_obj_1 == eq_group_obj_2
    print(is_same)






