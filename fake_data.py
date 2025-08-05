from faker import Faker
from app.models import User, Product, Order, OrderItem, Delivery
import random
from datetime import datetime

# créee une instance de Faker
fake = Faker()
Faker.seed(0)  # pour avoir les mêmes données à chaque exécution
random.seed(0)

def create_fake_users(n):
    users = []
    for _ in range(n):
        user = User(
            first_name=fake.first_name(),  
            last_name=fake.last_name(), 
            email=fake.unique.email(),  
            role=random.choice(["admin", "employee", "client"]),  
            password_hashed="motdepasse",  
            address_user=fake.unique.email(), 
            phone=fake.unique.phone_number(),
            created_at = fake.date_time() 
            
        )
        users.append(user)
    return users

def create_fake_products(n):
    products = []
    for _ in range(n):
        product = Product(
            name=fake.word().capitalize(),  
            unit_price=round(random.uniform(10, 100), 2),  # prix entre 10€ et 100€ avec deux chiffres apres la virgule
            category=random.choice(["Entrée", "Plat principal", "Dessert", "Boisson", "Snack", "Menu enfant"]),  
            description=fake.text(max_nb_chars=50),  # petite description
            stock=random.randint(10, 100), # stock entre 10 et 100 unités
            created_at =fake.date_time()
        )
        products.append(product)
    return products

def create_fake_deliveries(n):
    deliveries = []
    for _ in range(n):
        delivery = Delivery(
            address_delivery=fake.address(),  
            status=random.choice(["En cours", "Délivrée"]),
            created_at = fake.date_time()
        )
        deliveries.append(delivery)
    return deliveries

def create_fake_orders(users, deliveries, n):
    orders = []
    for _ in range(n):
        user = random.choice(users)  
        delivery = random.choice(deliveries)  
        order = Order(
            user_id=user.id,  
            total_amount=0.0,  
            status=random.choice(["En préparation", "Prete", "Servie"]),
            created_at = fake.date_time(),  
            delivery_id=delivery.id  
        )
        orders.append(order)
    return orders

def create_fake_order_items(orders, products):
    order_items = []
    for order in orders:
        selected_products = random.sample(products, k=random.randint(1, 3))

        for product in selected_products:
            quantity = random.randint(1, 5)  
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity
            )

            order_items.append(order_item)
            order.total_amount += quantity * product.unit_price

    return order_items


