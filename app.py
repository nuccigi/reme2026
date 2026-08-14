import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Desafio 1 - Pontos de Mobilização",
    page_icon="🚦",
    layout="wide"
)

st.title("Desafio 1 — Pontos de Mobilização")

# ============================================================
# DADOS
# ============================================================

dados = pd.read_csv("instancia_localizacao_OFICINA.csv")
atribuicoes = pd.read_csv("atribuicoes.csv")

nos = dados[
    [
        "ID_Origem",
        "Logradouro",
        "Bairro",
        "Latitude",
        "Longitude",
        "Frequencia_Acidentes"
    ]
].drop_duplicates(subset="ID_Origem")

nos_acidentes = nos[
    nos["Frequencia_Acidentes"] > 0
].copy()

pontos_finais = [86, 98, 210, 227, 440]

# ============================================================
# CARDS
# ============================================================

total_pontos = atribuicoes["ponto_acidente"].nunique()
total_acidentes = atribuicoes["frequencia_acidentes"].sum()
distancia_total_km = atribuicoes["distancia_metros"].sum() / 1000

col1, col2, col3 = st.columns(3)

col1.metric(
    "Pontos atendidos",
    f"{int(total_pontos):,}".replace(",", ".")
)

col2.metric(
    "Acidentes cobertos",
    f"{int(total_acidentes):,}".replace(",", ".")
)

col3.metric(
    "Distância total",
    f"{distancia_total_km:,.2f} km"
    .replace(",", "X")
    .replace(".", ",")
    .replace("X", ".")
)

# ============================================================
# MAPA INTERATIVO
# ============================================================

fig = go.Figure()

# ------------------------------------------------------------
# PONTOS ATENDIDOS POR MOBILIZAÇÃO
# ------------------------------------------------------------

for mobilizacao in pontos_finais:

    pontos_mob = atribuicoes[
        atribuicoes["mobilizacao"] == mobilizacao
    ]

    info = nos_acidentes[
        nos_acidentes["ID_Origem"].isin(
            pontos_mob["ponto_acidente"]
        )
    ].copy()

    info = info.merge(
        pontos_mob[
            [
                "ponto_acidente",
                "distancia_metros"
            ]
        ],
        left_on="ID_Origem",
        right_on="ponto_acidente",
        how="left"
    )

    hover = []

    for _, linha in info.iterrows():

        hover.append(
            f"""
            <b>Ponto {int(linha['ID_Origem'])}</b><br>
            {linha['Logradouro']}<br>
            {linha['Bairro']}<br>
            Acidentes: {int(linha['Frequencia_Acidentes'])}<br>
            Mobilização: {mobilizacao}<br>
            Distância: {linha['distancia_metros']/1000:.2f} km
            """
        )

    fig.add_trace(
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
            name=f"Mobilização {mobilizacao}"
        )
    )

# ------------------------------------------------------------
# CENTROS DE MOBILIZAÇÃO
# ------------------------------------------------------------

centros = nos_acidentes[
    nos_acidentes["ID_Origem"].isin(pontos_finais)
].copy()

hover_centros = []

for _, linha in centros.iterrows():

    hover_centros.append(
        f"""
        <b>Mobilização {int(linha['ID_Origem'])}</b><br>
        {linha['Logradouro']}<br>
        {linha['Bairro']}
        """
    )

fig.add_trace(
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
        name="Pontos de mobilização"
    )
)

# ------------------------------------------------------------
# AJUSTES DO MAPA
# ------------------------------------------------------------

fig.update_layout(
    height=750,
    showlegend=False,
    map=dict(
        style="open-street-map",
        center=dict(
            lat=nos_acidentes["Latitude"].mean(),
            lon=nos_acidentes["Longitude"].mean()
        ),
        zoom=11
    ),
    margin=dict(
        l=0,
        r=0,
        t=20,
        b=0
    )
)
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)

# ============================================================
# RESUMO DAS MOBILIZAÇÕES
# ============================================================

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
    [
        "ID_Origem",
        "Logradouro",
        "Bairro"
    ]
].rename(
    columns={
        "ID_Origem": "mobilizacao"
    }
)

resumo = resumo.merge(
    info_centros,
    on="mobilizacao",
    how="left"
)

resumo["Distância total (km)"] = (
    resumo["distancia_total_metros"] / 1000
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

st.dataframe(
    resumo,
    use_container_width=True,
    hide_index=True
)
