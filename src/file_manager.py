class FileManager:
    def __init__(self):
        self.account_file = "files/account.txt"
        self.inventory_file = "files/inventory.txt"
        # self.log_all_file = "files/log_all.txt"
        self.purchases_file = "files/purchases.txt"

    def load_users(self):
        users = {}
        try:
            with open(self.account_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) != 3:
                        continue
                    username, password, is_admin = parts
                    if is_admin not in ["0", "1"]:
                        continue
                    users[username] = {"password": password, "is_admin": is_admin == "1"}
        except FileNotFoundError:
            print("Account file not found")
            open(self.account_file,"w").close()
        except Exception as e:
            print(f"Error loading users: {e}")
        return users

    def save_users(self, users):
        try:
            with open(self.account_file, "w") as f:
                for username, details in users.items():
                    is_admin = "1" if details["is_admin"] else "0"
                    f.write(f"{username},{details['password']},{is_admin}\n")
        except Exception as e:
            print(f"Error saving users: {e}")

    def load_inventory(self):
        inventory = {}
        try:
            with open(self.inventory_file, "r") as file:
                for line in file:
                    parts = line.strip().split(",")
                    if len(parts) == 3:
                        # Old format: item,quantity,price
                        item, quantity, price = parts
                        reorder_point = 5000  # Default reorder point
                    elif len(parts) == 4:
                        # New format: item,quantity,price,reorder_point
                        item, quantity, price, reorder_point = parts
                    else:
                        continue  # Skip malformed lines

                    inventory[item] = {
                        "quantity": int(quantity),
                        "price": float(price),
                        "reorder_point": int(reorder_point)
                    }
        except FileNotFoundError:
            open(self.inventory_file, "w").close()
        except Exception as e:
            print(f"Error loading inventory: {e}")
        return inventory


    def save_inventory(self, inventory):
        try:
            with open(self.inventory_file, "w") as file:
                for item, details in inventory.items():
                    # reorder_point = details.get("reorder_point", 5)
                    file.write(f"{item},{details['quantity']},{details['price']},{details['reorder_point']}\n")
        except Exception as e:
            print(f"Error saving inventory: {e}")


    def load_purchases(self):
        purchases = []
        try:
            with open(self.purchases_file, "r") as file:
                for line in file:
                    user, item, quantity, price, cost, time, date, month = line.strip().split(",")
                    purchases.append({
                        "user": user,
                        "item_name": item,
                        "quantity": int(quantity),
                        "price_per_item": float(price),
                        "cost": float(cost),
                        "time": time,
                        "date": date,
                        "month": month
                    })
        except FileNotFoundError:
            open(self.purchases_file, "w").close()
        except Exception as e:
            print(f"Error loading purchases: {e}")
        return purchases

    def save_purchases(self, purchases):
        try:
            with open(self.purchases_file, "w") as file:
                for purchase in purchases:
                    file.write(
                        f"{purchase['user']},{purchase['item_name']},{purchase['quantity']},"
                        f"{purchase['price_per_item']},{purchase['cost']},{purchase['time']},"
                        f"{purchase['date']},{purchase['month']}\n"
                    )
        except Exception as e:
            print(f"Error saving purchases: {e}")

    def save_history(self, content, filename):
        try:
            with open(filename, "a") as f:
                f.write("==================== Start ====================\n")
                f.write(content)
                f.write("==================== End ====================\n\n")
        except Exception as e:
            print(f"Error saving history: {e}")



                    