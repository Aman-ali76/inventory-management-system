import pandas as pd
class InventoryManager:
    def __init__(self,inventory):
        self.inventory = inventory

    def view_inventory(self):
        output  = "\nInventory:\n====================================\n"
        output += " Item Name  : Quantity  : Price  \n------------------------------------\n"
        for item, details in self.inventory.items():
            output += f" {item.title():<11}: {details['quantity']:<10}: {details['price']:.2f} $\n"
        output += "====================================\n"
        return output
    
    def add_item(self, item_name, quantity, price, user_manager):
        if not user_manager.is_admin():
            message = "Only admins can add items"
            return False,message
        if quantity <= 0 :
            message = "Quantity can not be negative or Zero"
            return False,message
        if price <= 0:
            message = "Price can not be nagative or Zero"
            return False,message
        item_name = item_name.lower().strip()
        if item_name in self.inventory:
            message = f"Item '{item_name.title()}' already exist in inventory"
            return False,message
        self.inventory[item_name] = {"quantity": quantity, "price": price}
        message = f"Item '{item_name.title()}' is successfully added to inventory"
        return True,message
    
    def update_inventory(self, item_name,user_manager,reorder=None, quantity=None,price=None ):
        if not user_manager.is_admin():
            message = "Only admins can update items"
            return False,message
        item_name = item_name.lower().strip()
        if item_name not in self.inventory:
            message = f"Item '{item_name.title()}' not exist in inventory"
            return False,message
        if quantity == None and price == None:
            message = "Quantity and price is not given"
            return False,message
        if quantity == None:
            quantity = self.inventory[item_name]["quantity"]
        elif quantity <= 0:
            message = "Quantity can not be nagative or Zero"
            return False,message
        if price == None:
            price = self.inventory[item_name]["price"]
        elif price <= 0:
            message = "Price can not be nagative or Zero"
            return False,message
        if reorder == None:
            self.inventory[item_name]["reorder_point"] = reorder
        elif reorder < 0:
            message = "Reorder point can not be nagative"
            return False,message
        
        
        str_quanity = f"new Quantity '{quantity}'" if quantity != self.inventory[item_name]["quantity"] else f"old Quantity '{quantity}'"
        str_price = f"new Price '{price:.2f} $'" if price != self.inventory[item_name]["price"] else f"old Price '{price:.2f} $'"
        self.inventory[item_name] = {"quantity": quantity, "price": price,"reorder_point": reorder}
        message = f"Item '{item_name.title()}' is successfully updated with {str_quanity} and {str_price}"
        return True,message
        
    def remove_item(self, item_name, user_manager):
        if not user_manager.is_admin():
            message = "Only admins can remove items"
            return False,message
        item_name = item_name.lower().strip()
        if item_name not in self.inventory:
            message = f"Item '{item_name.title()}' not exist in inventory"
            return False,message
        del self.inventory[item_name]
        message = f"Item '{item_name.title()}' is successfully removed from inventory"
        return True,message
    
    def get_item(self, item_name):
        return self.inventory.get(item_name.lower().strip(),True)

    def get_stock_vs_reorder_data(self):
        """
        Returns a list of dicts with item name, units left, and reorder point
        """
        return [
            {
                "item_name": item.title(),
                "units_left": details["quantity"],
                "reorder_point": details.get("reorder_point", 5)  # default reorder point if not defined
            }
            for item, details in self.inventory.items()
        ]