#!/bin/bash

DB_NAME="cafe"
USERNAME="your_username"
BACKUP_PATH="/path/to/your/backup/directory"
BACKUP_FILENAME="db_backup_$(date +%Y%m%d_%H%M%S).sql"

# Создание резервной копии
pg_dump -U $USERNAME $DB_NAME > $BACKUP_PATH/$BACKUP_FILENAME

# Проверка, успешно ли выполнено копирование
if [ $? -eq 0 ]; then
  echo "Backup was created successfully"
else
  echo "Failed to create backup"
fi
