"""
Définitions des énumérations utilisées dans l'application.

Ces classes Enum représentent des valeurs fixes pour :
- Role : les rôles des utilisateurs (client, employé, admin).
- Status : le statut d'une commande (en préparation, prête, servie).
- StatusDelivery : le statut d'une livraison (en cours, délivrée).
- Category : les catégories de produits (entrée, plat principal, dessert, boisson, snack, menu enfant).

Les énumérations héritent de `str` pour faciliter leur utilisation avec SQLModel et Pydantic.
"""
from enum import Enum

class Role(str, Enum):
    CLIENT = "client"
    EMPLOYEE = "employée"
    ADMIN = "admin"


class Status(str, Enum):
    EN_PREPARATION = "En préparation"
    PRETE = "Prete"
    SERVIE = "Servie"


class StatusDelivery(str, Enum):
    EN_COURS = "En cours"
    DELIVREE = "Délivrée"


class Category(str, Enum):
    ENTREE = "Entrée"
    PLAT_PRINCIPAL = "Plat principal"
    DESSERT = "Dessert"
    BOISSON = "Boisson"
    SNACK = "Snack"
    MENU_ENFANT = "Menu enfant"
