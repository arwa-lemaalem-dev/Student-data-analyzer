# Student-data-analyzer
# Project for Excel File Analysis and Data Insertion

Get feedback of students 

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.x
- pandas (for data manipulation)
- mysql-connector-python (for MySQL connection)
- tqdm (for displaying progress bars)

## Usage

1. Place your images files to analyze in the `uploads` directory.

2. Run the main script ``mono_thread.py`` to start the processing:

```bash
python mono_thread.py
```

The script will process each Excel file found in the ``uploads`` directory, display a progress bar for each file, and insert the data into the database.

Mono thread : 27.95 secondes
