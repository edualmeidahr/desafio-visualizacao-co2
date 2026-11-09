# 🌎 Quem aquece o planeta?
### Emissões de CO₂ no mundo (1950–2024) e o lugar do Brasil nessa história

Atividade prática de **Ciência de Dados – Desafio de Visualização de Dados**.

🔗 **App publicado:** https://desafio-visualizacao-co2-w9pdf3vn5jxfqnf6vkafqk.streamlit.app/

> Se o app estiver "dormindo" (tela com o botão *"Yes, get this app back up!"*), clique no botão e aguarde
> cerca de 1 minuto. Versão estática sem servidor: abra `html/index.html`.

Este projeto é um painel interativo, feito em **Streamlit + Plotly**, que conta uma história a partir dos
dados de emissões de CO₂ do *Our World in Data*. A pergunta central é:

> **Quem é responsável pelas emissões de CO₂ e onde o Brasil entra nessa história?**

---

## 📦 Dataset

| Item | Descrição |
|---|---|
| **Nome** | *CO₂ and Greenhouse Gas Emissions* (`owid-co2-data.csv`) |
| **Fonte** | Our World in Data, com base no Global Carbon Project (Global Carbon Budget), Jones et al. e outros |
| **Link** | https://github.com/owid/co2-data · download direto: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv |
| **Licença** | Creative Commons BY 4.0 (uso livre com citação da fonte) |
| **Tamanho original** | 50.411 linhas × 79 colunas, anos 1750–2024, países e agregados regionais |
| **Versão usada** | baixada em 09/11/2026 (arquivos em `data/`) |

O dicionário completo das variáveis da fonte está em `data/owid-co2-codebook.csv`.

### Variáveis usadas (arquivo preparado `data/co2_paises.csv`)

| Coluna | Coluna original | Descrição | Unidade |
|---|---|---|---|
| `country` / `pais` | `country` | Nome do país (original em inglês / nome em português para os mais citados) | – |
| `iso_code` | `iso_code` | Código ISO de 3 letras (usado no mapa) | – |
| `ano` | `year` | Ano | – |
| `populacao` | `population` | População | pessoas |
| `co2` | `co2` | Emissão anual de CO₂ de combustíveis fósseis e indústria | Mt (milhões de t) |
| `co2_per_capita` | `co2_per_capita` | Emissão anual de CO₂ fóssil por pessoa | t/pessoa |
| `co2_uso_terra` | `land_use_change_co2` | Emissão anual de CO₂ por mudança no uso da terra (pode ser negativa) | Mt |
| `co2_com_uso_terra` | `co2_including_luc` | Emissão anual total (fóssil + uso da terra) | Mt |
| `co2_acumulado` | `cumulative_co2` | Emissão fóssil acumulada desde 1750 | Mt |
| `co2_acumulado_com_uso_terra` | `cumulative_co2_including_luc` | Emissão acumulada incluindo uso da terra | Mt |
| `parcela_acumulado` | `share_global_cumulative_co2` | Parcela do acumulado fóssil mundial | % |
| `parcela_acumulado_com_uso_terra` | `share_global_cumulative_co2_including_luc` | Parcela do acumulado mundial incluindo uso da terra | % |

O arquivo `data/co2_mundo.csv` tem as mesmas colunas para o agregado mundial (`World`).

---

## 🗂️ Estrutura do projeto

```
.
├── app.py                # Produto visual: app Streamlit (narrativa + gráficos)
├── visualizacoes.py      # Funções dos 5 gráficos Plotly e cálculo das descobertas
├── prepare_data.py       # Preparação dos dados (documentada passo a passo)
├── export_html.py        # Exporta os gráficos para HTML estático (pasta html/)
├── requirements.txt      # Dependências com versões fixadas
├── .streamlit/config.toml# Tema claro do app
├── data/
│   ├── owid-co2-data.csv      # dataset original (OWID)
│   ├── owid-co2-codebook.csv  # dicionário de variáveis (OWID)
│   ├── co2_paises.csv         # dados preparados – países, 1950–2024
│   └── co2_mundo.csv          # dados preparados – total mundial, 1950–2024
└── html/
    ├── index.html             # todos os gráficos em uma página (funciona offline)
    └── 1_…html a 5_…html      # cada gráfico em um arquivo separado
```

---

## ▶️ Como rodar

```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. (Opcional) Refazer a preparação dos dados e o export HTML
python prepare_data.py
python export_html.py

# 4. Rodar o app
streamlit run app.py
```

O app abre em `http://localhost:8501`. Para ver os gráficos **sem rodar servidor**, abra
`html/index.html` no navegador.

---

## 🧹 Preparação dos dados (`prepare_data.py`)

Os ajustes foram mínimos, e nenhum valor foi alterado ou inventado:

1. **Download automático** do CSV original, caso ele não esteja em `data/`.
2. **Somente países:** regiões e grupos (World, Africa, European Union, High-income countries…) não têm
   `iso_code` e foram separados. O agregado `World` foi salvo à parte, para a média mundial.
3. **Recorte 1950–2024:** antes de 1950 a cobertura por país é bem menor. Os acumulados já vêm calculados
   pela fonte desde o início das séries, então o recorte não muda esses valores.
4. **Seleção e renomeação** de 12 das 79 colunas, com nomes em português.
5. **Nomes em português** para cerca de 45 países mais citados. Os demais ficam em inglês.
6. **Valores faltantes não são preenchidos:** cada gráfico ignora o país/ano sem dado.

Resumo da exploração (gerado pelo script): 218 países e territórios; 16.350 linhas; faltam 6,6% dos
valores de CO₂ fóssil e 14,7% da estimativa com uso da terra.

---

## 📊 Visualizações e justificativas

| # | Pergunta | Gráfico | Interação | Por que este gráfico |
|---|---|---|---|---|
| 1 | Quem são os grandes emissores e como mudaram? | **Linhas** | escolha de países + alternar total/por pessoa | Melhor forma de mostrar evolução no tempo e cruzamento de séries (China × EUA). |
| 2 | Onde cada pessoa emite mais? | **Mapa coroplético animado** | slider de ano + botão ▶ Animar | Mostra o padrão geográfico, e a animação mostra a mudança em 75 anos. |
| 3 | Emitir muito no total = emitir muito por pessoa? | **Dispersão em bolhas** (eixo x log) | slider de ano + hover | Cruza três variáveis (total, por pessoa, população). O eixo log mostra países grandes e pequenos juntos. |
| 4 | Quem é responsável pelo CO₂ acumulado? | **Barras horizontais agrupadas** | hover | Ranking fácil de ler. As duas barras por país mostram o efeito de incluir o desmatamento. |
| 5 | De onde vêm as emissões do Brasil? | **Barras empilhadas + linha de total** | escolha de país | Mostra a composição ano a ano e funciona com valores negativos (reflorestamento), algo que a área empilhada não faz bem. |

**Comunicação visual:** cada país tem sempre a mesma cor (Brasil = verde, China = vermelho, EUA = azul…),
fósseis são sempre cinza-escuro e uso da terra é sempre marrom. Todos os títulos e eixos têm unidade, e os
números seguem o padrão brasileiro (vírgula decimal).

### Por que estas ferramentas?
- **Python + pandas:** leitura e preparação simples, reproduzível em qualquer máquina.
- **Plotly:** interatividade pronta (hover, zoom, legenda clicável, animação) e exportação para HTML
  que abre sem servidor.
- **Streamlit:** transforma um script Python em página web com filtros e texto narrativo, sem HTML ou
  JavaScript, e permite publicar de graça no Streamlit Community Cloud.
- Usar uma única biblioteca de gráficos (Plotly) mantém a identidade visual coerente.

---

## 🔎 As 3 descobertas

> Os números abaixo são calculados no código (`visualizacoes.calcular_descobertas`) a partir da versão do
> dataset baixada em 09/11/2026. No app, eles se atualizam sozinhos se os dados forem atualizados.

1. **O CO₂ do Brasil vem principalmente do uso da terra, não da queima de combustíveis.**
   Em 2024, **77%** do CO₂ brasileiro veio da mudança no uso da terra (1.600 Mt, contra 483 Mt de
   fósseis). Em todos os anos de 1950 a 2024, essa parcela foi maior que a fóssil. No acumulado histórico,
   o Brasil é o **19º** emissor considerando só fósseis (0,98% do mundo), mas sobe para **4º** (5,1%)
   quando o uso da terra entra na conta. A emissão por uso da terra teve pico em 2003 (2.999 Mt), caiu até
   2011 (1.058 Mt) e voltou a subir.

2. **O maior emissor de hoje não é o maior emissor da história.**
   A China passou os EUA nas emissões anuais em **2006** e, em 2024, emitiu cerca de 2,5 vezes mais
   (12,3 Gt contra 4,9 Gt). Mesmo assim, os EUA continuam sendo o maior emissor acumulado: **435 Gt** de
   CO₂ fóssil desde 1750, contra 285 Gt da China.

3. **Emitir muito no total não é o mesmo que emitir muito por pessoa.**
   A Índia é o 3º maior emissor total, mas cada indiano emitiu **2,2 t** em 2024, abaixo da média mundial
   (4,7 t). Cada americano emitiu 14,2 t (20,3 t em 1990), e o Catar teve o maior valor por pessoa:
   41,3 t. O Brasil, só com fósseis, fica em 2,3 t por pessoa.

---

## ⚠️ Limitações

- **Período:** o painel cobre 1950–2024. Os acumulados vêm da fonte e começam em 1750 (fósseis) e 1850
  (uso da terra). Por isso, as duas barras do gráfico 4 não são uma soma simples das partes.
- **Incerteza do uso da terra:** as emissões por mudança no uso da terra são **estimativas de modelos**
  (Global Carbon Project), com incerteza bem maior que as fósseis, e podem mudar entre versões do dataset.
- **Valores faltantes:** 44 países e territórios, quase todos pequenos, têm anos sem dado de CO₂ fóssil
  (por exemplo, Namíbia e Eritreia antes dos anos 1990; Mônaco, San Marino e Vaticano em todo o período).
  Cerca de 15% das linhas não têm a estimativa com uso da terra. Nenhum valor foi preenchido.
- **Viés territorial:** as emissões são atribuídas a quem produz, não a quem consome os produtos.
- **Só CO₂:** metano e óxido nitroso (relevantes na agropecuária) não foram analisados.
- **Correlação, não causa:** o dataset não traz as causas das variações. O painel descreve os padrões,
  mas não afirma o que os provocou.

## ✅ Conclusão

Não existe uma resposta única para "quem emite": a **China** lidera as emissões anuais, os **EUA**
lideram as históricas e países como o **Catar** lideram por pessoa. O **Brasil** parece um emissor pequeno
quando se olha só para combustíveis fósseis, mas está entre os maiores emissores históricos por causa da
mudança no uso da terra.

---

## 🚀 Publicar no Streamlit Community Cloud (gerar o link de entrega)

1. Crie um repositório **público** no GitHub e envie a pasta do projeto (o `.gitignore` já exclui o `.venv`):
   ```bash
   git init
   git add .
   git commit -m "Desafio de visualização de dados - emissões de CO2"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   git push -u origin main
   ```
2. Acesse https://share.streamlit.io e entre com sua conta do GitHub.
3. Clique em **Create app** → **Deploy a public app from GitHub**.
4. Escolha o repositório, a branch `main` e o arquivo principal `app.py`.
   Em **Advanced settings**, selecione Python **3.10** ou **3.11**.
5. Clique em **Deploy**. Em alguns minutos você recebe um link do tipo
   `https://SEU-APP.streamlit.app`, que é o link de entrega.

> Os CSVs ficam no repositório (o maior tem cerca de 14 MB, abaixo do limite de 100 MB do GitHub), então o
> app funciona sem baixar nada na hora.

---

**Fonte dos dados:** Our World in Data – *CO₂ and Greenhouse Gas Emissions*
(https://github.com/owid/co2-data), licença CC BY 4.0.
