#!/bin/bash # shebang para bash

# script de backup de la base de datos criptomed
# este script crea un backup de la base de datos postgresql usando pg_dump

# configuracion
CONTAINER_NAME="criptomed_db" # nombre del contenedor docker
DB_NAME="criptomed" # nombre de la base de datos
BACKUP_DIR="./backups" # directorio donde se guardan los backups
TIMESTAMP=$(date +"%Y%m%d_%H%M%S") # timestamp para el nombre del archivo
BACKUP_FILE="$BACKUP_DIR/criptomed_backup_$TIMESTAMP.sql" # nombre del archivo de backup

# crea el directorio de backups si no existe
mkdir -p "$BACKUP_DIR" # crea directorio

echo "=== iniciando backup de base de datos ===" # mensaje de inicio
echo "contenedor: $CONTAINER_NAME" # muestra contenedor
echo "base de datos: $DB_NAME" # muestra base de datos
echo "archivo de backup: $BACKUP_FILE" # muestra archivo

# ejecuta pg_dump dentro del contenedor docker
docker exec "$CONTAINER_NAME" pg_dump -U criptomed "$DB_NAME" > "$BACKUP_FILE" # ejecuta backup

if [ $? -eq 0 ]; then # si el backup fue exitoso
    echo "backup completado exitosamente: $BACKUP_FILE" # mensaje de exito
    echo "tamaño del backup: $(du -h "$BACKUP_FILE" | cut -f1)" # muestra tamaño
else # si el backup fallo
    echo "error al realizar el backup" # mensaje de error
    exit 1 # sale con error
fi

# mantener solo los ultimos 7 backups (opcional)
# elimina backups mas antiguos de 7 dias
find "$BACKUP_DIR" -name "criptomed_backup_*.sql" -mtime +7 -delete

echo "=== backup finalizado ===" # mensaje final
