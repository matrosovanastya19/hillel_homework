import os
class Product:
    def __init__(self, name:str, category:str, price:float, quantity:int):
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity
    def change_price(self, new_price):
        self.price = new_price
        return new_price
    def change_quantity(self, new_quantity):
        self.quantity = new_quantity
        return new_quantity

    def __repr__(self):
        return f"{self.name} ({self.category}) - {self.price} грн, {self.quantity} шт."

class Order:
    def __init__(self):
        self.list_of_products = []
        self.total_price = 0.0
    def add_product(self, product:Product, amount: int=1):
        if product.quantity >= amount:
            self.list_of_products.append((product, amount))
            product.change_quantity(product.quantity - amount)
            self.total_price += product.price * amount
        else:
            print("Not enough quantity")

    def calculate_total(self):
        self.total_price = sum(item[0].price * item[1] for item in self.list_of_products)
        return self.total_price

    def __repr__(self):
        items = ", ".join([f"{p[0].name} (x{p[1]})" for p in self.list_of_products])
        return f"Замовлення: [{items}] | Сума: {self.total_price:.2f} грн"
class Customer:
    def __init__(self, username:str, email:str):
        self.username = username
        self.email = email
        self.list_of_orders = []

    def add_order(self, order:Order):
        self.list_of_orders.append(order)
        return order

    def __repr__(self):
        return f"Клієнт: {self.username} ({self.email})"

def initialize_store_from_file(filename:str):
    products_list = []
    customers_list = []
    current_section=None
    if not os.path.exists(filename):
        print(f"Файл {filename} не знайдено!")
        return products_list, customers_list

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            if line=="PRODUCTS":
                current_section = "products"
                continue
            elif line=="CUSTOMERS":
                current_section = "customers"
                continue
            parts = [p.strip() for p in line.split(",")]
            if current_section=="products" and len(parts)==4:
                prod=Product(parts[0], parts[1], float(parts[2]), int(parts[3]))
                products_list.append(prod)
            elif current_section=="customers" and len(parts)==2:
                cust = Customer(parts[0], parts[1])
                customers_list.append(cust)
    return products_list, customers_list
if __name__ == "__main__":
    print("Завантаження магазину")
    store_products, store_customers = initialize_store_from_file("store.txt")
    print("Товари на складі:")
    for p in store_products:
        print("  -", p)

    print("\nКлієнти:")
    for c in store_customers:
        print("  -", c)

    if store_products and store_customers:
        client1=store_customers[0]
        new_order = Order()

        new_order.add_product(store_products[0],3)
        new_order.add_product(store_products[2],4)
        client1.add_order(new_order)
        print(f"{client1.username} Ваше замовлення прийняте")
        print(new_order)
        print("\nЗалишки на складі після замовлення:")
        for p in store_products:
            print("  -", p)
