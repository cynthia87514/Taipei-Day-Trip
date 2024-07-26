#!/bin/sh

echo "Waiting for database connection..."
while ! nc -z db 3306; do
  sleep 1
done
echo "Database is up!"

echo "Checking if database initialization is necessary..."
# 檢查資料庫中是否存在 attrations table
if ! mysql -h db -u root -p$MYSQL_PASSWORD -e "USE taipei-day-trip; SHOW TABLES LIKE 'attractions';" | grep "attractions" > /dev/null; then
  echo "Initializing database..."
  mysql -h db -u root -p$MYSQL_PASSWORD < /docker-entrypoint-initdb.d/init.sql
else
  echo "Table 'attractions' already exists."
fi

echo "Running data processing script if necessary..."
# 檢查 attractions table 中是否有資料
if mysql -h db -u root -p$MYSQL_PASSWORD -e "USE taipei-day-trip; SELECT COUNT(*) FROM attractions;" | grep -q "0"; then
  echo "Populating database with initial data..."
  python /app/data/data_process.py
else
  echo "Table 'attractions' already has data."
fi

echo "Starting web server..."
uvicorn app:app --host 0.0.0.0 --port 8000