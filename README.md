# Student-data-analyzer
Get feedback of students 

## Prerequisites
Before you begin, make sure you have the following installed:
- Python 3.x

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
* Mono thread : 4.22 secondes
* Multi threads : 2.55 secondes
