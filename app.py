""" Module for our Flask app """

from flask import Flask, request, make_response, redirect, url_for, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message
import smtplib
import asyncio
from models import db, User, Buttery, MenuItem, Ingredient, Order, OrderItem, MenuItemIngredient, OOSIngredient
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


# -----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')
auth = HTTPBasicAuth()

# -----------------------------------------------------------------------

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# -----------------------------------------------------------------------

def get_current_buttery():
    buttery_id = session.get('buttery_id')
    if buttery_id is None:
        return None
    
    buttery = Buttery.query.filter_by(buttery_id=buttery_id).first()
    if not buttery:
        return None
    
    return buttery

# loads email creds from .env file # ! can also put user and buttery credentials in .env and make init_db.py load from that! 
load_dotenv()

app = Flask(__name__, template_folder='./html')

# SQLite configuration
# Okay, this is how this works because I just learned this:

# __file__ is the path to the current file (app.py)
# os.path.dirname() gets the directory containing this file
# os.path.abspath() converts it to an absolute path
# This ensures the database file is created in the correct location regardless of where you run the app from
basedir = os.path.abspath(os.path.dirname(__file__))

# Sets secret key for session signing
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

# Sets up the database connection string
# sqlite:/// specifies we're using SQLite
# os.path.join(basedir, 'butterrush.db') creates the path to the database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'butterrush.db')

# Disables the SQLAlchemy modification tracking system
# Disabling it improves performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

#-----------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return "404 error."

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    html = render_template('index.html')
    response = make_response(html)

    return response

#-----------------------------------------------------------------------
# USER SIDE
#-----------------------------------------------------------------------

@app.route('/createaccount', methods=['GET', 'POST'])
def u_createAccount():
    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["pword"]
        email = request.form["email"]  # Add email field to form

        if not (username and password and email):
            return render_template('u_createAccount.html', 
                                message="All fields are required.",
                                user=username)

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return render_template('u_createAccount.html', 
                                message="An account with this email already exists")
            
        if User.query.filter_by(username=username).first():
            return render_template('u_createAccount.html', 
                                message="An account with this username already exists")

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect to login page with success message
        response = make_response(redirect(url_for('u_login')))
        flash("Account created successfully! Please log in.", 'success')
        return response
    
    return render_template('u_createAccount.html')


@app.route('/user/login', methods=['GET'])
def u_login():
    if 'user_id' in session:
        return redirect(url_for('u_butteries'))

    # username = request.cookies.get('username')  # Cookie for login attempt username
    html = render_template('u_login.html', 
                         username="",
                         password="")
                         
    response = make_response(html)
    return response


@app.route('/user/login/submit', methods=['GET'])
def u_login_submit():
    username = request.args.get('uname')
    password = request.args.get('pword')

    if not (username and password):
        response = redirect(url_for('u_login'))
        response.set_cookie('username', username)
        flash('Username and password cannot be empty.', 'danger')
        return response

    user = User.query.filter_by(username=username).first()

    if not user:
        response = redirect(url_for('u_login'))
        response.set_cookie('username', username)
        flash('Username not found.', 'danger')
        return response

    if not check_password_hash(user.password_hash, password):
        response = redirect(url_for('u_login'))
        response.set_cookie('username', username)
        flash("Incorrect password", 'danger')
        return response

    # Update last login
    user.last_login = datetime.now()
    db.session.commit()

    response = make_response(redirect(url_for('u_butteries')))
    session['user_id'] = str(user.user_id)
    session['u_username'] = username
    return response


@app.route('/user/butteries', methods=['GET'])  
def u_butteries():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    # Get the username from the session
    username = session.get('u_username', 'User')

    butteries = Buttery.query.all()
    return render_template('u_butteries.html', 
                         butteries=[b.buttery_name for b in butteries],
                         username=username)


@app.route('/user/getbutterymenu', methods=['GET'])
def u_get_buttery_menu():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    buttery_name = request.args.get('buttery')
    if not buttery_name:
        return "Request missing a buttery", 400
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    if not buttery:
        return "Buttery not found", 400
    
    menu_items = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id,
        is_available=True
    ).all()
    
    return render_template('u_butteryMenu.html',
                         buttery=buttery_name,
                         menuItems=menu_items,
                         opening_hours=buttery.opening_hours)


@app.route('/user/item', methods=['GET'])
def u_display_item():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    # Verify that request contains a valid buttery
    buttery = request.args.get('buttery')
    if not buttery:
        return "Request missing a buttery", 400
    
    buttery_obj = Buttery.query.filter_by(buttery_name=buttery).first()
    if not buttery_obj:
        return "Buttery not found", 400
    
    # Verify that request contains a valid menu item from given buttery and get item
    menu_item_name = request.args.get('menu_item')
    if not menu_item_name:
        return "Request missing a menu item", 400
    
    menu_item = MenuItem.query.filter_by(
        buttery_id=buttery_obj.buttery_id,
        item_name=menu_item_name
    ).first()
    if not menu_item:
        return "Menu item not found", 400
    
    return render_template('u_menuItem.html',
                         menu_item=menu_item,  # Pass the entire menu_item object
                         buttery=buttery)


@app.route('/user/cart/add', methods=['POST'])
def u_add_to_cart():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    menu_item = request.form.get('menu_item')
    buttery = request.form.get('buttery')
    quantity = int(request.form.get('quantity', 1))
    note = request.form.get('note', '')

    # Get the menu item from database
    buttery_obj = Buttery.query.filter_by(buttery_name=buttery).first()
    if not buttery_obj:
        return "Buttery not found", 404

    menu_item_obj = MenuItem.query.filter_by(
        buttery_id=buttery_obj.buttery_id,
        item_name=menu_item
    ).first()

    if not menu_item_obj:
        return "Menu item not found", 404

    cart = session.get('cart', [])

    # Add new item to cart with all necessary data
    cart.append({
        'menu_item': {
            'name': menu_item_obj.item_name,
            'price': float(menu_item_obj.price)
        },
        'buttery': buttery,
        'quantity': quantity,
        'note': note
    })

    # Create response with updated cart
    html = render_template('u_cart.html', cart=cart)
    response = make_response(html)
    session['cart'] = cart
    return response


@app.route('/user/cart', methods=['GET'])
def u_cart():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))

    cart = session.get('cart', [])
    if cart:
        try:
            # Filter out any invalid items from the cart
            valid_cart = []
            for item in cart:
                if isinstance(item, dict) and 'menu_item' in item and item['menu_item']:
                    valid_cart.append(item)
            cart = valid_cart
        except (KeyError):
            cart = []
    else:
        cart = []
    
    return render_template('u_cart.html', cart=cart)


@app.route('/user/cart/remove', methods=['POST'])
def u_remove_from_cart():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    index = int(request.form.get('index'))

    cart = session.get('cart', [])

    # remove item if index is valid
    if 0 <= index < len(cart):
        cart.pop(index)

    response = make_response(redirect(url_for('u_cart')))
    session['cart'] = cart
    return response


@app.route('/user/cart/order', methods=['POST'])
def u_submit_order():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))

    cart = session.get('cart', [])
    user_id = int(session.get('user_id'))
    
    if not cart:
        return redirect(url_for('u_cart'))
    
    # Create order for each buttery in the cart
    buttery_orders = {}
    
    # Add order items
    for item in cart:
        # Add one new order for each buttery with ordered items
        if item['buttery'] not in buttery_orders:
            buttery = Buttery.query.filter_by(buttery_name=item['buttery']).first()
            buttery_orders[item['buttery']] = Order(
                user_id=user_id,
                buttery_id=buttery.buttery_id,
                total_price=0,
                status='pending'
            )
            db.session.add(buttery_orders[item['buttery']])
            db.session.flush()  # Get order_id without committing
        
        # Add item to its buttery's order
        buttery_order = buttery_orders[item["buttery"]]
        menu_item = MenuItem.query.filter_by(item_name=item['menu_item']['name']).first()
        order_item = OrderItem(
            order_id=buttery_order.order_id,
            menu_item_id=menu_item.menu_item_id,
            quantity=item['quantity'],
            item_price=item['menu_item']['price'],
            note=item['note']
        )
        buttery_order.total_price += item['menu_item']['price'] * item['quantity']
        db.session.add(order_item)

    db.session.commit()
    
    response = make_response(redirect(url_for('u_ordersIP')))
    session.pop('cart', None)
    return response


@app.route('/user/orders', methods=['GET'])  
def u_ordersIP():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    user_id = session.get('user_id')
    
    # Get all non-completed orders for this user
    orders = Order.query.filter_by(
        user_id=user_id
    ).filter(
        Order.status.in_(['pending', 'ready'])
    ).all()
    
    # Format orders for template
    formatted_orders = []
    for order in orders:
        order_items = []
        for item in order.order_items:
            menu_item = MenuItem.query.get(item.menu_item_id)
            order_items.append({
                'name': menu_item.item_name,
                'quantity': item.quantity,
                'note': item.note,
                'item_price': item.item_price
            })
        
        buttery = Buttery.query.get(order.buttery_id)
        formatted_orders.append({
            'id': order.order_id,
            'buttery': buttery.buttery_name,
            'order_items': order_items,
            'status': order.status,
            'total_price': float(order.total_price),
            'order_date': order.order_date
        })
    
    return render_template('u_ordersIP.html', orders=formatted_orders)


@app.route('/user/account', methods=['GET'])  
def u_account():
    if 'user_id' not in session:
        return redirect(url_for('u_login'))
    
    html = render_template('u_account.html', username=session.get('u_username'))
    response = make_response(html)
    
    return response


@app.route('/user/cart/updatequantity', methods=['POST'])
def u_update_quantity():
    index = int(request.form.get('index'))
    new_quantity = int(request.form.get('quantity'))
    
    cart = session.get('cart', [])
    
    # Update quantity if index is valid
    if 0 <= index < len(cart):
        cart[index]['quantity'] = new_quantity
    
    response = make_response(redirect(url_for('u_cart')))
    session['cart'] = cart
    return response


#-----------------------------------------------------------------------
# BUTTERY SIDE
#-----------------------------------------------------------------------

@app.route('/buttery/login', methods=['GET'])
def b_login():
    # remember the user
    if session.get('buttery_id') is not None:
        return redirect(url_for('b_myButtery'))
    
    # username = request.cookies.get('buttery')

    html = render_template('b_login.html', username="")
    response = make_response(html)

    return response


@app.route('/buttery/login/submit', methods=['GET'])  
def b_login_submit():
    username = request.args.get('uname')
    password = request.args.get('pword')

    username = username if username else ""
    password = password if password else ""
    
    if (username.strip() == '' or password.strip() == ''):
        response = redirect(url_for('b_login'))
        flash('Username or password empty.', 'danger')

    else:
        # Query the Buttery from database instead of using BUTTERY_PASSWORD_DB
        buttery = Buttery.query.filter_by(buttery_name=username).first()

        if not buttery:
            response = redirect(url_for('b_login'))
            error_msg = 'Username not found. Create an account.'
            flash(error_msg, 'danger')

        # TODO: Add proper password handling here
        elif not check_password_hash(buttery.password_hash, password):
            response = redirect(url_for('b_login'))
            error_msg = 'Password incorrect.'
            flash(error_msg, 'danger')

        else:
            session['buttery_id'] = buttery.buttery_id
            return redirect(url_for('b_myButtery'))

    response.set_cookie('buttery', username) 

    return response


@app.route('/buttery/menu', methods=['GET'])  
def b_myButtery():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    # Get all available menu items for this buttery
    menu_items = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id
        # is_available=True
    ).all()

    # Get all ingredients of menu items for this buttery
    # also get whether or not they are available
    ing_and_avail = []
    ingredients = Ingredient.query.all()
    for ing in ingredients:
        if OOSIngredient.query.filter_by(ingredient_id=ing.ingredient_id, buttery_id=buttery.buttery_id).first():
            ing_and_avail.append((ing, False)) # False = not available
        else:
            ing_and_avail.append((ing, True))
    
    html = render_template('b_myButtery.html', 
                         buttery=buttery.buttery_name,
                         menuItems=menu_items,
                         itemIDs=[item.menu_item_id for item in menu_items],
                         ingredients=ing_and_avail,
                         buttery_id=buttery.buttery_id)
    response = make_response(html)

    return response


@app.route('/buttery/item/<string:item_id>', methods=['GET', 'POST'])
def b_display_item(item_id):
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    try:
        item_id = int(item_id)
    except ValueError:
        return redirect(url_for('b_myButtery'))

    menu_item = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id,
        menu_item_id=item_id).first()
    
    if not menu_item:
        print("Menu item not found in DB!")
        return redirect(url_for('b_myButtery'))
    
    if request.method == "GET":
        html = render_template('b_menuItem.html',
                        ingredients=[ing.ingredient_name for ing in menu_item.ingredients],
                        buttery=buttery.buttery_name,
                        menuItem=menu_item.item_name,
                        price=menu_item.price,
                        description=menu_item.description,
                        category=menu_item.category,
                        edit_mode=True,
                        menuItemID=menu_item.menu_item_id)
        response = make_response(html)
        return response

    elif request.method == "POST":
        post_action = request.form.get('action')
        if post_action == "delete":
            db.session.delete(menu_item)
            db.session.commit()
            return redirect(url_for('b_myButtery'))
        
        elif post_action == "edit_ingredients":
            return redirect(url_for('b_edit_item_ingredients', item_id=item_id ))

        elif post_action == "edit_item":
            item_name = request.form.get('item_name')
            price = request.form.get('price')
            description = request.form.get('description')
            category = request.form.get('category')
            
            if not menu_item:
                print("Menu item not found in DB!")
                return redirect(url_for('b_myButtery'))
            
            menu_item.item_name = item_name
            menu_item.description = description
            menu_item.price = price
            menu_item.category = category
            db.session.commit()
            return redirect(url_for('b_display_item', item_id=item_id))


@app.route('/buttery/item/edit/<string:item_id>', methods=['GET', 'POST'])
def b_edit_item_ingredients(item_id):
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    try:
        item_id = int(item_id)
    except ValueError:
        print("ID can't be converted to int")
        return redirect(url_for('b_myButtery'))
    
    item = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id,
        menu_item_id=item_id).first()
    
    if not item:
        print("Menu item not found in DB!")
        return redirect(url_for('b_myButtery'))
    
    item_ingredients = [ing.ingredient_name for ing in item.ingredients]
    
    ingredients = [ingredient.ingredient_name for ingredient in Ingredient.query.all()]
        
    if request.method == 'GET':
        return render_template('b_edit_item_ingredients.html',
                               item_id=item_id,
                               item_name=item.item_name,
                               item_ingredients=item_ingredients,
                               ingredients=ingredients)
    elif request.method == 'POST':
        action = request.form.get('action')

        if action == "add_ingredient":
            ingredient_name = request.form.get('ingredient')
            ingredient = Ingredient.query.filter_by(ingredient_name=ingredient_name).first()
            
            message = ""
            if not ingredient:
                message = f"{ingredient_name} not found in buttery ingredients list. New ingredients can be added on the right.\n"
            elif ingredient_name in item_ingredients:
                message = f"Ingredients can only be added once."
                
            if message:
                return render_template('b_edit_item_ingredients.html', 
                                item_id=item_id,
                                item_name=item.item_name,
                                ingredients=ingredients,
                                item_ingredients=item_ingredients,
                                message=message)

            db.session.add(MenuItemIngredient(menu_item_id=item_id,
                            ingredient_id=ingredient.ingredient_id,
                            quantity=1)) # Quantity default 1
            db.session.commit()
            return redirect(url_for('b_edit_item_ingredients', item_id=item_id))
        
        elif action == "remove_ingredient":
            ingredient_name = request.form.get('ingredient')
            ingredient = Ingredient.query.filter_by(ingredient_name=ingredient_name).first()
            if not ingredient:
                return "Removed ingredient not found", 404
            
            item_ingredient = MenuItemIngredient.query.filter_by(menu_item_id=item_id, ingredient_id=ingredient.ingredient_id).first()
            db.session.delete(item_ingredient)
            
            db.session.commit()
            return redirect(url_for('b_edit_item_ingredients', item_id=item_id))
        
        elif action == "new_ingredient":
            name = request.form.get('ingredient').strip()
            if not name or name in ingredients:
                message = f"{name} already exists." if name in ingredients else ""
                return make_response(render_template('b_edit_item_ingredients.html',
                            item_id=item_id,
                            item_name=item.item_name,
                            item_ingredients=item_ingredients,
                            ingredients=ingredients,
                            message=message))
                
            # Add new ingredient to database
            quantity = 100 # where should quantity be set?
            new_ingredient = Ingredient(ingredient_name=name, inventory_quantity=quantity)
            db.session.add(new_ingredient)
            db.session.commit()
            
            return redirect(url_for('b_edit_item_ingredients', item_id=item_id))


@app.route('/buttery/createitem', methods=['GET', 'POST'])
def b_create_item():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    # item_ingredients = request.cookies.get('item_ingredients')
    item_ingredients = session.get('item_ingredients')
    pending = ""
    if item_ingredients:
        item_ingredients = item_ingredients.split(",")
    else:
        item_ingredients = []
        
    ingredients = [ingredient.ingredient_name for ingredient in Ingredient.query.all()]
    
    if request.method == 'GET': 
        return render_template('b_create_item.html', 
                             buttery=buttery.buttery_name,
                             ingredients=ingredients, # ! note that this is not used anywhere
                             item_ingredients=item_ingredients)
        
    elif request.method == 'POST':
        action = request.form.get('action')
        if action == "create_item":
            item_name = request.form.get('item_name')
            price = request.form.get('price')
            description = request.form.get('description')
            category = request.form.get('category')
            # ingredient_ids = []
            
            message = ""
            if not item_name or not price:
                message = "Item name and price are required."
            elif float(price) < 0:
                message="Price cannot be negative."
            elif item_name in [item.item_name for item in MenuItem.query.filter_by(buttery_id=buttery.buttery_id).all()]:
                message = f"{item_name} already exists."
            
            if message: # Some ingredients were not found in the ingredients database
                return render_template('b_create_item.html', 
                                buttery=buttery.buttery_name,
                                ingredients=ingredients,
                                item_ingredients=item_ingredients,
                                message=message) # Change this, allow adding ingredients
                
            # Create new menu item
            new_item = MenuItem(
                buttery_id=buttery.buttery_id,
                item_name=item_name,
                description=description,
                price=price,
                category=category,
                is_available=True
            )
            db.session.add(new_item)
            db.session.commit()
            
            return redirect(url_for('b_edit_item_ingredients', item_id=new_item.menu_item_id))
    
    
@app.route('/buttery/queue', methods=['GET']) 
def b_orderQueue():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    # Get orders that are pending or ready (not picked up) # ! does this mean we keep all orders in history ever in our orders table? we could delete or we could recommend based on most frequently ordered
    orders = Order.query.filter_by(
        buttery_id=buttery.buttery_id
    ).filter(
        Order.status.in_(['pending', 'ready', 'picked up'])
    ).all()
    
    # Format orders for template
    formatted_orders = [[], []] # pending & ready orders separately
    for order in orders:
        order_items = []
        for item in order.order_items:
            menu_item = MenuItem.query.get(item.menu_item_id)
            order_items.append({
                'id': item.order_item_id,  # Need this for checkbox updates
                'name': menu_item.item_name,
                'quantity': item.quantity,
                'note': item.note,
                'checked': item.checked  # Include checked status
            })
        print(order.user_id)
        user = User.query.filter_by(user_id=order.user_id).first()
        # user = User.query.get(order.user_id)
        username = user.username if user else 'Unknown User'
        
        # Only include pending and ready orders in the queue
        if order.status in ['pending', 'ready']:
            status_index = 0 if order.status == 'pending' else 1
            formatted_orders[status_index].append({
                'id': order.order_id,
                'username': username,
                'order_items': order_items,
                'total_price': float(order.total_price)
            })
    
    return render_template('b_orderQueue.html', orders=formatted_orders)

# async def send_email(user_email, buttery_name):
#     asyncio.to_thread(
#         yag.send,
#         to=user_email,
#         subject='[Butterrush] Your buttery order is ready!',
#         contents=f"Your order from {buttery_name} buttery is ready!"
#     ) # do not wait for result

# Citation: This code is adapted from Python smtplib documentation.
# Link: https://docs.python.org/3/library/smtplib.html#smtplib.SMTP.sendmail
# Additionally, further credit is given to "How to send text messages with Python for Free" by David Mentgen/
# Link: https://medium.com/testingonprod/how-to-send-text-messages-with-python-for-free-a7c92816e1a4
async def send_email(email, message, subject):
    def send():
        recipient = email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        msg_subj_formatted = 'Subject: {}\n\n{}'.format(subject, message)
        server.sendmail(MAIL_USERNAME, recipient, msg_subj_formatted)
    
    asyncio.to_thread(send())


@app.route('/buttery/queue/updatestatus', methods=['POST'])
def b_update_order_status():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')

    order = Order.query.get(order_id)

    if order:
        # send email to user
        if new_status == "ready":
            user = User.query.get(order.user_id)
            if user:
                message = f"Your order from {buttery.buttery_name} is ready. Please come pick it up :)"
                asyncio.run(send_email(user.email, message, 'Your ButterRush Order is Ready!')) 

        order.status = new_status
        # Don't reset the checked status of items when updating order status
        db.session.commit()
    
    return redirect(url_for('b_orderQueue'))


@app.route('/buttery/account', methods=['GET']) 
def b_account():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    html = render_template('b_account.html', 
                         username=buttery.buttery_name,
                         buttery=buttery)  # Pass the buttery object to template
    response = make_response(html)
    
    return response


@app.route('/buttery/account/updatehours', methods=['POST'])
def b_update_hours():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    new_hours = request.form.get('opening_hours')
    if new_hours:
        buttery.opening_hours = new_hours
        db.session.commit()
    
    return redirect(url_for('b_account'))

# allows checked items to persist when order status is updated
@app.route('/buttery/menu/updateitemcheck', methods=['POST'])
def b_update_item_check():
    data = request.get_json()
    
    order_id = data.get('order_id')
    item_id = data.get('item_id')
    checked = data.get('checked')

    order_item = OrderItem.query.filter_by(
        order_id=order_id,
        order_item_id=item_id
    ).first()
    
    if order_item:
        order_item.checked = checked
        db.session.commit()
        print(f"Updated checked status to: {checked}")  # Debug print
    
    return '', 200

# toggles when item is OOS
@app.route('/buttery/toggleoutofstock', methods=['POST'])
def b_toggleIngredientOOS():
    buttery = get_current_buttery()
    if not buttery:
        return redirect(url_for('b_login'))
    
    data = request.get_json()
    
    ingredient_id = data.get('ingredient_id')
    buttery_id = data.get('buttery_id')
    if int(buttery_id) != int(buttery.buttery_id):
        return redirect(url_for('home'))
    
    set_unavailable = data.get('set_unavailable')

    oos = OOSIngredient.query.filter_by(ingredient_id=ingredient_id, buttery_id=buttery_id).first()
    # print("hi: ", oos, set_unavailable)

    if oos is not None and not set_unavailable: # need this check for oos so we don't delete something that doesn't exist
        # print("REMOVING FROM OOS")
        db.session.delete(oos)
        db.session.commit()

        # now, need to make corresponding menu items reappear
        menu_item_ingreds = MenuItemIngredient.query.filter_by(ingredient_id=ingredient_id).all()
        menu_item_ingreds_ids = [menu_item_ingred.menu_item_id for menu_item_ingred in menu_item_ingreds]
        menu_items = MenuItem.query.filter(MenuItem.menu_item_id.in_(menu_item_ingreds_ids)).all()

        for menu_item in menu_items:
            # print('HELLO')
            if int(menu_item.buttery_id) == int(buttery_id):
                available = True
                for ingredient in menu_item.ingredients: # only make reappear if rest of ingredients also in stock
                    if OOSIngredient.query.filter_by(ingredient_id=ingredient.ingredient_id, buttery_id=buttery_id).first():
                        available = False
                        break
                
                menu_item.is_available = available

        db.session.commit()

    elif oos is None and set_unavailable:
        # print("ADDING TO OOS")
        new_oos = OOSIngredient(ingredient_id=ingredient_id, buttery_id=buttery_id)
        db.session.add(new_oos)
        db.session.commit()

        # now, need to make corresponding menu items disappear
        menu_item_ingreds = MenuItemIngredient.query.filter_by(ingredient_id=ingredient_id).all()
        menu_item_ingreds_ids = [menu_item_ingred.menu_item_id for menu_item_ingred in menu_item_ingreds]
        menu_items = MenuItem.query.filter(MenuItem.menu_item_id.in_(menu_item_ingreds_ids)).all()

        for menu_item in menu_items:
            if int(menu_item.buttery_id) == int(buttery_id):
                menu_item.is_available = False

        db.session.commit()
    
    return '', 200

#-----------------------------------------------------------------------

@app.route('/logout', methods=['GET'])  # ! should we separate user and buttery logout
def logout():
    # clear session
    html = redirect(url_for("home"))
    response = make_response(html)
    session.clear()
    
    return response