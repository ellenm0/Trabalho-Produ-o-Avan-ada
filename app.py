```python
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

    resultado = []

    for _ in range(previsoes):

        resultado.append(round(suavizado, 2))

    return resultado


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

    if denominador == 0:

        b = 0

    else:

        b = numerador / denominador

    a = media_y - b * media_x

    resultado = []

    for i in range(previsoes):

        resultado.append(round(a + b * (n + i), 2))

    return resultado


def calcular_mae(reais, previstos):

    erros = []

    for real, previsto in zip(reais, previstos):

        erros.append(abs(real - previsto))

    return round(sum(erros) / len(erros), 2)


# ==========================
# BOTÃO
# ==========================

if st.button(
    "🚀 Gerar Previsão",
    use_container_width=True
):

    try:

        dados = [
            float(valor.strip())
            for valor in dados_texto.split(",")
            if valor.strip()
        ]

        # --------------------------
        # VALIDAÇÕES
        # --------------------------

        if produto.strip() == "":

            st.error("Informe o nome do produto.")

            st.stop()

        if len(dados) < 8 or len(dados) > 12:

            st.error(
                "Informe entre 8 e 12 valores de demanda."
            )

            st.stop()

        if any(valor < 0 for valor in dados):

            st.error(
                "A demanda não pode conter valores negativos."
            )

            st.stop()

        media = sum(dados) / len(dados)

        amplitude = max(dados) - min(dados)

        if amplitude > media * 0.40:

            st.warning(
                "Os dados apresentam grande variação. "
                "A previsão pode possuir menor confiabilidade."
            )

        # --------------------------
        # CÁLCULO DOS MÉTODOS
        # --------------------------

        previsao_mm = media_movel_simples(dados)

        previsao_se = suavizacao_exponencial(dados)

        previsao_rl = regressao_linear(dados)

               # ==========================================
        # TABELAS
        # ==========================================

        df_historico = pd.DataFrame({
            "Semana": list(range(1, len(dados) + 1)),
            "Demanda": dados
        })

        df_previsao = pd.DataFrame({
            "Semana": list(
                range(
                    len(dados) + 1,
                    len(dados) + 1 + semanas_futuras
                )
            ),
            "Média Móvel": previsao_mm,
            "Suavização Exponencial": previsao_se,
            "Regressão Linear": previsao_rl
        })

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("📋 Histórico de Demanda")

            st.dataframe(
                df_historico,
                use_container_width=True
            )

        with col2:

            st.subheader("🔮 Previsões")

            st.dataframe(
                df_previsao,
                use_container_width=True
            )

        # ==========================================
        # COMPARAÇÃO DOS MÉTODOS (MAE)
        # ==========================================

        reais = dados[3:]

        # Média Móvel

        mm_historico = []

        for i in range(3, len(dados)):

            media = sum(dados[i-3:i]) / 3

            mm_historico.append(media)

        # Suavização Exponencial

        se_historico = []

        alfa = 0.30

        suavizado = dados[0]

        for valor in dados[1:]:

            suavizado = alfa * valor + (1 - alfa) * suavizado

            se_historico.append(suavizado)

        se_historico = se_historico[2:]

       # Regressão Linear
rl_historico = []

for i in range(3, len(dados)):

    dados_parciais = dados[:i]

    n = len(dados_parciais)

    media_x = sum(range(n)) / n
    media_y = sum(dados_parciais) / n

    numerador = sum(
        (x - media_x) * (dados_parciais[x] - media_y)
        for x in range(n)
    )

    denominador = sum(
        (x - media_x) ** 2
        for x in range(n)
    )

    if denominador == 0:
        b = 0
    else:
        b = numerador / denominador

    a = media_y - b * media_x

    previsao = a + b * n

    rl_historico.append(previsao)

        mae_mm = calcular_mae(
            reais,
            mm_historico
        )

        mae_se = calcular_mae(
            reais,
            se_historico
        )

        mae_rl = calcular_mae(
            reais,
            rl_historico
        )

        df_mae = pd.DataFrame({

            "Método": [

                "Média Móvel Simples",

                "Suavização Exponencial",

                "Regressão Linear"

            ],

            "MAE": [

                round(mae_mm,2),

                round(mae_se,2),

                round(mae_rl,2)

            ]

        })

        melhor_metodo = df_mae.loc[
            df_mae["MAE"].idxmin(),
            "Método"
        ]

        menor_erro = df_mae["MAE"].min()

        st.divider()

        st.subheader("📊 Comparação dos Métodos")

        st.dataframe(
            df_mae,
            use_container_width=True
        )

        st.success(

            f"Melhor método para estes dados: "
            f"**{melhor_metodo}** "
            f"(MAE = {menor_erro:.2f})"

        )

        # ==========================================
        # ESCOLHA DO MÉTODO PARA O GRÁFICO
        # (mantém a Média Móvel como principal)
        # ==========================================

        previsao = previsao_mm

                # ==========================================
        # GRÁFICO
        # ==========================================

        st.divider()

        st.subheader("📈 Histórico x Previsão")

        fig, ax = plt.subplots(figsize=(10,5))

        ax.plot(
            df_historico["Semana"],
            df_historico["Demanda"],
            marker="o",
            linewidth=2,
            label="Histórico"
        )

        ax.plot(
            df_previsao["Semana"],
            df_previsao["Média Móvel"],
            marker="o",
            linewidth=2,
            label="Média Móvel"
        )

        ax.set_xlabel("Semana")

        ax.set_ylabel("Demanda")

        ax.set_title(f"Previsão de Demanda - {produto}")

        ax.grid(True, linestyle="--", alpha=0.4)

        ax.legend()

        st.pyplot(fig)

        # ==========================================
        # RECOMENDAÇÃO GERENCIAL
        # ==========================================

        media_historica = sum(dados) / len(dados)

        media_prevista = sum(previsao) / len(previsao)

        st.divider()

        st.subheader("📌 Recomendação Gerencial")

        if media_prevista > media_historica:

            st.success(
                "A previsão indica aumento da demanda. "
                "Recomenda-se aumentar as compras de armações "
                "para evitar falta de estoque."
            )

        elif media_prevista < media_historica:

            st.warning(
                "A previsão indica redução da demanda. "
                "Recomenda-se reduzir as compras para evitar "
                "excesso de estoque."
            )

        else:

            st.info(
                "A demanda prevista permanece semelhante "
                "ao histórico. Recomenda-se manter o "
                "planejamento atual."
            )

        # ==========================================
        # MÉTRICAS RESUMIDAS
        # ==========================================

        st.divider()

        st.subheader("📊 Resumo")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Média Histórica",
                f"{media_historica:.2f}"
            )

        with col2:

            st.metric(
                "Média Prevista",
                f"{media_prevista:.2f}"
            )

        with col3:

            st.metric(
                "Melhor Método",
                melhor_metodo
            )

    except ValueError:

        st.error(
            "Erro no preenchimento. Informe apenas números "
            "separados por vírgula.\n\n"
            "Exemplo:\n"
            "120,125,130,128,135,140,145,150"
        )

    except Exception as erro:

        st.error(
            f"Ocorreu um erro inesperado:\n\n{erro}"
        )
