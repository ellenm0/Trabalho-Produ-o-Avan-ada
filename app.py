import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# CONFIGURAÇÃO
# ==========================

st.set_page_config(
    page_title="Previsão de Demanda - Veneziana Óculos",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Previsor de Demanda Semanal")
st.subheader("Veneziana Óculos")

st.info(
    "Ferramenta de previsão de demanda usando múltiplos modelos estatísticos "
    "para apoio ao planejamento de estoque."
)

st.divider()

# ==========================
# ENTRADA
# ==========================

col1, col2 = st.columns(2)

with col1:
    produto = st.text_input("Nome do produto", placeholder="Ex.: Armação de Óculos")

with col2:
    semanas_futuras = 4
    st.metric("Semanas previstas", semanas_futuras)

dados_texto = st.text_area(
    "Demandas históricas (8 a 12 semanas)",
    placeholder="120,125,130,128,135,140,138,142",
    height=120
)

# ==========================
# FUNÇÕES
# ==========================

def media_movel(dados, janela=3, previsoes=4):
    temp = list(dados)
    resultado = []

    for _ in range(previsoes):
        media = sum(temp[-janela:]) / janela
        resultado.append(round(media, 2))
        temp.append(media)

    return resultado


def suavizacao_exponencial(dados, alfa=0.30, previsoes=4):
    s = dados[0]

    for v in dados[1:]:
        s = alfa * v + (1 - alfa) * s

    return [round(s, 2)] * previsoes


def regressao_linear(dados, previsoes=4):
    n = len(dados)

    mx = sum(range(n)) / n
    my = sum(dados) / n

    num = sum((i - mx) * (dados[i] - my) for i in range(n))
    den = sum((i - mx) ** 2 for i in range(n))

    b = num / den if den != 0 else 0
    a = my - b * mx

    return [round(a + b * (n + i), 2) for i in range(previsoes)]


def mae(real, pred):
    return round(sum(abs(r - p) for r, p in zip(real, pred)) / len(real), 2)

# ==========================
# EXECUÇÃO
# ==========================

if st.button("🚀 Gerar Previsão", use_container_width=True):

    try:
        dados = [
            float(x.strip())
            for x in dados_texto.split(",")
            if x.strip()
        ]

        # --------------------------
        # VALIDAÇÕES
        # --------------------------

        if not produto.strip():
            st.error("Informe o nome do produto.")
            st.stop()

        if len(dados) < 8 or len(dados) > 12:
            st.error("Informe entre 8 e 12 valores.")
            st.stop()

        if any(x < 0 for x in dados):
            st.error("Valores negativos não são permitidos.")
            st.stop()

        media_hist = sum(dados) / len(dados)

        if (max(dados) - min(dados)) > media_hist * 0.4:
            st.warning("Alta variação nos dados → menor confiabilidade.")

        # --------------------------
        # MODELOS
        # --------------------------

        mm = media_movel(dados)
        se = suavizacao_exponencial(dados)
        rl = regressao_linear(dados)

        # --------------------------
        # MAE (backtesting)
        # --------------------------

        reais = dados[3:]

        mm_hist = [sum(dados[i-3:i]) / 3 for i in range(3, len(dados))]

        s = dados[0]
        se_hist = []
        for v in dados[1:]:
            s = 0.3 * v + 0.7 * s
            se_hist.append(s)
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

        mae_mm = mae(reais, mm_hist)
        mae_se = mae(reais, se_hist)
        mae_rl = mae(reais, rl_hist)

        df_mae = pd.DataFrame({
            "Modelo": ["Média Móvel", "Suavização Exponencial", "Regressão Linear"],
            "MAE": [mae_mm, mae_se, mae_rl]
        })

        melhor = df_mae.loc[df_mae["MAE"].idxmin(), "Modelo"]

        # --------------------------
        # ESCOLHA AUTOMÁTICA
        # --------------------------

        previsoes = {
            "Média Móvel": mm,
            "Suavização Exponencial": se,
            "Regressão Linear": rl
        }

        previsao_final = previsoes[melhor]

        semanas = list(range(len(dados) + 1, len(dados) + 1 + semanas_futuras))

        df_hist = pd.DataFrame({
            "Semana": range(1, len(dados) + 1),
            "Demanda": dados
        })

        df_prev = pd.DataFrame({
            "Semana": semanas,
            f"Previsão ({melhor})": previsao_final
        })

        # ==========================
        # EXIBIÇÃO
        # ==========================

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Histórico")
            st.dataframe(df_hist, use_container_width=True)

        with col2:
            st.subheader("🔮 Previsão (Modelo recomendado)")
            st.dataframe(df_prev, use_container_width=True)

        # --------------------------
        # COMPARAÇÃO
        # --------------------------

        st.divider()
        st.subheader("📊 Comparação dos Modelos")
        st.dataframe(df_mae, use_container_width=True)

        st.success(f"Melhor modelo: **{melhor}**")

        # --------------------------
        # GRÁFICO
        # --------------------------

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(df_hist["Semana"], df_hist["Demanda"], marker="o", label="Histórico")
        ax.plot(semanas, previsao_final, marker="o", label=f"Previsão ({melhor})")

        ax.set_title(f"Previsão de Demanda - {produto}")
        ax.set_xlabel("Semana")
        ax.set_ylabel("Demanda")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()

        st.pyplot(fig)

        # --------------------------
        # RECOMENDAÇÃO
        # --------------------------

        media_prev = sum(previsao_final) / len(previsao_final)

        st.divider()
        st.subheader("📌 Recomendação Gerencial")

        if media_prev > media_hist:
            st.success("Tendência de aumento → aumentar estoque.")
        elif media_prev < media_hist:
            st.warning("Tendência de queda → reduzir compras.")
        else:
            st.info("Estabilidade → manter estratégia atual.")

        # --------------------------
        # RESUMO
        # --------------------------

        st.divider()
        st.subheader("📊 Resumo")

        c1, c2, c3 = st.columns(3)

        c1.metric("Média Histórica", f"{media_hist:.2f}")
        c2.metric("Média Prevista", f"{media_prev:.2f}")
        c3.metric("Melhor Modelo", melhor)

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
