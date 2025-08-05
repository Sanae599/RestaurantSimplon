from db import init_db

def startup_tasks():
    init_db()


if __name__ == "__main__":
    startup_tasks()