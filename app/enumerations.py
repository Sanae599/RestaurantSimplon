from enum import Enum

class Role(str, Enum):
    CLIENT = "client"
    EMPLOYEE = "employée"
    ADMIN = "admin"