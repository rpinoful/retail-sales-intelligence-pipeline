# Retail Sales Intelligence Pipeline

## Project Overview

This project processes an Excel workbook (`.xlsx`) with multiple sheets, where each sheet represents historical operational data from a retail store.

The data provided by the store includes sales, products, stores, and fixed costs.

The pipeline reads each sheet, converts the data into Parquet tables, validates the information, and applies data quality checks to prepare it for analysis.

The final result is intended to answer key business questions such as:

- Where does the company sell the most?
- Are sales enough to cover fixed costs?
- Which products sell the most?
- Which products have low or no sales?
- Which store generates the most sales?

---

## Architecture

The project follows a layered data architecture using Bronze, Silver, and Gold layers.

```text
Excel (.xlsx)
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
Analysis / BI
```

### Bronze Layer

The Bronze layer receives the raw Excel (`.xlsx`) file, where each sheet represents a different operational dataset.

Using Pandas, each sheet is extracted and loaded into a dictionary of DataFrames. Each DataFrame is then validated to confirm that the expected columns are present and is saved as a Parquet table.

The data flow in this layer is:

```text
Excel (.xlsx)
    ↓
Pandas extraction
    ↓
Dictionary of DataFrames
    ↓
Column validation
    ↓
Parquet tables
    ↓
Silver layer
```

Main functions used in the Bronze layer:

- `read_excel`
- `validate_all_columns`
- `save_parquet`

### Silver Layer

The Silver layer is where the data starts to be transformed according to the business and data quality rules defined for each dataset.

Some of the main transformations applied in this layer include:

- reviewing and correcting data types such as numeric, date, and string fields;
- standardizing inconsistent column names;
- rounding numeric values when necessary;
- creating derived columns in fact tables, such as sales metrics like `gross_amount` and related calculated fields.

Before implementing the final transformation logic, an `exploration_silver` file was used to test and validate the transformation steps. This helped avoid unnecessary or experimental logic in the main pipeline code.

The data flow in this layer is:

```text
Bronze Parquet tables
    ↓
Read into DataFrames
    ↓
Apply transformations
    ↓
Return transformed DataFrames
    ↓
Save as Silver Parquet tables
```

Main functions used in the Silver layer:

- `read_parquet_files`
- `transform_all_dataframes_bronze`
- `save_parquet`

`read_parquet_files` loads the Bronze Parquet tables into DataFrames.

`transform_all_dataframes_bronze` receives the DataFrames, applies the transformation logic required for each dataset, and returns a dictionary with the transformed DataFrames.

`save_parquet` receives the transformed DataFrames and writes them to the configured Silver path.

### Gold Layer

The Gold layer is the final stage of the pipeline, where the data is modeled specifically to support business analysis.

The design of this layer is driven by the main business questions the project aims to answer, such as:

- Which products sell the most?
- Are sales enough to cover fixed costs?
- Which products have low or no sales?
- Which store generates the most sales?

To support these questions, the analytical model was structured using a dimensional modeling approach based on a star schema, with fact tables containing measurable business events and dimension tables providing descriptive context for analysis.

The main dimension tables are:

- `dim_date`: generated within the project to support filtering and time-based analysis.
- `dim_products`: created to analyze sales from the product perspective.
- `dim_stores`: created to analyze sales and fixed costs from the store perspective.

The main fact tables are:

- `fact_sales`: contains the main sales transactions and metrics related to products and stores.
- `fact_fixed_costs`: contains the fixed costs associated with each store or sales channel, such as rent, payroll, utilities, and other expenses.

The general model follows this structure:

```text
              dim_date
                 |
                 |
dim_products — fact_sales — dim_stores
                               |
                               |
                      fact_fixed_costs
```

Because the model contains two fact tables sharing dimensions, it is not a single classic star schema, but it still follows a dimensional modeling approach with shared dimensions.

---

## Data Model

The Gold layer is organized around dimension and fact tables designed to support the main business questions of the project.

### Dimension Tables

- `dim_stores`: represents the stores or sales locations.
- `dim_products`: represents the products sold by the store.
- `dim_date`: represents the calendar dimension used for time-based analysis and filtering.

### Fact Tables

- `fact_sales`: represents sales transactions and the main metrics related to each sale.
- `fact_fixed_costs`: represents monthly fixed costs associated with stores or sales channels.

### Logical Keys

The following columns act as logical identifiers in the analytical model:

- `dim_stores.store_id`: logical identifier for each store.
- `dim_products.product_id`: logical identifier for each product.
- `fact_sales.sale_id`: unique identifier for each sales transaction.
- `dim_date.date`: logical identifier for each calendar date.
- `fact_fixed_costs`: its logical uniqueness is defined by the combination of `store_id` and `start_month`.

### Expected Relationships

The analytical model expects the following logical relationships:

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

These relationships are currently logical relationships within the analytical model. They are validated through the pipeline, but they are not enforced through database Primary Key / Foreign Key constraints because the project currently stores the analytical tables as Parquet files rather than inside a relational database.

---

## Data Quality & Validation

The Gold datasets were explored and validated to check structural consistency, referential integrity, business rules, and calculated values. The exploratory validation logic is available in `exploration_gold/validate_gold.py`.

### `fact_sales` Validation

- **Columns and data types:** checked column names and data types against the expected structure.
- **Null values:** no null values were found.
- **Record count:** the Gold table contains **239 sales records**.
- **Uniqueness:** checked `sale_id` for duplicates; none were found.
- **Referential integrity:** checked `product_id`, `store_id`, and sales dates against their respective dimension tables.
- **Valid ranges:** checked positive values for `quantity` and `unit_price_brl`, and the expected range for `discount_pct`.
- **Calculated fields:** audited `gross_amount`, `discount_amount`, and `net_amount` for mathematical consistency and rounding behavior, along with other invalid-value checks.
- **Result:** no significant data-quality inconsistencies were found within the tested rules.

### `dim_products` Validation

- **Identity and duplicates:** checked that `product_id` identifies products uniquely; no repeated IDs were found.
- **Categories:** compared `category` values with a defined list of accepted categories using `isin()`.
- **Costs:** required `unit_cost` to be greater than zero. Also explored unusually high costs using a threshold of three times the mean.
- **Supplier currency:** accepted only `BRL` and `USD`, checked using `isin()`.
- **Active status:** confirmed `active` has boolean values and inspected its distribution with `value_counts()`; all six products were active.
- **Result:** no inconsistencies were found under the current project rules.

### `dim_stores` Validation

- **Identity and duplicates:** checked `store_id` with `duplicated()` and `sum()`.
- **Empty strings:** implemented a reusable function that iterates over text columns, applies `strip()` and `len()`, and returns a dictionary of empty-string counts by column. Null checks are treated separately.
- **Sales channels:** checked `channel` against the accepted values `Física` and `Online` using `isin()`.
- **Potential business duplicates:** explored repeated combinations of store attributes with `duplicated(subset=..., keep=False)` and store names associated with multiple IDs using `groupby()` and `nunique()`.
- **City/state consistency:** identified the need for a reference table or reliable API to verify city–state combinations; this external validation has not been implemented.
- **Result:** no inconsistencies were identified by the implemented checks.

### `fact_fixed_costs` Validation

- **Monthly uniqueness:** verified uniqueness of the combination `store_id` and `start_month` using `duplicated()` and `groupby().size()`.
- **Referential integrity:** checked that every `store_id` exists in `dim_stores` using `isin()`; no invalid relationships were found.
- **Negative costs:** developed a reusable function that counts negative values per monetary column and returns a dictionary summary.
- **Zero-cost analysis:** counted zeros by column and used boolean masks with `any(axis=1)` to find rows containing at least one zero cost.
- **Business rule for rent:** zero rent can be valid for an online channel. Used a left merge with `dim_stores` to check for physical stores with `rent_brl = 0`; no such inconsistencies were found.
- **Date consistency:** checked that `start_month` falls on the first day of the month; no invalid dates were found.
- **Potential outliers:** counted costs above **three times each column's mean**, reporting results by column. This is an exploratory heuristic, not a formally established business constraint.
- **Result:** no inconsistencies were identified in the checked structural, referential, or business rules.

### `dim_date` Validation

The date dimension is generated programmatically rather than imported from an external source, so checks focus on its internal consistency.

- **Uniqueness:** checked `date` using `duplicated()`; no duplicate dates were found.
- **Continuity:** calculated consecutive date differences with `diff()` and compared against `pd.Timedelta(days=1)`; no gaps were detected.
- **Derived fields:** verified `year` and `month` against `date.dt.year` and `date.dt.month` using boolean masks.
- **Result:** all implemented checks passed, with no duplicate dates, continuity gaps, or year/month inconsistencies found.

---

## Project Structure

The repository separates data files, Python source code, and exploratory scripts to keep processing logic organized and make it easier to trace issues across pipeline stages.

### Directory Structure

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

### Directory & Module Responsibilities

#### `data/` — Data Storage

The `data/` directory is separated from the Python source code to improve project organization and avoid mixing datasets with application code.

The directory follows a **Medallion Architecture**, where each layer stores data at a different processing stage:

- **Raw:** contains the original Excel files received from the data source.
- **Bronze:** stores the extracted datasets in Parquet format after initial column validation.
- **Silver:** contains cleaned and transformed datasets produced from the Bronze layer.
- **Gold:** stores analytical tables modeled for business analysis.

This organization improves **data traceability**, making it easier to investigate errors, identify the stage where an issue was introduced, and inspect the data at different points in the pipeline.

#### `src/` — Source Code

The `src/` directory contains the main Python source code responsible for executing the pipeline and applying the data processing logic.

Unlike the `data/` directory, which stores datasets at different processing stages, `src/` contains the functions and modules that extract, validate, transform, model, and save the data.

The project logic is divided into separate Python modules instead of being concentrated in a single file. This approach improves **code reusability, maintainability, and separation of responsibilities**, allowing functions to be imported and reused across different parts of the project.

#### `src/main.py` — Pipeline Execution

The `main.py` module acts as the main entry point and coordinates the execution of the different pipeline stages.

It imports functions from other modules, passes the required parameters, and uses the results of each operation to execute the next stage of the data pipeline.

This approach keeps the execution flow organized without concentrating all processing logic in a single file.

#### `src/config.py` — Centralized Configuration

The `config.py` module centralizes project configurations, including file paths, required columns, and auxiliary lists used throughout the pipeline.

Keeping these configurations in one place avoids code duplication, improves maintainability, and reduces the risk of inconsistencies when changes are required.

#### `src/extract.py` — Data Extraction

The `extract.py` module is responsible for reading data from the project's data sources.

It receives file paths defined in `config.py` and extracts information from Excel workbooks, returning a dictionary of Pandas DataFrames where each DataFrame represents a worksheet.

The module also provides functionality for reading Parquet files from previously processed data layers.

Separating extraction from transformation improves code organization and allows changes to data processing logic without modifying how the source data is read.

#### `src/validate.py` — Data Structure Validation

The `validate.py` module is responsible for checking whether the extracted datasets contain the required columns defined in `config.py`.

It validates the structure of each DataFrame against the expected column lists.

When required columns are missing, the validation raises an error identifying the affected dataset and the missing columns.

This process helps prevent unexpected data structures from entering subsequent pipeline stages, reducing processing errors and unnecessary rework.

#### `src/load.py` — Data Storage

The `load.py` module is responsible for saving processed DataFrames to the destination paths provided as parameters.

It receives a dictionary of DataFrames and an output path, generating individual Parquet files using the dictionary keys as filenames.

Separating data storage from extraction and transformation improves code organization, reusability, and maintainability. It also allows changes to the storage logic without modifying extraction or transformation processes.

#### `src/transform.py` — Data Transformation

The `transform.py` module is responsible for applying data cleaning and transformation rules to the datasets extracted from the Bronze layer.

The main transformations include:

- Creating additional calculated columns.
- Renaming and standardizing column names.
- Converting columns to appropriate data types.
- Applying transformations according to the structure and business logic of each dataset.

Different datasets require different transformation rules. For example, a product table mainly contains descriptive information, while a sales fact table requires additional calculations to generate business metrics.

The `transform_all_dataframes_bronze()` function receives a dictionary of DataFrames and coordinates the execution of the corresponding transformation functions for each dataset.

After processing, it returns a dictionary containing the cleaned and transformed DataFrames, ready to be saved in the Silver layer.

#### `src/model.py` — Analytical Data Modeling

The `model.py` module is responsible for building the analytical tables used in the Gold layer.

Unlike `transform.py`, which focuses on cleaning and transforming data, `model.py` organizes the processed datasets into a dimensional model designed to answer business questions.

The modeling approach follows a star-schema-based design, using two types of tables:

- **Dimension tables:** `dim_products`, `dim_stores`, and `dim_date` provide descriptive information and support filtering and analysis.
- **Fact tables:** `fact_sales` and `fact_fixed_costs` contain business transactions and measurable values related to sales and operational costs.

The `build_gold_model()` function receives a dictionary of Silver DataFrames along with a start and end date for generating the calendar dimension.

It coordinates the creation of the analytical tables and returns a dictionary of Gold DataFrames, which are subsequently saved in Parquet format.

This structure makes the data more suitable for analytical tools such as Power BI, supporting the creation of relationships, business metrics, reports, and dashboards.

#### `exploration_bronze/` and `exploration_gold/` — Data Exploration and Validation

These directories contain exploratory scripts used to develop, test, and verify data processing logic separately from the main pipeline modules.

Separating exploratory code helps keep production-oriented modules organized and prevents experimental or unnecessary logic from being included in the main processing workflow.

- **`exploration_bronze/explore_bronze.py`:** used for initial data exploration and testing extraction-related logic.
- **`exploration_gold/explore_gold.py`:** used to examine the general structure and quality of Gold tables, including null values, duplicated records, and other initial checks.
- **`exploration_gold/validate_gold.py`:** used to perform more detailed data-quality validations, including referential integrity, business rules, mathematical consistency, and checks specific to each analytical table.

These scripts provide a reference for the decisions and checks performed during development; they should not be confused with an automated test suite executed on every pipeline run.

#### `MANUAL_DEBUGGING.md` — Python Debugging Guide

The `MANUAL_DEBUGGING.md` file was created to document and resolve debugging and module import issues encountered when executing Python scripts located outside the `src/` directory.

The guide covers:

- Differences between executing Python scripts directly and running them as modules.
- Configuring VS Code debugging through `.vscode/launch.json`.
- Managing imports across different project directories.
- Configuring the working directory and Python interpreter with Poetry.
- Using breakpoints and debugging tools to inspect execution across multiple modules.

This documentation provides a reusable reference for troubleshooting execution issues and configuring debugging for new Python modules without modifying the main pipeline code.

### Supporting Configuration Files

| File or directory | Purpose                                                    |
| ----------------- | ---------------------------------------------------------- |
| `pyproject.toml`  | Project metadata, dependencies, and tooling configuration. |
| `poetry.lock`     | Locked dependency versions for reproducible installations. |
| `poetry.toml`     | Local Poetry configuration for this project.               |
| `.python-version` | Selected Python version.                                   |
| `.gitignore`      | Files and directories excluded from Git tracking.          |
| `.vscode/`        | VS Code editor and debugging configurations.               |
| `README.md`       | Main project documentation.                                |

---

## How to Run

### Prerequisites

Before running the pipeline, make sure the following tools are available:

- **Python 3.12:** the Python version used during project development.
- **Poetry:** used for dependency management and virtual environment isolation.
- **Git:** required for cloning the repository using Git commands (optional if downloading the source as a ZIP file).

The project uses Poetry to manage Python dependencies and maintain a reproducible development environment. The `pyproject.toml` file defines the project's dependencies, while `poetry.lock` records their resolved versions to help ensure consistent installations across environments.

A code editor such as VS Code is optional.

### Clone Repository

Clone the repository using Git to obtain a local copy of the project:

```bash
git clone <repository-url>
```

Navigate to the project's root directory:

```bash
cd retail-sales-intelligence-pipeline
```

The project root contains the `pyproject.toml` and `poetry.lock` files used by Poetry to manage dependencies and configure the development environment.

Cloning preserves the repository's Git history and remote configuration, allowing developers to track changes and contribute to the project.

### Environment Setup

This project uses Poetry to manage dependencies and provide an isolated Python environment.

After cloning the repository and navigating to the project root, install the required dependencies:

```bash
poetry install
```

Poetry uses `pyproject.toml` and `poetry.lock` to install the project's dependencies and prepare its virtual environment.

To execute Python modules using the project environment, use `poetry run`.

### Run the Pipeline

After installing the dependencies, execute the pipeline from the project root:

```bash
poetry run python -m src.main
```

This command executes the main module using the Python environment managed by Poetry.

The `src/main.py` module coordinates the pipeline execution, including data extraction, validation, transformation, analytical modeling, and storage across the Bronze, Silver, and Gold layers.

### Expected Output

After successfully executing the pipeline, the processed datasets are stored as Parquet files in their respective data layers.

| Layer     | Output Directory | Parquet Files |
| --------- | ---------------- | ------------: |
| Bronze    | `data/bronze/`   |             4 |
| Silver    | `data/silver/`   |             4 |
| Gold      | `data/gold/`     |             5 |
| **Total** |                  |        **13** |

The Gold layer produces the following analytical datasets:

- `dim_products.parquet`
- `dim_stores.parquet`
- `dim_date.parquet`
- `fact_sales.parquet`
- `fact_fixed_costs.parquet`

Developers can verify that the expected files were generated and inspect their contents using Pandas.

Additional data quality and consistency checks were performed during development using the exploratory scripts in `exploration_gold/`, particularly `validate_gold.py`.

These detailed Gold validations are currently separate from the main pipeline execution.

## Tech Stack

This project uses Python and its data processing ecosystem to build a reproducible ETL pipeline following the Bronze, Silver, and Gold architecture.

### Python 3.12 — Programming Language

Python was chosen as the main programming language because of its extensive ecosystem of libraries for data processing, transformation, and automation.

Its libraries provide reusable tools that simplify pipeline development and reduce the need to implement common data processing operations from scratch.

### Pandas — Data Processing

Pandas is the main library used for data extraction, cleaning, transformation, and validation throughout the pipeline.

DataFrames serve as the primary in-memory data structure, enabling operations such as data type conversions, column transformations, calculations, and data quality checks.

### OpenPyXL — Excel File Reading

OpenPyXL is used by Pandas as the reading engine for Excel (`.xlsx`) files.

It interprets Excel workbook structures, including worksheets, cells, and values, allowing Pandas to extract the data and organize it into DataFrames.

### PyArrow — Columnar Data Processing and Serialization

PyArrow provides the engine used by Pandas to read and write Parquet files.

It converts DataFrames into Apache Arrow's columnar in-memory representation and handles the encoding and serialization required for Parquet storage.

### Apache Parquet — Data Storage

Apache Parquet is the primary storage format across the Bronze, Silver, and Gold layers.

It was selected for its efficient columnar storage, compression capabilities, support for typed schemas, and ability to read selected columns without loading entire datasets.

Parquet is also widely supported by modern data engineering and cloud analytics platforms.

### Poetry — Dependency and Environment Management

Poetry manages project dependencies and isolated Python virtual environments.

The `pyproject.toml` file defines project metadata, Python compatibility requirements, and dependency constraints.

The `poetry.lock` file records resolved dependency versions, supporting reproducible installations across compatible environments.

### Git & GitHub — Version Control and Repository Hosting

Git tracks source code changes and maintains the project's version history through commits.

GitHub provides remote repository hosting, making the source code, documentation, and development history accessible to other developers.

---

## Limitations & Next Steps

The current version demonstrates a complete local Excel-to-Parquet pipeline with Bronze, Silver, and Gold layers. The following limitations and proposed improvements describe **future work**, not functionality already implemented in the main pipeline.

### 1. Manual Execution and Workflow Orchestration

**Current limitation:** The pipeline must be started manually with `poetry run python -m src.main`. It does not currently run on a schedule or in response to changes in the source Excel file.

**Next step:** Introduce a workflow orchestrator such as **Apache Airflow** to schedule executions, coordinate pipeline stages, and monitor task status. A future event-driven workflow could also respond to new or updated source files, with safeguards to avoid processing a file before it has finished being written.

### 2. Execution Logging, Monitoring, and Failure Alerts

**Current limitation:** The project does not yet provide an integrated mechanism for structured execution logs, centralized run monitoring, or automatic notifications when an execution fails. Troubleshooting requires manually inspecting the execution output.

**Next step:** Add stage-level logging for key events and exceptions, potentially using Python's standard `logging` module or **Loguru**. When the pipeline is orchestrated with Airflow, use its task execution logs and web interface to investigate failures, and configure email or other failure notifications. Airflow can recognize failed tasks through uncaught exceptions or nonzero process exit codes; Loguru is optional and is not required to signal failure to Airflow.

### 3. Manual Gold Validations and Data Quarantine

**Current limitation:** The detailed checks in `exploration_gold/validate_gold.py` are currently run separately and are not automatically called by `src.main`. Consequently, invalid business data could be written to Gold without passing those checks during each run.

**Next step:** Refactor the existing checks into reusable validation functions and invoke them as part of the pipeline. Validate input business rules before Gold modeling and verify Gold-specific relationships, unique keys, calculations, and consistency **before publishing the Gold Parquet files**.

For record-level issues, implement a **data quarantine** workflow that:

- Separates accepted and rejected records (for example, sales with null or nonpositive quantities).
- Stores rejected records in a separate dataset with an explicit rejection reason and enough context to investigate them.
- Reports rejected record counts and percentages so that downstream users understand any excluded data.
- Uses a configurable rejection threshold; critical structural failures or a rejection rate above the allowed limit should stop publication rather than silently producing incomplete or unreliable data.

A declarative DataFrame validation library such as **Pandera** could be evaluated later, but automated checks can first be implemented using the project's existing Pandas-based logic.

### 4. Full Reprocessing Instead of Incremental Updates

**Current limitation:** Each run reads and processes the full Excel dataset, even when only a few sales have been added or corrected. This can become costly as data volumes grow and delay downstream analytics updates.

**Next step:** Implement **incremental processing** to distinguish between:

- **New sales:** `sale_id` values that have not been processed before, regardless of `sale_date`.
- **Modified sales:** previously processed `sale_id` values whose business attributes have changed.
- **Late-arriving sales:** newly received records with older transaction dates that still need to be included in the analytical results.

A first implementation could compare current and previously processed records using Pandas `merge()` and apply insert/update (**upsert**) logic. For larger systems, evaluate change-tracking fields such as `updated_at` or change data capture (CDC). With a single cumulative Excel file, the source may still need to be read in full to discover changes, even if only new or modified records are transformed afterward.

These improvements would make the pipeline more reliable, observable, and scalable while preserving the existing layered architecture.
