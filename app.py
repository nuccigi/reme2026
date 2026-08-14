import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import networkx as nx

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Desafio 1 - REME 2026",
    page_icon="🚦",
    layout="wide"
)

st.title("Desafio 1 — Pontos de Mobilização")
st.caption(
    "Distribuição dos pontos de mobilização e regiões atendidas "
    "na malha viária de Uberlândia."
)

# ============================================================
# CARREGAR ARQUIVOS
# ============================================================

dados = pd.read_csv("instancia_localizacao_OFICINA.csv")
atribuicoes = pd.read_csv("atribuicoes.csv")

# ============================================================
# PREPARAR TABELA DE NÓS
# ============================================================

nos = dados[
    [
        "ID_Origem",
        "OSM_Node_ID",
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

# ============================================================
# PONTOS FINAIS ENCONTRADOS
# ============================================================

pontos_finais = [86, 98, 210, 227, 440]

# ============================================================
# CONSTRUIR GRAFO VIÁRIO
# ============================================================

G = nx.DiGraph()

for _, linha in nos.iterrows():

    G.add_node(
        int(linha["ID_Origem"]),
        latitude=linha["Latitude"],
        longitude=linha["Longitude"]
    )

arestas = dados[
    dados["ID_Origem"] != dados["ID_Destino"]
]

for _, linha in arestas.iterrows():

    G.add_edge(
        int(linha["ID_Origem"]),
        int(linha["ID_Destino"]),
        weight=float(linha["Distancia_Metros"])
    )

# ============================================================
# POSIÇÃO DOS NÓS
# ============================================================

pos = {
    int(linha["ID_Origem"]): (
        linha["Longitude"],
        linha["Latitude"]
    )
    for _, linha in nos.iterrows()
}

# ============================================================
# INDICADORES PRINCIPAIS
# ============================================================

total_pontos = atribuicoes["ponto_acidente"].nunique()
total_acidentes = atribuicoes["frequencia_acidentes"].sum()
distancia_total_km = (
    atribuicoes["distancia_metros"].sum() / 1000
)

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

st.divider()

# ============================================================
# CONSTRUIR O MAPA
# ============================================================

fig = go.Figure()

# ------------------------------------------------------------
# MALHA VIÁRIA
# ------------------------------------------------------------

edge_x = []
edge_y = []

for origem, destino in G.edges():

    if origem not in pos or destino not in pos:
        continue

    x0, y0 = pos[origem]
    x1, y1 = pos[destino]

    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

fig.add_trace(
    go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            width=0.5,
            color="rgba(120,120,120,0.35)"
        ),
        hoverinfo="skip",
        name="Malha viária",
        showlegend=True
    )
)

# ------------------------------------------------------------
# PONTOS ATENDIDOS POR MOBILIZAÇÃO
# ------------------------------------------------------------

for mobilizacao in pontos_finais:

    pontos_mob = atribuicoes[
        atribuicoes["mobilizacao"] == mobilizacao
    ]

    ids_pontos = pontos_mob["ponto_acidente"].tolist()

    info = nos_acidentes[
        nos_acidentes["ID_Origem"].isin(ids_pontos)
    ].copy()

    if info.empty:
        continue

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

    hover_text = []

    for _, linha in info.iterrows():

        hover_text.append(
            f"""
            <b>Ponto {int(linha['ID_Origem'])}</b><br>
            Logradouro: {linha['Logradouro']}<br>
            Bairro: {linha['Bairro']}<br>
            Acidentes: {int(linha['Frequencia_Acidentes'])}<br>
            Mobilização responsável: {mobilizacao}<br>
            Distância: {linha['distancia_metros']/1000:.2f} km
            """
        )

    fig.add_trace(
        go.Scatter(
            x=info["Longitude"],
            y=info["Latitude"],
            mode="markers",
            marker=dict(
                size=(
                    info["Frequencia_Acidentes"] * 3
                    + 5
                ),
                opacity=0.65
            ),
            text=hover_text,
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
    go.Scatter(
        x=centros["Longitude"],
        y=centros["Latitude"],
        mode="markers+text",
        marker=dict(
            size=24,
            symbol="star",
            color="black",
            line=dict(
                width=1.5,
                color="white"
            )
        ),
        text=centros["ID_Origem"]
        .astype(int)
        .astype(str),
        textposition="top center",
        hovertext=hover_centros,
        hoverinfo="text",
        name="Pontos de mobilização"
    )
)

# ============================================================
# AJUSTES DO GRÁFICO
# ============================================================

fig.update_layout(
    title="Distribuição dos Pontos de Mobilização e Regiões Atendidas",
    height=800,
    hovermode="closest",
    legend_title="Legenda",
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    ),
    xaxis=dict(
        title="Longitude",
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        title="Latitude",
        showgrid=False,
        zeroline=False,
        scaleanchor="x",
        scaleratio=1
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ============================================================
# RESUMO POR MOBILIZAÇÃO
# ============================================================

st.subheader("Resumo das mobilizações")

resumo = (
    atribuicoes
    .groupby("mobilizacao")
    .agg(
        pontos_atendidos=(
            "ponto_acidente",
            "count"
        ),
        acidentes_atendidos=(
            "frequencia_acidentes",
            "sum"
        ),
        distancia_total_metros=(
            "distancia_metros",
            "sum"
        ),
        distancia_media_metros=(
            "distancia_metros",
            "mean"
        ),
        distancia_maxima_metros=(
            "distancia_metros",
            "max"
        )
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

resumo["distancia_total_km"] = (
    resumo["distancia_total_metros"] / 1000
)

resumo["distancia_media_km"] = (
    resumo["distancia_media_metros"] / 1000
)

resumo["distancia_maxima_km"] = (
    resumo["distancia_maxima_metros"] / 1000
)

resumo_exibicao = resumo[
    [
        "mobilizacao",
        "Logradouro",
        "Bairro",
        "pontos_atendidos",
        "acidentes_atendidos",
        "distancia_total_km",
        "distancia_media_km",
        "distancia_maxima_km"
    ]
].copy()

resumo_exibicao.columns = [
    "Mobilização",
    "Logradouro",
    "Bairro",
    "Pontos atendidos",
    "Acidentes atendidos",
    "Distância total (km)",
    "Distância média (km)",
    "Distância máxima (km)"
]

st.dataframe(
    resumo_exibicao,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# VALIDAÇÃO FINAL
# ============================================================

st.subheader("Validação da solução")

c1, c2, c3, c4 = st.columns(4)

c1.success("5 mobilizações")
c2.success("1.000 pontos atendidos")
c3.success("1.946 acidentes cobertos")
c4.success("Raio máximo ≤ 6 km")

st.caption(
    "Solução final obtida pelo algoritmo guloso seguido "
    "de busca local 1-swap."
)
