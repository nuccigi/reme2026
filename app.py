import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Pontos de Mobilização e Regiões Atendidas")

fig = go.Figure()

# ----------------------------
# MALHA VIÁRIA
# ----------------------------

edge_x = []
edge_y = []

for origem, destino in G.edges():

    x0, y0 = pos[origem]
    x1, y1 = pos[destino]

    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

fig.add_trace(
    go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=0.5),
        opacity=0.25,
        hoverinfo="skip",
        name="Malha viária"
    )
)

# ----------------------------
# PONTOS ATENDIDOS
# ----------------------------

for mobilizacao in pontos_finais:

    pontos = atribuicoes[
        atribuicoes["mobilizacao"] == mobilizacao
    ]

    info = nos_acidentes[
        nos_acidentes["ID_Origem"].isin(
            pontos["ponto_acidente"]
        )
    ].copy()

    fig.add_trace(
        go.Scatter(
            x=info["Longitude"],
            y=info["Latitude"],
            mode="markers",
            marker=dict(
                size=info["Frequencia_Acidentes"] * 3 + 4,
                opacity=0.6
            ),
            text=[
                f"""
                Ponto: {int(row.ID_Origem)}<br>
                Logradouro: {row.Logradouro}<br>
                Bairro: {row.Bairro}<br>
                Acidentes: {int(row.Frequencia_Acidentes)}<br>
                Mobilização: {mobilizacao}
                """
                for _, row in info.iterrows()
            ],
            hoverinfo="text",
            name=f"Mobilização {mobilizacao}"
        )
    )

# ----------------------------
# CENTROS
# ----------------------------

centros = nos_acidentes[
    nos_acidentes["ID_Origem"].isin(pontos_finais)
]

fig.add_trace(
    go.Scatter(
        x=centros["Longitude"],
        y=centros["Latitude"],
        mode="markers+text",
        marker=dict(
            size=20,
            symbol="star",
            line=dict(width=1.5)
        ),
        text=centros["ID_Origem"].astype(int).astype(str),
        textposition="top center",
        name="Pontos de mobilização",
        hovertext=[
            f"{row.Logradouro} - {row.Bairro}"
            for _, row in centros.iterrows()
        ],
        hoverinfo="text"
    )
)

fig.update_layout(
    height=800,
    xaxis_title="Longitude",
    yaxis_title="Latitude",
    legend_title="Regiões atendidas",
    hovermode="closest"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------
# TABELA RESUMO
# ----------------------------

st.subheader("Resumo das mobilizações")

st.dataframe(
    resumo_mobilizacoes,
    use_container_width=True
)
