"""
Exporta as 5 visualizações como arquivos HTML estáticos na pasta html/.
Os arquivos abrem direto no navegador, sem precisar rodar o Streamlit.

Para rodar:  python export_html.py
"""

from pathlib import Path

import visualizacoes as viz

PASTA_HTML = Path(__file__).parent / "html"


def exportar() -> None:
    PASTA_HTML.mkdir(exist_ok=True)
    paises, mundo = viz.carregar_dados()
    ultimo_ano = int(paises["ano"].max())

    # Nos HTMLs estáticos não há os filtros do Streamlit, então usamos as opções padrão
    graficos = {
        "1_linhas_emissoes_anuais.html": viz.grafico_linhas(paises, viz.PAISES_PADRAO),
        "1b_linhas_emissoes_por_pessoa.html": viz.grafico_linhas(paises, viz.PAISES_PADRAO, por_pessoa=True),
        "2_mapa_animado_por_pessoa.html": viz.grafico_mapa(paises),
        "3_dispersao_total_vs_por_pessoa.html": viz.grafico_dispersao(paises, mundo, ultimo_ano),
        "4_barras_acumulado_historico.html": viz.grafico_barras_acumulado(paises),
        "5_composicao_brasil.html": viz.grafico_composicao(paises, "Brasil"),
    }

    # include_plotlyjs="cdn" deixa os arquivos leves (precisa de internet para abrir).
    # auto_play=False: o mapa só anima quando a pessoa clica em "▶ Animar".
    for nome, fig in graficos.items():
        fig.write_html(PASTA_HTML / nome, include_plotlyjs="cdn", auto_play=False)
        print(f"Gerado: html/{nome}")

    # Página índice com todos os gráficos juntos (plotly.js embutido: funciona offline)
    partes = [fig.to_html(full_html=False, include_plotlyjs=(i == 0), auto_play=False)
              for i, fig in enumerate(graficos.values())]
    indice = (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<title>Quem aquece o planeta? – Visualizações</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:1200px;margin:auto;padding:20px}"
        "div.grafico{margin-bottom:50px}</style></head><body>"
        "<h1>Quem aquece o planeta? Emissões de CO₂ (1950–%d)</h1>"
        "<p>Versão estática das visualizações. Fonte: Our World in Data – "
        "<a href='https://github.com/owid/co2-data'>github.com/owid/co2-data</a> (CC BY 4.0). "
        "O texto completo, com interpretações e descobertas, está no app Streamlit.</p>" % ultimo_ano
        + "".join(f"<div class='grafico'>{p}</div>" for p in partes)
        + "</body></html>"
    )
    (PASTA_HTML / "index.html").write_text(indice, encoding="utf-8")
    print("Gerado: html/index.html (todos os gráficos, funciona offline)")


if __name__ == "__main__":
    exportar()
