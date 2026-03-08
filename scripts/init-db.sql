-- Create gas_user_db for auth service (gas_signals is created by POSTGRES_DB env)
SELECT 'CREATE DATABASE gas_user_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gas_user_db')\gexec
