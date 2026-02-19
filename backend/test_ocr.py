# script prermettant de tester l'endpoint OCR du backend


import os
import requests
import dotenv

dotenv.load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Erreur : la variable d'environnement GROQ_API_KEY n'est pas définie.")
    exit(1)

BASE_URL = "http://localhost:5000/api"
IMAGE_PATHS = [
    r"images\IMG_20260219_081540.jpg",
    r"images\IMG_20260219_081548.jpg"
]

def test_ocr():
    files = []
    handles = []
    try:
        for path in IMAGE_PATHS:
            f = open(path, "rb")
            handles.append(f)
            files.append(("images", (os.path.basename(path), f, "image/jpeg")))

        response = requests.post(f"{BASE_URL}/ocr", files=files)
    finally:
        for f in handles:
            f.close()

    print(f"Status : {response.status_code}")

    if response.ok:
        data = response.json()
        print(f"Matière  : {data.get('matiere')}")
        print(f"Cours    : {data.get('nom_cours')}")
        print(f"Fichier  : {data.get('fichier')}")
        print(f"\nTexte extrait :\n{data.get('texte')}")
    else:
        print(f"Erreur : {response.json()}")

if __name__ == "__main__":
    test_ocr()
