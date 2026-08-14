import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

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
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1 {
        font-weight: 700;
    }

    /* Tabela limpa e responsiva */
    .tabela-container {
        width: 100%;
        overflow-x: auto;
        margin-top: 1rem;
    }

    .tabela-custom {
        width: 100%;
        border-collapse: collapse;
        font-size: 15px;
    }

    .tabela-custom th {
        background-color: #f3f4f6;
        color: #111827;
        text-align: left;
        padding: 12px 14px;
        border-bottom: 1px solid #d1d5db;
        white-space: nowrap;
    }

    .tabela-custom td {
        padding: 12px 14px;
        border-bottom: 1px solid #e5e7eb;
        color: #111827;
        white-space: nowrap;
    }

    @media (max-width: 768px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.8rem !important;
        }

        .tabela-custom {
            font-size: 13px;
        }

        .tabela-custom th,
        .tabela-custom td {
            padding: 9px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# MENU SUPERIOR
# ============================================================

pagina = st.radio(
    "",
    ["Desafio 1", "Desafio 2"],
    horizontal=True,
    label_visibility="collapsed"
)

# ============================================================
# FUNÇÃO PARA EXIBIR TABELA SEM TOOLBAR
# ============================================================

def mostrar_tabela(df):

    html = df.to_html(
        index=False,
        classes="tabela-custom",
        border=0,
        escape=False
    )

    st.markdown(
        f"""
        <div class="tabela-container">
            {html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DESAFIO 1
# ============================================================

if pagina == "Desafio 1":

    st.title("Desafio 1 — Pontos de Mobilização")

    # --------------------------------------------------------
    # DADOS
    # --------------------------------------------------------

    dados = pd.read_csv(
        "instancia_localizacao_OFICINA.csv"
    )

    atribuicoes = pd.read_csv(
        "atribuicoes.csv"
    )

    nos = dados[
        [
            "ID_Origem",
            "Logradouro",
            "Bairro",
            "Latitude",
            "Longitude",
            "Frequencia_Acidentes"
        ]
    ].drop_duplicates(
        subset="ID_Origem"
    )

    nos_acidentes = nos[
        nos["Frequencia_Acidentes"] > 0
    ].copy()

    pontos_finais = [
        86,
        98,
        210,
        227,
        440
    ]

    # ========================================================
    # MAPA
    # ========================================================

    fig = go.Figure()

    for mobilizacao in pontos_finais:

        pontos_mob = atribuicoes[
            atribuicoes["mobilizacao"]
            == mobilizacao
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
                    size=(
                        info["Frequencia_Acidentes"]
                        * 2 + 5
                    ),
                    opacity=0.65
                ),
                text=hover,
                hoverinfo="text",
                name=f"Mobilização {mobilizacao}"
            )
        )

    # --------------------------------------------------------
    # CENTROS
    # --------------------------------------------------------

    centros = nos_acidentes[
        nos_acidentes["ID_Origem"].isin(
            pontos_finais
        )
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

            text=(
                centros["ID_Origem"]
                .astype(int)
                .astype(str)
            ),

            textposition="top center",

            hovertext=hover_centros,
            hoverinfo="text",

            name="Mobilizações"
        )
    )

    fig.update_layout(

        height=720,

        showlegend=False,

        map=dict(

            style="open-street-map",

            center=dict(
                lat=nos_acidentes[
                    "Latitude"
                ].mean(),

                lon=nos_acidentes[
                    "Longitude"
                ].mean()
            ),

            zoom=11
        ),

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": True
        }
    )

    # ========================================================
    # RESUMO
    # ========================================================

    st.subheader(
        "Resumo das mobilizações"
    )

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

    resumo["Distância total (km)"] = (
        resumo["distancia_total_metros"]
        / 1000
    ).round(2)

    resumo["acidentes_atendidos"] = (
        resumo["acidentes_atendidos"]
        .astype(int)
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

    mostrar_tabela(resumo)


# ============================================================
# DESAFIO 2
# ============================================================

else:

    st.title(
        "Desafio 2 — Jornada Recomendada"
    )

    # ========================================================
    # MAPA DA ROTA
    # ========================================================

    if os.path.exists(
        "rotas_desafio2.csv"
    ):

        rotas = pd.read_csv(
            "rotas_desafio2.csv"
        )

        fig2 = go.Figure()

        for trecho in rotas[
            "trecho"
        ].unique():

            rota = (
                rotas[
                    rotas["trecho"]
                    == trecho
                ]
                .sort_values("ordem")
            )

            fig2.add_trace(

                go.Scattermap(

                    lat=rota[
                        "latitude"
                    ],

                    lon=rota[
                        "longitude"
                    ],

                    mode="lines+markers",

                    line=dict(
                        width=5
                    ),

                    marker=dict(
                        size=6
                    ),

                    name=str(trecho),

                    text=[
                        f"{trecho}"
                        for _ in range(
                            len(rota)
                        )
                    ],

                    hoverinfo="text"
                )
            )

        fig2.update_layout(

            height=720,

            showlegend=False,

            map=dict(

                style="open-street-map",

                center=dict(
                    lat=rotas[
                        "latitude"
                    ].mean(),

                    lon=rotas[
                        "longitude"
                    ].mean()
                ),

                zoom=11
            ),

            margin=dict(
                l=0,
                r=0,
                t=10,
                b=0
            )
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": True
            }
        )

    else:

        st.info(
            "O mapa será exibido aqui quando "
            "o arquivo rotas_desafio2.csv "
            "for adicionado ao projeto."
        )

    # ========================================================
    # TABELA DESAFIO 2
    # ========================================================

    st.subheader(
        "Decomposição da Jornada Recomendada por Trecho"
    )

    tabela_desafio2 = pd.DataFrame({

        "Trecho": [
            "Perna 1",
            "Perna 2",
            "Perna 3",
            "Jornada Total"
        ],

        "Caminho / Origem → Destino": [

            "Casa (924) → UFU (1810)",

            "UFU (1810) → Hospital (1350)",

            "Hospital (1350) → Casa (924)",

            "Casa → UFU → Hosp → Casa"
        ],

        "Distância": [
            "5,770 km",
            "9,879 km",
            "8,547 km",
            "24,196 km"
        ],

        "Risco Acum.": [
            "340,0",
            "105,0",
            "193,0",
            "638,0"
        ],

        "Risco Máx.": [
            "150,0",
            "15,0",
            "155,0",
            "155,0"
        ],

        "ID Pareto": [
            "T1_P004",
            "T2_P023",
            "T3_P021",
            "J004"
        ]
    })

    mostrar_tabela(
        tabela_desafio2
    )
