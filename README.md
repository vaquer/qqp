# API QQP

El API QQP es una interfaz publica de consulta que permite a los consumidores de este servicio obtener datos de valor, principalmente precios, relacionados con los productos registrados en la base e datos Quién es Quién en los Precios de [PROFECO](https://www.profeco.gob.mx/precios/canasta/default.aspx).

El proyecto se divide en dos principales bloques:
- ETL QQP
- API QQP

## ETL QQP
Los endpoints originales construidos por PROFECO se encuentra fuertemente ligados a la implementación de su plataforma movil y web y presentan problemas al momento de exponerlas como un API de consumo estandard.

ETL QQP consume los datos expuestos en estos enpoints y los organiza de tal forma que son represendatos en un esquema de datos pensado para consulta y consumo abierto e intensivo de los datos.

Los datos recolectados en cada ejecución del ETL son etiquetados con el timestamp de la fecha en la cual se ejecuto el ETL. El formato corresponde a `Ymd`. Por ejemplo: `20180514` para `14 de Mayo del 2018`.

El ETL se construye de steps o pasos que ejecutan cada una de las tareas necesarias para descargar y procesar los datos de origen. Cada paso o step arroja archivos con el resultado de su ejecución en la carpeta `otuput` del proyecto. Los pasos que componen el ETL es descrito en el diagrama siguiente:

![Diagrama de ETL](qqp/media/ETLQQP.png)

### 1.1 Descargar Categorias
El diseño de datos expuesto por PROFECO refleja que los productos se dividen en grupos principales los cuales a su vez contienen sub categorias y para poder obtener el catalogo completo de productos es necesario descargar esta jerarquia de grupos.

Las peticiones a los endpoints son realizadas mediante consultas GET con parametros de url. Los endpoints usados son los siguientes:
- Categorias principales: http://200.53.148.112:82/jsonApps/qqp_secciones.aspx
- Sub-Categorias tipo A: http://200.53.148.112:82/jsonApps/qqp_subseccion1.aspx
    - Parametros:
        - **seccion**: Nombre de la sección principal obtenida en el endpoint anterior.
- Sub-Categorias tipo B: http://200.53.148.112:82/jsonApps/qqp_subseccion2.aspx
    - Parametros:
        - **subseccion1**: Nombre de la sub-sección obtenida en el endpoint anterior.

El resultado final de este step es la generación del archivo `output/categories-{timestamp}.json`. Ejemplo: `output/categories-20180514.json`.

Layout ejemplo:
```json
[
    {
        "id": "01",
        "nombre": "ALIMENTOS",
        "subcategoria": [
            {
                "id": "01",
                "nombre": "ACEITES, GRASAS Y VINAGRES",
                "subcategoria": [
                    {
                        "id": "01",
                        "nombre": "ACEITES Y GRASAS"
                    },
                    {
                        "id": "02",
                        "nombre": "VINAGRES"
                    }
                ]
            },
            ...
            {
                "id": "09",
                "nombre": "ALIMENTOS EN LATA Y PROCESADOS",
                "subcategoria": [
                    {
                        "id": "01",
                        "nombre": "ALIMENTOS EN LATA Y PROCESADOS"
                    }
                ]
            }
]
```
### 1.2 Descargar ciudad y municipios
Otro rasgo adicional en los datos expuestos por PROFECO es que es necesario consultar la información por ciudad y municipio. Por lo que es requisito descargar el catalogo completo de con el listado de ciudades y municipios registrados en la base de QQP para poder obtener el catálogo completo de productos.

Las peticiones a los endpoints son realizadas mediante consultas GET con parametros de url. Los endpoints usados son los siguientes:
- Endpoint: http://200.53.148.112:82/jsonApps/qqp2.aspx
    - Parametros:
        - **ve**: Operación a realizar (Tiene dos valores).
            - **selecCiudad**
            - **selecMuni**
        - **idCiudad**: Se utiliza para obtener los municipios de una ciudad y solo se usa con `ve=selecMuni`.

El resultado final de este step es la generación del archivo `output/geography-{timestamp}.json`. Ejemplo: `output/geography-20180514.json`

Layout ejemplo:
```json
[
    {
        "id": "1201",
        "titulo": "Acapulco",
        "municipios": [
            {
                "id": "001",
                "titulo": "Acapulco de Ju\u00e1rez"
            }
        ]
    },
    ...
    {
        "id": "0101",
        "titulo": "Aguascalientes",
        "municipios": [
            {
                "id": "001",
                "titulo": "Aguascalientes"
            }
        ]
    }
]
```
### 2 Descargar catálogo de productos
Una vez que se cuentan con el catalogo de zonas geograficas registradas por profeco y con las categorias registradas el siguiente paso es descargar el catalogo de productos sin precios.

Las peticiones a los endpoints son realizadas mediante consultas GET con parametros de url. Los endpoints usados son los siguientes:
- Endpoint: http://200.53.148.112/json/qqp_subseccionInter.php
    - Parametros:
        - **qqp_subseccion2**: Id de la subcession o subcategoria de productos.
        - **idCiudad**: Id de la ciudad donde se buscaran productos.
        - **idMunicipio**: Id del municipio donde se buscaran productos.

El resultado final de este step es la generación del archivo `output/products-{timestamp}.json`. Ejemplo: `output/products-20180514.json`

Layout ejemplo:
```json
[
    {
        "id": 994,
        "nombre": "FLAN",
        "catalogo": "ALIMENTOS",
        "categoria": "AZUCAR, ENDULZANTES Y CAFE"
    },
    ...
    {
        "id": 984,
        "nombre": "POLVO P/HORNEAR",
        "catalogo": "ALIMENTOS",
        "categoria": "AZUCAR, ENDULZANTES Y CAFE"
    }
]
```
### 3 Descargar marcas por producto
Una vez que se cuentan con el catalogo de productos sin precios y las categorias registradas por profeco el siguiente paso es descargar el catalogo de marcas por producto sin precios.

Las peticiones a los endpoints son realizadas mediante consultas GET con parametros de url. Los endpoints usados son los siguientes:
- Endpoint: http://200.53.148.112:82/jsonApps/jsonApps2/qqp_subseccion3.aspx
    - Parametros:
        - **cveProducto**: Id del producto del que se desea obtener sus marcas.
        - **idCiudad**: Id de la ciudad donde se buscaran productos.
        - **idMunicipio**: Id del municipio donde se buscaran productos.

El resultado final de este step es la generación del archivo `output/branded-products-{timestamp}.json`. Ejemplo: `output/branded-products-20180514.json`

Layout ejemplo:
```json
[
    {
        "id": 166,
        "nombre": "ACEITE",
        "catalogo": "ALIMENTOS",
        "categoria": "ACEITES, GRASAS Y VINAGRES",
        "marcas": [
            {
                "id": "058",
                "marca": "ACEITE 123 BOTELLA 1 LT. MIXTO"
            },
            {
                "id": "127",
                "marca": "ACEITE CANOIL BOTELLA 1 LT. CANOLA"
            },
            {
                "id": "014",
                "marca": "ACEITE CAPULLO BOTELLA 840 ML. CANOLA"
            },
            {
                "id": "125",
                "marca": "ACEITE KARTAMUS BOTELLA 900 ML. MIXTO"
            },
            {
                "id": "112",
                "marca": "ACEITE 1-2-3 BOTELLA 500 ML. MIXTO"
            }
        ]
    },
    {
        "id": 9000,
        "nombre": "ACEITE DE OLIVA",
        "catalogo": "ALIMENTOS",
        "categoria": "ACEITES, GRASAS Y VINAGRES",
        "marcas": [
            {
                "id": "026",
                "marca": "ACEITE DE OLIVA BORGES BOTELLA 500 ML. (ETIQ. AMARILLA)."
            },
            {
                "id": "023",
                "marca": "ACEITE DE OLIVA BORGES. ORIGINAL BOTELLA 500 ML. EXTRA VIRGEN (ETIQ. VERDE)."
            },
            {
                "id": "004",
                "marca": "ACEITE DE OLIVA CARBONELL BOTELLA 750 ML. EXTRA VIRGEN"
            },
            {
                "id": "035",
                "marca": "ACEITE DE OLIVA CARBONELL. CL\u00c1SICO LATA 450 ML."
            },
            {
                "id": "036",
                "marca": "ACEITE DE OLIVA CARBONELL. CL\u00c1SICO LATA 950 ML."
            },
            {
                "id": "021",
                "marca": "ACEITE DE OLIVA FILIPPO BERIO BOTELLA 750 ML. (IDEAL PARA COCINAR SALSAS Y PASTAS)"
            }
        ]
    },
    {
        "id": 9002,
        "nombre": "ALCAPARRA",
        "catalogo": "ALIMENTOS",
        "categoria": "ACEITES, GRASAS Y VINAGRES",
        "marcas": [
            {
                "id": "003",
                "marca": "ALCAPARRA EL SERPIS FRASCO 100 GR."
            }
        ]
    }
]
```
### 4 Descargar precios por marca y municipio
Una vez que se cuentan con el catalogo de productos sin precios y marcas registradas por profeco el siguiente paso es descargar la lista de precios por la relación producto/marca.

Las peticiones a los endpoints son realizadas mediante consultas GET con parametros de url. Los endpoints usados son los siguientes:
- Endpoint: http://200.53.148.112/json/listaEst.php
    - Parametros:
        - **idProducto**: Id del producto del que se desea obtener sus precios.
        - **idMarca**: Id de la marca relacionada al producto.
        - **idCiudad**: Id de la ciudad donde se buscaran productos.
        - **idMunicipio**: Id del municipio donde se buscaran productos.

El resultado final de este step es la generación del archivo `output/prices-per-product-{timestamp}.json`. Ejemplo: `output/prices-per-product-20180514.json`
Layout ejemplo:
```json
[
    {
        "producto_id": 166,
        "marca": "ACEITE CAPULLO BOTELLA 840 ML. CANOLA",
        "id_marca": "014",
        "date": "20180725",
        "idEstablecimiento": "39000",
        "estado": "Guerrero",
        "establecimiento": "SORIANA HIPER SUCURSAL ACAPULCO COSTERA (274)",
        "observacion": "17/07/2018",
        "direccion": "COSTERA MIGUEL ALEMAN 240, ENTRE JUAN S. CANO Y GABRIEL",
        "colonia": "FRACCIONAMIENTO HORNOS",
        "ciudad": "Acapulco de Ju\u00e1rez",
        "cp": "39350",
        "telefono": "(744)4696160",
        "latitud": "16.858598",
        "longitud": "-99.890270",
        "precio": "29.9",
        "distancia": "0"
    },
    ...
    {
        "producto_id": 166,
        "marca": "ACEITE CAPULLO BOTELLA 840 ML. CANOLA",
        "id_marca": "014",
        "date": "20180725",
        "idEstablecimiento": "39003",
        "estado": "Guerrero",
        "establecimiento": "MEGA SORIANA SUCURSAL LA DIANA",
        "observacion": "18/07/2018",
        "direccion": "AV. FARALLON DEL OBISPO 216, ENTRE NAVEGANTE JUAN PEREZ",
        "colonia": "FARALLON",
        "ciudad": "Acapulco de Ju\u00e1rez",
        "cp": "39690",
        "telefono": "(744)4847861",
        "latitud": "16.861329",
        "longitud": "-99.870535",
        "precio": "31.5",
        "distancia": "0"
    }
]
```
## Especificaciones tecnicas
### Instalación Local
Para instalar la aplicación en ambientes locales en ambientes `Linux`, se debe hacer lo siguiente.
1. Definir variables de entorno con los valores necesarios.
```sh
export DATABASE_HOST="0.0.0.0"
export DATABASE_USERNAME="username"
export DATABASE_PASSWORD="password"
export DATABASE_PORT="5435"
export RUN_MIGRATIONS="True"
```
2. Correr los siguientes comandos.
```sh
git clone git@github.com:vaquer/qqp.git
cd qqp
python setup.py install
```
### Instalación Kubernetes
Para implementaciones basadas en Kubernetes se tienen definidos los archivos de definición para deployment manejando la versión `v1beta1`.

1. Editar variables de entorno en los archivos `kubernetes/postgres.yml` y `kubernetes/etl.yml`, los valores deben coincidir en ambos archivos.

2. Correr los siguientes comandos.
```sh
git clone git@github.com:vaquer/qqp.git
cd qqp
kubectl apply -f kubernetes/etl.yml
```
*NOTA: Esta aplicación no requiere definición de servicio puesto que no expone puertos para consumo exterior*

### Ejecucion Local del ETL
Una vez dentro de la carpeta de qqp se debe correr el siguiente comando.
```sh
luigi --module qqp.etl.pipeline StartETL --local-scheduler
```

## API QQP

Se contruyo un API con una mejor estructura para consumo y consulta de datos de la base de datos QQP. API QQP esta diseñada con base en los estandares REST y regresa resultados en formato JSON.

### Uso
El uso del API puede consultarse en la [documentación](https://vaquer.github.io/qqp-docs/#introduccion) oficial.

### Instalación local
Para instalar la aplicación en ambientes locales en ambientes `Linux`, se debe hacer lo siguiente.
1. Definir variables de entorno con los valores necesarios.
```sh
export DATABASE_HOST="0.0.0.0"
export DATABASE_USERNAME="username"
export DATABASE_PASSWORD="password"
export DATABASE_PORT="5435"
export RUN_MIGRATIONS="True"
```
2. Correr los siguientes comandos.
```sh
git clone git@github.com:vaquer/qqp.git
cd qqp
python setup.py install
```
### Instalación Kubernetes
Para implementaciones basadas en Kubernetes se tienen definidos los archivos de definición para deployment manejando la versión `v1beta1`.

1. Editar variables de entorno en los archivos `kubernetes/postgres.yml` y `kubernetes/api.yml`, los valores deben coincidir en ambos archivos.


2. Correr los siguientes comandos.
```sh
git clone git@github.com:vaquer/qqp.git
cd qqp
kubectl apply -f kubernetes/postgres.yml
kubectl apply -f kubernetes/api.yml
```

*NOTA 1: La aplicación es expuesta en el puerto 8000 en el deployment de Kubernetes*

*NOTA 2: No es necessario editar ni levantar el archivo kubernetes/postgres.yml si ya se hizo en la instalación del ETL*

*NOTA 3: Es responsabilidad del administrador del sistema la creación los archivos con las definiciones de los servicios Kubernetes que expondran la aplicación.*

# Construcción de imagenes Docker
Un paso necesario para generar el ambiente Kubernetes es generar las imagenes Docker. Se necesitan correr los siguientes comandos desde la carpeta raiz del proyecto.

- Docker API
```sh
docker build -t mxabierto/qqp-api:v1.0 api/Dockerfile
```

- Docker ETL
```sh
docker build -t mxabierto/qqp-etl:v1.0 etl/Dockerfile
```

- Docker Postgres
```sh
docker build -t mxabierto/qqp-postgres:v1.0 postgres
```

*NOTA: Se debera cambiar la versión que se coloca en el tag de la imagen cada vez que se realice un cambio*