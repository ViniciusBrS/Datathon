import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Alunos - Passos Mágicos", layout="wide")

### RETORNA DATAFRAME
@st.cache_data
def fn_retorna_dados():
    """
    Ler base de dados
    """
    #return pd.read_csv(r".\base\df_vw_info_aluno.csv",sep=";")
    v_link = "https://raw.githubusercontent.com/ViniciusBrS/Datathon/main/base/df_vw_info_aluno.csv"
    return pd.read_csv(v_link,sep=";")

df = fn_retorna_dados()


### SIDEBAR
base_dir = os.getcwd()
path_dash = os.path.join(base_dir, "pages", "dash_alunos.py")
with st.sidebar:
    st.page_link("app.py", label="Página principal", icon='📊')
    st.page_link(path_dash, label="Análise Alunos", icon='🔍')
    st.divider()
    sld_ano = st.slider("Ano", min_value=df.siglaperiodo.min(), max_value=df.siglaperiodo.max())

v_ano = sld_ano
df_filtro = df[df.siglaperiodo == v_ano].query("nomecurso == 'ALFABETIZAÇÃO' or nomecurso.str.contains('FASE')")
df_filtro['nomedisciplina'] = df_filtro['nomedisciplina'].str[:20]
ls = pd.unique(df_filtro[['nome_prof_1', 'nome_prof_2','nome_prof_3','nome_prof_4']].values.ravel('K'))

v_check_ano = sld_ano > df.siglaperiodo.min()
v_ano_ant = sld_ano-1 if v_check_ano else sld_ano
df_filtro_ant = df[df.siglaperiodo == v_ano_ant].query("nomecurso == 'ALFABETIZAÇÃO' or nomecurso.str.contains('FASE')")
ls_ant = pd.unique(df_filtro_ant[['nome_prof_1', 'nome_prof_2','nome_prof_3','nome_prof_4']].values.ravel('K'))

v_aluno, v_aluno_ant = len(df_filtro['idaluno'].unique()), len(df_filtro_ant['idaluno'].unique())
v_turma, v_turma_ant = len(df_filtro['idturma'].unique()), len(df_filtro_ant['idturma'].unique())
v_prof, v_prof_ant = len([l for l in ls if l is not None]), len([l for l in ls_ant if l is not None])
v_dif_aluno = round((1-v_aluno_ant/v_aluno)*100,2)
v_dif_turma = round((1-v_turma_ant/v_turma)*100,2)
v_dif_prof = round((1-v_prof_ant/v_prof)*100,2)

cont_metricas = st.container(border=True)
with cont_metricas:
    col_card1, col_card2, col_card3 = st.columns(3)
    col_card1.metric(f"Alunos em {v_ano}", v_aluno, str(v_dif_aluno)+f"% vs {v_ano_ant}" if v_check_ano else None)
    col_card2.metric(f"Turmas em {v_ano}", v_turma, str(v_dif_turma)+f"% vs {v_ano_ant}" if v_check_ano else None)
    col_card3.metric(f"Professores em {v_ano}", v_prof, str(v_dif_prof)+f"% vs {v_ano_ant}" if v_check_ano else None)


col1, col2 = st.columns(2)

with col1:
    df_1 = df_filtro[['idaluno','nomecurso']].groupby('nomecurso').idaluno.nunique().reset_index()
    fig_1 = px.bar(df_1, x='nomecurso',y='idaluno', labels={'idaluno':'Qtde.','nomecurso':'Fase'}, title="Quantidade de alunos por fase")
    st.plotly_chart(fig_1, theme="streamlit" ,use_container_width=True)
    st.divider()
    lst_rd_fase = df_filtro.nomecurso.unique()
    lst_rd_fase.sort()
    rd_fase = st.radio("Fase: ", options=lst_rd_fase, horizontal=True)
    v_filtro_fase = rd_fase
    df_3 = df_filtro[['idaluno','nomecurso','nomedisciplina','notafase']].query('notafase >= 0 and nomecurso == @v_filtro_fase') #.groupby(['idaluno','nomedisciplina']).idaluno.nunique().reset_index()
    df_3 = df_3.groupby(['idaluno','nomedisciplina']).notafase.mean().reset_index()
    fig_3 = px.box(df_3, x="nomedisciplina", y="notafase", title=f"Variação das notas na {v_filtro_fase} - {v_ano}")
    st.plotly_chart(fig_3, theme="streamlit" ,use_container_width=True)


with col2:
    df_2 = df_filtro[['idaluno','nomecurso','idturma']].groupby(['nomecurso','idturma']).idaluno.nunique().reset_index()
    df_2 = df_2.groupby('nomecurso').idaluno.mean().round(1).reset_index()
    fig_2 = px.bar(df_2, x='nomecurso',y='idaluno', labels={'idaluno':'Média','nomecurso':'Fase'}, title="Média de alunos por turma")
    st.plotly_chart(fig_2, theme="streamlit" ,use_container_width=True)
    st.divider()
    with st.container():
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
    v_filtro_fase = rd_fase
    df_filtro_ = df.query("nomecurso == 'ALFABETIZAÇÃO' or nomecurso.str.contains('FASE')")
    df_filtro_['nomedisciplina'] = df_filtro_['nomedisciplina'].str[:20]
    df_4 = df_filtro_[['idaluno','nomecurso','siglaperiodo','nomedisciplina','notafase']]\
            .query('notafase >= 0 and nomecurso == @v_filtro_fase')
    df_4 = df_4.groupby(['siglaperiodo','nomedisciplina']).notafase.mean().round(2).reset_index()
    fig_4 = px.line(df_4, x="siglaperiodo", y="notafase", color='nomedisciplina',
                    labels={'notafase':'Nota','siglaperiodo':'Ano','nomedisciplina':''},
                    title=f"Média de nota por ano - {v_filtro_fase}")
    fig_4.update_xaxes(type='category')
    fig_4.update_layout(yaxis_range = [0,10], legend=dict(
    orientation="h",yanchor="bottom",    y=-1,    xanchor="left",    x=0.01
))
    st.plotly_chart(fig_4, theme="streamlit" ,use_container_width=True)
