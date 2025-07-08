# ETL Data Pipeline

A basic ETL (Extract, Transform, Load) data pipeline that processes country metrics data using Apache Spark and PostgreSQL databases.

## Overview

This project implements a data pipeline that:

1. **Extracts** data from a source PostgreSQL database
2. **Transforms** the data by filtering countries based on GDP per capita and HDI criteria
3. **Loads** the filtered results into a target PostgreSQL database

### Transformation Logic

The pipeline filters countries that meet the following criteria:

- **GDP per capita** greater than the mean GDP per capita across all countries
- **HDI (Human Development Index)** greater than 1.2 standard deviations above the mean HDI

This identifies countries that are both economically prosperous and have high human development indicators.

## Project Structure

```
ETL_Pipeline/
├── artifacts/              # Build outputs and logs (gitignored)
├── data/
│   └── countries_metric.csv    # Source data file
├── db_init/
│   ├── load_source.py      # Script to load CSV data into source DB
│   ├── source_init.sql     # Source database schema
│   └── target_init.sql     # Target database schema
├── jdbc_drivers/
│   └── postgresql-42.7.7.jar  # PostgreSQL JDBC driver (gitignored)
├── compose.yml             # Docker Compose configuration
├── pipeline.py             # Main ETL pipeline script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Prerequisites

### 1. Docker and Docker Compose

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Ensure Docker Compose is available

### 2. Python Environment

- Python 3.8 or higher
- pip package manager

### 3. Hadoop Installation (Windows)

**Download and Setup:**

1. Download Hadoop 3.3.4 from [Apache Hadoop](https://hadoop.apache.org/releases.html)
2. Extract to `C:\hadoop\hadoop-3.3.4`
3. Set environment variables:
   ```
   HADOOP_HOME=C:\hadoop\hadoop-3.3.4
   PATH=%PATH%;%HADOOP_HOME%\bin
   ```

**Alternative: Use WSL2 for better Hadoop support on Windows**

### 4. Java Requirements

- Java 8 or higher (required for Apache Spark)
- Set `JAVA_HOME` environment variable

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ETL_Pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download JDBC Driver

The PostgreSQL JDBC driver is required for Spark to connect to PostgreSQL databases. The driver file `postgresql-42.7.7.jar` should be placed in the `jdbc_drivers/` directory.

**Manual Download:**

1. Download [PostgreSQL JDBC Driver](https://jdbc.postgresql.org/download/)
2. Place `postgresql-42.7.7.jar` in the `jdbc_drivers/` folder

## Usage

### 1. Start the Databases

```bash
docker-compose up -d
```

This starts two PostgreSQL databases:

- **Source DB**: `localhost:5433` (database: `source`)
- **Target DB**: `localhost:5434` (database: `target`)

### 2. Load Source Data

```bash
python db_init/load_source.py
```

This script:

- Reads the CSV data from `data/countries_metric.csv`
- Cleans and normalizes the data
- Loads it into the source database

### 3. Run the ETL Pipeline

```bash
python pipeline.py
```

The pipeline will:

1. Connect to the source database
2. Read country metrics data
3. Calculate mean and standard deviation for GDP per capita and HDI
4. Filter countries based on the transformation criteria
5. Write results to the target database

### 4. Verify Results

Connect to the target database to view the filtered results:

```sql
-- Connect to target DB (localhost:5434)
SELECT * FROM target_table;
```

## Database Schemas

### Source Database (`source`)

```sql
CREATE TABLE source_table (
    country_name TEXT PRIMARY KEY,
    population BIGINT,
    nominal_gdp_usd BIGINT,
    nominal_gdp_per_capita_usd DOUBLE PRECISION,
    gdp_per_capita_ppp_usd DOUBLE PRECISION,
    hdi DOUBLE PRECISION,
    gini DOUBLE PRECISION,
    area_sq_km DOUBLE PRECISION
);
```

### Target Database (`target`)

```sql
CREATE TABLE target_table (
    country_name TEXT PRIMARY KEY,
    nominal_gdp_per_capita_usd DOUBLE PRECISION,
    hdi DOUBLE PRECISION
);
```

## Configuration

### Database Connections

- **Source DB**: `jdbc:postgresql://localhost:5433/source`
- **Target DB**: `jdbc:postgresql://localhost:5434/target`
- **Username**: `postgres`
- **Password**: `password`

### Spark Configuration

- **App Name**: "ETL Pipeline"
- **JDBC Driver**: `org.postgresql.Driver`
- **Hadoop Home**: `C:/hadoop/hadoop-3.3.4`

## Troubleshooting

### Common Issues

1. **Hadoop not found**: Ensure `HADOOP_HOME` is set correctly
2. **JDBC driver missing**: Verify `postgresql-42.7.7.jar` is in `jdbc_drivers/`
3. **Database connection failed**: Check if Docker containers are running
4. **Java not found**: Install Java 8+ and set `JAVA_HOME`

### Windows-Specific Notes

- Use forward slashes in file paths for Hadoop
- Consider using WSL2 for better Hadoop compatibility
- Ensure Docker Desktop is running before starting containers

## Data Flow

1. **Extract**: CSV data → Source PostgreSQL database
2. **Transform**: Filter countries based on GDP and HDI criteria
3. **Load**: Filtered results → Target PostgreSQL database

The transformation identifies countries that are both economically prosperous (high GDP per capita) and have excellent human development indicators (high HDI relative to the global average).

## Dependencies

- **Apache Spark**: Distributed computing framework
- **PostgreSQL**: Database systems
- **pandas**: Data manipulation
- **psycopg2**: PostgreSQL adapter for Python
- **Docker**: Containerization platform
