from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Replaces USERNAME_PASSWORD_DB dictionary
# Added fields: email
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)  # New required field
    password_hash = db.Column(db.String, nullable=False)  # Changed to store hashed passwords
    
    # Relationship to orders - allows easy access to user's orders
    orders = db.relationship('Order', backref='user', lazy=True)

# Replaces BUTTERY_PASSWORD_DB dictionary
# Added field: opening_hours
class Buttery(db.Model):
    __tablename__ = 'butteries'
    
    buttery_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buttery_name = db.Column(db.String, nullable=False)
    opening_hours = db.Column(db.String)
    password_hash = db.Column(db.String, nullable=False)
    
    # Relationships for access to menu items and orders
    menu_items = db.relationship('MenuItem', backref='buttery', lazy=True)
    orders = db.relationship('Order', backref='buttery', lazy=True)

# Model to track ingredients and inventory
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_name = db.Column(db.String, nullable=False, unique=True)
    inventory_quantity = db.Column(db.Float, default=0)

# Replaces BUTTERY_MENU_DB and MENU_ITEM_DB dictionaries
# Added fields: description, price, category, is_available
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    menu_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buttery_id = db.Column(db.Integer, db.ForeignKey('butteries.buttery_id'), nullable=False)
    item_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)  # New field for item description
    price = db.Column(db.Numeric(10,2), nullable=False)  # New field for item price
    category = db.Column(db.String)  # New field to group menu items
    is_available = db.Column(db.Boolean, default=True)  # Can mark items as unavailable
    
    # Many-to-many relationship with ingredients through menu_item_ingredients table
    ingredients = db.relationship('Ingredient', 
                                secondary='menu_item_ingredients',
                                backref='menu_items')

# New junction table for many-to-many relationship between MenuItems and Ingredients
class MenuItemIngredient(db.Model):
    __tablename__ = 'menu_item_ingredients'
    
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.menu_item_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), primary_key=True)
    quantity = db.Column(db.Float)  # Amount of ingredient needed for menu item

# Replaces BUTTERY_ORDERS_DB and STUDENT_ORDERS_DB dictionaries
# Added fields: order_date, total_price, status
class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    buttery_id = db.Column(db.Integer, db.ForeignKey('butteries.buttery_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)  # When order was placed
    total_price = db.Column(db.Numeric(10,2), nullable=False)  # Total order cost
    status = db.Column(db.String, default='pending')  # Order status tracking
    
    # Relationship to order items
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

# Tracks individual items in an order
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.menu_item_id'), primary_key=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)  # How many of this item
    note = db.Column(db.String)  # Special instructions
    item_price = db.Column(db.Numeric(10,2), nullable=False)  # Price at time of order 