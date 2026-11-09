"""
Funções que carregam os dados, criam os gráficos Plotly e calculam as descobertas.

Ficam separadas do app.py para que o mesmo gráfico seja usado em dois lugares:
  - app.py         -> aplicação Streamlit interativa
  - export_html.py -> exportação estática em HTML (pasta html/)
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

PASTA_DADOS = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Identidade visual: mesma cor para o mesmo país/categoria em todos os gráficos
# ---------------------------------------------------------------------------
CORES_PAISES = {
    "China": "#D62728",
    "Estados Unidos": "#1F77B4",
    "Índia": "#FF7F0E",
    "Rússia": "#9467BD",
    "Brasil": "#2CA02C",
    "Alemanha": "#7F7F7F",
    "Japão": "#E377C2",
    "Reino Unido": "#17BECF",
    "Indonésia": "#BCBD22",
}
COR_OUTROS = "#C7C7C7"
COR_FOSSIL = "#4D4D4D"        # combustíveis fósseis e indústria
COR_USO_TERRA = "#A0522D"     # mudança no uso da terra (desmatamento etc.)
COR_TOTAL = "#000000"

PAISES_PADRAO = ["China", "Estados Unidos", "Índia", "Rússia", "Brasil"]
LIMITE_MAPA = 20  # t/pessoa; acima disso o país aparece na cor máxima


def _layout(fig: go.Figure, titulo: str, altura: int = 500) -> go.Figure:
    """Aplica o mesmo estilo (fonte, fundo, separador decimal brasileiro) a todos os gráficos."""
    fig.update_layout(
        title=dict(text=titulo, x=0, xanchor="left", font=dict(size=18)),
        template="plotly_white",
        height=altura,
        separators=",.",                 # vírgula decimal e ponto de milhar
        font=dict(family="Arial", size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None),
        margin=dict(l=10, r=10, t=90, b=10),
        hoverlabel=dict(font_size=13),
    )
    return fig


def num(valor: float, casas: int = 1) -> str:
    """Formata número no padrão brasileiro: 12345.6 -> '12.345,6'."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê os CSVs gerados pelo prepare_data.py."""
    paises = pd.read_csv(PASTA_DADOS / "co2_paises.csv")
    mundo = pd.read_csv(PASTA_DADOS / "co2_mundo.csv")
    return paises, mundo


# ---------------------------------------------------------------------------
# Visualização 1 – Linhas: evolução das emissões anuais
# ---------------------------------------------------------------------------
def grafico_linhas(paises: pd.DataFrame, selecionados: list[str], por_pessoa: bool = False) -> go.Figure:
    coluna = "co2_per_capita" if por_pessoa else "co2"
    unidade = "t de CO₂ por pessoa" if por_pessoa else "milhões de t de CO₂ (Mt)"
    df = paises[paises["pais"].isin(selecionados)].dropna(subset=[coluna])

    fig = px.line(
        df, x="ano", y=coluna, color="pais",
        color_discrete_map=CORES_PAISES,
        category_orders={"pais": selecionados},
        labels={"ano": "Ano", coluna: unidade, "pais": "País"},
    )
    fig.update_traces(line=dict(width=2.5), hovertemplate="%{y:,.1f}")
    fig.update_layout(hovermode="x unified")

    # Marca o ano em que a China passou os EUA (só faz sentido no total)
    if not por_pessoa and {"China", "Estados Unidos"} <= set(selecionados):
        ano = ano_china_passa_eua(paises)
        fig.add_vline(x=ano, line_dash="dot", line_color="#999999")
        fig.add_annotation(x=ano, y=1, yref="paper", text=f"{ano}: China passa os EUA",
                           showarrow=False, xanchor="right", xshift=-4, font=dict(color="#555555"))

    titulo = "Emissões anuais de CO₂ " + ("por pessoa" if por_pessoa else "totais") + \
             " (combustíveis fósseis e indústria)"
    return _layout(fig, titulo)


# ---------------------------------------------------------------------------
# Visualização 2 – Mapa animado: emissão por pessoa no mundo, ano a ano
# ---------------------------------------------------------------------------
def grafico_mapa(paises: pd.DataFrame, passo_anos: int = 1) -> go.Figure:
    df = paises.dropna(subset=["co2_per_capita"])
    df = df[(df["ano"] - df["ano"].min()) % passo_anos == 0].sort_values("ano")

    fig = px.choropleth(
        df, locations="iso_code", color="co2_per_capita",
        hover_name="pais", animation_frame="ano",
        color_continuous_scale="YlOrRd", range_color=(0, LIMITE_MAPA),
        labels={"co2_per_capita": "t CO₂/pessoa", "ano": "Ano"},
        hover_data={"iso_code": False, "co2_per_capita": ":.1f"},
    )
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth",
                    showcountries=True, countrycolor="#FFFFFF")
    fig.update_layout(coloraxis_colorbar=dict(title="t CO₂<br>por pessoa",
                                              ticksuffix="", tickvals=[0, 5, 10, 15, 20],
                                              ticktext=["0", "5", "10", "15", "20+"]))
    # Deixa a animação um pouco mais lenta e suave
    botoes = fig.layout.updatemenus[0].buttons
    botoes[0].args[1]["frame"]["duration"] = 250
    botoes[0].args[1]["transition"]["duration"] = 0
    fig.layout.updatemenus[0].buttons[0].label = "▶ Animar"
    fig.layout.updatemenus[0].buttons[1].label = "■ Pausar"
    fig.layout.sliders[0].currentvalue.prefix = "Ano: "
    # Começa mostrando o último ano disponível
    ultimo = len(fig.frames) - 1
    fig.layout.sliders[0].active = ultimo
    fig.update_traces(z=fig.frames[ultimo].data[0].z,
                      locations=fig.frames[ultimo].data[0].locations,
                      hovertext=fig.frames[ultimo].data[0].hovertext,
                      customdata=fig.frames[ultimo].data[0].customdata)
    return _layout(fig, "Emissão de CO₂ por pessoa no mundo, 1950–2024", altura=560)


# ---------------------------------------------------------------------------
# Visualização 3 – Dispersão (bolhas): total x por pessoa
# ---------------------------------------------------------------------------
def grafico_dispersao(paises: pd.DataFrame, mundo: pd.DataFrame, ano: int, n_rotulos: int = 6) -> go.Figure:
    df = paises[(paises["ano"] == ano)].dropna(subset=["co2", "co2_per_capita", "populacao"])
    df = df[df["co2"] > 0]  # eixo x em escala log não aceita zero
    # Rótulos só para os maiores emissores, o Brasil e o maior emissor por pessoa (evita poluição)
    rotulados = (set(df.nlargest(n_rotulos, "co2")["pais"]) | {"Brasil"}
                 | {df.loc[df["co2_per_capita"].idxmax(), "pais"]})

    fig = go.Figure()
    # Bolhas cinzas para todos os países, coloridas para os destacados
    for destaque in (False, True):
        parte = df[df["pais"].isin(rotulados) == destaque]
        cores = [CORES_PAISES.get(p, "#555555") if destaque else COR_OUTROS for p in parte["pais"]]
        fig.add_trace(go.Scatter(
            x=parte["co2"], y=parte["co2_per_capita"],
            mode="markers+text" if destaque else "markers",
            text=parte["pais"] if destaque else None,
            # Brasil e Indonésia ficam próximos: rótulos para lados opostos
            textposition=[{"Brasil": "middle left", "Indonésia": "middle right"}.get(p, "top center")
                          for p in parte["pais"]],
            textfont=dict(size=12),
            marker=dict(size=parte["populacao"], sizemode="area",
                        sizeref=2 * df["populacao"].max() / 60 ** 2, sizemin=3,
                        color=cores, line=dict(width=0.5, color="#FFFFFF"), opacity=0.85),
            customdata=parte[["pais", "populacao"]].assign(populacao=parte["populacao"] / 1e6),
            hovertemplate="<b>%{customdata[0]}</b><br>Total: %{x:,.1f} Mt<br>"
                          "Por pessoa: %{y:,.1f} t<br>População: %{customdata[1]:,.1f} mi<extra></extra>",
            showlegend=False,
        ))

    media = mundo.loc[mundo["ano"] == ano, "co2_per_capita"]
    if not media.empty:
        fig.add_hline(y=media.iloc[0], line_dash="dash", line_color="#666666",
                      annotation_text=f"Média mundial: {num(media.iloc[0])} t/pessoa",
                      annotation_position="top left")

    fig.update_xaxes(type="log", title="Emissão total em " + str(ano) + " (Mt de CO₂, escala logarítmica)")
    fig.update_yaxes(title="Emissão por pessoa (t de CO₂)")
    return _layout(fig, f"Emitir muito no total ≠ emitir muito por pessoa ({ano})<br>"
                        "<sup>Tamanho da bolha = população</sup>", altura=600)


# ---------------------------------------------------------------------------
# Visualização 4 – Barras: emissões acumuladas na história
# ---------------------------------------------------------------------------
def grafico_barras_acumulado(paises: pd.DataFrame, n: int = 12) -> go.Figure:
    ultimo_ano = paises["ano"].max()
    df = paises[paises["ano"] == ultimo_ano].nlargest(n, "co2_acumulado_com_uso_terra")
    df = df.sort_values("co2_acumulado_com_uso_terra")  # maior no topo do gráfico horizontal

    fig = go.Figure()
    series = [
        ("co2_acumulado", "Só combustíveis fósseis e indústria", COR_FOSSIL),
        ("co2_acumulado_com_uso_terra", "Incluindo mudança no uso da terra (desmatamento)", COR_USO_TERRA),
    ]
    for coluna, nome, cor in series:
        fig.add_trace(go.Bar(
            y=df["pais"], x=df[coluna] / 1000, name=nome, orientation="h", marker_color=cor,
            hovertemplate="%{y}: %{x:,.1f} Gt<extra>" + nome + "</extra>",
        ))
    fig.update_xaxes(title="Bilhões de toneladas de CO₂ (Gt) acumuladas")
    fig.update_yaxes(title=None)
    fig = _layout(fig, f"Responsabilidade histórica: CO₂ acumulado até {ultimo_ano}<br>"
                       f"<sup>{n} maiores emissores considerando o uso da terra</sup>", altura=620)
    # Legenda embaixo para não encobrir o subtítulo; ordem igual à das barras
    fig.update_layout(barmode="group", bargap=0.25, margin=dict(t=80, b=100),
                      legend=dict(y=-0.14, yanchor="top", traceorder="reversed"))
    return fig


# ---------------------------------------------------------------------------
# Visualização 5 – Barras empilhadas por ano: de onde vêm as emissões de um país
# ---------------------------------------------------------------------------
def grafico_composicao(paises: pd.DataFrame, pais: str = "Brasil") -> go.Figure:
    df = paises[paises["pais"] == pais].dropna(subset=["co2", "co2_uso_terra"])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["ano"], y=df["co2"], name="Combustíveis fósseis e indústria",
                         marker_color=COR_FOSSIL, hovertemplate="%{y:,.0f} Mt"))
    fig.add_trace(go.Bar(x=df["ano"], y=df["co2_uso_terra"], name="Mudança no uso da terra",
                         marker_color=COR_USO_TERRA, hovertemplate="%{y:,.0f} Mt"))
    fig.add_trace(go.Scatter(x=df["ano"], y=df["co2"] + df["co2_uso_terra"], name="Total",
                             mode="lines", line=dict(color=COR_TOTAL, width=2),
                             hovertemplate="%{y:,.0f} Mt"))
    # "relative" empilha positivos para cima e negativos para baixo (reflorestamento)
    fig.update_layout(barmode="relative", bargap=0.1, hovermode="x unified")
    fig.update_xaxes(title="Ano")
    fig.update_yaxes(title="Milhões de t de CO₂ (Mt)")
    return _layout(fig, f"{pais}: de onde vêm as emissões de CO₂?")


# ---------------------------------------------------------------------------
# Descobertas: todos os números do texto do app saem daqui
# ---------------------------------------------------------------------------
def ano_china_passa_eua(paises: pd.DataFrame) -> int:
    tabela = paises.pivot(index="ano", columns="pais", values="co2")
    return int((tabela["China"] > tabela["Estados Unidos"]).idxmax())


def calcular_descobertas(paises: pd.DataFrame, mundo: pd.DataFrame) -> dict:
    ultimo = int(paises["ano"].max())
    atual = paises[paises["ano"] == ultimo].set_index("pais")
    br = paises[paises["pais"] == "Brasil"].set_index("ano")

    def posicao(coluna: str, pais: str) -> int:
        return int(atual[coluna].rank(ascending=False, method="min")[pais])

    eua_1990 = paises.query("pais == 'Estados Unidos' and ano == 1990")["co2_per_capita"].iloc[0]
    china_2000 = paises.query("pais == 'China' and ano == 2000")["co2_per_capita"].iloc[0]
    validos_pc = atual["co2_per_capita"].dropna()

    return {
        "ultimo_ano": ultimo,
        # Descoberta 1 – Brasil e uso da terra
        "br_parcela_uso_terra": 100 * br.loc[ultimo, "co2_uso_terra"] / br.loc[ultimo, "co2_com_uso_terra"],
        "br_rank_acum_fossil": posicao("co2_acumulado", "Brasil"),
        "br_rank_acum_total": posicao("co2_acumulado_com_uso_terra", "Brasil"),
        "br_parcela_acum_fossil": atual.loc["Brasil", "parcela_acumulado"],
        "br_parcela_acum_total": atual.loc["Brasil", "parcela_acumulado_com_uso_terra"],
        "br_pico_uso_terra_ano": int(br["co2_uso_terra"].idxmax()),
        "br_pico_uso_terra": br["co2_uso_terra"].max(),
        "br_min_uso_terra_pos_pico_ano": int(br.loc[br["co2_uso_terra"].idxmax():, "co2_uso_terra"].idxmin()),
        "br_min_uso_terra_pos_pico": br.loc[br["co2_uso_terra"].idxmax():, "co2_uso_terra"].min(),
        "br_uso_terra_ultimo": br.loc[ultimo, "co2_uso_terra"],
        "br_fossil_ultimo": br.loc[ultimo, "co2"],
        # Descoberta 2 – China x EUA
        "ano_china_eua": ano_china_passa_eua(paises),
        "china_anual": atual.loc["China", "co2"],
        "eua_anual": atual.loc["Estados Unidos", "co2"],
        "china_acum": atual.loc["China", "co2_acumulado"] / 1000,
        "eua_acum": atual.loc["Estados Unidos", "co2_acumulado"] / 1000,
        # Descoberta 3 – total x por pessoa
        "india_rank_total": posicao("co2", "Índia"),
        "india_pc": atual.loc["Índia", "co2_per_capita"],
        "mundo_pc": mundo.loc[mundo["ano"] == ultimo, "co2_per_capita"].iloc[0],
        "eua_pc": atual.loc["Estados Unidos", "co2_per_capita"],
        "eua_pc_1990": eua_1990,
        "maior_pc_pais": validos_pc.idxmax(),
        "maior_pc": validos_pc.max(),
        "br_pc": atual.loc["Brasil", "co2_per_capita"],
        "china_pc": atual.loc["China", "co2_per_capita"],
        "china_pc_2000": china_2000,
    }
