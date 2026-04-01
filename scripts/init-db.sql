-- Create databases for services
SELECT 'CREATE DATABASE gas_user_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gas_user_db')\gexec

SELECT 'CREATE DATABASE gas_chart'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gas_chart')\gexec

SELECT 'CREATE DATABASE gas_alerts'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gas_alerts')\gexec
