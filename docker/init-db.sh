#!/bin/bash
# Wait for SQL Server to start, then run initial SQL if needed
sleep 30
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${SA_PASSWORD}" -No -Q "
IF DB_ID('ProcurementDB') IS NULL
    CREATE DATABASE ProcurementDB COLLATE Vietnamese_CI_AS;
"
echo "Database initialization complete."
