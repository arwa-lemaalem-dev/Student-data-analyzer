# Student-data-analyzer
# Project for Excel File Analysis and Data Insertion

This Python project analyzes Excel files containing student information (name, date of birth, ID number, class) and inserts this data into a MySQL database.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.x
- pandas (for data manipulation)
- mysql-connector-python (for MySQL connection)
- tqdm (for displaying progress bars)

Install dependencies using `pip`:

```bash
pip install pandas mysql-connector-python tqdm
````

## Database Configuration

Ensure you have a configured MySQL database. You can set the connection parameters in the ``excel_analyzer.py`` file:

```bash	
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'excel_analyzer'
}
```

## Usage

1. Place your Excel files to analyze in the `uploads` directory.

2. Run the main script ``excel_analyzer.py`` to start the processing:

```bash
python excel_analyzer.py
```

The script will process each Excel file found in the ``uploads`` directory, display a progress bar for each file, and insert the data into the database.

Mono thread : 27.95 secondes
