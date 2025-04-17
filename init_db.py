from app import app, db
from models import User, Buttery, MenuItem, Ingredient, MenuItemIngredient
from datetime import datetime

def init_db():
    with app.app_context():
        # Create all database tables based on models
        db.create_all()
        
        # Initialize butteries with opening hours and passwords
        butteries_data = [
            ('Benjamin Franklin', '10PM-1AM', 'password'),
            ('Berkeley', '10PM-1AM', 'password'),
            ('Branford', '10PM-1AM', 'password'),
            ('Davenport', '10PM-1AM', 'password'),
            ('Ezra Stiles', '10PM-1AM', 'password'),
            ('Grace Hopper', '10PM-1AM', 'password'),
            ('Jonathan Edwards', '10PM-1AM', 'password'),
            ('Morse', '10PM-1AM', 'password'),
            ('Pauli Murray', '10PM-1AM', 'password'),
            ('Pierson', '10PM-1AM', 'password'),
            ('Saybrook', '10PM-1AM', 'password'),
            ('Silliman', '10PM-1AM', 'password'),
            ('Timothy Dwight', '10PM-1AM', 'password'),
            ('Trumbull', '10PM-1AM', 'password')
        ]
        
        for name, hours, password in butteries_data:
            buttery = Buttery(
                buttery_name=name, 
                opening_hours=hours,
                password_hash=password  # Should use proper password hashing in production
            )
            db.session.add(buttery)
        
        # Commit butteries to get their IDs for relationships
        db.session.commit()
        
        # Initialize ingredient inventory
        ingredients_data = [
            ('Cheese', 100),
            ('Flour tortilla', 200)
        ]
        
        for name, qty in ingredients_data:
            ingredient = Ingredient(ingredient_name=name, inventory_quantity=qty)
            db.session.add(ingredient)
        
        # Commit ingredients to get their IDs for relationships
        db.session.commit()
        
        # Initialize menu items with prices and categories
        # Replaces BUTTERY_MENU_DB dictionary

        # ! WILL NEED TO CHANGE THIS TO BE DYNAMIC
        davenport = Buttery.query.filter_by(buttery_name='Davenport').first()
        cheese = Ingredient.query.filter_by(ingredient_name='Cheese').first()
        tortilla = Ingredient.query.filter_by(ingredient_name='Flour tortilla').first()
        
        
        quesadilla = MenuItem(
            buttery_id=davenport.buttery_id,
            item_name='Quesadilla',
            description='Cheese quesadilla',
            price=2.50,
            category='Savory',
            is_available=True
        )
        db.session.add(quesadilla)
        db.session.commit()
        
        # Create ingredient relationships for menu items
        # Replaces static MENU_ITEM_DB dictionary
        menu_item_ingredients = [
            MenuItemIngredient(menu_item_id=quesadilla.menu_item_id, 
                             ingredient_id=cheese.ingredient_id,
                             quantity=1),  # Track ingredient quantities
            MenuItemIngredient(menu_item_id=quesadilla.menu_item_id,
                             ingredient_id=tortilla.ingredient_id,
                             quantity=1)
        ]
        
        for mii in menu_item_ingredients:
            db.session.add(mii)
        
        # Final commit to save all relationships
        db.session.commit()

if __name__ == '__main__':
    init_db() 