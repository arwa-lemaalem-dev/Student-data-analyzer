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

2. Run genrate images 

```bash
python generate_feedback_files.py
```

3. Run : 
   *  Run the main script ``mono_thread.py`` to start the processing:
    ```bash
    python mono_thread.py
    ```
   *  Run the main script ``multi_threads.py`` to start the processing:
    ```bash
    python multi_threads.py
    ```


<br><br>
* Mono thread : 25.81 secondes
* Multi threads : 10.62 secondes
