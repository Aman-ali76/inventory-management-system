import streamlit as st
import datetime as dt
import pandas as pd
from src.user_manager import UserManager
from src.inventory_manager import InventoryManager
from src.purchase_manager import PurchaseManager
from src.file_manager import FileManager
from src.admin_manager import AdminManager

class AppManager:
    @st.cache_resource
    def init_managers():
        file_manager = FileManager()
        user_manager = UserManager(file_manager.load_users())
        inventory_manager = InventoryManager(file_manager.load_inventory())
        purchase_manager = PurchaseManager(file_manager.load_purchases(), dt.datetime.now())
        admin_manager = AdminManager(user_manager.users, purchase_manager.purchases)
        return file_manager, user_manager, inventory_manager, purchase_manager, admin_manager

class Page:
    def __init__(self, managers):
        self.file_manager, self.user_manager, self.inventory_manager, self.purchase_manager, self.admin_manager = managers

class AuthPage(Page):
    def login_page(self):
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username").lower().strip()
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            condition,message = self.user_manager.login(username, password)
            if submit:
                if  condition:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    self.user_manager.current_user = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    def register_page(self):
        with st.form("register_form"):
            st.subheader("Register")
            username = st.text_input("Username").lower().strip()
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Register")
            condition,message = self.user_manager.register(username, password)
            if submit:
                if condition:
                    self.file_manager.save_users(self.user_manager.users)
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    self.user_manager.current_user = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    def forgot_password_page(self):
        with st.form("forgot_password_form"):
            st.subheader("Forgot Password")
            username = st.text_input("Username").lower().strip()
            position = st.selectbox("Position", ["first", "last"])
            char = st.text_input("Character")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Reset Password")
            if submit:
                condition,message = self.user_manager.forgot_password(username, char, position, new_password, confirm_password)
                if condition:
                    self.file_manager.save_users(self.user_manager.users)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

class InventoryPage(Page):
    def view_inventory_page(self):
        st.subheader("Inventory")
        inventory_data = [
            {"Item Name": item.title(), "Quantity": details["quantity"], "Price": details["price"]}
            for item, details in self.inventory_manager.inventory.items()
        ]
        if inventory_data:
            st.dataframe(pd.DataFrame(inventory_data),hide_index=True)
        else:
            st.write("No items in inventory")
    
    def add_item_page(self):
        with st.form("add_item_form"):
            st.subheader("Add Item")
            item_name = st.text_input("Item Name").lower().strip()
            quantity = st.number_input("Quantity", min_value=1, step=1)
            price = st.number_input("Price", min_value=0.01, step=0.01)
            submit = st.form_submit_button("Add Item")
            condition,message = self.inventory_manager.add_item(item_name, quantity, price, self.user_manager)
            if submit:
                if condition:
                    self.file_manager.save_inventory(self.inventory_manager.inventory)
                    st.success(message)
                else:
                    st.error(message)
    
    def update_item_page(self):
        with st.form("update_item_form"):
            st.subheader("Update Item")
            item_name = st.text_input("Item Name").lower().strip()
            quantity = st.number_input("Quantity", min_value=1, step=1)
            price = st.number_input("Price", min_value=0.01, step=0.01)
            reorder = st.number_input("Reorder Point", min_value=0, step=1, value=5000)
            submit = st.form_submit_button("Update Item")
            condition,message = self.inventory_manager.update_inventory(item_name, self.user_manager,reorder, quantity, price)
            if submit:
                if condition:
                    self.file_manager.save_inventory(self.inventory_manager.inventory)
                    st.success(message)
                else:
                    st.error(message)
    
    def remove_item_page(self):
        with st.form("remove_item_form"):
            st.subheader("Remove Item")
            item_name = st.text_input("Item Name").lower().strip()
            submit = st.form_submit_button("Remove Item")
            condition,message = self.inventory_manager.remove_item(item_name, self.user_manager)
            if submit:
                if condition:
                    self.file_manager.save_inventory(self.inventory_manager.inventory)
                    st.success(message)
                else:
                    st.error(message)

class PurchasePage(Page):
    def buy_product_page(self):
        with st.form("buy_product_form"):
            st.subheader("Buy Product")
            item_name = st.text_input("Item Name").lower().strip()
            quantity = st.number_input("Quantity", min_value=1, step=1)
            submit = st.form_submit_button("Buy")
            if submit:
                condition,message = self.purchase_manager.buy_item(self.user_manager.current_user, item_name, quantity, self.inventory_manager)
                if condition:
                    self.file_manager.save_inventory(self.inventory_manager.inventory)
                    self.file_manager.save_purchases(self.purchase_manager.purchases)
                    st.success(message)
                else:
                    st.error(message)
    
    def view_purchases_page(self):
        if 'today_or' not in st.session_state:
            st.session_state.today_or = True

        st.subheader("Purchases")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Today"):
                st.session_state.today_or = True
        with col2:
            if st.button("Old History"):
                st.session_state.today_or = False

        if st.session_state.today_or:
            output = self.purchase_manager.view_purchases(
                self.user_manager.current_user, 
                self.user_manager
            )
            if output != "Nothing":
                st.text(output)
            
            # Create purchase data with user information if admin
            purchase_data = []
            for p in self.purchase_manager.purchases:
                if (self.user_manager.is_admin() or p["user"] == self.user_manager.current_user) and \
                   p["date"] == self.purchase_manager.current_day and \
                   p["month"] == self.purchase_manager.current_month:
                    
                    purchase_dict = {
                        "Item Name": p["item_name"],
                        "Quantity": p["quantity"],
                        "Price": p["price_per_item"],
                        "Total Cost": p["cost"]
                    }
                    
                    # Add user information if current user is admin
                    if self.user_manager.is_admin():
                        purchase_dict["User"] = p["user"]
                        
                    purchase_data.append(purchase_dict)
            
            if purchase_data:
                df = pd.DataFrame(purchase_data)
                
                # Reorder columns for admin view
                if self.user_manager.is_admin() and "User" in df.columns:
                    columns = ["User", "Item Name", "Quantity", "Price", "Total Cost"]
                    columns = [col for col in columns if col in df.columns]
                    df = df[columns]
                
                st.dataframe(df)
                
                # Create chart - group by item if not admin, or by user if admin
                if self.user_manager.is_admin():
                    # For admin, show spending by user
                    user_spending = df.groupby("User")["Total Cost"].sum().reset_index()
                    st.bar_chart(user_spending.set_index("User")["Total Cost"])
                else:
                    # For regular user, show spending by item
                    st.bar_chart(df.set_index("Item Name")["Total Cost"])
            else:
                st.info("No purchases found for today")

        else:
            date_input = st.date_input("Select Date")
            if date_input:
                date = date_input.strftime("%d")
                month = date_input.strftime("%m")
                
                output = self.purchase_manager.view_purchases(
                    self.user_manager.current_user, 
                    self.user_manager, 
                    date, 
                    month
                )
                if output != "Nothing":
                    st.text(output)
                
                # Create purchase data with user information if admin
                purchase_data = []
                for p in self.purchase_manager.purchases:
                    if (self.user_manager.is_admin() or p["user"] == self.user_manager.current_user) and \
                       p["date"] == date and \
                       p["month"] == month:
                        
                        purchase_dict = {
                            "Item Name": p["item_name"],
                            "Quantity": p["quantity"],
                            "Price": p["price_per_item"],
                            "Total Cost": p["cost"]
                        }
                        
                        # Add user information if current user is admin
                        if self.user_manager.is_admin():
                            purchase_dict["User"] = p["user"]
                            
                        purchase_data.append(purchase_dict)
                
                if purchase_data:
                    df = pd.DataFrame(purchase_data)
                    
                    # Reorder columns for admin view
                    if self.user_manager.is_admin() and "User" in df.columns:
                        columns = ["User", "Item Name", "Quantity", "Price", "Total Cost"]
                        columns = [col for col in columns if col in df.columns]
                        df = df[columns]
                    
                    st.dataframe(df)
                    
                    # Create chart - group by item if not admin, or by user if admin
                    if self.user_manager.is_admin():
                        # For admin, show spending by user
                        user_spending = df.groupby("User")["Total Cost"].sum().reset_index()
                        st.bar_chart(user_spending.set_index("User")["Total Cost"])
                    else:
                        # For regular user, show spending by item
                        st.bar_chart(df.set_index("Item Name")["Total Cost"])
                else:
                    st.info(f"No purchases found for {date_input.strftime('%Y-%m-%d')}")
    
    def download_logs_page(self):
        download_ready = False
        with st.form("download_logs_form"):
            st.subheader("Download Logs")
            date_input = st.text_input("Enter DATE (01-31) and MONTH (01-12) or leave blank for today")
            submit = st.form_submit_button("Submit")
            if submit:
                date, month = None, None
                if date_input.strip():
                    try:
                        date, month = date_input.strip().split()
                    except ValueError:
                        st.error("Invalid format. Use 'DD MM'")
                        submit = False
                if submit:
                    filename = f"user_{self.user_manager.current_user}_{date or 'today'}_{month or 'today'}.txt"
                    content, fname = self.purchase_manager.download_logs(
                        self.user_manager.current_user, self.user_manager, filename, date, month
                    )
                    if content != "Nothing":
                        download_ready = True 
                    else:
                        st.info("No purchases found!")
        if download_ready:
            st.markdown("Click the button below to download your logs file:")
            st.download_button(
                label="Download Logs File",
                data=content,
                file_name=fname,
                mime="text/plain"
            )

class AdminPage(Page):
    def view_all_users_page(self):
        st.subheader("All Users")
        for username in self.admin_manager.check_users():
            if st.button(username, key=username, help=f"View {username}'s data"):
                st.session_state.selected_user = username
                st.rerun()

        if st.session_state.selected_user is not None:
            st.subheader(f"Data for {st.session_state.selected_user}")
            mode = st.selectbox("Visualize by", ["by_item_name", "by_quantity"], key="vis_mode")
            
            if mode == "by_item_name":
                # Get user's purchases aggregated by item
                df = self.admin_manager.get_user_purchases(st.session_state.selected_user)
                if df is not None:
                    # Aggregate by item
                    item_agg = df.groupby("Item")["Total Cost"].sum().reset_index()
                    st.dataframe(item_agg)
                    st.bar_chart(item_agg.set_index("Item")["Total Cost"])
                else:
                    st.write("No purchases for this user")
                    
            elif mode == "by_quantity":
                # Get user's purchases aggregated by quantity
                df = self.admin_manager.get_user_purchases(st.session_state.selected_user)
                if df is not None:
                    # Aggregate by quantity
                    quantity_agg = df.groupby("Item")["Quantity"].sum().reset_index()
                    st.dataframe(quantity_agg)
                    st.bar_chart(quantity_agg.set_index("Item")["Quantity"])
                else:
                    st.write("No purchases for this user")
    
    def visualize_sales_page(self):
        with st.form("visualize_sales_form"):
            st.subheader("Visualize Sales")
            mode = st.selectbox("Visualize by", ["by_user", "by_date", "by_item_name", "by_quantity"])
            submit = st.form_submit_button("Visualize")
            if submit:
                df = self.admin_manager.visualize_all(mode)
                if df is not None:
                    st.dataframe(df)
                    
                    if mode == "by_user":
                        st.bar_chart(df.set_index("User")["Total Spent"])
                    elif mode == "by_date":
                        st.bar_chart(df.set_index("Date")["Total Sales"])
                    elif mode == "by_quantity":
                        st.bar_chart(df.set_index("Item")["Total Quantity"])
                    elif mode == "by_item_name":
                        st.bar_chart(df.set_index("Item")["Total Spent"])
                else:
                    st.error("No data available for visualization")
    
    def set_role_page(self):
        with st.form("set_role_form"):
            st.subheader("Set User Role")
            self.admin_manager.refresh_users(self.file_manager)
            username = st.selectbox("Username", self.admin_manager.get_user())
            role_option = st.radio(
                "Select role:",
                options=["Set as Admin", "Remove as Admin"],
                index=None
            )
            submit = st.form_submit_button("Set Role")
            if submit:
                if role_option is None:
                    st.error("Please select a role option")
                else:
                    is_admin = role_option == "Set as Admin"
                    raw_username = username.split(" ", 1)[1].split(" (")[0].lower()
                    condition,message = self.user_manager.set_role(raw_username, is_admin)
                    if condition:
                        self.file_manager.save_users(self.user_manager.users)
                        st.success(message)
                    else:
                        st.error(message)
    
    def stock_vs_reorder_page(self):
        st.subheader("Stock vs Reorder Point")
        data = self.inventory_manager.get_stock_vs_reorder_data()

        if data:
            df = pd.DataFrame(data)

            low_stock_items = df[df["units_left"] <= df["reorder_point"]]

            if not low_stock_items.empty:
                warning_lines = [
                    f"- {row['item_name']} ({row['units_left']})"
                    for _, row in low_stock_items.iterrows()
                ]
                warning_msg = "⚠️ **We are running short of:**\n\n" + "\n".join(warning_lines)
                st.error(warning_msg)

            st.dataframe(df)

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(df['item_name'], df['units_left'], color='skyblue', label='Units Left')
            ax.scatter(df['reorder_point'], df['item_name'], color='red', label='Reorder Point', marker='o', zorder=5)
            ax.set_xlabel("Units")
            ax.set_ylabel("Item Name")
            ax.invert_yaxis()
            ax.legend()
            st.pyplot(fig)
        else:
            st.warning("No inventory data available.")

class UserPage(Page):
    def profile_page(self):
        st.subheader("👤 Profile")

        username = st.session_state.current_user
        role = "Admin" if self.user_manager.is_admin() else "User"
        st.markdown(f"**Username:**   {username.title()}")
        st.markdown(f"**Role:**   {role}")
        user_purchases = [
            p for p in self.purchase_manager.purchases if p["user"] == username
        ]

        if user_purchases:
            total_spent = sum(p["cost"] for p in user_purchases)
            total_items = sum(p["quantity"] for p in user_purchases)

            st.markdown(f"**Total Purchases:** {len(user_purchases)}")
            st.markdown(f"**Total Items Bought:** {total_items}")
            st.markdown(f"**Total Spent:** $ {total_spent:.2f}")

            df = pd.DataFrame(user_purchases)
            st.bar_chart(df.groupby("item_name")["cost"].sum())
        else:
            st.info("No purchases yet.")

        with st.expander("🛡️ Change Password"):
            position = st.selectbox("Position", ["first", "last"])
            char = st.text_input("Enter character for security check")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            if st.button("Update Password"):
                success, msg = self.user_manager.forgot_password(
                    username, char, position, new_pass, confirm_pass
                )
                if success:
                    self.file_manager.save_users(self.user_manager.users)
                    st.success("Password updated!")
                else:
                    st.error(msg)
    
    def logout_page(self):
        self.user_manager.logout()
        self.file_manager.save_users(self.user_manager.users)
        self.file_manager.save_inventory(self.inventory_manager.inventory)
        self.file_manager.save_purchases(self.purchase_manager.purchases)
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.selected_user = None
        self.user_manager.current_user = None
        st.success("Logged out!")
        st.rerun()

class MainApp:
    def __init__(self, managers):
        self.managers = managers
        self.auth = AuthPage(managers)
        self.inventory = InventoryPage(managers)
        self.purchase = PurchasePage(managers)
        self.admin = AdminPage(managers)
        self.user = UserPage(managers)
        self.init_session()
    
    def init_session(self):
        if "current_user" in st.session_state and st.session_state.current_user:
            self.managers[1].current_user = st.session_state.current_user
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = self.managers[1].is_authenticated()
        if "current_user" not in st.session_state:
            st.session_state.current_user = self.managers[1].current_user
        if "selected_user" not in st.session_state:
            st.session_state.selected_user = None
    
    def run(self):
        st.title("Inventory Management System")
        pages = {}
        
        if not st.session_state.authenticated:
            pages = {
                "Authentication": [
                    st.Page(self.auth.login_page, title="Login"),
                    st.Page(self.auth.register_page, title="Register"),
                    st.Page(self.auth.forgot_password_page, title="Forgot Password")
                ]
            }
        else:
            if not self.managers[1].is_admin():
                pages = {
                    "Inventory": [
                        st.Page(self.inventory.view_inventory_page, title="View Inventory"),
                        st.Page(self.purchase.buy_product_page, title="Buy Product"),
                    ],
                    "Logs" : [
                        st.Page(self.purchase.view_purchases_page, title="View Purchases"),
                        st.Page(self.purchase.download_logs_page, title="Download Logs"),
                    ],
                    "Account": [
                        st.Page(self.user.profile_page, title="Profile"),
                        st.Page(self.user.logout_page, title="Logout")
                    ]
                }
            else:
                pages = {
                    "Inventory": [
                        st.Page(self.inventory.view_inventory_page, title="View Inventory"),
                        st.Page(self.purchase.buy_product_page, title="Buy Product"),
                        st.Page(self.inventory.add_item_page, title="Add Item"),
                        st.Page(self.inventory.update_item_page, title="Update Item"),
                        st.Page(self.inventory.remove_item_page, title="Remove Item"),
                    ],
                    "Logs" : [
                        st.Page(self.purchase.view_purchases_page, title="View Purchases"),
                        st.Page(self.purchase.download_logs_page, title="Download Logs"),
                    ],
                    "Account": [
                        st.Page(self.user.profile_page, title="Profile"),
                        st.Page(self.user.logout_page, title="Logout")
                    ],
                    "Records" : [
                        st.Page(self.admin.view_all_users_page, title="View All Users"),
                        st.Page(self.admin.visualize_sales_page, title="Visualize Sales"),
                        st.Page(self.admin.set_role_page, title="Set User Role"),
                        st.Page(self.admin.stock_vs_reorder_page, title="Stock vs Reorder Point")
                    ]
                }

        with st.sidebar:
            st.markdown("""
            <style>
                header {
                    color: #000 !important;
                    font-weight: 700;
            </style>
                        """,unsafe_allow_html=True)
        
        pg = st.navigation(pages)
        pg.run()


managers = AppManager.init_managers()
app = MainApp(managers)
app.run()