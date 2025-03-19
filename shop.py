import csv
import logging
import os

log_file = "shop_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def to_dict(self):
        return {"ID": self.product_id, "Name": self.name, "Price": self.price, "Stock": self.stock}


class Inventory:
    FILE_NAME = "inventory.csv"

    def __init__(self):
        self.products = self.load_inventory()

    def load_inventory(self):
        products = {}
        if not os.path.exists(self.FILE_NAME):
            logging.warning("Inventory file not found. Starting with an empty inventory.")
            return products

        try:
            with open(self.FILE_NAME, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    products[row["ID"]] = Product(row["ID"], row["Name"], float(row["Price"]), int(row["Stock"]))
        except Exception as e:
            logging.error(f"Error loading inventory: {e}")
        return products

    def save_inventory(self):
        try:
            with open(self.FILE_NAME, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["ID", "Name", "Price", "Stock"])
                writer.writeheader()
                for product in self.products.values():
                    writer.writerow(product.to_dict())
            logging.info("Inventory saved successfully.")
        except Exception as e:
            logging.error(f"Error saving inventory: {e}")

    def add_product(self, product):
        if product.product_id in self.products:
            logging.warning(f"Product {product.product_id} already exists.")
            print("Product already exists!")
            return

        self.products[product.product_id] = product
        self.save_inventory()
        logging.info(f"Product added: {product.name} (ID: {product.product_id})")
        print(f"Product '{product.name}' added successfully!")

    def view_inventory(self):
        if not self.products:
            print("Inventory is empty!")
            logging.info("User tried to view an empty inventory.")
        else:
            print("\n--- Inventory ---")
            for product in self.products.values():
                print(f"ID: {product.product_id} | {product.name} | Price: ${product.price} | Stock: {product.stock}")

    def update_stock(self, product_id, quantity):
        if product_id in self.products:
            self.products[product_id].stock -= quantity
            self.save_inventory()
            logging.info(f"Stock updated: {product_id} | Remaining Stock: {self.products[product_id].stock}")


class Sale:
    def __init__(self, sale_id, items):
        self.sale_id = sale_id
        self.items = items  # Dictionary {product_id: quantity}

    def to_dict(self):
        return {"SaleID": self.sale_id, "Items": str(self.items)}


class SalesManager:
    FILE_NAME = "sales.csv"

    def __init__(self, inventory):
        self.inventory = inventory
        self.sales = []

    def record_sale(self, sale):
        self.sales.append(sale)
        try:
            with open(self.FILE_NAME, "a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["SaleID", "Items"])
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow(sale.to_dict())

            for product_id, quantity in sale.items.items():
                self.inventory.update_stock(product_id, quantity)

            logging.info(f"Sale recorded: Sale ID {sale.sale_id}, Items: {sale.items}")
            print(f"Sale {sale.sale_id} recorded successfully.")
        except Exception as e:
            logging.error(f"Error recording sale {sale.sale_id}: {e}")

    def view_sales(self):
        if not os.path.exists(self.FILE_NAME):
            print("No sales recorded yet.")
            logging.info("User tried to view an empty sales record.")
            return

        try:
            with open(self.FILE_NAME, "r") as file:
                reader = csv.DictReader(file)
                print("\n--- Sales Report ---")
                for row in reader:
                    print(f"Sale ID: {row['SaleID']} | Items: {row['Items']}")
        except Exception as e:
            logging.error(f"Error viewing sales: {e}")


class ShopSystem:
    def __init__(self):
        self.inventory = Inventory()
        self.sales_manager = SalesManager(self.inventory)

    def menu(self):
        while True:
            print("\n--- Small Shop Management System ---")
            print("1. View Inventory")
            print("2. Add Product to Inventory")
            print("3. Process a Sale")
            print("4. View Sales Report")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.inventory.view_inventory()
            elif choice == "2":
                self.add_product_to_inventory()
            elif choice == "3":
                self.process_sale()
            elif choice == "4":
                self.sales_manager.view_sales()
            elif choice == "5":
                print("Exiting... Thank you!")
                logging.info("Shop System closed.")
                break
            else:
                print("Invalid choice, please try again.")

    def add_product_to_inventory(self):
        product_id = input("Enter Product ID: ")
        name = input("Enter Product Name: ")
        price = float(input("Enter Product Price: "))
        stock = int(input("Enter Stock Quantity: "))
        product = Product(product_id, name, price, stock)
        self.inventory.add_product(product)

    def process_sale(self):
        sale_id = input("Enter Sale ID: ")
        items = {}

        while True:
            product_id = input("Enter Product ID to sell (or 'done' to finish): ")
            if product_id.lower() == "done":
                break
            if product_id not in self.inventory.products:
                print("Invalid Product ID. Try again.")
                logging.warning(f"User entered invalid product ID: {product_id}")
                continue

            quantity = int(input(f"Enter quantity for {self.inventory.products[product_id].name}: "))
            if quantity > self.inventory.products[product_id].stock:
                print("Not enough stock available!")
                logging.warning(f"User tried to sell more than available stock: {product_id}")
                continue

            items[product_id] = quantity

        if items:
            sale = Sale(sale_id, items)
            self.sales_manager.record_sale(sale)
        else:
            print("No items selected for sale.")


if __name__ == "__main__":
    ShopSystem().menu()

