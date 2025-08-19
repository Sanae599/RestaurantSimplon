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
