import pytesseract
from PIL import Image
import os
from textblob import TextBlob
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Spécifiez explicitement le chemin de Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\lemaa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Définition des chemins et dossiers
UPLOADS_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'

# Création des dossiers 'uploads' et 'reports' s'ils n'existent pas
os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Initialisation du sémaphore avec une limite de 4 threads
semaphore = threading.Semaphore(8)

def extract_feedback_data(image_path):
    # Utilisation de pytesseract pour OCR l'image et extraire le texte
    try:
        extracted_text = pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte pour {image_path}: {e}")
        extracted_text = ""
    return extracted_text

def analyze_feedback(feedback_text):
    # Analyse de sentiment avec TextBlob
    blob = TextBlob(feedback_text)
    sentiment = blob.sentiment.polarity
    sentiment_label = "positif" if sentiment > 0 else "négatif" if sentiment < 0 else "neutre"
    return sentiment_label, sentiment

def generate_report_summary(student_feedbacks):
    # Compter le nombre total d'étudiants ayant donné leur feedback
    total_students = len(student_feedbacks)
    
    # Initialiser les compteurs de feedbacks
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    # Liste des feedbacks négatifs
    negative_feedbacks = []
    
    # Analyser chaque feedback
    for feedback in student_feedbacks.values():
        if feedback['sentiment_label'] == 'positif':
            positive_count += 1
        elif feedback['sentiment_label'] == 'négatif':
            negative_count += 1
            negative_feedbacks.append(feedback['feedback'])
        elif feedback['sentiment_label'] == 'neutre':
            neutral_count += 1
    
    # Construction du contenu du rapport
    report_content = f"Nombre d'étudiants ayant donné leur feedback : {total_students}\n\n"
    report_content += f"Nombre de feedbacks positifs : {positive_count}\n"
    report_content += f"Nombre de feedbacks négatifs : {negative_count}\n"
    report_content += f"Nombre de feedbacks neutres : {neutral_count}\n\n"
    
    if negative_feedbacks:
        report_content += "Liste des feedbacks négatifs :\n"
        for index, feedback in enumerate(negative_feedbacks, start=1):
            report_content += f"{index}. {feedback}\n"
    
    # Sauvegarde du rapport dans un fichier texte
    report_path = os.path.join(REPORTS_FOLDER, 'summary_report.txt')
    with open(report_path, 'w', encoding='utf-8') as file:
        file.write(report_content)

def process_feedback_image(image_path):
    # Extraire les données du formulaire
    extracted_text = extract_feedback_data(image_path)
    
    # Traiter les données extraites pour obtenir le nom de l'étudiant et le feedback
    lines = extracted_text.splitlines()
    if len(lines) >= 2:
        student_name = lines[0].strip()  # Supposons que le nom de l'étudiant est la première ligne
        feedback = lines[1].strip()      # Supposons que le feedback est la deuxième ligne
    else:
        student_name = "Nom non trouvé"
        feedback = "Feedback non trouvé"
    
    # Analyser le feedback pour obtenir le sentiment
    sentiment_label, sentiment_score = analyze_feedback(feedback)
    
    # Retourner les données du feedback
    return student_name, feedback, sentiment_label

def process_feedback_image_semaphore(image_path):
    with semaphore:
        return process_feedback_image(image_path)

def process_feedback_forms_multithread_with_semaphore():
    # Liste des chemins pour les images générées
    image_paths = [os.path.join(UPLOADS_FOLDER, filename) for filename in os.listdir(UPLOADS_FOLDER) if filename.endswith('.jpg')]
    
    # Dictionnaire pour stocker les feedbacks par étudiant
    student_feedbacks = {}
    
    # Mesurer le temps d'exécution total
    start_time = time.time()
    
    # Utilisation de tqdm pour la barre de progression
    with tqdm(total=len(image_paths), desc='Traitement des formulaires') as pbar:
        
        # Utilisation de ThreadPoolExecutor pour exécuter les traitements en parallèle
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_feedback_image_semaphore, image_path) for image_path in image_paths]
            
            # Attendre la fin de tous les threads et récupérer les résultats
            for future in as_completed(futures):
                student_name, feedback, sentiment_label = future.result()
                # Stocker le feedback dans le dictionnaire par étudiant
                student_feedbacks[student_name] = {
                    'feedback': feedback,
                    'sentiment_label': sentiment_label
                }
                pbar.update(1)
    
    # Générer le rapport récapitulatif
    generate_report_summary(student_feedbacks)
    
    # Afficher le temps d'exécution total
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Temps d'exécution total : {execution_time:.2f} secondes")

# Appel de la fonction multithread pour traiter les formulaires
process_feedback_forms_multithread_with_semaphore()
