import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# CONFIGURAÇÃO DA PÁGINA
# ==========================

st.set_page_config(
    page_title="Previsão de Demanda - Veneziana Óculos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Previsor de Demanda Semanal")
st.subheader("Veneziana Óculos")

st.info(
    "Este aplicativo utiliza métodos simples de previsão de demanda para auxiliar "
    "o planejamento de compras de armações de óculos."
)

st.divider()

# ==========================
# ENTRADA DOS DADOS
# ==========================

col1, col2 = st.columns(2)

with col1:
    produto = st.text_input(
        "Nome do produto",
        placeholder="Ex.: Armação de Óculos"
    )

with col2:
    semanas_futuras = 4
    st.metric("Semanas previstas", semanas_futuras)

dados_texto = st.text_area(
    "Demandas históricas (entre 8 e 12 semanas)",
    placeholder="120,125,130,128,135,140,138,142",
    height=120
)

# ==========================
# FUNÇÕES
# ==========================

def media_movel_simples(dados, janela=3, previsoes=4):
    dados_temp = list(dados)
    resultado = []

    for _ in range(previsoes):
        media = round(sum(dados_temp[-janela:]) / janela, 2)
        resultado.append(media)
        dados_temp.append(media)

    return resultado


def suavizacao_exponencial(dados, alfa=0.30, previsoes=4):
    suavizado = dados[0]

    for valor in dados[1:]:
        suavizado = alfa * valor + (1 - alfa) * suavizado

    return [round(suavizado, 2) for _ in range(previsoes)]


def regressao_linear(dados, previsoes=4):
    n = len(dados)

    media_x = sum(range(n)) / n
    media_y = sum(dados) / n

    numerador = sum(
        (i - media_x) * (dados[i] - media_y)
        for i in range(n)
    )

    denominador = sum(
        (i - media_x) ** 2
        for i in range(n)
    )

    b = numerador / denominador if denominador != 0 else 0
    a = media_y - b * media_x

    return [
        round(a + b * (n + i), 2)
        for i in range(previsoes)
    ]


def calcular_mae(reais, previstos):
    erros = [abs(r - p) for r, p in zip(reais, previstos)]
    return round(sum(erros) / len(erros), 2)


# ==========================
# BOTÃO
# ==========================

if st.button("🚀 Gerar Previsão", use_container_width=True):

    try:

        # --------------------------
        # TRATAMENTO DOS DADOS
        # --------------------------

        dados = [
            float(valor.strip())
            for valor in dados_texto.split(",")
            if valor.strip()
        ]

        # VALIDAÇÕES
        if produto.strip() == "":
            st.error("Informe o nome do produto.")
            st.stop()

        if len(dados) < 8 or len(dados) > 12:
            st.error("Informe entre 8 e 12 valores de demanda.")
            st.stop()

        if any(v < 0 for v in dados):
            st.error("A demanda não pode conter valores negativos.")
            st.stop()

        media = sum(dados) / len(dados)
        amplitude = max(dados) - min(dados)

        if amplitude > media * 0.40:
            st.warning(
                "Os dados apresentam grande variação. "
                "A previsão pode ser menos confiável."
            )

        # --------------------------
        # PREVISÕES
        # --------------------------

        previsao_mm = media_movel_simples(dados)
        previsao_se = suavizacao_exponencial(dados)
        previsao_rl = regressao_linear(dados)

        # --------------------------
        # TABELAS
        # --------------------------

        df_historico = pd.DataFrame({
            "Semana": list(range(1, len(dados) + 1)),
            "Demanda": dados
        })

        df_previsao = pd.DataFrame({
            "Semana": list(range(len(dados) + 1, len(dados) + 1 + semanas_futuras)),
            "Média Móvel": previsao_mm,
            "Suavização Exponencial": previsao_se,
            "Regressão Linear": previsao_rl
        })

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Histórico")
            st.dataframe(df_historico, use_container_width=True)

        with col2:
            st.subheader("🔮 Previsão")
            st.dataframe(df_previsao, use_container_width=True)

        # --------------------------
        # MAE (avaliação)
        # --------------------------

        reais = dados[3:]

        mm_hist = [sum(dados[i-3:i]) / 3 for i in range(3, len(dados))]

        alfa = 0.30
        suavizado = dados[0]
        se_hist = []

        for v in dados[1:]:
            suavizado = alfa * v + (1 - alfa) * suavizado
            se_hist.append(suavizado)

        se_hist = se_hist[2:]

        rl_hist = []

        for i in range(3, len(dados)):
            parcial = dados[:i]
            n = len(parcial)

            mx = sum(range(n)) / n
            my = sum(parcial) / n

            num = sum((x - mx) * (parcial[x] - my) for x in range(n))
            den = sum((x - mx) ** 2 for x in range(n))

            b = num / den if den != 0 else 0
            a = my - b * mx

            rl_hist.append(a + b * n)

        mae_mm = calcular_mae(reais, mm_hist)
        mae_se = calcular_mae(reais, se_hist)
        mae_rl = calcular_mae(reais, rl_hist)

        df_mae = pd.DataFrame({
            "Método": [
                "Média Móvel",
                "Suavização Exponencial",
                "Regressão Linear"
            ],
            "MAE": [
                mae_mm,
                mae_se,
                mae_rl
            ]
        })

        melhor = df_mae.loc[df_mae["MAE"].idxmin(), "Método"]

        st.divider()
        st.subheader("📊 Comparação dos Métodos")
        st.dataframe(df_mae, use_container_width=True)

        st.success(f"Melhor método: **{melhor}**")

        # --------------------------
        # GRÁFICO
        # --------------------------

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(df_historico["Semana"], df_historico["Demanda"], marker="o", label="Histórico")
        ax.plot(df_previsao["Semana"], df_previsao["Média Móvel"], marker="o", label="Média Móvel")

        ax.set_title(f"Previsão de Demanda - {produto}")
        ax.set_xlabel("Semana")
        ax.set_ylabel("Demanda")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()

        st.pyplot(fig)

        # --------------------------
        # RECOMENDAÇÃO
        # --------------------------

        media_hist = sum(dados) / len(dados)
        media_prev = sum(previsao_mm) / len(previsao_mm)

        st.divider()
        st.subheader("📌 Recomendação")

        if media_prev > media_hist:
            st.success("Tendência de aumento de demanda → aumentar estoque.")
        elif media_prev < media_hist:
            st.warning("Tendência de queda → reduzir compras.")
        else:
            st.info("Demanda estável → manter planejamento.")

        # --------------------------
        # RESUMO
        # --------------------------

        st.divider()
        st.subheader("📊 Resumo")

        col1, col2, col3 = st.columns(3)

        col1.metric("Média Histórica", f"{media_hist:.2f}")
        col2.metric("Média Prevista", f"{media_prev:.2f}")
        col3.metric("Melhor Método", melhor)

    except ValueError:
        st.error("Use apenas números separados por vírgula.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
