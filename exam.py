from fastapi import FastAPI, HTTPException, Depends, Header, Query, Body
from typing import List, Optional, Dict, Set
import pandas as pd
import random
from pydantic import BaseModel, Field

app = FastAPI(title="My API BY FASTAPI",
    description="Mon API consiste à charger des questions prensentes dans une base de donnés.",
    version="1.0.1")

# Charger les données depuis le fichier CSV (questions.csv) sous forme de dataframe
questions_df = pd.read_csv("questions.csv")

# Dictionnaire des identifiants (j'ai ajouté les identifiants de l'admin)
users = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine",
    "admin": "4dm1N",
}

class Question(BaseModel):
    """Question nous permet d'avoir dans le body les attributs et leurs types pour 
    pouvoir ajouter la question par l admin
    """
    question: str
    subject: str
    correct: str
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: Optional[str] = None
    remark: Optional[str] = None

class NewQuestion(BaseModel):
    question: str
    subject: str
    correct: str
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: Optional[str] = None
    remark: Optional[str] = None

def authenticate_user(username: str, password: str) -> str:
    if username in users and users[username] == password:
        return username
    raise HTTPException(status_code=401, detail="Unauthorized")
@app.get("/",name="TEST API")
def read_root():
    """Ce point permet de tester le bon fonctionnemen de mon API
    """
    return {"message": "BRAVO ! API fonctionnelle"}

@app.get("/questions/",name="CHARGEMENT DE QUESTIONS PAR LES UUTILISATEURS")
def get_questions(
    use: Optional[Set[str]] = Query(None, description="Liste des types de questions"),
    subject: Optional[Set[str]] = Query(None, description="Liste des catégories"),
    num_questions: int = 10,
    current_user: str = Depends(authenticate_user),
):
    """Ce point consiste à charger la question aprés que l'utilisateur s'est identifié.

    L'utilisateur doit choisir un type de test (use) et un ou plusieurs categories (subject).

    Pour subject : Systèmes distribués, Streaming de données,
    Classification, Automation, Data Science, Machine Learning, BDD, Docker, Sytèmes distribués                  
    
    Pour use: Test de validation, Test de positionnement, Total Bootcamp
    """
    filtered_questions = questions_df
    if use:
        filtered_questions = filtered_questions[filtered_questions["use"].isin(use)]
    if subject:
        filtered_questions = filtered_questions[filtered_questions["subject"].isin(subject)]
    if num_questions not in [5, 10, 20]:
        raise HTTPException(status_code=400, detail="Nombre de questions invalide")
    if len(filtered_questions) < num_questions:
        raise HTTPException(status_code=400, detail="Pas assez de questions disponibles")
    random_questions = filtered_questions.sample(num_questions)["question"]
    return random_questions.to_dict()


@app.post("/questions/",name="AJOUT DE QUESTION PAR ADMIN")
def create_question(
    new_question: NewQuestion,
    current_user: str = Depends(authenticate_user),
):
    """Ce point permet à l'admin d'ajouter une question dans la base de données aprés identification
    """
    global questions_df  # Ajoutez cette ligne
    # Vérifiez si l'utilisateur est un administrateur
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Créez un DataFrame à partir de la nouvelle question
    question_df = pd.DataFrame([new_question.dict()])

    # Concaténez le DataFrame existant avec le nouveau DataFrame
    questions_df = pd.concat([questions_df, question_df], ignore_index=True)
    
    return {"message": "Question ajoutée avec succès"}
