"""
App Streamlit: "Quem aquece o planeta? Emissões de CO₂ no mundo e o caso do Brasil"

Para rodar:  streamlit run app.py

Estrutura (narrativa):
  Introdução -> 5 visualizações com interpretação -> 3 descobertas
  -> limitações -> conclusão -> sobre o projeto
Os gráficos ficam em visualizacoes.py; aqui fica só o texto e a interação.
"""

import streamlit as st

import visualizacoes as viz
from visualizacoes import num

st.set_page_config(page_title="Quem aquece o planeta?", page_icon="🌎", layout="wide")


@st.cache_data
def dados():
    """Carrega os dados uma única vez (o Streamlit guarda em cache)."""
    return viz.carregar_dados()


paises, mundo = dados()
d = viz.calcular_descobertas(paises, mundo)  # todos os números citados no texto
ANO = d["ultimo_ano"]
lista_paises = sorted(paises["pais"].unique())

# ---------------------------------------------------------------------------
# Introdução
# ---------------------------------------------------------------------------
st.title("🌎 Quem aquece o planeta?")
st.subheader("Emissões de CO₂ no mundo, de 1950 a %d, e o lugar do Brasil nessa história" % ANO)

st.markdown(
    f"""
O dióxido de carbono (CO₂) é o principal gás responsável pelo aquecimento global. Mas **quem emite**
esse CO₂? A resposta muda bastante conforme a forma de olhar: o total de um país, quanto cada
habitante emite, o que foi emitido ao longo da história e **de onde** vêm as emissões.

**Pergunta central:** *quem é responsável pelas emissões de CO₂ e onde o Brasil entra nessa história?*

Para responder, este painel usa os dados de emissões do **Our World in Data** para {paises['pais'].nunique()}
países e territórios. As visualizações seguem uma sequência: do panorama global ao caso brasileiro.
"""
)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Emissão mundial em {ANO} (fóssil)",
          f"{num(mundo.loc[mundo['ano'] == ANO, 'co2'].iloc[0] / 1000)} Gt")
c2.metric(f"Média mundial por pessoa em {ANO}", f"{num(d['mundo_pc'])} t")
c3.metric("Brasil por pessoa (só fóssil)", f"{num(d['br_pc'])} t")
c4.metric("Emissões do Brasil vindas do uso da terra", f"{num(d['br_parcela_uso_terra'], 0)}%")

st.caption("Gt = bilhões de toneladas · Mt = milhões de toneladas · t = toneladas. "
           "Passe o mouse sobre os gráficos para ver os valores exatos.")
st.divider()

# ---------------------------------------------------------------------------
# Visualização 1 – Linhas
# ---------------------------------------------------------------------------
st.header("1. Quem são os grandes emissores e como eles mudaram?")
col_filtro, col_tipo = st.columns([3, 1])
selecionados = col_filtro.multiselect("Escolha os países para comparar", lista_paises,
                                      default=viz.PAISES_PADRAO)
medida = col_tipo.radio("Medida", ["Total", "Por pessoa"], horizontal=True)

if selecionados:
    st.plotly_chart(viz.grafico_linhas(paises, selecionados, por_pessoa=(medida == "Por pessoa")),
                    width="stretch")
else:
    st.info("Selecione ao menos um país.")

st.markdown(
    f"""
**Interpretação.** Até o começo dos anos 2000, os Estados Unidos eram o maior emissor anual. Em
**{d['ano_china_eua']}** a China passou os EUA e, em {ANO}, emitiu {num(d['china_anual'] / 1000)} Gt,
cerca de **{num(d['china_anual'] / d['eua_anual'])} vezes** o valor americano ({num(d['eua_anual'] / 1000)} Gt).
A Índia também cresce rápido. Ao trocar para **"Por pessoa"**, o quadro se inverte: os EUA continuam
muito acima de China, Índia e Brasil.
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Visualização 2 – Mapa animado
# ---------------------------------------------------------------------------
st.header("2. Onde, no mapa, cada pessoa emite mais?")
st.markdown("Use o **slider** abaixo do mapa para escolher o ano ou clique em **▶ Animar** "
            "para ver as emissões por pessoa mudando de 1950 até hoje.")
st.plotly_chart(viz.grafico_mapa(paises), width="stretch")
st.markdown(
    f"""
**Interpretação.** As cores mais escuras se concentram na América do Norte, na Austrália, na Rússia e
nos países produtores de petróleo do Golfo Pérsico. Em {ANO}, o maior valor foi o do **{d['maior_pc_pais']}**
({num(d['maior_pc'])} t por pessoa). Grande parte da África, do sul da Ásia e da América Latina fica em tons
claros, abaixo da média mundial de {num(d['mundo_pc'])} t. Na animação, a China escurece depois de 2000: a
emissão por pessoa passou de {num(d['china_pc_2000'])} t em 2000 para {num(d['china_pc'])} t em {ANO}.
*A escala para em 20 t: países acima disso aparecem com a cor máxima.*
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Visualização 3 – Dispersão
# ---------------------------------------------------------------------------
st.header("3. Quem emite muito no total também emite muito por pessoa?")
ano_disp = st.slider("Ano", min_value=1950, max_value=ANO, value=ANO, step=1)
st.plotly_chart(viz.grafico_dispersao(paises, mundo, ano_disp), width="stretch")
st.markdown(
    f"""
**Interpretação.** Os países mais à direita emitem mais no total, e os mais altos emitem mais por pessoa.
Em {ANO}, a **Índia** foi o {d['india_rank_total']}º maior emissor do mundo no total, mas cada indiano emitiu
**{num(d['india_pc'])} t**, menos da metade da média mundial ({num(d['mundo_pc'])} t). Catar e Kuwait fazem o
contrário: estão longe dos maiores emissores no total, mas estão entre os maiores por pessoa. O **Brasil** ({num(d['br_pc'])} t por pessoa só com fósseis)
também fica abaixo da média. Ou seja, o total depende muito do tamanho da população.
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Visualização 4 – Barras acumuladas
# ---------------------------------------------------------------------------
st.header("4. Quem é responsável pelo CO₂ já acumulado na atmosfera?")
st.markdown("O aquecimento depende do CO₂ **acumulado** ao longo do tempo, não só do que é emitido hoje. "
            "Aqui comparamos o acumulado só de combustíveis fósseis com o acumulado que inclui a "
            "**mudança no uso da terra** (principalmente desmatamento).")
st.plotly_chart(viz.grafico_barras_acumulado(paises), width="stretch")
st.markdown(
    f"""
**Interpretação.** Mesmo emitindo menos que a China hoje, os **EUA** continuam sendo o maior emissor
histórico: {num(d['eua_acum'], 0)} Gt de CO₂ fóssil contra {num(d['china_acum'], 0)} Gt da China. O caso mais
chamativo é o do **Brasil**: considerando só combustíveis fósseis, ele é apenas o {d['br_rank_acum_fossil']}º do
ranking ({num(d['br_parcela_acum_fossil'])}% do total mundial). Quando o uso da terra entra na conta, ele sobe
para **{d['br_rank_acum_total']}º** ({num(d['br_parcela_acum_total'])}%). A Indonésia passa por algo parecido.
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Visualização 5 – Composição das emissões (Brasil por padrão)
# ---------------------------------------------------------------------------
st.header("5. De onde vêm as emissões do Brasil?")
paises_com_luc = sorted(paises.dropna(subset=["co2_uso_terra"])["pais"].unique())
pais_comp = st.selectbox("País (compare o Brasil com outros)", paises_com_luc,
                         index=paises_com_luc.index("Brasil"))
st.plotly_chart(viz.grafico_composicao(paises, pais_comp), width="stretch")
st.markdown(
    f"""
**Interpretação (Brasil).** Em todo o período, a maior parte do CO₂ brasileiro vem da **mudança no uso da
terra** (barras marrons), e não da queima de combustíveis (barras cinzas). Essa parcela chegou ao pico em
**{d['br_pico_uso_terra_ano']}** ({num(d['br_pico_uso_terra'], 0)} Mt), caiu até {num(d['br_min_uso_terra_pos_pico'], 0)} Mt
em {d['br_min_uso_terra_pos_pico_ano']} e depois voltou a subir, chegando a {num(d['br_uso_terra_ultimo'], 0)} Mt em {ANO}.
Isso é mais que o triplo das emissões fósseis do país no mesmo ano ({num(d['br_fossil_ultimo'], 0)} Mt).
Troque o país para comparar: na Alemanha ou na China, quase tudo é fóssil. Valores abaixo de zero indicam
que a vegetação absorveu mais carbono do que foi emitido pelo uso da terra.
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Descobertas, limitações e conclusão
# ---------------------------------------------------------------------------
st.header("🔎 Três descobertas")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
#### 1. O CO₂ do Brasil vem principalmente do uso da terra, não da queima de combustíveis
Em {ANO}, **{num(d['br_parcela_uso_terra'], 0)}%** do CO₂ brasileiro veio da mudança no uso da terra. No acumulado
histórico, o Brasil sobe do **{d['br_rank_acum_fossil']}º** lugar (só fósseis) para o **{d['br_rank_acum_total']}º** lugar
no mundo quando o desmatamento é contado.
"""
    )
with col2:
    st.markdown(
        f"""
#### 2. O maior emissor de hoje não é o maior emissor da história
A China emite mais que os EUA desde **{d['ano_china_eua']}** e hoje emite cerca de
{num(d['china_anual'] / d['eua_anual'])} vezes mais. Mesmo assim, os EUA acumularam
**{num(d['eua_acum'], 0)} Gt** de CO₂ fóssil, contra {num(d['china_acum'], 0)} Gt da China.
"""
    )
with col3:
    st.markdown(
        f"""
#### 3. Emitir muito no total ≠ emitir muito por pessoa
A Índia é o {d['india_rank_total']}º maior emissor total, mas cada habitante emite {num(d['india_pc'])} t, abaixo
da média mundial ({num(d['mundo_pc'])} t). Um americano emite {num(d['eua_pc'])} t (eram {num(d['eua_pc_1990'])} t
em 1990), e um habitante do {d['maior_pc_pais']} emite {num(d['maior_pc'])} t.
"""
    )

st.header("⚠️ Limitações dos dados")
st.markdown(
    f"""
- **Período:** o painel cobre 1950–{ANO}. Os valores acumulados vêm prontos da fonte e consideram
  desde o início das séries (1750 para fósseis e 1850 para uso da terra). Por isso, as duas barras do
  gráfico 4 não são uma simples soma das partes.
- **Incerteza do uso da terra:** as emissões por mudança no uso da terra são **estimadas por modelos**
  (Global Carbon Project) e têm incerteza bem maior que as emissões fósseis. Os valores podem mudar entre
  versões do dataset.
- **Valores faltantes:** 44 países e territórios, quase todos pequenos, têm anos sem dado de CO₂ fóssil
  (por exemplo, Namíbia e Eritreia antes dos anos 1990; Mônaco, San Marino e Vaticano em todo o período).
  Além disso, cerca de 15% das linhas não têm a estimativa com uso da terra.
  Países sem dado aparecem em branco no mapa e ficam fora dos gráficos. Nenhum valor foi preenchido.
- **Emissões territoriais:** os dados atribuem as emissões a quem produz, não a quem consome. Um país
  que importa muitos produtos industrializados "terceiriza" parte de suas emissões.
- **Só CO₂:** metano e óxido nitroso (importantes na agropecuária brasileira) não estão nestes gráficos.
- **Os dados mostram o quê, não o porquê:** o dataset não traz as causas das variações (políticas,
  economia, fiscalização), então este painel não faz afirmações sobre causa e efeito.
- Alguns nomes de países menos citados permanecem em inglês, como na fonte original.
"""
)

st.header("✅ Conclusão")
st.markdown(
    """
A pergunta "quem é responsável pelas emissões?" não tem uma resposta única. A **China** lidera as
emissões anuais, os **EUA** lideram as históricas e os **países do Golfo** lideram por pessoa. O
**Brasil**, que parece um emissor pequeno quando se olha só para combustíveis fósseis, aparece entre os
maiores emissores históricos do mundo por causa da mudança no uso da terra. Para o Brasil, então, a
discussão sobre clima passa principalmente pelo uso da terra, e não só pela matriz energética.
"""
)
st.divider()

# ---------------------------------------------------------------------------
# Sobre o projeto
# ---------------------------------------------------------------------------
st.header("ℹ️ Sobre o projeto")
st.markdown(
    """
**Fonte dos dados.** *CO₂ and Greenhouse Gas Emissions*, do Our World in Data
([github.com/owid/co2-data](https://github.com/owid/co2-data)), baseado no Global Carbon Project
(Global Carbon Budget). Licença **CC BY 4.0**. Arquivo usado: `owid-co2-data.csv`, preparado pelo
script `prepare_data.py`.

**Ferramentas.**
- **Python + pandas**: leitura e preparação simples dos dados.
- **Plotly**: gráficos interativos (hover, zoom, legenda clicável e animação), que também podem ser
  exportados para HTML e abertos sem servidor.
- **Streamlit**: transforma o script Python em uma página web com filtros e texto, sem precisar
  escrever HTML ou JavaScript, e pode ser publicado gratuitamente no Streamlit Community Cloud.
  Usar uma única biblioteca de gráficos mantém o visual coerente.

**Por que cada visualização?**
| # | Gráfico | Por quê |
|---|---|---|
| 1 | Linhas | Melhor forma de mostrar a evolução no tempo e o momento em que uma série cruza outra (China × EUA). |
| 2 | Mapa coroplético animado | Mostra o padrão geográfico, e o slider de ano mostra a mudança ao longo de décadas. |
| 3 | Dispersão em bolhas (eixo log) | Cruza duas medidas (total × por pessoa) mais a população. O eixo log permite ver países grandes e pequenos juntos. |
| 4 | Barras horizontais agrupadas | Compara rankings de forma direta. As duas barras lado a lado mostram o efeito de incluir o uso da terra. |
| 5 | Barras empilhadas + linha | Mostra a composição das emissões ano a ano e funciona com valores negativos (reflorestamento). |

**Cores consistentes:** cada país mantém a mesma cor em todos os gráficos (Brasil = verde, China =
vermelho, EUA = azul). Cinza-escuro representa sempre os fósseis, e marrom, o uso da terra.
"""
)
st.caption("Atividade prática – Ciência de Dados · Desafio de Visualização de Dados")
