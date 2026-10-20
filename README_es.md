# Retail Sales Intelligence Pipeline

## Descripción General del Proyecto

Este proyecto procesa un libro de Excel (`.xlsx`) con varias hojas, cada una de las cuales representa datos operativos históricos de una empresa minorista.

Los datos proporcionados por la empresa incluyen ventas, productos, tiendas y costos fijos.

El pipeline lee cada hoja, convierte los datos en tablas Parquet, valida la información y aplica comprobaciones de calidad para prepararla para el análisis.

El resultado final busca responder preguntas importantes del negocio, como:

- ¿Dónde vende más la empresa?
- ¿Las ventas son suficientes para cubrir los costos fijos?
- ¿Cuáles son los productos más vendidos?
- ¿Qué productos tienen pocas ventas o ninguna?
- ¿Qué tienda genera el mayor volumen de ventas?

---

## Arquitectura

El proyecto sigue una arquitectura de datos por capas: Bronze, Silver y Gold.

```text
Excel (.xlsx)
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Análisis / BI
```

### Capa Bronze

La capa Bronze recibe el archivo original de Excel (`.xlsx`), donde cada hoja representa un conjunto de datos operativos diferente.

Mediante Pandas, cada hoja se extrae y se carga en un diccionario de DataFrames. Después, cada DataFrame se valida para confirmar que contiene las columnas esperadas y se guarda como una tabla Parquet.

El flujo de datos de esta capa es:

```text
Excel (.xlsx)
    ↓
Extracción con Pandas
    ↓
Diccionario de DataFrames
    ↓
Validación de columnas
    ↓
Tablas Parquet
    ↓
Capa Silver
```

Funciones principales utilizadas en la capa Bronze:

- `read_excel`
- `validate_all_columns`
- `save_parquet`

### Capa Silver

La capa Silver es donde los datos comienzan a transformarse según las reglas de negocio y de calidad definidas para cada conjunto de datos.

Entre las principales transformaciones realizadas en esta capa se incluyen:

- revisar y corregir tipos de datos, como campos numéricos, fechas y cadenas de texto;
- estandarizar nombres de columnas inconsistentes;
- redondear valores numéricos cuando sea necesario;
- crear columnas derivadas en las tablas de hechos, como métricas de ventas del tipo `gross_amount` y otros campos calculados.

Antes de implementar la lógica definitiva de transformación, se utilizó un archivo `exploration_silver` para probar y validar los pasos de transformación. Esto ayudó a evitar la incorporación de lógica experimental o innecesaria al código principal del pipeline.

El flujo de datos de esta capa es:

```text
Tablas Parquet de Bronze
    ↓
Lectura en DataFrames
    ↓
Aplicación de transformaciones
    ↓
Devolución de DataFrames transformados
    ↓
Guardado de tablas Parquet de Silver
```

Funciones principales utilizadas en la capa Silver:

- `read_parquet_files`
- `transform_all_dataframes_bronze`
- `save_parquet`

`read_parquet_files` carga las tablas Parquet de Bronze en DataFrames.

`transform_all_dataframes_bronze` recibe los DataFrames, aplica la lógica de transformación necesaria para cada conjunto de datos y devuelve un diccionario con los DataFrames transformados.

`save_parquet` recibe los DataFrames transformados y los escribe en la ruta configurada para Silver.

### Capa Gold

La capa Gold es la etapa final del pipeline, donde los datos se modelan específicamente para apoyar el análisis del negocio.

El diseño de esta capa responde a las principales preguntas que el proyecto pretende resolver, como:

- ¿Cuáles son los productos más vendidos?
- ¿Las ventas son suficientes para cubrir los costos fijos?
- ¿Qué productos tienen pocas ventas o ninguna?
- ¿Qué tienda genera el mayor volumen de ventas?

Para responder estas preguntas, el modelo analítico se estructuró mediante un enfoque de modelado dimensional basado en un esquema en estrella, con tablas de hechos que contienen eventos de negocio medibles y tablas de dimensiones que aportan contexto descriptivo para el análisis.

Las principales tablas de dimensiones son:

- `dim_date`: generada dentro del proyecto para permitir filtros y análisis temporales.
- `dim_products`: creada para analizar las ventas desde la perspectiva de los productos.
- `dim_stores`: creada para analizar las ventas y los costos fijos desde la perspectiva de las tiendas.

Las principales tablas de hechos son:

- `fact_sales`: contiene las principales transacciones de venta y métricas relacionadas con los productos y las tiendas.
- `fact_fixed_costs`: contiene los costos fijos asociados con cada tienda o canal de ventas, como alquiler, nómina, servicios y otros gastos.

El modelo general sigue esta estructura:

```text
              dim_date
                 |
                 |
dim_products — fact_sales — dim_stores
                               |
                               |
                      fact_fixed_costs
```

Como el modelo contiene dos tablas de hechos que comparten dimensiones, no es un único esquema en estrella clásico. Sin embargo, sigue un enfoque de modelado dimensional con dimensiones compartidas.

---

## Modelo de Datos

La capa Gold está organizada en tablas de dimensiones y hechos diseñadas para responder las principales preguntas del negocio.

### Tablas de Dimensiones

- `dim_stores`: representa las tiendas o puntos de venta.
- `dim_products`: representa los productos vendidos.
- `dim_date`: representa la dimensión calendario utilizada para filtros y análisis temporales.

### Tablas de Hechos

- `fact_sales`: representa las transacciones de venta y las principales métricas relacionadas con cada venta.
- `fact_fixed_costs`: representa los costos fijos mensuales asociados con tiendas o canales de ventas.

### Claves Lógicas

Las siguientes columnas actúan como identificadores lógicos del modelo analítico:

- `dim_stores.store_id`: identificador lógico de cada tienda.
- `dim_products.product_id`: identificador lógico de cada producto.
- `fact_sales.sale_id`: identificador único de cada transacción de venta.
- `dim_date.date`: identificador lógico de cada fecha del calendario.
- `fact_fixed_costs`: su unicidad lógica se define por la combinación de `store_id` y `start_month`.

### Relaciones Esperadas

El modelo analítico contempla las siguientes relaciones lógicas:

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

Actualmente, estas son relaciones lógicas dentro del modelo analítico. Se revisan mediante las validaciones del proyecto, pero no se imponen mediante restricciones de clave primaria (*Primary Key*) o clave foránea (*Foreign Key*) de una base de datos, porque las tablas analíticas se almacenan como archivos Parquet y no en una base de datos relacional.

---

## Calidad de Datos y Validación

Los conjuntos de datos de Gold se exploraron y validaron para comprobar consistencia estructural, integridad referencial, reglas de negocio y valores calculados. La lógica de validación exploratoria está disponible en `exploration_gold/validate_gold.py`.

### Validación de `fact_sales`

- **Columnas y tipos de datos:** comprobación de nombres y tipos de datos frente a la estructura esperada.
- **Valores nulos:** no se encontraron valores nulos.
- **Cantidad de registros:** la tabla Gold contiene **239 registros de ventas**.
- **Unicidad:** revisión de duplicados en `sale_id`; no se encontraron.
- **Integridad referencial:** comprobación de `product_id`, `store_id` y fechas de venta frente a sus respectivas tablas de dimensiones.
- **Rangos válidos:** verificación de valores positivos en `quantity` y `unit_price_brl`, así como del rango esperado de `discount_pct`.
- **Campos calculados:** auditoría de `gross_amount`, `discount_amount` y `net_amount` para comprobar consistencia matemática y comportamiento del redondeo, además de otras comprobaciones de valores inválidos.
- **Resultado:** no se encontraron inconsistencias significativas de calidad según las reglas evaluadas.

### Validación de `dim_products`

- **Identidad y duplicados:** comprobación de que `product_id` identifica cada producto de forma única; no se encontraron IDs repetidos.
- **Categorías:** comparación de los valores de `category` con una lista de categorías aceptadas mediante `isin()`.
- **Costos:** se exigió que `unit_cost` fuera mayor que cero. También se investigaron costos inusualmente altos mediante un umbral de tres veces la media.
- **Moneda del proveedor:** se aceptaron únicamente `BRL` y `USD`, utilizando `isin()`.
- **Estado activo:** confirmación de valores booleanos en `active` e inspección de su distribución con `value_counts()`; los seis productos estaban activos.
- **Resultado:** no se encontraron inconsistencias según las reglas actuales del proyecto.

### Validación de `dim_stores`

- **Identidad y duplicados:** comprobación de `store_id` con `duplicated()` y `sum()`.
- **Cadenas vacías:** implementación de una función reutilizable que recorre las columnas de texto, aplica `strip()` y `len()` y devuelve un diccionario con la cantidad de cadenas vacías por columna. Las comprobaciones de valores nulos se realizan por separado.
- **Canales de venta:** comprobación de `channel` frente a los valores aceptados `Física` y `Online` mediante `isin()`.
- **Posibles duplicados de negocio:** investigación de combinaciones repetidas de atributos de tiendas mediante `duplicated(subset=..., keep=False)` y de nombres de tiendas asociados con múltiples IDs mediante `groupby()` y `nunique()`.
- **Consistencia ciudad/estado:** se identificó la necesidad de una tabla de referencia o API confiable para comprobar combinaciones de ciudad y estado; esta validación externa todavía no se ha implementado.
- **Resultado:** las comprobaciones implementadas no identificaron inconsistencias.

### Validación de `fact_fixed_costs`

- **Unicidad mensual:** verificación de la combinación `store_id` y `start_month` mediante `duplicated()` y `groupby().size()`.
- **Integridad referencial:** comprobación mediante `isin()` de que cada `store_id` existe en `dim_stores`; no se encontraron relaciones inválidas.
- **Costos negativos:** desarrollo de una función reutilizable que cuenta valores negativos por columna monetaria y devuelve un resumen en un diccionario.
- **Análisis de costos cero:** recuento de ceros por columna y uso de máscaras booleanas con `any(axis=1)` para identificar filas que contienen al menos un costo igual a cero.
- **Regla de negocio para alquiler:** un alquiler igual a cero puede ser válido para un canal en línea. Se utilizó un `merge` izquierdo con `dim_stores` para comprobar si existían tiendas físicas con `rent_brl = 0`; no se encontraron inconsistencias de ese tipo.
- **Consistencia de fechas:** comprobación de que `start_month` corresponde al primer día del mes; no se encontraron fechas inválidas.
- **Posibles valores atípicos:** recuento de costos superiores a **tres veces la media de cada columna**, con resultados por columna. Se trata de una heurística exploratoria, no de una restricción formal del negocio.
- **Resultado:** no se identificaron inconsistencias en las reglas estructurales, referenciales o de negocio comprobadas.

### Validación de `dim_date`

La dimensión de fechas se genera mediante programación y no se importa desde una fuente externa; por eso, las comprobaciones se centran en su consistencia interna.

- **Unicidad:** comprobación de `date` con `duplicated()`; no se encontraron fechas duplicadas.
- **Continuidad:** cálculo de las diferencias entre fechas consecutivas mediante `diff()` y comparación con `pd.Timedelta(days=1)`; no se detectaron saltos.
- **Campos derivados:** verificación de `year` y `month` frente a `date.dt.year` y `date.dt.month` mediante máscaras booleanas.
- **Resultado:** todas las comprobaciones implementadas fueron satisfactorias: no hubo fechas duplicadas, saltos en la secuencia ni inconsistencias de año o mes.

---
## Estructura del Proyecto

El repositorio separa los archivos de datos, el código fuente de Python y los scripts exploratorios para mantener organizada la lógica de procesamiento y facilitar el seguimiento de problemas entre las etapas del pipeline.

### Estructura de Directorios

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

### Responsabilidades de los Directorios y Módulos

#### `data/` — Almacenamiento de Datos

El directorio `data/` está separado del código fuente de Python para mejorar la organización del proyecto y evitar mezclar conjuntos de datos con el código de la aplicación.

El directorio sigue una **Arquitectura Medallion**, donde cada capa almacena datos en una etapa distinta del procesamiento:

- **Raw:** contiene los archivos Excel originales recibidos de la fuente de datos.
- **Bronze:** almacena los conjuntos de datos extraídos en formato Parquet después de la validación inicial de columnas.
- **Silver:** contiene los conjuntos de datos limpios y transformados a partir de la capa Bronze.
- **Gold:** almacena las tablas analíticas modeladas para el análisis del negocio.

Esta organización mejora la **trazabilidad de los datos**, lo que facilita investigar errores, identificar la etapa en la que surgió un problema e inspeccionar los datos en distintos puntos del pipeline.

#### `src/` — Código Fuente

El directorio `src/` contiene el código Python principal encargado de ejecutar el pipeline y aplicar la lógica de procesamiento de datos.

A diferencia de `data/`, que almacena conjuntos de datos en distintas etapas, `src/` contiene las funciones y módulos que extraen, validan, transforman, modelan y guardan los datos.

La lógica del proyecto se divide en módulos Python independientes en lugar de concentrarse en un solo archivo. Este enfoque mejora la **reutilización del código, la mantenibilidad y la separación de responsabilidades**, y permite importar y reutilizar funciones en distintas partes del proyecto.

#### `src/main.py` — Ejecución del Pipeline

El módulo `main.py` actúa como punto de entrada principal y coordina la ejecución de las diferentes etapas del pipeline.

Importa funciones de otros módulos, transmite los parámetros necesarios y utiliza los resultados de cada operación para ejecutar la siguiente etapa del flujo de datos.

Así, el flujo de ejecución permanece organizado sin concentrar toda la lógica de procesamiento en un único archivo.

#### `src/config.py` — Configuración Centralizada

El módulo `config.py` centraliza la configuración del proyecto, incluidos las rutas de archivos, las columnas obligatorias y las listas auxiliares utilizadas a lo largo del pipeline.

Mantener estas configuraciones en un único lugar evita duplicación de código, facilita el mantenimiento y reduce el riesgo de inconsistencias cuando es necesario introducir cambios.

#### `src/extract.py` — Extracción de Datos

El módulo `extract.py` se encarga de leer los datos de las fuentes del proyecto.

Recibe las rutas definidas en `config.py` y extrae información de libros de Excel, devolviendo un diccionario de DataFrames de Pandas donde cada DataFrame representa una hoja.

Este módulo también proporciona funcionalidades para leer archivos Parquet de capas previamente procesadas.

Separar la extracción de la transformación mejora la organización y permite cambiar la lógica de procesamiento sin modificar la forma de leer los datos originales.

#### `src/validate.py` — Validación de la Estructura de Datos

El módulo `validate.py` comprueba si los conjuntos de datos extraídos contienen las columnas obligatorias definidas en `config.py`.

Valida la estructura de cada DataFrame comparándola con las listas esperadas de columnas.

Si faltan columnas obligatorias, la validación lanza un error que identifica el conjunto de datos afectado y las columnas ausentes.

Este proceso ayuda a impedir que estructuras de datos inesperadas avancen a las siguientes etapas, reduciendo errores y trabajo innecesario.

#### `src/load.py` — Almacenamiento de Datos

El módulo `load.py` guarda los DataFrames procesados en las rutas de destino recibidas como parámetros.

Recibe un diccionario de DataFrames y una ruta de salida, y genera archivos Parquet individuales utilizando las claves del diccionario como nombres de archivo.

Separar el almacenamiento de la extracción y la transformación mejora la organización, la reutilización y el mantenimiento del código. También permite modificar la lógica de almacenamiento sin cambiar los procesos de extracción o transformación.

#### `src/transform.py` — Transformación de Datos

El módulo `transform.py` aplica reglas de limpieza y transformación a los conjuntos de datos extraídos de Bronze.

Las principales transformaciones incluyen:

- Creación de nuevas columnas calculadas.
- Cambio y estandarización de nombres de columnas.
- Conversión de columnas a tipos de datos adecuados.
- Aplicación de transformaciones según la estructura y las reglas de negocio de cada conjunto de datos.

Cada conjunto de datos necesita reglas distintas. Por ejemplo, una tabla de productos contiene principalmente información descriptiva, mientras que una tabla de hechos de ventas necesita cálculos adicionales para generar métricas del negocio.

La función `transform_all_dataframes_bronze()` recibe un diccionario de DataFrames y coordina la ejecución de las funciones de transformación correspondientes a cada conjunto de datos.

Después del procesamiento, devuelve un diccionario de DataFrames limpios y transformados, listos para guardarse en Silver.

#### `src/model.py` — Modelado Analítico de Datos

El módulo `model.py` se encarga de construir las tablas analíticas de la capa Gold.

A diferencia de `transform.py`, que se centra en limpiar y transformar datos, `model.py` organiza los conjuntos procesados en un modelo dimensional diseñado para responder preguntas del negocio.

El enfoque se basa en un diseño de esquema en estrella y utiliza dos tipos de tablas:

- **Tablas de dimensiones:** `dim_products`, `dim_stores` y `dim_date` proporcionan información descriptiva y permiten realizar filtros y análisis.
- **Tablas de hechos:** `fact_sales` y `fact_fixed_costs` contienen transacciones del negocio y valores medibles relacionados con ventas y costos operativos.

La función `build_gold_model()` recibe un diccionario de DataFrames de Silver, junto con una fecha inicial y final para generar la dimensión calendario.

Coordina la creación de las tablas analíticas y devuelve un diccionario de DataFrames Gold, que posteriormente se guardan en formato Parquet.

Esta estructura hace que los datos sean más adecuados para herramientas analíticas como Power BI y permite crear relaciones, métricas, informes y dashboards.

#### `exploration_bronze/` y `exploration_gold/` — Exploración y Validación de Datos

Estos directorios contienen scripts exploratorios utilizados para desarrollar, probar y verificar la lógica de procesamiento de manera independiente de los módulos principales del pipeline.

Separar el código exploratorio ayuda a mantener organizados los módulos orientados a la ejecución y evita que lógica experimental o innecesaria quede integrada en el flujo principal.

- **`exploration_bronze/explore_bronze.py`:** utilizado para la exploración inicial de datos y pruebas relacionadas con la extracción.
- **`exploration_gold/explore_gold.py`:** utilizado para examinar la estructura general y calidad de las tablas Gold, incluidos valores nulos, registros duplicados y otras comprobaciones iniciales.
- **`exploration_gold/validate_gold.py`:** utilizado para validaciones de calidad más detalladas, como integridad referencial, reglas de negocio, consistencia matemática y comprobaciones específicas de cada tabla analítica.

Estos scripts sirven como referencia de las decisiones y comprobaciones realizadas durante el desarrollo; no deben confundirse con un conjunto de pruebas automatizadas que se ejecuta en cada ejecución del pipeline.

#### `MANUAL_DEBUGGING.md` — Guía de Depuración en Python

El archivo `MANUAL_DEBUGGING.md` se creó para documentar y resolver problemas de depuración e importación de módulos encontrados al ejecutar scripts Python ubicados fuera del directorio `src/`.

La guía aborda:

- Diferencias entre ejecutar scripts Python directamente y ejecutarlos como módulos.
- Configuración de la depuración en VS Code mediante `.vscode/launch.json`.
- Administración de imports entre distintos directorios del proyecto.
- Configuración del directorio de trabajo y del intérprete de Python con Poetry.
- Uso de breakpoints y herramientas de depuración para inspeccionar la ejecución entre múltiples módulos.

Esta documentación ofrece una referencia reutilizable para resolver problemas de ejecución y configurar la depuración de nuevos módulos Python sin modificar el código principal del pipeline.

### Archivos de Configuración Complementarios

| Archivo o directorio | Propósito |
| --- | --- |
| `pyproject.toml` | Metadatos del proyecto, dependencias y configuración de herramientas. |
| `poetry.lock` | Versiones fijadas de dependencias para instalaciones reproducibles. |
| `poetry.toml` | Configuración local de Poetry para este proyecto. |
| `.python-version` | Versión seleccionada de Python. |
| `.gitignore` | Archivos y directorios excluidos del seguimiento de Git. |
| `.vscode/` | Configuración del editor y la depuración en VS Code. |
| `README.md` | Documentación principal del proyecto. |

---

## Cómo Ejecutar el Proyecto

### Requisitos Previos

Antes de ejecutar el pipeline, comprueba que estén disponibles las siguientes herramientas:

- **Python 3.12:** versión de Python utilizada durante el desarrollo del proyecto.
- **Poetry:** utilizado para administrar dependencias y aislar el entorno virtual.
- **Git:** necesario para clonar el repositorio mediante comandos Git (opcional si descargas el código fuente como archivo ZIP).

El proyecto utiliza Poetry para administrar dependencias de Python y mantener un entorno de desarrollo reproducible. El archivo `pyproject.toml` define las dependencias del proyecto, mientras que `poetry.lock` registra sus versiones resueltas para facilitar instalaciones consistentes entre entornos.

Un editor de código, como VS Code, es opcional.

### Clonar el Repositorio

Clona el repositorio con Git para obtener una copia local del proyecto:

```bash
git clone <repository-url>
```

Accede al directorio raíz del proyecto:

```bash
cd retail-sales-intelligence-pipeline
```

En la raíz se encuentran los archivos `pyproject.toml` y `poetry.lock`, que Poetry utiliza para administrar las dependencias y configurar el entorno de desarrollo.

La clonación conserva el historial de Git y la configuración del repositorio remoto, lo que permite seguir los cambios y colaborar en el proyecto.

### Preparación del Entorno

Este proyecto utiliza Poetry para administrar dependencias y proporcionar un entorno Python aislado.

Después de clonar el repositorio y entrar en la raíz del proyecto, instala las dependencias necesarias:

```bash
poetry install
```

Poetry utiliza `pyproject.toml` y `poetry.lock` para instalar las dependencias del proyecto y preparar su entorno virtual.

Para ejecutar módulos Python mediante el entorno del proyecto, utiliza `poetry run`.

### Ejecutar el Pipeline

Tras instalar las dependencias, ejecuta el pipeline desde la raíz del proyecto:

```bash
poetry run python -m src.main
```

Este comando ejecuta el módulo principal utilizando el entorno Python administrado por Poetry.

El módulo `src/main.py` coordina el pipeline, incluidas las etapas de extracción, validación, transformación, modelado analítico y almacenamiento en Bronze, Silver y Gold.

### Resultado Esperado

Una vez que el pipeline se ejecuta correctamente, los conjuntos de datos procesados se guardan como archivos Parquet en las capas correspondientes.

| Capa | Directorio de Salida | Archivos Parquet |
| --- | --- | ---: |
| Bronze | `data/bronze/` | 4 |
| Silver | `data/silver/` | 4 |
| Gold | `data/gold/` | 5 |
| **Total** | | **13** |

La capa Gold genera los siguientes conjuntos de datos analíticos:

- `dim_products.parquet`
- `dim_stores.parquet`
- `dim_date.parquet`
- `fact_sales.parquet`
- `fact_fixed_costs.parquet`

Los desarrolladores pueden verificar que se generaron los archivos esperados e inspeccionar su contenido utilizando Pandas.

Durante el desarrollo se realizaron comprobaciones adicionales de calidad y consistencia mediante los scripts exploratorios de `exploration_gold/`, especialmente `validate_gold.py`.

Estas validaciones detalladas de Gold todavía se ejecutan por separado del pipeline principal.

## Tecnologías Utilizadas

Este proyecto utiliza Python y su ecosistema de procesamiento de datos para construir un pipeline ETL reproducible siguiendo la arquitectura Bronze, Silver y Gold.

### Python 3.12 — Lenguaje de Programación

Python se eligió como lenguaje principal debido a su amplio ecosistema de bibliotecas para procesamiento, transformación y automatización de datos.

Estas bibliotecas proporcionan herramientas reutilizables que simplifican el desarrollo del pipeline y reducen la necesidad de implementar operaciones comunes de procesamiento desde cero.

### Pandas — Procesamiento de Datos

Pandas es la biblioteca principal utilizada para extraer, limpiar, transformar y validar los datos a lo largo del pipeline.

Los DataFrames funcionan como la principal estructura de datos tabular en memoria y permiten realizar conversiones de tipos, transformaciones de columnas, cálculos y comprobaciones de calidad.

### OpenPyXL — Lectura de Archivos Excel

OpenPyXL es utilizado por Pandas como motor de lectura (*engine*) de archivos Excel (`.xlsx`).

Interpreta la estructura de los libros de Excel, incluidas hojas, celdas y valores, y permite que Pandas extraiga los datos y los organice en DataFrames.

### PyArrow — Procesamiento Columnar y Serialización

PyArrow proporciona el motor que utiliza Pandas para leer y escribir archivos Parquet.

Convierte DataFrames a la representación columnar en memoria de Apache Arrow y realiza la codificación y serialización necesarias para el almacenamiento en Parquet.

### Apache Parquet — Almacenamiento de Datos

Apache Parquet es el formato principal de almacenamiento en las capas Bronze, Silver y Gold.

Se eligió por su almacenamiento columnar eficiente, sus capacidades de compresión, su soporte para esquemas tipados y su capacidad para leer columnas seleccionadas sin cargar conjuntos de datos completos.

Parquet también es ampliamente compatible con las plataformas modernas de ingeniería de datos y análisis en la nube.

### Poetry — Gestión de Dependencias y Entornos

Poetry administra las dependencias del proyecto y los entornos virtuales aislados de Python.

El archivo `pyproject.toml` define los metadatos del proyecto, los requisitos de compatibilidad con Python y las restricciones de dependencias.

El archivo `poetry.lock` registra las versiones resueltas de las dependencias, lo que favorece instalaciones reproducibles en entornos compatibles.

### Git y GitHub — Control de Versiones y Alojamiento del Repositorio

Git registra los cambios del código fuente y conserva el historial de versiones del proyecto mediante commits.

GitHub proporciona alojamiento remoto del repositorio y permite compartir el código fuente, la documentación y el historial de desarrollo con otros desarrolladores.

---

## Limitaciones y Próximos Pasos

La versión actual demuestra un pipeline local completo de Excel a Parquet, con las capas Bronze, Silver y Gold. Las siguientes limitaciones y mejoras propuestas describen **trabajos futuros**, no funcionalidades ya implementadas en el pipeline principal.

### 1. Ejecución Manual y Orquestación del Flujo

**Limitación actual:** el pipeline debe iniciarse manualmente con `poetry run python -m src.main`. Actualmente no se ejecuta de manera programada ni como respuesta a cambios en el Excel de origen.

**Próximo paso:** incorporar un orquestador de flujos de trabajo, como **Apache Airflow**, para programar ejecuciones, coordinar las etapas del pipeline y supervisar el estado de las tareas. Un flujo futuro orientado a eventos también podría responder a archivos nuevos o actualizados, con medidas para evitar procesar un archivo antes de que termine de escribirse.

### 2. Logs de Ejecución, Monitoreo y Alertas de Fallos

**Limitación actual:** el proyecto todavía no cuenta con un mecanismo integrado de logs estructurados, monitoreo centralizado de ejecuciones ni notificaciones automáticas cuando una ejecución falla. La resolución de problemas requiere inspeccionar manualmente la salida de la ejecución.

**Próximo paso:** agregar logs por etapa para registrar eventos importantes y excepciones, posiblemente mediante el módulo estándar `logging` de Python o **Loguru**. Cuando el pipeline esté orquestado con Airflow, utilizar sus logs de tareas y su interfaz web para investigar fallos, y configurar alertas por correo u otros canales. Airflow puede reconocer tareas fallidas mediante excepciones no controladas o códigos de salida distintos de cero; Loguru es opcional y no es necesario para indicar un fallo a Airflow.

### 3. Validaciones Manuales de Gold y Cuarentena de Datos

**Limitación actual:** las comprobaciones detalladas de `exploration_gold/validate_gold.py` se ejecutan por separado y no son llamadas automáticamente desde `src.main`. Por lo tanto, podrían guardarse datos de negocio inválidos en Gold sin pasar por estas comprobaciones durante cada ejecución.

**Próximo paso:** reorganizar las comprobaciones existentes en funciones de validación reutilizables e integrarlas en la ejecución del pipeline. Validar las reglas de negocio de entrada antes de construir Gold y verificar las relaciones, claves únicas, cálculos y consistencia propios del modelo Gold **antes de publicar los archivos Parquet de esa capa**.

Para problemas que afectan registros individuales, implementar un flujo de **cuarentena de datos** (*data quarantine*) que:

- Separe los registros aceptados y rechazados (por ejemplo, ventas con cantidades nulas o no positivas).
- Guarde los registros rechazados en un conjunto de datos separado, con un motivo explícito del rechazo y suficiente contexto para investigarlo.
- Informe el número y porcentaje de registros rechazados para que los usuarios posteriores comprendan las exclusiones.
- Utilice un límite configurable de rechazos; los fallos estructurales críticos o una tasa de rechazo superior al máximo permitido deben detener la publicación en vez de generar silenciosamente datos incompletos o poco confiables.

Más adelante podría evaluarse una biblioteca declarativa de validación de DataFrames como **Pandera**, pero las comprobaciones automáticas pueden implementarse primero con la lógica de Pandas que ya tiene el proyecto.

### 4. Reprocesamiento Completo en Lugar de Actualizaciones Incrementales

**Limitación actual:** cada ejecución lee y procesa todo el conjunto de datos de Excel, incluso cuando solamente se añadieron o corrigieron unas pocas ventas. Esto puede aumentar el costo del procesamiento a medida que crece el volumen de datos y retrasar la actualización de los análisis.

**Próximo paso:** implementar **procesamiento incremental** para distinguir entre:

- **Ventas nuevas:** valores de `sale_id` que todavía no se han procesado, independientemente de `sale_date`.
- **Ventas modificadas:** valores de `sale_id` previamente procesados cuyos atributos de negocio han cambiado.
- **Ventas recibidas con retraso:** registros recibidos recientemente con fechas de transacción antiguas que también deben incluirse en los resultados analíticos.

Una primera implementación podría comparar los registros actuales con los ya procesados mediante `merge()` de Pandas y aplicar una lógica de inserción/actualización (**upsert**). Para sistemas más grandes, se podrían evaluar campos que registren modificaciones, como `updated_at`, o captura de cambios de datos (*Change Data Capture*, CDC). Con un único Excel acumulativo, quizá todavía sea necesario leer el archivo completo para descubrir cambios, aunque después solo se transformen los registros nuevos o modificados.

Estas mejoras harían que el pipeline fuera más confiable, observable y escalable, manteniendo la arquitectura por capas existente.
