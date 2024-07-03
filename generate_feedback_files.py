from PIL import Image, ImageDraw, ImageFont
import os
import random
from faker import Faker

def generate_feedback_form_image(student_name, feedback, signed, image_path):
    # Dimensions de l'image
    width, height = 800, 400
    
    # Créer une nouvelle image blanche
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Police et taille
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Position des textes
    name_position = (50, 50)
    feedback_position = (50, 100)
    signature_position = (50, 150)
    
    # Texte à écrire
    name_text = f"Nom de l'étudiant : {student_name}"
    feedback_text = f"Feedback : {feedback}"
    signature_text = f"Signature : {'signé' if signed else 'non signé'}"
    
    # Écrire les textes sur l'image
    draw.text(name_position, name_text, fill='black', font=font)
    draw.text(feedback_position, feedback_text, fill='black', font=font)
    draw.text(signature_position, signature_text, fill='black', font=font)
    
    # Sauvegarder l'image
    image.save(image_path)

# Création du dossier 'uploads' s'il n'existe pas
os.makedirs('uploads', exist_ok=True)

# Initialisation de Faker pour générer des noms
fake = Faker()

# Génération de 100 images de formulaires avec des noms d'étudiants aléatoires
feedbacks = [
    "Great course!",
    "Too difficult.",
    "Well organized.",
    "Boring lectures.",
    "Loved the practical sessions.",
    "Excellent teaching!",
    "Needs improvement.",
    "Very engaging.",
    "Not enough practical examples.",
    "Great interaction with students."
]
signatures = [True, False]

for i in range(100):
    student_name = fake.name()
    feedback = random.choice(feedbacks)
    signed = random.choice(signatures)
    image_path = f'uploads/form_{i+1}.jpg'
    generate_feedback_form_image(student_name, feedback, signed, image_path)
