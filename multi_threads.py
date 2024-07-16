import pytesseract
from PIL import Image
import os
from textblob import TextBlob
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\lemaa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

UPLOADS_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'

# Initialization of the queue
image_queue = queue.Queue()

student_feedbacks = {}

# synchronize access to the feedback dictionary
feedbacks_lock = threading.Lock()

def extract_feedback_data(image_path):
    try:
        extracted_text = pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte pour {image_path}: {e}")
        extracted_text = ""
    return extracted_text

def analyze_feedback(feedback_text):
    blob = TextBlob(feedback_text)
    sentiment = blob.sentiment.polarity
    sentiment_label = "positif" if sentiment > 0 else "négatif" if sentiment < 0 else "neutre"
    return sentiment_label, sentiment

def generate_report_summary(student_feedbacks):
    total_students = len(student_feedbacks)
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    negative_feedbacks = []
    
    for feedback in student_feedbacks.values():
        if feedback['sentiment_label'] == 'positif':
            positive_count += 1
        elif feedback['sentiment_label'] == 'négatif':
            negative_count += 1
            negative_feedbacks.append(feedback['feedback'])
        elif feedback['sentiment_label'] == 'neutre':
            neutral_count += 1
    
    report_content = f"Nombre d'étudiants ayant donné leur feedback : {total_students}\n\n"
    report_content += f"Nombre de feedbacks positifs : {positive_count}\n"
    report_content += f"Nombre de feedbacks négatifs : {negative_count}\n"
    report_content += f"Nombre de feedbacks neutres : {neutral_count}\n\n"
    
    if negative_feedbacks:
        report_content += "Liste des feedbacks négatifs :\n"
        for index, feedback in enumerate(negative_feedbacks, start=1):
            report_content += f"{index}. {feedback}\n"
    
    report_path = os.path.join(REPORTS_FOLDER, 'summary_report.txt')
    with open(report_path, 'w', encoding='utf-8') as file:
        file.write(report_content)

def process_feedback_image(image_path):
    extracted_text = extract_feedback_data(image_path)
    lines = extracted_text.splitlines()
    if len(lines) >= 2:
        student_name = lines[0].strip()
        feedback = lines[1].strip()
    else:
        student_name = "Nom non trouvé"
        feedback = "Feedback non trouvé"
    
    sentiment_label, sentiment_score = analyze_feedback(feedback)
    
    with feedbacks_lock:
        student_feedbacks[student_name] = {
            'feedback': feedback,
            'sentiment_label': sentiment_label
        }

def producer(image_paths, producer_pbar):
    for image_path in image_paths:
        image_queue.put(image_path)
        producer_pbar.update(1)
    producer_pbar.close()

def consumer(consumer_id, total_images):
    consumer_pbar = tqdm(total=total_images, desc=f'Consommateur {consumer_id}')
    while not image_queue.empty():
        image_path = image_queue.get()
        process_feedback_image(image_path)
        consumer_pbar.update(1)
        image_queue.task_done()
    consumer_pbar.close()

def process_feedback_forms_producer_consumer():
    print("=== Mode d'exécution : Producteur/Consommateur ===")
    start_time = time.time()
    
    image_paths = [os.path.join(UPLOADS_FOLDER, filename) for filename in os.listdir(UPLOADS_FOLDER) if filename.endswith('.jpg')]
    total_images = len(image_paths)
    
    producer_pbar = tqdm(total=total_images, desc='Producteur')
    
    # Initialization of producer threads
    producer_thread = threading.Thread(target=producer, args=(image_paths, producer_pbar))
    producer_thread.start()
    
    # Initialization of consumer threads
    consumer_threads = []
    num_consumers = 4  
    for i in range(num_consumers):
        t = threading.Thread(target=consumer, args=(i + 1, total_images // num_consumers))
        consumer_threads.append(t)
        t.start()
    
    # Wait until the producer finished
    producer_thread.join()
    
    # Wait until all consumers finish
    for t in consumer_threads:
        t.join()
    
    generate_report_summary(student_feedbacks)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Temps d'exécution total : {execution_time:.2f} secondes")

process_feedback_forms_producer_consumer()
