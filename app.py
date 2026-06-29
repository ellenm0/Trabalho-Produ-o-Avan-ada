import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Previsão de Demanda - Veneziana Óculos", layout="centered")

st.title("📊 Previsão de Demanda Semanal")
st.caption("Veneziana Óculos")
st.write("Aplicação para previsão de demanda utilizando Média Móvel Simples (3 semanas).")

with st.container():
    produto = st.text_input("Nome do produto")
    dados_texto = st.text_area(
        "Demandas históricas (8 a 12 semanas, separadas por vírgula)",
        placeholder="120, 125, 130, 128, 135, 140, 138, 142"
    )

def media_movel_simples(dados, janela=3, previsoes=4):
    dados_temp = list(dados)
    resultado = []
    for _ in range(previsoes):
        media = round(sum(dados_temp[-janela:]) / janela, 2)
        resultado.append(media)
        dados_temp.append(media)
    return resultado

if st.button("🚀 Gerar previsão", use_container_width=True):
    try:
        dados = [float(x.strip()) for x in dados_texto.split(",") if x.strip()]
        if not produto:
            st.error("Informe o nome do produto.")
            st.stop()
        if len(dados) < 8 or len(dados) > 12:
            st.error("Informe entre 8 e 12 valores de demanda.")
            st.stop()

        previsao = media_movel_simples(dados)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Histórico")
            df_hist = pd.DataFrame({"Semana": range(1, len(dados)+1), "Demanda": dados})
            st.dataframe(df_hist, use_container_width=True)
        with col2:
            st.subheader("Previsão")
            df_prev = pd.DataFrame({"Semana": range(len(dados)+1, len(dados)+5), "Previsão": previsao})
            st.dataframe(df_prev, use_container_width=True)

        st.subheader("📈 Histórico x Previsão")
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(df_hist["Semana"], df_hist["Demanda"], marker="o", linewidth=2, label="Histórico")
        ax.plot(df_prev["Semana"], df_prev["Previsão"], marker="o", linewidth=2, label="Previsão")
        ax.set_xlabel("Semana")
        ax.set_ylabel("Demanda")
        ax.grid(True, alpha=0.3)
        ax.legend()
        st.pyplot(fig)

        media_hist = sum(dados)/len(dados)
        media_prev = sum(previsao)/len(previsao)

        st.subheader("📋 Recomendação Gerencial")
        if media_prev > media_hist:
            st.success("A previsão indica aumento da demanda. Recomenda-se aumentar as compras de armações.")
        elif media_prev < media_hist:
            st.warning("A previsão indica redução da demanda. Recomenda-se reduzir as compras para evitar excesso de estoque.")
        else:
            st.info("A demanda prevista é semelhante ao histórico. Recomenda-se manter o planejamento atual.")
    except ValueError:
        st.error("Digite apenas números separados por vírgula.")
