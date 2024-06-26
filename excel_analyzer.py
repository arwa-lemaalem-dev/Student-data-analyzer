import os
import pandas as pd
import mysql.connector
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Configuration de la base de données MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,  # Port par défaut de MySQL
    'user': 'root',
    'password': '',  # Assurez-vous que ce champ est correct
    'database': 'excel_analyzer'
}

# Fonction de prétraitement des données
def preprocess_data(df):
    # Exemple de prétraitement : conversion des dates et normalisation des données
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    df = df.dropna()
    
    # Encodage des variables catégorielles
    label_encoder = LabelEncoder()
    df['classe'] = label_encoder.fit_transform(df['classe'])
    
    X = df[['cin', 'classe']]  # Supposons que 'cin' et 'classe' sont les caractéristiques
    y = df['nom']  # Supposons que 'nom' est la variable cible pour cet exemple
    return X, y, label_encoder

# Fonction pour entraîner le modèle
def train_model(X_train, y_train):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    return model, scaler

# Fonction pour traiter un fichier Excel
def process_excel_file(file_path, model, scaler, label_encoder):
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        X, y, _ = preprocess_data(df)
        X = scaler.transform(X)
        
        # Prédiction des noms des étudiants (exemple)
        predictions = model.predict(X)
        df['predicted_nom'] = predictions

        # Connexion à la base de données
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insérer les données dans la base de données
        total_rows = len(df)
        with tqdm(total=total_rows, desc=os.path.basename(file_path)) as pbar:
            for _, row in df.iterrows():
                query = """
                INSERT INTO etudiants (nom, date_naissance, cin, classe, predicted_nom)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (row['nom'], row['date_naissance'], row['cin'], row['classe'], row['predicted_nom'])
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
    # Générer un DataFrame d'exemple pour l'entraînement du modèle
    data = {
        'nom': ['John Doe', 'Jane Doe', 'Jim Beam', 'Jill Valentine'],
        'date_naissance': ['1990-01-01', '1992-02-02', '1991-03-03', '1993-04-04'],
        'cin': [12345678, 87654321, 11223344, 44332211],
        'classe': ['Math', 'Science', 'History', 'Art']
    }
    df_train = pd.DataFrame(data)
    X, y, label_encoder = preprocess_data(df_train)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model, scaler = train_model(X_train, y_train)

    # Évaluer le modèle
    X_test = scaler.transform(X_test)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Précision du modèle: {accuracy:.2f}")

    # Obtenir tous les fichiers Excel du dossier
    excel_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]
    total_files = len(excel_files)

    print(f"Début du traitement de {total_files} fichiers")

    start_time = time.time()

    # Utiliser ThreadPoolExecutor pour traiter les fichiers en parallèle
    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path in excel_files:
            futures.append(executor.submit(process_excel_file, file_path, model, scaler, label_encoder))
        
        # Attendre que tous les fichiers soient traités
        for future in futures:
            future.result()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Traitement de tous les fichiers terminé en {elapsed_time:.2f} secondes")

if __name__ == "__main__":
    folder_path = "uploads"
    main(folder_path)
