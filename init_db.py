from app import app, db
from models import User, Buttery, MenuItem, Ingredient, MenuItemIngredient
from datetime import datetime
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all database tables based on models
        db.create_all()
        
        # Initialize butteries with opening hours and passwords
        butteries_data = [
            ('Benjamin Franklin', '10PM-1AM', 'temp_password'),
            ('Berkeley', '10PM-1AM', 'temp_password'),
            ('Branford', '10PM-1AM', 'temp_password'),
            ('Davenport', '10PM-1AM', 'temp_password'),
            ('Ezra Stiles', '10PM-1AM', 'temp_password'),
            ('Grace Hopper', '10PM-1AM', 'temp_password'),
            ('Jonathan Edwards', '10PM-1AM', 'temp_password'),
            ('Morse', '10PM-1AM', 'temp_password'),
            ('Pauli Murray', '10PM-1AM', 'temp_password'),
            ('Pierson', '10PM-1AM', 'temp_password'),
            ('Saybrook', '10PM-1AM', 'temp_password'),
            ('Silliman', '10PM-1AM', 'temp_password'),
            ('Timothy Dwight', '10PM-1AM', 'temp_password'),
            ('Trumbull', '10PM-1AM', 'temp_password')
        ]
        
        for name, hours, password in butteries_data:
            buttery = Buttery(
                buttery_name=name, 
                opening_hours=hours,
                password_hash=generate_password_hash(password)  # Should use proper password hashing in production
            )
            db.session.add(buttery)
        
        # Commit butteries to get their IDs for relationships
        db.session.commit()
        
        # Initialize ingredient inventory
        ingredients_data = [
            # Savory ingredients
            ('Chicken Tenders', 100),
            ('Chicken Nuggets', 100),
            ('Mozz Sticks', 100),
            ('Mac n Cheese', 100),
            ('Curly Fries', 100),
            ('Ramen Noodles', 100),
            ('Tater Tots', 100),
            ('Pizza Rolls', 100),
            ('Flour Tortilla', 100),
            ('Cheese', 100),
            ('Bread', 100),
            ('Peanut Butter', 100),
            ('Honey', 100),
            ('Jelly', 100),
            ('Nutella', 100),
            
            # Sweet ingredients
            ('Cookie Dough', 100),
            ('Ice Cream', 100),
            ('Candy', 100),
            
            # Healthy ingredients
            ('Hummus', 100),
            ('Chobani Yogurt', 100),
            
            # Drink ingredients
            ('Chamomile Tea', 100),
            ('Chai Tea', 100),
            ('English Breakfast Tea', 100),
            ('Earl Grey Tea', 100),
            ('Red Raspberry Tea', 100),
            ('Black Tea', 100),
            # New soda ingredients
            ('Coke', 100),
            ('Diet Coke', 100),
            ('Orange Soda', 100),
            ('Dr. Pepper', 100),
            ('Sprite', 100),
            ('Ginger Ale', 100)
        ]
        
        for name, qty in ingredients_data:
            ingredient = Ingredient(ingredient_name=name, inventory_quantity=qty)
            db.session.add(ingredient)
        
        # Commit ingredients to get their IDs for relationships
        db.session.commit()
        
        # Get all ingredient objects
        ingredients = {ing.ingredient_name: ing for ing in Ingredient.query.all()}
        
        # Initialize menu items with prices and categories
        menu_items_data = [
            # Savory items
            {
                'name': 'Tenders',
                'description': '3 chicken tenders',
                'price': 2.00,
                'category': 'Savory',
                'ingredients': [('Chicken Tenders', 3)]
            },
            {
                'name': 'Nuggets',
                'description': '6 chicken nuggets',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Chicken Nuggets', 6)]
            },
            {
                'name': 'Mozz Sticks',
                'description': 'Mozzarella cheese sticks',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Mozz Sticks', 3)]
            },
            {
                'name': 'Mac n\' Cheese Bites',
                'description': 'Macaroni and cheese bites',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Mac n Cheese', 1)]
            },
            {
                'name': 'Curly Fries',
                'description': 'Curly fries',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Curly Fries', 1)]
            },
            {
                'name': 'Ramen',
                'description': 'Instant ramen',
                'price': 0.50,
                'category': 'Savory',
                'ingredients': [('Ramen Noodles', 1)]
            },
            {
                'name': 'Tater Tots',
                'description': 'Tater tots',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Tater Tots', 1)]
            },
            {
                'name': 'Pizza Rolls',
                'description': 'Pizza rolls',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Pizza Rolls', 6)]
            },
            {
                'name': 'Quesadilla',
                'description': 'Cheese quesadilla',
                'price': 1.50,
                'category': 'Savory',
                'ingredients': [('Flour Tortilla', 1), ('Cheese', 1)]
            },
            {
                'name': 'Grilled Cheese',
                'description': 'Grilled cheese sandwich',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Bread', 2), ('Cheese', 1)]
            },
            {
                'name': 'PB & Honey Sandwich',
                'description': 'Peanut butter and honey sandwich',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Bread', 2), ('Peanut Butter', 1), ('Honey', 1)]
            },
            {
                'name': 'PB & Jelly Sandwich',
                'description': 'Peanut butter and jelly sandwich',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Bread', 2), ('Peanut Butter', 1), ('Jelly', 1)]
            },
            {
                'name': 'PB & Nutella Sandwich',
                'description': 'Peanut butter and Nutella sandwich',
                'price': 1.00,
                'category': 'Savory',
                'ingredients': [('Bread', 2), ('Peanut Butter', 1), ('Nutella', 1)]
            },
            
            # Sweet items
            {
                'name': 'Nutella-dilla',
                'description': 'Nutella quesadilla',
                'price': 1.50,
                'category': 'Sweet',
                'ingredients': [('Flour Tortilla', 1), ('Nutella', 1)]
            },
            {
                'name': 'Candy',
                'description': 'Assorted candy',
                'price': 0.50,
                'category': 'Sweet',
                'ingredients': [('Candy', 1)]
            },
            {
                'name': 'Ice Cream Sandwich',
                'description': 'Ice cream sandwich',
                'price': 1.00,
                'category': 'Sweet',
                'ingredients': [('Ice Cream', 1)]
            },
            {
                'name': 'Cookie Dough',
                'description': 'Cookie dough',
                'price': 1.00,
                'category': 'Sweet',
                'ingredients': [('Cookie Dough', 1)]
            },
            
            # Healthy items
            {
                'name': 'Hummus',
                'description': 'Hummus',
                'price': 1.50,
                'category': 'Healthy',
                'ingredients': [('Hummus', 1)]
            },
            {
                'name': 'Chobani',
                'description': 'Chobani yogurt',
                'price': 2.00,
                'category': 'Healthy',
                'ingredients': [('Chobani Yogurt', 1)]
            },
            
            # Drink items
            {
                'name': 'Chamomile Tea',
                'description': 'Chamomile tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Chamomile Tea', 1)]
            },
            {
                'name': 'Chai Tea',
                'description': 'Chai tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Chai Tea', 1)]
            },
            {
                'name': 'English Breakfast Tea',
                'description': 'English breakfast tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('English Breakfast Tea', 1)]
            },
            {
                'name': 'Earl Grey Tea',
                'description': 'Earl grey tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Earl Grey Tea', 1)]
            },
            {
                'name': 'Red Raspberry Tea',
                'description': 'Red raspberry tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Red Raspberry Tea', 1)]
            },
            {
                'name': 'Black Tea',
                'description': 'Black tea',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Black Tea', 1)]
            },
            {
                'name': 'Coke',
                'description': 'Coca-Cola',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Coke', 1)]
            },
            {
                'name': 'Diet Coke',
                'description': 'Diet Coca-Cola',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Diet Coke', 1)]
            },
            {
                'name': 'Orange Soda',
                'description': 'Orange flavored soda',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Orange Soda', 1)]
            },
            {
                'name': 'Dr. Pepper',
                'description': 'Dr. Pepper soda',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Dr. Pepper', 1)]
            },
            {
                'name': 'Sprite',
                'description': 'Lemon-lime soda',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Sprite', 1)]
            },
            {
                'name': 'Ginger Ale',
                'description': 'Ginger flavored soda',
                'price': 0.50,
                'category': 'Drinks',
                'ingredients': [('Ginger Ale', 1)]
            }
        ]
        
        # Create menu items and their ingredient relationships for each buttery
        for buttery in Buttery.query.all():
            for item_data in menu_items_data:
                menu_item = MenuItem(
                    buttery_id=buttery.buttery_id,
                    item_name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    category=item_data['category'],
                    is_available=True
                )
                db.session.add(menu_item)
                db.session.flush()  # Get menu_item_id without committing
                
                # Create ingredient relationships
                for ingredient_name, quantity in item_data['ingredients']:
                    ingredient = ingredients[ingredient_name]
                    menu_item_ingredient = MenuItemIngredient(
                        menu_item_id=menu_item.menu_item_id,
                        ingredient_id=ingredient.ingredient_id,
                        quantity=quantity
                    )
                    db.session.add(menu_item_ingredient)
        
        # Final commit to save all relationships
        db.session.commit()

if __name__ == '__main__':
    init_db() 