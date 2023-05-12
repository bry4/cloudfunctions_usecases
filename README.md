# USE CASE - CLOUD FUNCTIONS

## UC 1

### DESARROLLO DEL APP EN PYTHON
La solución se ha dado en 4 casos el cual se desarrolló en cloud functions cada uno:

 - App migracion de CSV a Base de datos(BD)

La app se encuentra en la siguiente ruta: gcf/csv-migration

Dentro del cual se encuentra una carpeta "src" donde se encuentra el código que se sube a cloud function, y también está un ejemplo de service account que enviaré por correo y el Dockerfile para testear localmente.

La ejecución local sería así:

`docker build -t csv-migration . && docker run --rm csv-migration`


 - App de un REST API para insertar a BD

La app se encuentra en la siguiente ruta: gcf/backup-process

Dentro del cual se encuentra una carpeta "src" donde se encuentra el código que se sube a cloud function, y también está un ejemplo de service account que enviaré por correo y el Dockerfile para testear localmente.

La ejecución local sería así:

`docker build -t rest-api . && docker run --rm -p 8080:8080 rest-api`


 - App de generación de backups de todas las tablas a cloud storage

La app se encuentra en la siguiente ruta: gcf/backup-process

Dentro del cual se encuentra una carpeta "src" donde se encuentra el código que se sube a cloud function, y también está un ejemplo de service account que enviaré por correo y el Dockerfile para testear localmente.

La ejecución local sería así:

`docker build -t backup-process . && docker run --rm -p 8080:8080 backup-process`

 - App para restauración de tablas a partir del backup

La app se encuentra en la siguiente ruta: gcf/restore-process

Dentro del cual se encuentra una carpeta "src" donde se encuentra el código que se sube a cloud function, y también está un ejemplo de service account que enviaré por correo y el Dockerfile para testear localmente.

La ejecución local sería así:

`docker build -t restore-process . && docker run --rm -p 8080:8080 restore-process`

- Para el caso de REST-API cumple con una estructura como la siguiente:
```json
{
    "table": "table_name",
    "values": [
        {"col1": "val1","col2": "val2"},
        {"col1": "val3","col2": "val4"}
    ],
    "mode": "append"
}
```
- Para testear REST-API localmente hay dos opciones:
    - Se debe acceder a GCP por gcloud localmente y se ejecutaría el siguiente comando:

    ```bash
    curl -m 70 -X POST https://us-central1-green-device-382800.cloudfunctions.net/rest-api-function \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
    "table": "departments",
    "values": [
        {"id": 1,"department": "Supply Chain"},
        {"id": 2,"department": "Sales"}
        ],
    "mode": "append"
}'
    ```

#### Dentro de los recursos creados dentro de GCP están:

 - Google Cloud Storage:
    - artifacts-bjvc-test: 
        - Para almacenar source del script en Python de cada Cloud Functions
        - Para almacenar backups programados de cada tabla de la Base de Datos
    - data-bjvc-test: Almacena la data histórica por archivo, se ingesta a la Base de datos cada vez que se suba un archivo referente a cada tabla de la BD.
    - terraform-state-bjvc-test: Almacena el archivo de estados de Terraform, donde se encuentra todos los recursos mapeados y desplegados por Terraform.
 
 - Google Cloud Functions: Se creo un cloud functions por cada caso
    - csv-migration-function
    - rest-api-function
    - backup-process-function
    - restore-process-function


### DESPLIEGUE DE LA INFRAESTRUCTURA CON TERRAFORM

Para poder desplegar de forma continua, se está usando terraform para mapear los recursos que se están usando y además se está usando CLOUD BUILD para desplegar de manera automática cada vez que detecte un cambio dentro de cada SRC de cloud functions, cuando se haga PUSH  a la rama MAIN del repositorio.

El archivo de estados se está manejando de manera remota, por lo que para ejecutar localmente deberá tener accceso por gcloud y luego se pueden utilizar los siguiente comandos dentro de la carpeta 'terraform/':

Para inicializar el workspace de terraform
`terraform init`

Para mapear recursos y compararlos con el archivo de estados
`terraform plan`

Para ejecutar cambios en el código de infraestructura
`terraform apply`

Para el despliegue automático se usa CLOUD BUILD el cuál despliega el siguiente yaml: cloudbuild.yaml
Donde se encuentra los steps de los comando de terraform: init, plan, apply

## UC 2

 - App end-point para recibir resultado por caso o requerimiento(Query hecho a medida por caso)

La app se encuentra en la siguiente ruta: gcf/end-point-requirement

Dentro del cual se encuentra una carpeta "src" donde se encuentra el código que se sube a cloud function, y también está un ejemplo de service account que enviaré por correo y el Dockerfile para testear localmente.

La ejecución local sería así:

`docker build -t endpoint-requirement . && docker run --rm -p 8080:8080 endpoint-requirement`
