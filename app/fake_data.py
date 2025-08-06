from faker import Faker
from schemas.user import UserCreate
from schemas.product import ProductCreate
from schemas.delivery import DeliveryCreate
from schemas.order import OrderCreate
from schemas.order_item import OrderItemCreate
from models import User, Product, Order, OrderItem, Delivery
import random
from datetime import datetime, timedelta, timezone  
from enumerations import *
from security import hash_password

# créee une instance de Faker
fake = Faker()
fake.unique.clear()
Faker.seed(0)  # pour avoir les mêmes données à chaque exécution
random.seed(0)


def generate_fr_phone():
    return "0" + "".join(str(random.randint(0, 9)) for _ in range(9))

def remove_dot(text):
    return text.rstrip(".").replace(".", "")

def create_fake_users(n):
    # recup heure actuelle
    users = []
    for _ in range(n):
        # entre 30 et 10 jours dans le passé
        # user_date: instance du schéma
        user_data = UserCreate(
            first_name=fake.first_name(),  
            last_name=fake.last_name(), 
            email=fake.unique.email(),  
            role=random.choice(list(Role)).value,  
            password_hashed=hash_password("Motdepasse111111111!"),  
            address_user=fake.unique.address(), 
            phone=generate_fr_phone(),
            created_at = fake.date_time()
        )
        # convertit modèle pydantic à modèle orm
        user = User(**user_data.model_dump())  # transformer en modèle SQLModel
        users.append(user)
    return users

def create_fake_products(n):
    products = []
    for _ in range(n):
        product_data = ProductCreate(
            name=fake.word().capitalize(),  
            unit_price=random.uniform(10, 100),  # prix entre 10€ et 100€ avec deux chiffres apres la virgule
            category=random.choice(list(Category)).value,  
            description=remove_dot(fake.text(max_nb_chars=50)),
            stock=random.randint(10, 100), # stock entre 10 et 100 unités
            created_at = fake.date_time()
        )
        product = Product(**product_data.model_dump())  # transforme en modèle SQLModel
        products.append(product)
    return products

def create_fake_deliveries(orders,n):
    deliveries = []
    selected_order = random.sample(orders, k=min(n, len(orders)))
    for order in selected_order:
        delivery_data = DeliveryCreate(
            order_id=order.id,
            address_delivery=fake.address(),  
            status=random.choice(list(StatusDelivery)).value,
            created_at = fake.date_time()

        )
        delivery = Delivery(**delivery_data.model_dump())  # transformer en modèle SQLModel
        deliveries.append(delivery)
    return deliveries

def create_fake_orders(users, n):
    orders = []
    for _ in range(n):
        user = random.choice(users)  
        # décalage 1 à 30j avec creation user
        days_offset = random.randint(1, 30)
        order_data = OrderCreate(
            user_id=user.id,  
            total_amount=0,  
            status=random.choice(list(Status)).value,
            created_at = fake.date_time()
        )
        order = Order(**order_data.model_dump())  # transformer en modèle SQLModel
        orders.append(order)
    return orders

def create_fake_order_items(orders, products):
    order_items = []
    for order in orders:
        selected_products = random.sample(products, k=random.randint(1, 3))
        total_amount = 0

        for product in selected_products:
            quantity = random.randint(1, 5)  
            order_item_data = OrderItemCreate(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                created_at = fake.date_time()
            )
            
            order_item = OrderItem(**order_item_data.model_dump())
            #print(order_item)
            order_items.append(order_item)
            total_amount += quantity * product.unit_price
        order.total_amount = round(total_amount, 2)
    return order_items

def reset_db(session):
    session.query(OrderItem).delete()
    session.query(Order).delete()
    session.query(Delivery).delete()
    session.query(Product).delete()
    session.query(User).delete()
    session.commit()

def add_fake_data(session):
    # obligé de commit souvent pour pouvoir recup les id 
    users = create_fake_users(5)
    products = create_fake_products(10)

    session.add_all(users + products)
    session.commit()  # Pour générer les IDs

    orders = create_fake_orders(users, 7)
    session.add_all(orders)
    session.commit()

    order_items = create_fake_order_items(orders, products)
    session.add_all(order_items)
    session.commit()
    session.add_all(orders)
    session.commit()

    deliveries = create_fake_deliveries(orders, 3)
    session.add_all(deliveries)
    session.commit()
