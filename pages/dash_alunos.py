from datetime import datetime
import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

### RETORNA DATAFRAME
@st.cache_data
def fn_retorna_dados():
    """
    Ler base de dados
    """
    return pd.read_csv(r".\base\df_vw_info_aluno.csv",sep=";")

df = fn_retorna_dados()

#### SIDEBAR

base_dir = os.getcwd()
path_dash = os.path.join(base_dir, "pages", "dash_alunos.py")
with st.sidebar:
    st.page_link("app.py", label="Página principal", icon='📊')
    st.page_link(path_dash, label="Análise Alunos", icon='🔍')
    st.divider()
    df_filtro_mat = df.query("nomecurso == 'ALFABETIZAÇÃO' or nomecurso.str.contains('FASE')")
    lst_fase = df_filtro_mat.nomecurso.unique()
    lst_fase.sort()
    slct_fase = st.selectbox("Fase:", lst_fase)

    lst_turma = df.query("nometurma.notna() and nomecurso == @slct_fase").nometurma.unique()
    lst_turma.sort()
    slct_turma = st.selectbox("Turma:", lst_turma)

    lst_aluno = df.query("nomealuno.notna() and nometurma == @slct_turma").nomealuno.unique()
    slct_aluno = st.selectbox("Aluno:", lst_aluno)

df_filtro_aluno = df.query("nomealuno == @slct_aluno")
df_info = df_filtro_aluno[['idaluno','nomealuno','datanascimento','sexo']]
df_info = df_info.groupby('idaluno').agg({'nomealuno':'max','datanascimento':'max','sexo':'max'})
df_info.reset_index(inplace=True)
dic_sexo = {"F":"Feminino", "M":"Masculino"}

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown(f" #### {df_info["nomealuno"][0]}")
        df_ava = df_filtro_aluno[['siglaperiodo','avaliacao_desc']].query('avaliacao_desc.notna()')\
                .groupby('siglaperiodo').avaliacao_desc.max().reset_index()
        V_STR_AVA = ""
        for i,r in df_ava.iterrows():
            V_STR_AVA = V_STR_AVA +f"- *Avaliação {r['siglaperiodo']}*: {r['avaliacao_desc']} \n"
        st.markdown(V_STR_AVA)

    with st.container(border=True):
        df_falta = df_filtro_aluno[['nomedisciplina','nomefase','faltas']]\
                    .query('nomefase.str.contains("SEMESTRE") and faltas.notna()')
        df_falta = df_falta.groupby(['nomedisciplina','nomefase']).faltas.sum().reset_index()
        fig_2 = px.bar(df_falta, x="nomedisciplina", y="faltas", color="nomefase",
                       labels={'nomedisciplina':'Matéria','faltas':'Faltas', 'nomefase':'Período'},
                       title="Faltas por matéria")
        fig_2.update_layout(legend=dict(orientation="h"))
        st.plotly_chart(fig_2, theme="streamlit" ,use_container_width=True)

with col2:
    with st.container(border=True):
        V_DT_NASC = datetime.strptime(df_info["datanascimento"][0],"%Y-%m-%d %H:%M:%S")
        V_DT_NASC = V_DT_NASC.strftime("%d/%m/%Y")
        st.markdown(f"""
                    ##### Informações gerais
                    ###### ID: {df_info["idaluno"][0]}
                    ###### Data de nascimento: {V_DT_NASC}
                    ###### Sexo: {dic_sexo.get(df_info["sexo"][0])}
        """)

    with st.container(border=True):
        st.markdown(" **Desempenho do aluno** ")
        df_f_aluno_ano_slider = df_filtro_aluno[['nomedisciplina','siglaperiodo',
                                                 'numerofase','nomefase','notafase']]\
                                                .query("notafase.notna()")

        if df_f_aluno_ano_slider.siglaperiodo.min() != df_f_aluno_ano_slider.siglaperiodo.max():
            v_ano = st.slider("Ano", min_value=df_f_aluno_ano_slider.siglaperiodo.min(),
                              max_value=df_f_aluno_ano_slider.siglaperiodo.max())
        else:
            v_ano = df_f_aluno_ano_slider.siglaperiodo.min()

        df_f_aluno_ano = df_filtro_aluno[['nomedisciplina','siglaperiodo',
                                          'numerofase','nomefase','notafase']]\
                                        .query("siglaperiodo == @v_ano and notafase.notna()")
        df_f_aluno_ano_grp = df_f_aluno_ano.groupby(['nomedisciplina','numerofase','nomefase'])\
                            .notafase.mean().reset_index()
        df_f_aluno_ano_grp.sort_values(by=['nomedisciplina','numerofase'],
                                       ascending=False, inplace=True)
        fig_1 = px.line_polar(df_f_aluno_ano_grp, r="notafase", theta="nomefase",
                              color="nomedisciplina", line_close=True,  range_r=[0,10],
                              labels={'notafase':'Nota','nomefase':'nomefase',
                                      'nomedisciplina':'Matéria'})
        fig_1.update_layout(legend=dict(orientation="h")
)
        st.plotly_chart(fig_1, theme="streamlit" ,use_container_width=True)
