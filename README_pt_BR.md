# Retail Sales Intelligence Pipeline

## Visão Geral do Projeto

Este projeto processa uma pasta de trabalho do Excel (`.xlsx`) com várias abas, cada uma representando dados operacionais históricos de uma empresa varejista.

Os dados fornecidos pela empresa incluem vendas, produtos, lojas e custos fixos.

O pipeline lê cada aba, converte os dados em tabelas Parquet, valida as informações e aplica verificações de qualidade para prepará-las para análise.

O resultado final busca responder a perguntas importantes de negócio, como:

- Onde a empresa vende mais?
- As vendas são suficientes para cobrir os custos fixos?
- Quais produtos são os mais vendidos?
- Quais produtos têm poucas vendas ou nenhuma venda?
- Qual loja gera o maior volume de vendas?

---

## Arquitetura

O projeto segue uma arquitetura de dados em camadas, utilizando Bronze, Silver e Gold.

```text
Excel (.xlsx)
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Análise / BI
```

### Camada Bronze

A camada Bronze recebe o arquivo Excel (`.xlsx`) original, no qual cada aba representa um conjunto diferente de dados operacionais.

Com Pandas, cada aba é extraída e carregada em um dicionário de DataFrames. Em seguida, cada DataFrame é validado para confirmar a presença das colunas esperadas e salvo como uma tabela Parquet.

O fluxo de dados dessa camada é:

```text
Excel (.xlsx)
    ↓
Extração com Pandas
    ↓
Dicionário de DataFrames
    ↓
Validação das colunas
    ↓
Tabelas Parquet
    ↓
Camada Silver
```

Principais funções utilizadas na camada Bronze:

- `read_excel`
- `validate_all_columns`
- `save_parquet`

### Camada Silver

A camada Silver é onde os dados começam a ser transformados de acordo com as regras de negócio e de qualidade definidas para cada conjunto de dados.

Entre as principais transformações aplicadas nessa camada estão:

- revisão e correção de tipos de dados, como números, datas e textos;
- padronização de nomes de colunas inconsistentes;
- arredondamento de valores numéricos quando necessário;
- criação de colunas derivadas nas tabelas fato, incluindo métricas de vendas como `gross_amount` e outros campos calculados.

Antes da implementação da lógica definitiva de transformação, foi utilizado um arquivo `exploration_silver` para testar e validar as etapas de transformação. Isso ajudou a evitar a inclusão de lógica experimental ou desnecessária no código principal do pipeline.

O fluxo de dados dessa camada é:

```text
Tabelas Parquet da Bronze
    ↓
Leitura em DataFrames
    ↓
Aplicação das transformações
    ↓
Retorno dos DataFrames transformados
    ↓
Gravação das tabelas Parquet da Silver
```

Principais funções utilizadas na camada Silver:

- `read_parquet_files`
- `transform_all_dataframes_bronze`
- `save_parquet`

`read_parquet_files` carrega as tabelas Parquet da Bronze em DataFrames.

`transform_all_dataframes_bronze` recebe os DataFrames, aplica a lógica de transformação necessária para cada conjunto de dados e retorna um dicionário com os DataFrames transformados.

`save_parquet` recebe os DataFrames transformados e os grava no caminho configurado para a Silver.

### Camada Gold

A camada Gold é a etapa final do pipeline, na qual os dados são modelados especificamente para apoiar análises de negócio.

O desenho dessa camada é orientado pelas principais perguntas que o projeto pretende responder, como:

- Quais produtos são os mais vendidos?
- As vendas são suficientes para cobrir os custos fixos?
- Quais produtos têm poucas vendas ou nenhuma venda?
- Qual loja gera o maior volume de vendas?

Para responder a essas perguntas, o modelo analítico foi estruturado com uma abordagem de modelagem dimensional baseada em esquema estrela, com tabelas fato contendo eventos de negócio mensuráveis e tabelas dimensão fornecendo contexto descritivo para as análises.

As principais tabelas dimensão são:

- `dim_date`: gerada no próprio projeto para permitir filtros e análises temporais.
- `dim_products`: criada para analisar as vendas sob a perspectiva dos produtos.
- `dim_stores`: criada para analisar vendas e custos fixos sob a perspectiva das lojas.

As principais tabelas fato são:

- `fact_sales`: contém as principais transações de venda e métricas relacionadas a produtos e lojas.
- `fact_fixed_costs`: contém os custos fixos associados a cada loja ou canal de vendas, como aluguel, folha de pagamento, serviços públicos e outras despesas.

O modelo geral segue esta estrutura:

```text
              dim_date
                 |
                 |
dim_products — fact_sales — dim_stores
                               |
                               |
                      fact_fixed_costs
```

Como o modelo possui duas tabelas fato que compartilham dimensões, ele não constitui um único esquema estrela clássico. Ainda assim, segue uma abordagem de modelagem dimensional com dimensões compartilhadas.

---

## Modelo de Dados

A camada Gold está organizada em tabelas dimensão e fato projetadas para apoiar as principais perguntas de negócio do projeto.

### Tabelas Dimensão

- `dim_stores`: representa as lojas ou pontos de venda.
- `dim_products`: representa os produtos comercializados.
- `dim_date`: representa a dimensão calendário, utilizada em filtros e análises temporais.

### Tabelas Fato

- `fact_sales`: representa as transações de venda e as principais métricas relacionadas a cada venda.
- `fact_fixed_costs`: representa os custos fixos mensais associados às lojas ou aos canais de vendas.

### Chaves Lógicas

As seguintes colunas funcionam como identificadores lógicos no modelo analítico:

- `dim_stores.store_id`: identificador lógico de cada loja.
- `dim_products.product_id`: identificador lógico de cada produto.
- `fact_sales.sale_id`: identificador único de cada transação de venda.
- `dim_date.date`: identificador lógico de cada data do calendário.
- `fact_fixed_costs`: sua unicidade lógica é definida pela combinação de `store_id` e `start_month`.

### Relacionamentos Esperados

O modelo analítico considera os seguintes relacionamentos lógicos:

```text
dim_products.product_id
        ↓
fact_sales.product_id


dim_stores.store_id
        ↓
fact_sales.store_id


dim_stores.store_id
        ↓
fact_fixed_costs.store_id


dim_date.date
        ↓
fact_sales.sale_date
```

Atualmente, esses são relacionamentos lógicos do modelo analítico. Eles são verificados durante as validações do projeto, mas não são impostos por restrições de chave primária (*Primary Key*) ou chave estrangeira (*Foreign Key*) de um banco de dados, pois as tabelas analíticas são armazenadas como arquivos Parquet, e não em um banco de dados relacional.

---

## Qualidade de Dados e Validação

Os conjuntos de dados da Gold foram explorados e validados para verificar consistência estrutural, integridade referencial, regras de negócio e valores calculados. A lógica de validação exploratória está disponível em `exploration_gold/validate_gold.py`.

### Validação de `fact_sales`

- **Colunas e tipos de dados:** conferência dos nomes e tipos de dados em relação à estrutura esperada.
- **Valores nulos:** nenhum valor nulo foi encontrado.
- **Quantidade de registros:** a tabela Gold contém **239 registros de vendas**.
- **Unicidade:** verificação de duplicidades em `sale_id`; nenhuma foi encontrada.
- **Integridade referencial:** conferência de `product_id`, `store_id` e datas de venda em relação às respectivas dimensões.
- **Intervalos válidos:** verificação de valores positivos em `quantity` e `unit_price_brl`, além do intervalo esperado para `discount_pct`.
- **Campos calculados:** auditoria de `gross_amount`, `discount_amount` e `net_amount` quanto à consistência matemática e ao arredondamento, além de outras verificações de valores inválidos.
- **Resultado:** não foram encontradas inconsistências significativas de qualidade de dados nas regras testadas.

### Validação de `dim_products`

- **Identificação e duplicidades:** verificação de que `product_id` identifica os produtos de forma única; não foram encontrados IDs repetidos.
- **Categorias:** comparação dos valores de `category` com uma lista de categorias permitidas por meio de `isin()`.
- **Custos:** exigência de `unit_cost` maior que zero. Também foram investigados custos excepcionalmente altos usando o limite de três vezes a média.
- **Moeda do fornecedor:** aceitação apenas de `BRL` e `USD`, verificada com `isin()`.
- **Status ativo:** confirmação de valores booleanos em `active` e inspeção de sua distribuição com `value_counts()`; os seis produtos estavam ativos.
- **Resultado:** não foram encontradas inconsistências segundo as regras atuais do projeto.

### Validação de `dim_stores`

- **Identificação e duplicidades:** verificação de `store_id` com `duplicated()` e `sum()`.
- **Strings vazias:** implementação de uma função reutilizável que percorre colunas de texto, aplica `strip()` e `len()` e retorna um dicionário com a contagem de strings vazias por coluna. Valores nulos são verificados separadamente.
- **Canais de vendas:** conferência de `channel` com os valores permitidos `Física` e `Online`, utilizando `isin()`.
- **Possíveis duplicidades de negócio:** investigação de combinações repetidas de atributos da loja com `duplicated(subset=..., keep=False)` e de nomes de lojas associados a múltiplos IDs por meio de `groupby()` e `nunique()`.
- **Consistência cidade/estado:** identificada a necessidade de uma tabela de referência ou API confiável para verificar as combinações de cidade e estado; essa validação externa ainda não foi implementada.
- **Resultado:** as verificações implementadas não identificaram inconsistências.

### Validação de `fact_fixed_costs`

- **Unicidade mensal:** verificação da combinação `store_id` e `start_month` com `duplicated()` e `groupby().size()`.
- **Integridade referencial:** verificação, com `isin()`, de que cada `store_id` existe em `dim_stores`; não foram encontrados relacionamentos inválidos.
- **Custos negativos:** desenvolvimento de uma função reutilizável que conta valores negativos por coluna monetária e retorna um resumo em dicionário.
- **Análise de custos zerados:** contagem de zeros por coluna e uso de máscaras booleanas com `any(axis=1)` para localizar linhas que contêm ao menos um custo igual a zero.
- **Regra de negócio para aluguel:** aluguel zero pode ser válido para um canal on-line. Foi utilizado um `merge` à esquerda com `dim_stores` para verificar lojas físicas com `rent_brl = 0`; nenhuma inconsistência desse tipo foi encontrada.
- **Consistência de datas:** verificação de que `start_month` corresponde ao primeiro dia do mês; nenhuma data inválida foi encontrada.
- **Possíveis outliers:** contagem de custos acima de **três vezes a média de cada coluna**, com resultados por coluna. Trata-se de uma heurística exploratória, não de uma restrição formal de negócio.
- **Resultado:** não foram identificadas inconsistências nas regras estruturais, referenciais e de negócio verificadas.

### Validação de `dim_date`

A dimensão de datas é gerada programaticamente, em vez de ser importada de uma fonte externa. Por isso, as verificações se concentram em sua consistência interna.

- **Unicidade:** verificação de `date` com `duplicated()`; nenhuma data duplicada foi encontrada.
- **Continuidade:** cálculo das diferenças entre datas consecutivas com `diff()` e comparação com `pd.Timedelta(days=1)`; não foram encontradas lacunas.
- **Campos derivados:** conferência de `year` e `month` com `date.dt.year` e `date.dt.month`, utilizando máscaras booleanas.
- **Resultado:** todas as verificações implementadas passaram, sem datas duplicadas, lacunas na sequência ou inconsistências de ano e mês.

---
## Estrutura do Projeto

O repositório separa os arquivos de dados, o código-fonte Python e os scripts exploratórios para manter a lógica de processamento organizada e facilitar o rastreamento de problemas ao longo das etapas do pipeline.

### Estrutura de Diretórios

```text
retail-sales-intelligence-pipeline/
├── .gitignore
├── .python-version
├── MANUAL_DEBUGGING.md
├── README.md
├── poetry.lock
├── poetry.toml
├── pyproject.toml
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── data/
│   ├── raw/
│   │   └── excel/
│   │       └── store_operations.xlsx
│   ├── bronze/
│   │   ├── fixed_costs.parquet
│   │   ├── products.parquet
│   │   ├── sales.parquet
│   │   └── stores.parquet
│   ├── silver/
│   │   ├── fixed_costs.parquet
│   │   ├── products.parquet
│   │   ├── sales.parquet
│   │   └── stores.parquet
│   └── gold/
│       ├── dim_date.parquet
│       ├── dim_products.parquet
│       ├── dim_stores.parquet
│       ├── fact_fixed_costs.parquet
│       └── fact_sales.parquet
├── exploration_bronze/
│   └── explore_bronze.py
├── exploration_gold/
│   ├── explore_gold.py
│   └── validate_gold.py
└── src/
    ├── __init__.py
    ├── config.py
    ├── extract.py
    ├── load.py
    ├── main.py
    ├── model.py
    ├── transform.py
    └── validate.py
```

### Responsabilidades dos Diretórios e Módulos

#### `data/` — Armazenamento de Dados

O diretório `data/` fica separado do código-fonte Python para melhorar a organização e evitar a mistura de conjuntos de dados com o código da aplicação.

O diretório segue uma **Arquitetura Medallion**, na qual cada camada armazena os dados em uma etapa diferente do processamento:

- **Raw:** contém os arquivos Excel originais recebidos da fonte de dados.
- **Bronze:** armazena os conjuntos de dados extraídos em formato Parquet após a validação inicial das colunas.
- **Silver:** contém os conjuntos de dados limpos e transformados a partir da Bronze.
- **Gold:** armazena tabelas analíticas modeladas para análise de negócio.

Essa organização melhora a **rastreabilidade dos dados**, facilitando a investigação de erros, a identificação da etapa em que um problema surgiu e a inspeção dos dados em diferentes pontos do pipeline.

#### `src/` — Código-Fonte

O diretório `src/` contém o código Python principal responsável por executar o pipeline e aplicar a lógica de processamento dos dados.

Diferentemente de `data/`, que armazena conjuntos de dados nas diferentes etapas, `src/` reúne as funções e os módulos que extraem, validam, transformam, modelam e salvam os dados.

A lógica do projeto é dividida em módulos Python independentes, em vez de ficar concentrada em um único arquivo. Essa abordagem melhora a **reutilização de código, a manutenção e a separação de responsabilidades**, permitindo importar e reutilizar funções em diferentes partes do projeto.

#### `src/main.py` — Execução do Pipeline

O módulo `main.py` é o ponto de entrada principal e coordena a execução das diferentes etapas do pipeline.

Ele importa funções de outros módulos, fornece os parâmetros necessários e utiliza os resultados de cada operação para executar a próxima etapa do fluxo de dados.

Essa abordagem mantém o fluxo de execução organizado, sem concentrar toda a lógica de processamento em um único arquivo.

#### `src/config.py` — Configuração Centralizada

O módulo `config.py` centraliza as configurações do projeto, incluindo caminhos de arquivos, colunas obrigatórias e listas auxiliares utilizadas no pipeline.

Manter essas configurações em um único lugar evita duplicação de código, facilita a manutenção e reduz o risco de inconsistências quando são necessárias alterações.

#### `src/extract.py` — Extração de Dados

O módulo `extract.py` é responsável por ler dados das fontes utilizadas pelo projeto.

Ele recebe os caminhos definidos em `config.py` e extrai informações de pastas de trabalho do Excel, retornando um dicionário de DataFrames Pandas, no qual cada DataFrame representa uma aba.

O módulo também oferece funcionalidades para ler arquivos Parquet das camadas já processadas.

Separar extração de transformação melhora a organização do código e permite modificar a lógica de processamento sem alterar a leitura dos dados de origem.

#### `src/validate.py` — Validação da Estrutura dos Dados

O módulo `validate.py` verifica se os conjuntos de dados extraídos contêm as colunas obrigatórias definidas em `config.py`.

Ele valida a estrutura de cada DataFrame em relação às listas de colunas esperadas.

Quando faltam colunas obrigatórias, a validação lança um erro indicando o conjunto de dados afetado e as colunas ausentes.

Esse processo ajuda a impedir que estruturas inesperadas avancem para as próximas etapas, reduzindo erros de processamento e retrabalho.

#### `src/load.py` — Armazenamento de Dados

O módulo `load.py` salva os DataFrames processados nos caminhos de destino recebidos como parâmetros.

Ele recebe um dicionário de DataFrames e um caminho de saída, gerando arquivos Parquet individuais com os nomes das chaves do dicionário.

Separar a gravação dos dados da extração e transformação melhora a organização, a reutilização e a manutenção do código. Também permite alterar a lógica de armazenamento sem modificar os processos de extração ou transformação.

#### `src/transform.py` — Transformação de Dados

O módulo `transform.py` aplica regras de limpeza e transformação aos conjuntos de dados extraídos da camada Bronze.

As principais transformações incluem:

- Criação de novas colunas calculadas.
- Renomeação e padronização dos nomes das colunas.
- Conversão das colunas para tipos de dados adequados.
- Aplicação de transformações de acordo com a estrutura e as regras de negócio de cada conjunto de dados.

Conjuntos de dados diferentes exigem regras de transformação diferentes. Por exemplo, uma tabela de produtos contém principalmente informações descritivas, enquanto uma tabela fato de vendas exige cálculos adicionais para gerar métricas de negócio.

A função `transform_all_dataframes_bronze()` recebe um dicionário de DataFrames e coordena a execução das funções de transformação correspondentes a cada conjunto de dados.

Após o processamento, retorna um dicionário com os DataFrames limpos e transformados, prontos para serem salvos na camada Silver.

#### `src/model.py` — Modelagem Analítica de Dados

O módulo `model.py` constrói as tabelas analíticas utilizadas na camada Gold.

Diferentemente de `transform.py`, que se concentra na limpeza e transformação, `model.py` organiza os conjuntos de dados processados em um modelo dimensional criado para responder a perguntas de negócio.

A modelagem segue uma abordagem baseada em esquema estrela, com dois tipos de tabelas:

- **Tabelas dimensão:** `dim_products`, `dim_stores` e `dim_date` fornecem informações descritivas e apoiam filtros e análises.
- **Tabelas fato:** `fact_sales` e `fact_fixed_costs` contêm transações de negócio e valores mensuráveis relacionados a vendas e custos operacionais.

A função `build_gold_model()` recebe um dicionário de DataFrames Silver, além de datas inicial e final para gerar a dimensão calendário.

Ela coordena a criação das tabelas analíticas e retorna um dicionário de DataFrames Gold, posteriormente salvos em formato Parquet.

Essa estrutura torna os dados mais adequados a ferramentas analíticas como o Power BI, apoiando a criação de relacionamentos, métricas, relatórios e dashboards.

#### `exploration_bronze/` e `exploration_gold/` — Exploração e Validação de Dados

Esses diretórios contêm scripts exploratórios utilizados para desenvolver, testar e verificar a lógica de processamento separadamente dos módulos principais do pipeline.

A separação do código exploratório ajuda a manter os módulos orientados à execução organizados e impede que lógica experimental ou desnecessária seja incluída no fluxo principal de processamento.

- **`exploration_bronze/explore_bronze.py`:** utilizado na exploração inicial dos dados e nos testes da lógica de extração.
- **`exploration_gold/explore_gold.py`:** utilizado para examinar a estrutura geral e a qualidade das tabelas Gold, incluindo valores nulos, registros duplicados e verificações iniciais.
- **`exploration_gold/validate_gold.py`:** utilizado para validações mais detalhadas de qualidade, incluindo integridade referencial, regras de negócio, consistência matemática e verificações específicas de cada tabela analítica.

Esses scripts servem como referência para decisões e verificações realizadas durante o desenvolvimento; não devem ser confundidos com uma suíte de testes automatizados executada a cada execução do pipeline.

#### `MANUAL_DEBUGGING.md` — Guia de Depuração Python

O arquivo `MANUAL_DEBUGGING.md` foi criado para documentar e resolver problemas de depuração e importação de módulos encontrados ao executar scripts Python fora do diretório `src/`.

O guia aborda:

- Diferenças entre executar scripts Python diretamente e executá-los como módulos.
- Configuração da depuração no VS Code por meio de `.vscode/launch.json`.
- Gerenciamento de imports entre diretórios do projeto.
- Configuração do diretório de trabalho e do interpretador Python com Poetry.
- Uso de breakpoints e ferramentas de depuração para inspecionar a execução entre vários módulos.

Essa documentação oferece uma referência reutilizável para solucionar problemas de execução e configurar a depuração de novos módulos Python sem modificar o código principal do pipeline.

### Arquivos de Configuração Complementares

| Arquivo ou diretório | Finalidade |
| --- | --- |
| `pyproject.toml` | Metadados do projeto, dependências e configuração de ferramentas. |
| `poetry.lock` | Versões fixadas das dependências para instalações reproduzíveis. |
| `poetry.toml` | Configuração local do Poetry para este projeto. |
| `.python-version` | Versão selecionada do Python. |
| `.gitignore` | Arquivos e diretórios excluídos do rastreamento do Git. |
| `.vscode/` | Configurações do editor e da depuração no VS Code. |
| `README.md` | Documentação principal do projeto. |

---

## Como Executar

### Pré-requisitos

Antes de executar o pipeline, verifique se as seguintes ferramentas estão disponíveis:

- **Python 3.12:** versão do Python utilizada durante o desenvolvimento do projeto.
- **Poetry:** utilizado para gerenciamento de dependências e isolamento do ambiente virtual.
- **Git:** necessário para clonar o repositório por comandos Git (opcional se o código-fonte for baixado como arquivo ZIP).

O projeto utiliza Poetry para gerenciar dependências Python e manter um ambiente de desenvolvimento reproduzível. O arquivo `pyproject.toml` define as dependências do projeto, enquanto `poetry.lock` registra as versões resolvidas para ajudar a manter instalações consistentes em diferentes ambientes.

Um editor de código, como o VS Code, é opcional.

### Clonar o Repositório

Clone o repositório com Git para obter uma cópia local do projeto:

```bash
git clone <repository-url>
```

Entre no diretório raiz do projeto:

```bash
cd retail-sales-intelligence-pipeline
```

A raiz do projeto contém `pyproject.toml` e `poetry.lock`, utilizados pelo Poetry para gerenciar dependências e configurar o ambiente de desenvolvimento.

A clonagem preserva o histórico do Git e a configuração do repositório remoto, permitindo acompanhar alterações e contribuir com o projeto.

### Preparar o Ambiente

Este projeto utiliza Poetry para gerenciar dependências e fornecer um ambiente Python isolado.

Depois de clonar o repositório e acessar sua raiz, instale as dependências necessárias:

```bash
poetry install
```

O Poetry utiliza `pyproject.toml` e `poetry.lock` para instalar as dependências do projeto e preparar seu ambiente virtual.

Para executar módulos Python usando o ambiente do projeto, utilize `poetry run`.

### Executar o Pipeline

Após instalar as dependências, execute o pipeline a partir da raiz do projeto:

```bash
poetry run python -m src.main
```

Esse comando executa o módulo principal usando o ambiente Python gerenciado pelo Poetry.

O módulo `src/main.py` coordena a execução do pipeline, incluindo extração, validação, transformação, modelagem analítica e armazenamento nas camadas Bronze, Silver e Gold.

### Saída Esperada

Após a execução bem-sucedida do pipeline, os conjuntos de dados processados são armazenados como arquivos Parquet em suas respectivas camadas.

| Camada | Diretório de Saída | Arquivos Parquet |
| --- | --- | ---: |
| Bronze | `data/bronze/` | 4 |
| Silver | `data/silver/` | 4 |
| Gold | `data/gold/` | 5 |
| **Total** | | **13** |

A camada Gold produz os seguintes conjuntos de dados analíticos:

- `dim_products.parquet`
- `dim_stores.parquet`
- `dim_date.parquet`
- `fact_sales.parquet`
- `fact_fixed_costs.parquet`

Os desenvolvedores podem conferir se os arquivos esperados foram gerados e inspecionar seu conteúdo com Pandas.

Verificações adicionais de qualidade e consistência foram realizadas durante o desenvolvimento por meio dos scripts exploratórios de `exploration_gold/`, especialmente `validate_gold.py`.

Essas validações detalhadas da Gold ainda são executadas separadamente do pipeline principal.

## Tecnologias Utilizadas

Este projeto utiliza Python e seu ecossistema de processamento de dados para construir um pipeline ETL reproduzível, seguindo a arquitetura Bronze, Silver e Gold.

### Python 3.12 — Linguagem de Programação

Python foi escolhido como linguagem principal por seu amplo ecossistema de bibliotecas para processamento, transformação e automação de dados.

Essas bibliotecas fornecem ferramentas reutilizáveis que simplificam o desenvolvimento do pipeline e reduzem a necessidade de implementar operações comuns de processamento do zero.

### Pandas — Processamento de Dados

Pandas é a principal biblioteca utilizada para extração, limpeza, transformação e validação de dados ao longo do pipeline.

Os DataFrames funcionam como a principal estrutura tabular em memória, permitindo conversões de tipos, transformações de colunas, cálculos e verificações de qualidade.

### OpenPyXL — Leitura de Arquivos Excel

OpenPyXL é utilizado pelo Pandas como mecanismo de leitura (*engine*) de arquivos Excel (`.xlsx`).

Ele interpreta a estrutura das pastas de trabalho do Excel, incluindo abas, células e valores, permitindo que Pandas extraia os dados e os organize em DataFrames.

### PyArrow — Processamento Colunar e Serialização

PyArrow fornece o mecanismo utilizado por Pandas para ler e gravar arquivos Parquet.

Ele converte DataFrames para a representação colunar em memória do Apache Arrow e realiza a codificação e a serialização necessárias ao armazenamento em Parquet.

### Apache Parquet — Armazenamento de Dados

Apache Parquet é o principal formato de armazenamento nas camadas Bronze, Silver e Gold.

Foi escolhido por seu armazenamento colunar eficiente, recursos de compressão, suporte a esquemas tipados e capacidade de ler colunas selecionadas sem carregar conjuntos de dados completos.

Parquet também possui amplo suporte nas plataformas modernas de engenharia de dados e análise em nuvem.

### Poetry — Gerenciamento de Dependências e Ambientes

Poetry gerencia as dependências do projeto e ambientes virtuais Python isolados.

O arquivo `pyproject.toml` define metadados do projeto, requisitos de compatibilidade com Python e restrições de dependências.

O arquivo `poetry.lock` registra as versões resolvidas das dependências, permitindo instalações reproduzíveis em ambientes compatíveis.

### Git e GitHub — Versionamento e Hospedagem do Repositório

Git acompanha as alterações do código-fonte e mantém o histórico de versões do projeto por meio de commits.

GitHub oferece hospedagem remota para o repositório, tornando o código-fonte, a documentação e o histórico de desenvolvimento acessíveis a outros desenvolvedores.

---

## Limitações e Próximos Passos

A versão atual demonstra um pipeline local completo de Excel para Parquet, com camadas Bronze, Silver e Gold. As limitações e melhorias propostas a seguir descrevem **trabalhos futuros**, e não funcionalidades já implementadas no pipeline principal.

### 1. Execução Manual e Orquestração do Fluxo

**Limitação atual:** o pipeline precisa ser iniciado manualmente com `poetry run python -m src.main`. Atualmente não é executado de forma agendada nem em resposta a alterações no arquivo Excel de origem.

**Próximo passo:** introduzir um orquestrador de workflows, como **Apache Airflow**, para agendar execuções, coordenar as etapas do pipeline e monitorar o estado das tarefas. Um futuro fluxo orientado a eventos também poderia responder a arquivos novos ou atualizados, com mecanismos que evitem processar um arquivo antes de sua gravação estar concluída.

### 2. Logs de Execução, Monitoramento e Alertas de Falha

**Limitação atual:** o projeto ainda não possui um mecanismo integrado de logs estruturados, monitoramento centralizado das execuções ou notificações automáticas em caso de falha. A investigação de problemas exige inspecionar manualmente a saída da execução.

**Próximo passo:** adicionar logs por etapa para registrar eventos importantes e exceções, possivelmente utilizando o módulo padrão `logging` do Python ou **Loguru**. Com a orquestração pelo Airflow, utilizar seus logs de tarefas e sua interface web para investigar falhas e configurar notificações por e-mail ou outros canais. O Airflow identifica tarefas com falha por exceções não tratadas ou códigos de saída diferentes de zero; Loguru é opcional e não é necessário para sinalizar falhas ao Airflow.

### 3. Validações Manuais da Gold e Quarentena de Dados

**Limitação atual:** as verificações detalhadas em `exploration_gold/validate_gold.py` são executadas separadamente e não são chamadas automaticamente por `src.main`. Portanto, dados de negócio inválidos podem ser gravados na Gold sem passar por essas verificações a cada execução.

**Próximo passo:** refatorar as verificações existentes em funções de validação reutilizáveis e integrá-las à execução do pipeline. Validar as regras de negócio de entrada antes da modelagem Gold e verificar relacionamentos, chaves únicas, cálculos e consistência específicos da Gold **antes de publicar os arquivos Parquet dessa camada**.

Para problemas em registros individuais, implementar um fluxo de **quarentena de dados** (*data quarantine*) que:

- Separe registros aceitos e rejeitados (por exemplo, vendas com quantidade nula ou não positiva).
- Armazene os registros rejeitados em um conjunto de dados separado, com motivo explícito de rejeição e contexto suficiente para investigá-los.
- Informe as quantidades e os percentuais rejeitados, para que os usuários dos dados entendam eventuais exclusões.
- Utilize um limite configurável de rejeições; falhas estruturais críticas ou uma taxa de rejeição acima do limite permitido devem impedir a publicação, em vez de produzir silenciosamente dados incompletos ou pouco confiáveis.

Uma biblioteca declarativa de validação de DataFrames, como **Pandera**, poderá ser avaliada posteriormente. Entretanto, as verificações automáticas podem ser implementadas inicialmente com a lógica já existente em Pandas.

### 4. Reprocessamento Completo em Vez de Atualizações Incrementais

**Limitação atual:** cada execução lê e processa todo o conjunto de dados do Excel, mesmo quando apenas algumas vendas foram adicionadas ou corrigidas. Isso pode aumentar os custos de processamento conforme o volume de dados cresce e atrasar as atualizações das análises.

**Próximo passo:** implementar **processamento incremental** para distinguir entre:

- **Vendas novas:** valores de `sale_id` ainda não processados, independentemente de `sale_date`.
- **Vendas modificadas:** valores de `sale_id` já processados cujos atributos de negócio foram alterados.
- **Vendas recebidas com atraso:** registros recebidos recentemente com datas de transação antigas, que ainda precisam ser incluídos nos resultados analíticos.

Uma primeira implementação poderia comparar os registros atuais com os já processados usando `merge()` do Pandas e aplicar lógica de inserção/atualização (**upsert**). Para sistemas maiores, avaliar campos de rastreamento de alterações, como `updated_at`, ou captura de alterações de dados (*Change Data Capture*, CDC). Com um único arquivo Excel acumulativo, talvez ainda seja necessário ler toda a origem para identificar mudanças, mesmo que depois somente os registros novos ou modificados sejam transformados.

Essas melhorias tornariam o pipeline mais confiável, observável e escalável, preservando a arquitetura em camadas existente.
