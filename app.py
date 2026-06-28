import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Previsão de Demanda - Veneziana Óculos",
    layout="centered"
)

st.title("📊 Previsão de Demanda Semanal")
st.subheader("Veneziana Óculos")

st.write(
    "Esta aplicação utiliza Média Móvel Simples (janela de 3 semanas) "
    "para prever a demanda de armações de óculos."
)

# Entrada do usuário
produto = st.text_input("Nome do produto")

dados_texto = st.text_area(
    "Insira os dados históricos de demanda (8 a 12 semanas, separados por vírgula)",
    placeholder="Ex: 120, 125, 130, 128, 135, 140, 138, 142"
)

def media_movel_simples(dados, janela=3, previsoes=4):
    # CORREÇÃO: Jeito correto de copiar uma lista no Python
    dados_temp = list(dados) 
    resultado = []

    for _ in range(previsoes):
        if len(dados_temp) < janela:
            break

        media = sum(dados_temp[-janela:]) / janela
        media = round(media, 2)

        resultado.append(media)
        dados_temp.append(media)

    return resultado

if st.button("Gerar previsão"):

    try:
        # Transformar texto em lista de números
        dados = [float(x.strip()) for x in dados_texto.split(",") if x.strip()]

        # Validação simples
        if len(dados) < 8 or len(dados) > 12:
            st.error("Insira entre 8 e 12 valores de demanda.")
        else:

            previsao = media_movel_simples(dados)

            # Criar tabelas
            df_hist = pd.DataFrame({
                "Semana": list(range(1, len(dados) + 1)),
                "Demanda": dados
            })

            df_prev = pd.DataFrame({
                "Semana": list(range(len(dados) + 1, len(dados) + 1 + len(previsao))),
                "Previsão": previsao
            })

            st.subheader("📌 Histórico de Demanda")
            st.dataframe(df_hist)

            st.subheader("📌 Previsão (4 semanas)")
            st.dataframe(df_prev)

            # Gráfico
            st.subheader("📈 Histórico vs Previsão")

            fig, ax = plt.subplots()

            ax.plot(df_hist["Semana"], df_hist["Demanda"], marker="o", label="Histórico")
            ax.plot(df_prev["Semana"], df_prev["Previsão"], marker="o", label="Previsão")

            ax.set_xlabel("Semana")
            ax.set_ylabel("Demanda")
            ax.legend()
            ax.grid(True)

            st.pyplot(fig)

            # Recomendação simples
            tendencia = previsao[-1] - previsao[0] if len(previsao) > 1 else 0

            st.subheader("📌 Recomendação gerencial")

            if tendencia > 5:
                st.success("Tendência de crescimento. Aumentar estoque de armações.")
            elif tendencia < -5:
                st.warning("Tendência de queda. Reduzir compras para evitar excesso de estoque.")
            else:
                st.info("Demanda estável. Manter estratégia atual de estoque.")

    except ValueError:
        st.error("Verifique se os valores foram inseridos corretamente (apenas números separados por vírgula).")