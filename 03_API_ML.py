# Réalisé par J. RONZI


from fastapi import FastAPI, HTTPException
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

app = FastAPI()

# Charger les données
DATA_FILE = "/Users/Laetitia/Documents/Wild/Projet_2/Base donnée/df_v8.csv"  # Remplacez par le nom de votre fichier
df = pd.read_csv(DATA_FILE)
# définition du df GENZ
dfgenz=df[(df['date_sortie'] >= 1990) & (df['date_sortie'] <= 2010)]

# Endpoint pour rechercher des films par morceau de titre
@app.get("/search_movies")
def search_movies(morceau_titre: str):
    morceau_titre = morceau_titre.lower()  # Normaliser pour insensibilité à la casse
    # Rechercher dans 'title'
    films_trouves = df[df['title'].str.lower().str.contains(morceau_titre, na=False)]
    films_trouves = films_trouves.sort_values(by='Nb_votes', ascending=False)
    if not films_trouves.empty:
        return {"movies": films_trouves['title'].tolist()}
    else:
        print("Le film n'existe pas dans la base")

# # Endpoint pour recommander des films similaires
@app.get("/recommend_movies")
def recommend_movies(title: str, k: int = 5):

    # Trouver l'indice du film dans le DataFrame
    id_film = df[df['title'] == title].index[0]
    
    # Sélectionner les features nécessaires pour la recommandation
    features = ['Action', 'Adventure', 'Animation', 'Biography',
                   'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
                   'Music', 'Musical', 'Mystery', 'News', 'Reality-TV', 'Romance', 'Sport',
                   'Talk-Show', 'Thriller', 'War', 'Western', 'Science_Fiction']
    
    # Standardisation des données
    scaler = StandardScaler()
    X = scaler.fit_transform(dfgenz[features])
    
    # Appliquer l'algorithme KNN pour les recommandations
    nn = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree')
    nn.fit(X)
    

    # Trouver les films similaires
    distances, indices = nn.kneighbors([X[id_film]])
    
    # Exclure le film lui-même (l'index 0 sera le film sélectionné, donc on commence à 1)
    indices_sans_cible = [i for i in indices[0] if i != id_film]

    # Obtenir les films recommandés
    films_similaires = dfgenz.iloc[indices_sans_cible[:k]]  # Limiter à k recommandations
    
    # Retourner les films recommandés avec le titre, la note et le synopsis
    recommended_movies = films_similaires[['title', 'note', 'synopsis', 'runtimeMinutes', 'date_sortie', 'affiche']].to_dict(orient='records')
    return {"recommended_movies": recommended_movies}
