import random
from datetime import datetime, timedelta

from app.database import SessionLocal

from .models import Discount, Product


def generate_products(count: int = 51):
    brands = ["Nike", "Adidas", "Puma", "Reebok", "New Balance"]
    colors = ["Red", "Blue", "Green", "Black", "White"]
    sizes = ["S", "M", "L", "XL"]
    name = ["Sneaker", "Boot", "Sandal", "Loafer", "Heel", "Tshirt", "Jacket", "Jeans"]

    products_list = []

    for i in range(1, count + 1):
        product = {
            "name": random.choice(name),
            "brand": random.choice(brands),
            "color": random.choice(colors),
            "size": random.choice(sizes),
            "price": str(random.randint(50, 250)),
            "quantity": random.randint(1, 100),
        }
        products_list.append(product)
    return products_list


def generate_discounts(product_list: list = 20, count: int = 10):
    discounts_list = []

    today = datetime.now().date()

    # Generate start and end dates
    start_date = today - timedelta(days=random.randint(1, 30))
    end_date = today + timedelta(days=random.randint(1, 60))

    for i in range(1, count + 1):
        discount = {
            "discount_percent": round(random.uniform(5.0, 50.0), 2),
            "active": random.choice([True, False]),
            "start_date": start_date,
            "end_date": end_date,
            "products": random.choice(product_list),
        }
        discounts_list.append(discount)
    return discounts_list


def create_data_in_bulk():
    """Inserts all data into the database in bulk."""
    db = SessionLocal()
    try:
        # 1. Prepare product data
        products_data = generate_products(50)
        product_objects = [Product(**p) for p in products_data]

        # 2. Add all products to the session
        db.add_all(product_objects)
        db.commit()

        # 3. Get the newly created product IDs to link with discounts
        # The IDs are now populated because we committed the changes
        product_ids = [p.id for p in product_objects]

        # 4. Prepare discount data
        discounts_data = generate_discounts(product_ids, 20)
        discount_objects = [Discount(**d) for d in discounts_data]

        # 5. Add all discounts to the session
        db.add_all(discount_objects)
        db.commit()

        print("Successfully created 50 products and 20 discounts!")

    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()
