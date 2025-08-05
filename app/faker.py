from faker import Faker

fake = Faker()


def generate_fake_user():
    return {
        "nom": fake.last_name(),
        "prenom": fake.first_name(),
        "adresse": fake.address(),
        "tel": fake.phone_number(),
        "email": fake.email()
    }

# Exemple d'utilisation
fake_user = generate_fake_user()
print(fake_user)