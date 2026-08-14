import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="REME 2026",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# VISUAL — FORÇAR TEMA CLARO E DEIXAR APP LIMPO
# ============================================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: light !important;
    }

    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .stApp {
        background: #ffffff !important;
        color: #111827 !important;
    }

    [data-testid="stHeader"] {
        background: rgba(255,255,255,0) !important;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label, span {
        color: #111827;
    }

/* =========================================
   ABAS DESAFIO 1 / DESAFIO 2
   ========================================= */

/* Cada aba ocupa metade da largura */
div[data-baseweb="tab-list"] {
    gap: 8px !important;
    width: 100% !important;
}

/* Botão inteiro */
div[data-baseweb="tab-list"] button {
    flex: 1 1 50% !important;
    min-height: 60px !important;
    padding: 14px 20px !important;
}

/* Texto da aba */
div[data-baseweb="tab-list"] button div[data-testid="stMarkdownContainer"] p {
    font-size: 22px !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
}

/* CELULAR */
@media screen and (max-width: 768px) {

    div[data-baseweb="tab-list"] {
        width: 100% !important;
        gap: 4px !important;
    }

    div[data-baseweb="tab-list"] button {
        flex: 1 1 50% !important;
        min-width: 0 !important;
        min-height: 64px !important;
        padding: 12px 8px !important;
    }

    div[data-baseweb="tab-list"] button div[data-testid="stMarkdownContainer"] p {
        font-size: 21px !important;
        font-weight: 800 !important;
    }
}

    /* Tabela HTML sem toolbar */
    .table-wrap {
        width: 100%;
        overflow-x: auto;
        margin-top: 0.8rem;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
    }

    table.clean-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        font-size: 14px;
    }

    table.clean-table th {
        background: #f3f4f6;
        color: #111827;
        padding: 12px 14px;
        text-align: left;
        border-bottom: 1px solid #d1d5db;
        white-space: nowrap;
    }

    table.clean-table td {
        color: #111827;
        padding: 12px 14px;
        border-bottom: 1px solid #e5e7eb;
        white-space: nowrap;
    }

    table.clean-table tr:last-child td {
        border-bottom: none;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-top: 1rem;
        }

        h1 {
            font-size: 1.7rem !important;
        }

        table.clean-table {
            font-size: 12px;
        }

        table.clean-table th,
        table.clean-table td {
            padding: 8px 9px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


def show_html_table(df):
    html = df.to_html(
        index=False,
        classes="clean-table",
        border=0,
        escape=False
    )
    st.markdown(
        f'<div class="table-wrap">{html}</div>',
        unsafe_allow_html=True
    )


# ============================================================
# MENU SUPERIOR
# ============================================================

tab1, tab2 = st.tabs(["Desafio 1", "Desafio 2"])


# ============================================================
# DESAFIO 1
# ============================================================

with tab1:

    st.title("Desafio 1 — Pontos de Mobilização")

    # --------------------------------------------------------
    # Arquivos
    # --------------------------------------------------------

    dados = pd.read_csv("instancia_localizacao_OFICINA.csv")
    atribuicoes = pd.read_csv("atribuicoes.csv")

    nos = (
        dados[
            [
                "ID_Origem",
                "Logradouro",
                "Bairro",
                "Latitude",
                "Longitude",
                "Frequencia_Acidentes"
            ]
        ]
        .drop_duplicates(subset="ID_Origem")
        .copy()
    )

    nos_acidentes = nos[
        nos["Frequencia_Acidentes"] > 0
    ].copy()

    pontos_finais = [86, 98, 210, 227, 440]

    # --------------------------------------------------------
    # Mapa interativo
    # --------------------------------------------------------

    fig1 = go.Figure()

    for mobilizacao in pontos_finais:

        pontos_mob = atribuicoes[
            atribuicoes["mobilizacao"] == mobilizacao
        ].copy()

        info = nos_acidentes[
            nos_acidentes["ID_Origem"].isin(
                pontos_mob["ponto_acidente"]
            )
        ].copy()

        info = info.merge(
            pontos_mob[
                ["ponto_acidente", "distancia_metros"]
            ],
            left_on="ID_Origem",
            right_on="ponto_acidente",
            how="left"
        )

        hover = [
            (
                f"<b>Ponto {int(row.ID_Origem)}</b><br>"
                f"{row.Logradouro}<br>"
                f"{row.Bairro}<br>"
                f"Acidentes: {int(row.Frequencia_Acidentes)}<br>"
                f"Mobilização: {mobilizacao}<br>"
                f"Distância: {row.distancia_metros/1000:.2f} km"
            )
            for _, row in info.iterrows()
        ]

        fig1.add_trace(
            go.Scattermap(
                lat=info["Latitude"],
                lon=info["Longitude"],
                mode="markers",
                marker=dict(
                    size=info["Frequencia_Acidentes"] * 2 + 5,
                    opacity=0.65
                ),
                text=hover,
                hoverinfo="text",
                showlegend=False
            )
        )

    centros = nos_acidentes[
        nos_acidentes["ID_Origem"].isin(pontos_finais)
    ].copy()

    hover_centros = [
        (
            f"<b>Mobilização {int(row.ID_Origem)}</b><br>"
            f"{row.Logradouro}<br>"
            f"{row.Bairro}"
        )
        for _, row in centros.iterrows()
    ]

    fig1.add_trace(
        go.Scattermap(
            lat=centros["Latitude"],
            lon=centros["Longitude"],
            mode="markers+text",
            marker=dict(
                size=22,
                symbol="star"
            ),
            text=centros["ID_Origem"].astype(int).astype(str),
            textposition="top center",
            hovertext=hover_centros,
            hoverinfo="text",
            showlegend=False
        )
    )

    fig1.update_layout(
        height=720,
        showlegend=False,
        map=dict(
            style="open-street-map",
            center=dict(
                lat=nos_acidentes["Latitude"].mean(),
                lon=nos_acidentes["Longitude"].mean()
            ),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=5, b=0),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": True
        }
    )

    # --------------------------------------------------------
    # Resumo
    # --------------------------------------------------------

    st.subheader("Resumo das mobilizações")

    resumo = (
        atribuicoes
        .groupby("mobilizacao")
        .agg(
            pontos_atendidos=("ponto_acidente", "count"),
            acidentes_atendidos=("frequencia_acidentes", "sum"),
            distancia_total_metros=("distancia_metros", "sum")
        )
        .reset_index()
    )

    info_centros = centros[
        ["ID_Origem", "Logradouro", "Bairro"]
    ].rename(columns={"ID_Origem": "mobilizacao"})

    resumo = resumo.merge(
        info_centros,
        on="mobilizacao",
        how="left"
    )

    resumo["Distância total (km)"] = (
        resumo["distancia_total_metros"] / 1000
    ).round(2)

    resumo["acidentes_atendidos"] = (
        resumo["acidentes_atendidos"].astype(int)
    )

    resumo = resumo[
        [
            "mobilizacao",
            "Logradouro",
            "Bairro",
            "pontos_atendidos",
            "acidentes_atendidos",
            "Distância total (km)"
        ]
    ]

    resumo.columns = [
        "Mobilização",
        "Logradouro",
        "Bairro",
        "Pontos atendidos",
        "Acidentes atendidos",
        "Distância total (km)"
    ]

    show_html_table(resumo)


# ============================================================
# DESAFIO 2
# ============================================================

with tab2:

    st.title("Desafio 2 — Rota Recomendada")

    # --------------------------------------------------------
    # Arquivos finais da versão do ZIP
    # --------------------------------------------------------

    malha2 = pd.read_csv(
        "instancia_rotas_OFICINA_versao2.csv"
    )

    caminho = pd.read_csv(
        "caminho_recomendado.csv"
    )

    decomposicao = pd.read_csv(
        "decomposicao_recomendada.csv"
    )

    selecao = pd.read_csv(
        "selecao_principal.csv"
    )

    # Uma linha por nó com coordenadas
    coords2 = (
        malha2[
            ["ID_Origem", "Logradouro", "Latitude", "Longitude", "Indice_Periculosidade"]
        ]
        .drop_duplicates(subset="ID_Origem")
        .copy()
    )

    # --------------------------------------------------------
    # Coordenadas da rota J140 na ordem correta
    # --------------------------------------------------------

    rota = caminho.merge(
        coords2,
        left_on="No",
        right_on="ID_Origem",
        how="left"
    ).sort_values("Ordem")

    # --------------------------------------------------------
    # Informações da solução recomendada
    # --------------------------------------------------------

    rec = selecao[
        selecao["Solucao"] == "Recomendada (joelho)"
    ].iloc[0]

    # --------------------------------------------------------
    # Mapa interativo da rota recomendada
    # --------------------------------------------------------

    fig2 = go.Figure()

    # Rota completa
    fig2.add_trace(
        go.Scattermap(
            lat=rota["Latitude"],
            lon=rota["Longitude"],
            mode="lines",
            line=dict(width=5),
            text=[
                (
                    f"Nó: {int(row.No)}<br>"
                    f"{row.Logradouro}<br>"
                    f"Risco do nó: {row.Indice_Periculosidade:g}"
                )
                for _, row in rota.iterrows()
            ],
            hoverinfo="text",
            showlegend=False
        )
    )

    # Pontos-chave: Casa, UFU e Hospital
    pontos_chave = pd.DataFrame({
        "No": [924, 1810, 1350],
        "Nome": ["Casa", "UFU", "Hospital"]
    }).merge(
        coords2,
        left_on="No",
        right_on="ID_Origem",
        how="left"
    )

    fig2.add_trace(
        go.Scattermap(
            lat=pontos_chave["Latitude"],
            lon=pontos_chave["Longitude"],
            mode="markers+text",
            marker=dict(
                size=20,
                symbol="star"
            ),
            text=[
                f"{nome} ({no})"
                for nome, no in zip(
                    pontos_chave["Nome"],
                    pontos_chave["No"]
                )
            ],
            textposition="top center",
            hovertext=[
                (
                    f"<b>{row.Nome} ({int(row.No)})</b><br>"
                    f"{row.Logradouro}"
                )
                for _, row in pontos_chave.iterrows()
            ],
            hoverinfo="text",
            showlegend=False
        )
    )

    fig2.update_layout(
        height=720,
        showlegend=False,
        map=dict(
            style="open-street-map",
            center=dict(
                lat=rota["Latitude"].mean(),
                lon=rota["Longitude"].mean()
            ),
            zoom=12
        ),
        margin=dict(l=0, r=0, t=5, b=0),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": True
        }
    )

    # --------------------------------------------------------
    # Decomposição por trecho
    # --------------------------------------------------------

    st.subheader("Decomposição da jornada por trecho")

    tabela_trechos = decomposicao[
        [
            "Trecho",
            "Pareto_ID",
            "Distancia_km",
            "Risco_acumulado",
            "Risco_maximo"
        ]
    ].copy()

    tabela_trechos["Distancia_km"] = (
        tabela_trechos["Distancia_km"].round(3)
    )

    tabela_trechos["Risco_acumulado"] = (
        tabela_trechos["Risco_acumulado"].astype(int)
    )

    tabela_trechos["Risco_maximo"] = (
        tabela_trechos["Risco_maximo"].astype(int)
    )

    tabela_trechos.columns = [
        "Trecho",
        "ID Pareto",
        "Distância (km)",
        "Risco acumulado",
        "Risco máximo"
    ]

    # Linha total
    total = pd.DataFrame({
        "Trecho": ["Jornada Total"],
        "ID Pareto": [rec["Jornada_Pareto_ID"]],
        "Distância (km)": [round(float(rec["Distancia_km"]), 3)],
        "Risco acumulado": [int(rec["Risco_acumulado"])],
        "Risco máximo": [int(rec["Risco_maximo"])]
    })

    tabela_trechos = pd.concat(
        [tabela_trechos, total],
        ignore_index=True
    )

    show_html_table(tabela_trechos)
