import pandas as pd

class AdminManager:
    def __init__(self, users ,purchases):
        self.users = users
        self.purchases = purchases

    def refresh_users(self, filem_manager):
        self.users=  filem_manager.load_users()

    def get_user(self):
        usr_list = []
        for name,details in self.users.items():
            if details["is_admin"]:
                user_str = f"⭐ {name} (ADMIN)"
            else:
                user_str = f"👤 {name} (Customer)"
            usr_list.append(user_str)
        return usr_list

    def check_users(self):
        return list(self.users.keys())
    
    def get_user_purchases(self, username):
        user_purchases = [p for p in self.purchases if p["user"] == username]
        if not user_purchases:
            return None
        df = pd.DataFrame(user_purchases)
        grouped_df = df.groupby("item_name")["cost"].sum().reset_index()
        grouped_df.columns = ["Item", "Total Spent"]
        return grouped_df
    
    def visualize_all(self, mode):
        if not self.purchases:
            return None
            
        df = pd.DataFrame(self.purchases)
        
        if mode == "by_user":
            # Group by user and sum costs
            grouped = df.groupby("user")["cost"].sum().reset_index()
            grouped.columns = ["User", "Total Spent"]
            return grouped
            
        elif mode == "by_date":
            # Group by date and sum costs
            grouped = df.groupby("date")["cost"].sum().reset_index()
            grouped.columns = ["Date", "Total Sales"]
            return grouped
            
        elif mode == "by_item_name":
            # Group by item and sum costs
            grouped = df.groupby("item_name")["cost"].sum().reset_index()
            grouped.columns = ["Item", "Total Spent"]
            return grouped
            
        elif mode == "by_quantity":
            # Group by item and sum quantities
            grouped = df.groupby("item_name")["quantity"].sum().reset_index()
            grouped.columns = ["Item", "Total Quantity"]
            return grouped
            
        else:
            return None

    def get_user_purchases(self, username):
        """Get all purchases for a specific user"""
        user_purchases = [p for p in self.purchases if p["user"] == username]
        if not user_purchases:
            return None
            
        # Create a DataFrame with item, quantity, and total cost
        df = pd.DataFrame(user_purchases)
        return df[["item_name", "quantity", "cost"]].rename(columns={
            "item_name": "Item",
            "quantity": "Quantity",
            "cost": "Total Cost"
        })
    
    def view_all_users(self):
        """Returns a formatted string of all usernames."""
        output = "\nAll Users:\n================\n"
        for username in self.users:
            output += f"{username}\n"
        output += "================\n"
        return output
    
    def get_sales_summary(self, mode="by_item_name"):
        data = self.purchases  # list of dicts
        df = pd.DataFrame(data)

        if mode == "by_item_name":
            return df.groupby("item_name")["cost"].sum().reset_index(name="Total Spent")
        elif mode == "by_date":
            return df.groupby(["date", "month"])["cost"].sum().reset_index(name="Total Sales")
        elif mode == "by_user":
            return df.groupby("user")["cost"].sum().reset_index(name="Total Spent")
        elif mode == "by_category":
            return df.groupby("category")["cost"].sum().reset_index(name="Total Spent")  # only if you have category
        return None
