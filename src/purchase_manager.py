class PurchaseManager:
    def __init__(self,purchases, current_date):
        self.purchases = purchases
        self.current_date = current_date.strftime("%d %B %Y")
        self.current_day = current_date.strftime("%d")
        self.current_month = current_date.strftime("%m")

    def buy_item(self, user, item_name, quantity, inventory_manager):
        item_name = item_name.lower().strip()
        item = inventory_manager.get_item(item_name)
        if not item:
            message = f"Item {item_name.title()} not in inventory"
            return False,message
        if quantity <= 0:
            message = "Quantity must be positive"
            return False,message
        if item["quantity"] < quantity:
            message = "Not enough quantity available"
            return False,message
        price_per_item = item["price"]
        cost = quantity * price_per_item
        item["quantity"] -= quantity
        self.purchases.append({
            "user": user,
            "item_name": item_name,
            "quantity": quantity,
            "price_per_item": price_per_item,
            "cost": cost,
            "time": self.current_date,
            "date": self.current_day,
            "month": self.current_month
        })
        message = f"Quantity {quantity} of {item_name.title()} is purchased for {cost:.2f} $"
        return True,message
    
    def view_purchases(self, user, user_manager, date=None, month=None):
        output = "\nPurchase Detail:\n"
        total = 0
        if date is None or month is None:
            output += f"Purchase history for {user} on {self.current_date}\n"
            filter_date, filter_month = self.current_day, self.current_month
        else:
            output += f"Purchase history for {user} on {date}/{month}\n"
            filter_date, filter_month = date, month

        output += "==================================================================================\n"
        if user_manager.is_admin():
            output += "User      : Item Name : Quantity : Price   : Total Cost\n"
            output += "-----------------------------------------------------------------------------\n"
        else:
            output += "Item Name : Quantity : Price   : Total Cost\n"
            output += "-----------------------------------------------------------------------------\n"
        
        found = False
        for purchase in self.purchases:
            if user_manager.is_admin() or purchase["user"] == user:
                if purchase["date"] == filter_date and purchase["month"] == filter_month:
                    if user_manager.is_admin():
                        output += (
                            f"{purchase['user']:<10}:"
                            f"{purchase['item_name']:<10}:"
                            f" {purchase['quantity']:<9}:"
                            f" {purchase['price_per_item']:<7.2f}$:"
                            f" {purchase['cost']:<7.2f}$\n"
                        )
                    else:
                        output += (
                            f"{purchase['item_name']:<10}:"
                            f" {purchase['quantity']:<9}:"
                            f" {purchase['price_per_item']:<7.2f}$:"
                            f" {purchase['cost']:<7.2f}$\n"
                        )
                    total += purchase["cost"]
                    found = True
        
        if not found:
            output = "Nothing"
        else:
            output += "==================================================================================\n"
            output += f"Total spent: {total:.2f}$\n"
            output += "==================================================================================\n"
            
        return output
    
    def download_logs(self, user, user_manager, filename, date=None, month=None):
        content = self.view_purchases(user, user_manager, date, month)
        return content, filename