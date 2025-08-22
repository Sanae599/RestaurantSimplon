# RestaurantSimplon – API de gestion de commandes pour restaurant

##  Contexte

**RestaurantSimplon** est une API REST développée avec **FastAPI**, visant à digitaliser la gestion des commandes dans un restaurant traditionnellement basé sur le papier. Cette solution apporte un gain en efficacité, fiabilité et traçabilité des opérations quotidiennes.

Projet réalisé dans le cadre d’un sprint de **3 semaines** (du 4 au 22 août 2025).
---

##  Fonctionnalités principales

###  Authentification & Autorisation
- Création de comptes : `Admin`, `Employé`, `Client`
- Flux OAuth2 Password avec JWT (access & refresh tokens)
- Sécurité : hashage Bcrypt, gestion d’expiration, rotation de tokens
- Rôles et permissions gérés via scopes FastAPI

###  Gestion du Menu
- CRUD complet sur les articles (nom, prix, catégorie, description, stock)

### Gestion des Clients
- CRUD clients : nom, prénom, adresse, téléphone, email
- Un client peut commander uniquement pour lui-même

###  Gestion des Commandes
- Création d'une commande (client + articles + quantités)
- Calcul automatique du total
- Consultation des commandes par **client** ou **date**
- Statut : En préparation / Prête / Servie

###  Validation des données
- Modèles Pydantic v2
- Validateurs personnalisés
- Contraintes : prix > 0, quantité ≥ 1, commande ≥ 1 article, email valide…

---

##  Stack Technique

| Domaine            | Technologies                         |
|--------------------|--------------------------------------|
| Langage            | Python                               |
| Framework API      | FastAPI                              |
| ORM                | SQLModel / SQLAlchemy + Alembic      |
| Authentification   | JWT, Bcrypt, OAuth2                  |
| Base de données    | PostgreSQL                           |
| Conteneurisation   | Docker, Docker Compose               |
| CI/CD              | GitHub Actions, Pytest, Coverage     |
| Documentation API  | Swagger / OpenAPI (auto-générée)     |

---

## ⚙ Installation & Exécution

###  Prérequis
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

API accessible sur : http://localhost:8000

Documentation Swagger : http://localhost:8000/docs

###  Tests & Qualité

* Tests unitaires avec pytest

* Couverture minimale de 80%

* Vérification via GitHub Actions sur chaque pull request

* Linting : ruff, black

### Pipeline CI/CD

Pipeline automatisé avec GitHub Actions :

    - Lint & test

   -  Build es images Docker

    - Push vers un registre (DockerHub, GHCR)

    -Déploiement automatique (env. staging/production)

###  Documentation

    Swagger UI : /docs
