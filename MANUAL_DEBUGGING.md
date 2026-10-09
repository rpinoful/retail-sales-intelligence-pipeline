# Manual general de depuracion de proyectos Python en VS Code

Este manual explica como configurar y utilizar el depurador de VS Code en proyectos Python que tienen varios archivos, carpetas, modulos y paquetes.

El objetivo no es memorizar una configuracion concreta. El objetivo es entender:

- Como Python identifica un archivo dentro de un proyecto.
- Por que algunos archivos se ejecutan como programa y otros como modulo.
- Como configurar `launch.json` para diferentes partes del proyecto.
- Como depurar codigo que utiliza imports entre varias carpetas.
- Como crear una configuracion nueva sin depender de otra persona.

## 1. Conceptos fundamentales

### Archivo `.py`

Es un archivo fisico, por ejemplo:

```text
src/transform.py
```

### Modulo

Es la forma en que Python identifica un archivo para importarlo o ejecutarlo desde un paquete.

El archivo:

```text
src/transform.py
```

puede representarse como el modulo:

```text
src.transform
```

Para convertir una ruta en modulo:

1. Empieza desde la carpeta raiz del proyecto.
2. Reemplaza `/` por `.`.
3. Elimina la extension `.py`.

Ejemplos:

| Archivo | Modulo |
|---|---|
| `src/main.py` | `src.main` |
| `src/etl/load.py` | `src.etl.load` |
| `tests/test_transform.py` | `tests.test_transform` |
| `exploration_gold/validate_gold.py` | `exploration_gold.validate_gold` |

### Paquete

Una carpeta que organiza modulos relacionados. Por ejemplo:

```text
src/
  etl/
    extract.py
    transform.py
    load.py
```

En este ejemplo, `etl` agrupa tres modulos.

En Python moderno, una carpeta puede funcionar como paquete sin `__init__.py` en algunos casos. Sin embargo, agregar `__init__.py` hace explicita la intencion de que la carpeta es un paquete y puede facilitar el comportamiento entre herramientas.

## 2. La carpeta raiz es importante

La carpeta raiz es la carpeta que contiene la configuracion general del proyecto, por ejemplo:

```text
mi-proyecto/
  pyproject.toml
  .vscode/
  src/
  tests/
```

En VS Code debes abrir `mi-proyecto`, no solamente `src` ni una subcarpeta.

La raiz determina:

- Desde donde se resuelven los imports.
- Que significa `${workspaceFolder}`.
- Donde Python busca los modulos cuando usas `-m`.
- Que archivos quedan disponibles para el depurador.

Si abres una subcarpeta como si fuera el proyecto completo, un import que antes funcionaba puede fallar porque cambio el punto de partida de Python.

## 3. Dos formas de ejecutar un archivo

### Ejecutar por ruta con `program`

Esta forma utiliza la ubicacion fisica del archivo:

```bash
python src/main.py
```

En `launch.json`:

```json
{
    "name": "Debug main por archivo",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/src/main.py",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

`program` es util cuando el archivo es un script independiente y sus imports funcionan al ejecutarlo por ruta.

### Ejecutar como modulo con `module`

Esta forma utiliza el nombre del modulo:

```bash
python -m src.main
```

En `launch.json`:

```json
{
    "name": "Debug main como modulo",
    "type": "debugpy",
    "request": "launch",
    "module": "src.main",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

`module` suele ser la mejor opcion cuando el archivo forma parte de un proyecto con varios paquetes y utiliza imports desde la raiz.

### Que diferencia produce cada forma

Python no recibe exactamente el mismo contexto al ejecutar:

```bash
python src/main.py
```

que al ejecutar:

```bash
python -m src.main
```

Con `-m`, Python busca `src.main` dentro del entorno del proyecto y conserva mejor la estructura de paquetes. Esto es especialmente importante cuando existen imports entre carpetas o imports relativos.

Regla practica:

- Usa `program` para scripts independientes.
- Usa `module` para aplicaciones, paquetes, tests y modulos que importan otras partes del proyecto.

## 4. El archivo `.vscode/launch.json`

VS Code guarda las configuraciones de depuracion en:

```text
.vscode/launch.json
```

Una configuracion dentro de `configurations` aparece como una opcion en la vista **Run and Debug**.

Configuracion minima:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug modulo",
            "type": "debugpy",
            "request": "launch",
            "module": "paquete.archivo",
            "cwd": "${workspaceFolder}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

### Significado de las propiedades

- `version`: version del formato de configuracion de VS Code.
- `configurations`: lista de configuraciones disponibles.
- `name`: nombre visible en el selector de depuracion.
- `type`: depurador que se utilizara; `debugpy` es el depurador de Python.
- `request`: `launch` inicia un proceso nuevo.
- `module`: modulo que se ejecutara con el equivalente de `python -m`.
- `program`: ruta del archivo que se ejecutara directamente.
- `cwd`: directorio de trabajo del proceso; normalmente `${workspaceFolder}`.
- `console`: lugar donde se muestran los mensajes del programa.
- `justMyCode`: evita entrar normalmente en el codigo interno de librerias externas.

No uses `module` y `program` para ejecutar el mismo proceso dentro de una configuracion. Elige uno de los dos.

## 5. Como crear una configuracion para un archivo nuevo

Supongamos que creas:

```text
src/quality/check_data.py
```

### Paso 1: convertir la ruta en modulo

La ruta:

```text
src/quality/check_data.py
```

se convierte en:

```text
src.quality.check_data
```

### Paso 2: agregar la configuracion

Dentro de `configurations`, agrega un nuevo objeto:

```json
{
    "name": "Debug check_data",
    "type": "debugpy",
    "request": "launch",
    "module": "src.quality.check_data",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

Si ya existe otra configuracion antes, agrega una coma entre los objetos:

```json
"justMyCode": true
},
{
    "name": "Debug check_data",
```

### Paso 3: iniciar la depuracion

1. Guarda `launch.json`.
2. Abre **Run and Debug**.
3. Selecciona `Debug check_data`.
4. Abre `check_data.py`.
5. Coloca un breakpoint en una linea ejecutable.
6. Presiona `F5`.

## 6. Como elegir el modulo correcto

Para obtener el nombre del modulo, mira la ruta desde la raiz, no desde la carpeta donde esta abierto el archivo.

Ejemplo:

```text
mi-proyecto/
  app/
    services/
      users.py
```

El modulo es:

```text
app.services.users
```

No es:

```text
services.users
```

porque `services` no esta directamente en la raiz del proyecto.

Otro ejemplo:

```text
mi-proyecto/
  backend/
    api/
      main.py
```

El modulo es:

```text
backend.api.main
```

## 7. Imports entre carpetas

En un proyecto modular es preferible que los imports reflejen la estructura del proyecto.

Ejemplo de estructura:

```text
mi-proyecto/
  src/
    common/
      dates.py
    sales/
      report.py
```

Un import absoluto puede ser:

```python
from src.common.dates import format_date
```

Si `sales` y `common` son paquetes relacionados, un import relativo dentro de `sales/report.py` podria ser:

```python
from ..common.dates import format_date
```

Los imports relativos requieren que el archivo se ejecute como parte de un paquete. Por eso normalmente debes usar `module` en vez de ejecutar el archivo directamente con `program`.

Si aparece un error como:

```text
ImportError: attempted relative import with no known parent package
```

revisa si ejecutaste el archivo por ruta cuando debias ejecutarlo como modulo.

## 8. Parametros, variables de entorno y argumentos

Si el archivo recibe argumentos por terminal, puedes declararlos con `args`:

```json
{
    "name": "Debug report",
    "type": "debugpy",
    "request": "launch",
    "module": "src.reports.report",
    "cwd": "${workspaceFolder}",
    "args": ["--table", "sales", "--limit", "10"],
    "console": "integratedTerminal",
    "justMyCode": true
}
```

Esto equivale aproximadamente a:

```bash
python -m src.reports.report --table sales --limit 10
```

Si el programa utiliza variables de entorno, puedes definirlas con `env`:

```json
{
    "name": "Debug report con entorno",
    "type": "debugpy",
    "request": "launch",
    "module": "src.reports.report",
    "cwd": "${workspaceFolder}",
    "env": {
        "APP_ENV": "development",
        "LOG_LEVEL": "DEBUG"
    },
    "console": "integratedTerminal",
    "justMyCode": true
}
```

No coloques secretos o contrasenas directamente en `launch.json`.

## 9. Poetry y el interprete Python

Este proyecto utiliza Poetry. El depurador debe usar el mismo entorno donde estan instaladas las dependencias.

Para verificar el entorno desde la terminal:

```bash
poetry run python --version
```

Para ejecutar un modulo con ese entorno:

```bash
poetry run python -m paquete.archivo
```

Si VS Code informa que no encuentra pandas u otra dependencia:

1. Abre la paleta de comandos.
2. Ejecuta **Python: Select Interpreter**.
3. Selecciona el entorno creado por Poetry.
4. Reinicia la depuracion.

La configuracion de `.vscode/settings.json` puede indicar que Poetry es el gestor de entorno, pero aun debes verificar que VS Code haya seleccionado el interprete correcto.

## 10. Breakpoints y flujo de depuracion

Un breakpoint pausa la ejecucion cuando Python llega a una linea ejecutable.

No todos los lugares son equivalentes:

- En una definicion `def`, la funcion se registra, pero su cuerpo se ejecuta solamente cuando alguien la llama.
- En una asignacion, puedes revisar los valores usados para producir el resultado.
- En un `for`, puedes observar cada iteracion.
- En un `if`, puedes comprobar la condicion antes de que Python elija una rama.
- En una linea de `return`, puedes inspeccionar el valor que saldra de la funcion.

Controles principales:

- `F5`: continuar hasta el siguiente breakpoint.
- `F10`: ejecutar la linea actual sin entrar en otra funcion.
- `F11`: entrar en la funcion llamada.
- `Shift+F11`: salir de la funcion actual.
- `Ctrl+Shift+F5`: reiniciar la depuracion.
- `Shift+F5`: detener la depuracion.

## 11. Inspeccionar valores

Cuando el programa esta pausado, puedes utilizar:

- **Variables** para revisar las variables del contexto actual.
- **Watch** para guardar expresiones que quieras evaluar varias veces.
- **Debug Console** para evaluar expresiones en el punto actual.

Ejemplos genericos:

```python
type(data)
```

```python
data.shape
```

```python
list(data.columns)
```

```python
len(items)
```

Si una expresion compleja falla, dividela en variables temporales para observar cada paso:

```python
values = dataframe[column_name]
mask = values < 0
quantity = mask.sum()
```

## 12. Depurar varios modulos en una misma ejecucion

El depurador sigue el flujo real del programa, aunque el flujo pase por muchos archivos.

Ejemplo:

```text
src/main.py
  llama a src/extract.py
  llama a src/transform.py
  llama a src/load.py
```

Puedes colocar breakpoints en cualquiera de esos archivos y ejecutar una sola configuracion que inicie `src.main`.

Si quieres entrar en el codigo de una funcion importada, usa `F11` cuando la llamada se ejecute. Si solo quieres pasar por encima, usa `F10`.

Con `justMyCode: true`, VS Code normalmente entra en tus archivos y evita las librerias externas. Si necesitas investigar una dependencia, puedes cambiar temporalmente esa propiedad a `false`.

## 13. Configuraciones utiles para distintos tipos de proyecto

### Aplicacion principal

```json
{
    "name": "Debug aplicacion",
    "type": "debugpy",
    "request": "launch",
    "module": "src.main",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

### Script independiente

```json
{
    "name": "Debug script",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/scripts/clean_data.py",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

### Tests con pytest

```json
{
    "name": "Debug tests",
    "type": "debugpy",
    "request": "launch",
    "module": "pytest",
    "args": ["tests/test_transform.py", "-q"],
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

### Programa con argumentos

```json
{
    "name": "Debug importacion",
    "type": "debugpy",
    "request": "launch",
    "module": "src.importer",
    "args": ["--source", "data/input.csv"],
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

## 14. Errores frecuentes y su causa

### `ModuleNotFoundError`

Causas habituales:

- VS Code abrio una subcarpeta en vez de la raiz.
- `cwd` no apunta a `${workspaceFolder}`.
- El nombre del modulo no coincide con la estructura de carpetas.
- VS Code usa otro interprete Python.
- Falta una dependencia en el entorno de Poetry.

### Breakpoint gris o no alcanzado

Causas habituales:

- Se esta ejecutando otra configuracion.
- El flujo nunca llega a esa linea.
- El breakpoint esta en una linea no ejecutable.
- Se esta ejecutando una copia diferente del archivo.

### Error con imports relativos

Probablemente se ejecuto el archivo por ruta. Cambia de `program` a `module` y ejecuta desde la raiz.

### El programa usa datos de una ruta incorrecta

La ruta relativa se interpreta desde `cwd`, no necesariamente desde la carpeta donde esta el archivo `.py`. Usa rutas basadas en la raiz del proyecto o configura correctamente `cwd`.

### No se detiene dentro de una libreria

Esto suele ocurrir porque `justMyCode` esta en `true`. Cambialo temporalmente a `false` solo si necesitas investigar esa libreria.

## 15. Procedimiento general para cualquier archivo nuevo

Antes de depurar un archivo nuevo, sigue este orden:

1. Identifica la carpeta raiz del proyecto.
2. Identifica la ruta del archivo desde esa raiz.
3. Decide si es un script independiente o un modulo de un paquete.
4. Convierte la ruta a nombre de modulo si corresponde.
5. Revisa los imports del archivo.
6. Agrega una entrada en `.vscode/launch.json`.
7. Configura `cwd` como `${workspaceFolder}`.
8. Selecciona el interprete correcto de Python o Poetry.
9. Coloca un breakpoint en una linea ejecutable.
10. Ejecuta la configuracion con `F5`.
11. Revisa primero los argumentos y tipos de las variables.
12. Avanza con `F10` o entra en funciones con `F11`.

## 16. Plantillas rapidas

### Archivo en una carpeta de paquetes

```json
{
    "name": "Debug nombre_archivo",
    "type": "debugpy",
    "request": "launch",
    "module": "paquete.subpaquete.nombre_archivo",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

### Script por ruta

```json
{
    "name": "Debug nombre_archivo",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/scripts/nombre_archivo.py",
    "cwd": "${workspaceFolder}",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

La decision mas importante es escoger correctamente entre `module` y `program`. El resto de la configuracion suele mantenerse igual.
