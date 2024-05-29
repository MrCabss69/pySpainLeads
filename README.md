# pySpainLeads

## Descripción
pySpainLeadsFinder es una herramienta automatizada diseñada para extraer información de empresas en España, consultando directorios públicos disponibles en [Páginas Amarillas de España](https://www.paginasamarillas.es/). Este proyecto permite a los usuarios crear directorios de contacto personalizados, apoyando tareas de análisis de mercado, investigación de negocios, y más.


## Características
- **Extracción Automatizada**: Automatiza la extracción de datos desde las páginas amarillas españolas.
- **Facilidad de Uso**: Interfaz simple de línea de comandos para iniciar búsquedas personalizadas.
- **Almacenamiento en .csv**: Guarda la información extraída en csv local para un acceso fácil y rápido.
- **Filtrado por Localidad**: Permite la búsqueda por diferentes localidades, maximizando la relevancia de los datos recopilados.

## Comenzando

### Prerrequisitos
Antes de instalar y ejecutar `pySpainLeads`, necesitarás tener instalado Python 3.7 o superior. Además, asegúrate de tener pip disponible para instalar las dependencias requeridas.

### Instalación
Clona el repositorio a tu máquina local usando:

```bash
git clone https://github.com/MrCabss69/pySpainLeads.git
cd pySpainLeads
```
### Uso

Para iniciar una búsqueda, puedes utilizar el siguiente comando desde la terminal:

```bash
python3 main.py
```

Y te aparecerá una interfaz gráfica con la que puedes interactuar. Una vez rellenes los campos y pulses 'Buscar', se irá rellenando de forma progresiva el contenido de companies.csv con los datos scrapeados
