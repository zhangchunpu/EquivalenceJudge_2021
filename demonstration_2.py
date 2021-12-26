import sympy as sy
import streamlit as st
import sys

import os

cwd = os.getcwd()
sys.path.append(cwd)

from EquivalenceJudge.mathml_to_eq_group import mathml_to_eq_group

if __name__ == '__main__':

    st.markdown("<h1 style='text-align: center; color: black; font-size: 9mm '>Equivalence judgment of equation groups</h1>", unsafe_allow_html=True)

    #fileのpathを取得する
    file_name_1 = st.selectbox(
        'Enter file path one',
        ['equation_group_{}.html'.format(str(i)) for i in range(1, 31)]
    )

    file_name_2 = st.selectbox(
        'Enter file path two',
        ['equation_group_{}.html'.format(str(i)) for i in range(1, 31)]
    )

    eq_group_one_path = cwd + '/test_data/test_data_equation/' + file_name_1
    eq_group_two_path = cwd + '/test_data/test_data_equation/' + file_name_2

    #同義性判定を行う
    eq_group_obj_1, eq_group_obj_2 = mathml_to_eq_group(eq_group_one_path, eq_group_two_path)
    is_same = eq_group_obj_1 == eq_group_obj_2

    #mathmlの内容を取得
    with open(eq_group_one_path, 'r') as f:
        mathml_content_one = f.read()
    with open(eq_group_two_path, 'r') as f:
        mathml_content_two = f.read()

    #パラメーターの情報を取得
    eq_group_one_param = eq_group_obj_1.parameter.copy()
    eq_group_two_param = eq_group_obj_2.parameter.copy()

    button = st.sidebar.checkbox('show information of equation groups')

    #数式群1を表示する
    st.subheader('Equation group one')
    for eq in eq_group_obj_1.equation_list:
        st.latex(sy.latex(eq))
    # st.latex(r'\frac{\mathrm{d}C_\mathrm{A}}{\mathrm{d}t} = \frac{F}{V}(C_{\mathrm{A, in}}-C_\mathrm{A})-k_0\exp{\left(-\frac{E}{RT}\right)}C_\mathrm{A}')
    # st.latex(r'\frac{\mathrm{d}T}{\mathrm{d}t} = \frac{F}{V}(T_{\mathrm{in}}-T)+\frac{h_\mathrm{r}}{\rho{c_\mathrm{p}}}k_0\exp{\left(-\frac{E}{RT}\right)}C_\mathrm{A}-\frac{UA_\mathrm{r}}{V{\rho}c_\mathrm{p}}(T-T_\mathrm{j})')

    #数式群2を表示する
    st.subheader('Equation group two')
    for eq in eq_group_obj_2.equation_list:
        st.latex(sy.latex(eq))
    # st.latex(r'\frac{\mathrm{d}C_{\mathrm{A}}}{\mathrm{d}t} = \frac{F}{V}(C_{\mathrm{A, in}}-C_\mathrm{A})-k_0\exp{\left(-\frac{E}{RT}\right)}C_\mathrm{A}')
    # st.latex(r'\frac{\mathrm{d}T}{\mathrm{d}t} = \frac{F}{V}(T_{\mathrm{in}}-T)+\frac{h_\mathrm{r}}{\rho{c_\mathrm{p}}}k_0\exp{\left(-\frac{E}{RT}\right)}C_\mathrm{A}-\frac{Q}{V\rho{c_\mathrm{p}}}')
    # st.latex(r'Q = UA_\mathrm{r}(T-T_\mathrm{j})')




    #数式の詳しい情報を表示させる
    if button:

        if st.checkbox('show the mathml content of equation group one'):
            st.text(mathml_content_one)
        if st.checkbox('show the variables to be eliminated in equation group one'):
            if eq_group_one_param:
                eq_group_one_param_str = '\hspace{0.1in}'.join(map(str, eq_group_one_param))
                st.latex(eq_group_one_param_str)
            else:
                st.text('no variables to eliminate')

        if st.checkbox('show the mathml content of equation group two'):
            st.text(mathml_content_two)
        if st.checkbox('show the variables to be eliminated in equation group two'):
            if eq_group_two_param:
                eq_group_two_param_str = '\hspace{0.1in}'.join(map(str, eq_group_two_param))
                st.latex(eq_group_two_param_str)
            else:
                st.text('no variables to eliminate')

    #同義性の判定結果を示す
    if st.sidebar.checkbox('show result'):
        if is_same:
            st.subheader('Judgment result: same')
        else:
            st.subheader('Judgment result: different')


    #判定の過程と結果を示す
    if st.sidebar.checkbox('confirm the process of judgment'):

        st.subheader('process of judgment')

        if eq_group_obj_1.degree_of_freedom != eq_group_obj_2.degree_of_freedom:
            st.write('degree of freedom different')
        else:
            st.write('equations one with variables eliminated')

            with open('equation_one_final_latex.txt', 'r') as f:
                for eq in f.read().strip().split('\n'):
                    st.latex(eq)

            st.write('equations two with variables eliminated')

            with open('equation_two_final_latex.txt', 'r') as f:
                for eq in f.read().strip().split('\n'):
                    st.latex(eq)








