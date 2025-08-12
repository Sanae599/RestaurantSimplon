from faker import Faker
from app.models import User, Product, Order, OrderItem, Delivery
import random
from datetime import datetime, timedelta, timezone  
from app.enumerations import *
from app.security import hash_password

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
        user_data = User(
            first_name=fake.first_name(),  
            last_name=fake.last_name(), 
            email=fake.unique.email(),  
            role=random.choice(list(Role)).value,  
            password_hashed = hash_password(fake.password()),
            address_user=fake.unique.address(), 
            phone=generate_fr_phone(),
            created_at = fake.date_time()
        )
        users.append(user_data)
    return users

def create_fake_products(n):
    products = []
    for _ in range(n):
        product_data = Product(
            name=fake.word().capitalize(),  
            unit_price=round(random.uniform(10, 100),2),  # prix entre 10€ et 100€ avec deux chiffres apres la virgule
            category=random.choice(list(Category)).value,  
            description=remove_dot(fake.text(max_nb_chars=50)),
            stock=random.randint(10, 100), # stock entre 10 et 100 unités
            created_at = fake.date_time()
        )
        products.append(product_data)
    return products

def create_fake_deliveries(orders,n):
    deliveries = []
    selected_order = random.sample(orders, k=min(n, len(orders)))
    for order in selected_order:
        delivery_data = Delivery(
            order_id=order.id,
            address_delivery=fake.address(),  
            status=random.choice(list(StatusDelivery)).value,
            created_at = fake.date_time()

        )
        deliveries.append(delivery_data)
    return deliveries

def create_fake_orders(users, n):
    orders = []
    for _ in range(n):
        user = random.choice(users)  
        order_data = Order(
            user_id=user.id,  
            total_amount=0,  
            status=random.choice(list(Status)).value,
            created_at = fake.date_time()
        )
        orders.append(order_data)
    return orders

def create_fake_order_items(orders, products):
    order_items = []
    for order in orders:
        selected_products = random.sample(products, k=random.randint(1, 3))
        total_amount = 0

        for product in selected_products:
            quantity = random.randint(1, 5)  
            order_item_data = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                created_at = fake.date_time()
            )
            
            order_items.append(order_item_data)
            total_amount += quantity * product.unit_price
        order.total_amount = round(total_amount,2)
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
