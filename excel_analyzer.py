import os
import pandas as pd
import mysql.connector
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import time

# Configuration de la base de données MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,  # Port par défaut de MySQL
    'user': 'root',
    'password': '',  # Assurez-vous que ce champ est correct
    'database': 'excel_analyzer'
}

# Fonction pour traiter un fichier Excel
def process_excel_file(file_path):
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)

        # Connexion à la base de données
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insérer les données dans la base de données
        total_rows = len(df)
        with tqdm(total=total_rows, desc=os.path.basename(file_path)) as pbar:
            for _, row in df.iterrows():
                query = """
                INSERT INTO etudiants (nom, date_naissance, cin, classe)
                VALUES (%s, %s, %s, %s)
                """
                values = (row['nom'], row['date_naissance'], row['cin'], row['classe'])
                cursor.execute(query, values)
                pbar.update(1)

        # Valider les changements et fermer la connexion
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        tqdm.write(f"Erreur lors du traitement de {os.path.basename(file_path)}: {str(e)}")

# Fonction principale
def main(folder_path):
    # Obtenir tous les fichiers Excel du dossier
    excel_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]
    total_files = len(excel_files)

    print(f"Début du traitement de {total_files} fichiers")

    start_time = time.time()

    # Utiliser ThreadPoolExecutor pour traiter les fichiers en parallèle
    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path in excel_files:
            futures.append(executor.submit(process_excel_file, file_path))
        
        # Attendre que tous les fichiers soient traités
        for future in futures:
            future.result()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Traitement de tous les fichiers terminé en {elapsed_time:.2f} secondes")

if __name__ == "__main__":
    folder_path = "uploads"
    main(folder_path)
