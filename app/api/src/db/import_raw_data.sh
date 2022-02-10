for entry in /app/src/data/*.sql
do
  PGPASSWORD=${POSTGRES_PASSWORD} psql -U goat -d goat -h db -f "$entry"
done