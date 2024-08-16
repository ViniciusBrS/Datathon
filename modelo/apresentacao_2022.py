import os
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import joblib
import streamlit as st


# Função para carregar o modelo e o escalador para 2022
def carregar_modelo_e_scaler():
    model_path = r'C:\Users\Vinícius\Documents\PosTech\Datathon\Passos_Magicos_Final12A\modelo_2022.h5'
    scaler_path = r'C:\Users\Vinícius\Documents\PosTech\Datathon\Passos_Magicos_Final12A\scaler_2022.pkl'

    # Carregar o modelo
    try:
        model = tf.keras.models.load_model(model_path)
        print('Modelo TensorFlow para 2022 carregado com sucesso.')
    except Exception as e:
        print(f'Erro ao carregar o modelo para 2022: {e}')
        return None, None

    # Carregar o escalador
    try:
        scaler = joblib.load(scaler_path)
        print('Scaler para 2022 carregado com sucesso.')
    except Exception as e:
        print(f'Erro ao carregar o escalador para 2022: {e}')
        return None, None

    return model, scaler


# Função para preparar os dados para previsão
def preparar_dados_para_previsao(df, caracteristicas_numericas, scaler):
    # Garantir que todas as colunas estejam presentes no DataFrame
    for col in caracteristicas_numericas:
        if col not in df.columns:
            df[col] = 0

    # Selecionar as colunas e transformar os dados
    X_num = df[caracteristicas_numericas].apply(pd.to_numeric, errors='coerce').fillna(0).values
    X_num = scaler.transform(X_num)

    return X_num


# Função para fazer previsões com o modelo carregado e aplicar o threshold
def fazer_previsao_com_threshold(model, X_num, threshold):
    previsoes = model.predict(X_num)
    previsoes_binarias = (previsoes >= threshold).astype(int)
    return previsoes_binarias


# Função para mapear o resultado da previsão para "Sim" ou "Não"
def mapear_previsao(previsoes_binarias):
    return ["Sim" if pred == 1 else "Não" for pred in previsoes_binarias]


# Definindo variáveis numéricas para 2022
caracteristicas_numericas = [
    'IAA_2022', 'IEG_2022', 'IPS_2022',
    'IDA_2022', 'IPP_2022', 'IPV_2022', 'IAN_2022',
    'NOTA_MAT_2022', 'NOTA_PORT_2022', 'NOTA_ING_2022'
]

# Threshold para 2022
threshold = 0.5

# Interface do Streamlit
st.title("Previsão com Modelo Carregado")

# Carregar o modelo e o escalador para 2022
model, scaler = carregar_modelo_e_scaler()

if model is not None and scaler is not None:
    st.subheader("Entrada de dados")

    # Criar inputs para cada característica numérica
    inputs = {}
    for feature in caracteristicas_numericas:
        inputs[feature] = st.number_input(f"Insira o valor para {feature}", value=0.0)

    # Botão para fazer a previsão
    if st.button('Obter Previsão'):
        # Preparar os dados em formato de DataFrame
        input_data = pd.DataFrame([inputs])

        # Preparar os dados para previsão
        X_num = preparar_dados_para_previsao(input_data, caracteristicas_numericas, scaler)

        # Fazer a previsão com threshold específico
        previsao_binaria = fazer_previsao_com_threshold(model, X_num, threshold)

        # Mapear a previsão para "Sim" ou "Não"
        previsao = mapear_previsao(previsao_binaria.flatten())

        # Exibir resultados
        st.write(f'Previsão para 2022 com threshold {threshold}:')
        st.write(previsao)
else:
    st.error('Erro ao carregar o modelo ou escalador para 2022.')
