from feast import Entity

# Définition de l'entité principale "user"
user = Entity(
    name="user",                 # nom logique de l’entité
    join_keys=["user_id"],       # colonne(s) utilisée(s) pour relier les features
    description="Utilisateur StreamFlow, identifié par user_id"  # courte description
)

# L'entité "user" permet à Feast de savoir sur quelle clé les features seront jointes.
