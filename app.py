""" Module for our Flask app """

from flask import Flask, request, make_response, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message
import yagmail
import asyncio
from models import db, User, Buttery, MenuItem, Ingredient, Order, OrderItem
from datetime import datetime
import json
import os
from dotenv import load_dotenv

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

# Sets up the database connection string
# sqlite:/// specifies we're using SQLite
# os.path.join(basedir, 'butterrush.db') creates the path to the database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'butterrush.db')

# Disables the SQLAlchemy modification tracking system
# Disabling it improves performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sets up email sending stuff
# app.config['MAIL_SERVER']         = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT']           = os.getenv('MAIL_PORT')
# app.config['MAIL_USE_TLS']        = True # ! could it be replaced with 0 or 1 in the env file?
# app.config['MAIL_USE_SSL']        = False
# app.config['MAIL_USERNAME']       = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD']       = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# mail = Mail(app)
db.init_app(app)

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# print("UWU", MAIL_USERNAME, MAIL_PASSWORD)

yagmail.register(MAIL_USERNAME, MAIL_PASSWORD)
yag = yagmail.SMTP(MAIL_USERNAME)

'''
flask-mail.MAIL_SERVER: str = localhost
flask-mail.MAIL_PORT: int = 25
flask-mail.MAIL_USE_TLS: bool = False
flask-mail.MAIL_USE_SSL: bool = False
flask-mail.MAIL_DEBUG: bool = app.debug
flask-mail.MAIL_USERNAME: str | None = None
flask-mail.MAIL_PASSWORD: str | None = None
flask-mail.MAIL_DEFAULT_SENDER: str | None = None
flask-mail.MAIL_MAX_EMAILS: int | None = None
flask-mail.MAIL_SUPPRESS_SEND: bool = app.testing
flask-mail.MAIL_ASCII_ATTACHMENTS: bool = False'''

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

@app.route('/u_createAccount', methods=['GET', 'POST'])
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

        new_user = User(
            username=username,
            password_hash=password,  # Should use proper hashing
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()
        
        response = make_response(redirect("/u_butteries"))
        response.set_cookie('user_id', str(new_user.user_id))
        return response
    
    return render_template('u_createAccount.html')

#-----------------------------------------------------------------------

# ! apparently there is a Flask-Login extension that can handle this?
# change this in future
@app.route('/u_login', methods=['GET'])
def u_login():

    error_msg = request.cookies.get('error_msg')
    if error_msg is None:
        error_msg = ''

    # remember the user
    username = request.cookies.get('username')
    if username is None:
        username = ''

    password = request.cookies.get('password')
    if password is None:
        password = ''

    html = render_template('u_login.html', error_msg=error_msg,
                           username=username,
                           password=password)
    response = make_response(html)

    response.set_cookie('username', username)  # ! we need this so that if we reload this page we still have username and password
    response.set_cookie('password', password)
    return response

#-----------------------------------------------------------------------

@app.route('/u_login_submit', methods=['GET'])   # could this just be done in u_login?
def u_login_submit():
    username = request.args.get('uname')
    password = request.args.get('pword')

    if not (username and password):
        response = redirect(url_for('u_login'))
        response.set_cookie('error_msg', 'Username or password empty.')
        return response

    user = User.query.filter_by(username=username).first()
    
    if not user:
        response = redirect(url_for('u_login'))
        response.set_cookie('error_msg', 'Username not found.')
        return response

    if user.password_hash != password:  # Should use proper password verification
        response = redirect(url_for('u_login'))
        response.set_cookie('error_msg', 'Incorrect password.')
        return response

    # Update last login
    user.last_login = datetime.now()
    db.session.commit()

    response = make_response(redirect(url_for('u_butteries')))
    response.set_cookie('user_id', str(user.user_id))
    response.set_cookie('u_username', username)
    return response

#-----------------------------------------------------------------------

@app.route('/u_butteries', methods=['GET'])  
def u_butteries():
    butteries = Buttery.query.all()
    return render_template('u_butteries.html', 
                         butteries=[b.buttery_name for b in butteries])

#-----------------------------------------------------------------------

@app.route('/u_get_buttery_menu', methods=['GET'])
def u_get_buttery_menu():
    buttery_name = request.args.get('buttery')
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    
    # Remove is_available filter for now
    menu_items = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id
    ).all()
    
    return render_template('u_butteryMenu.html',
                         buttery=buttery_name,
                         menuItems=menu_items,
                         opening_hours=buttery.opening_hours)

#-----------------------------------------------------------------------

@app.route('/u_display_item', methods=['GET'])
def u_display_item():
    buttery = request.args.get('buttery')
    menu_item_name = request.args.get('menu_item')
    
    # Get menu item from database
    buttery_obj = Buttery.query.filter_by(buttery_name=buttery).first()
    menu_item = MenuItem.query.filter_by(
        buttery_id=buttery_obj.buttery_id,
        item_name=menu_item_name
    ).first()
    
    if not menu_item:
        return "Menu item not found", 404
    
    return render_template('u_menuItem.html',
                         menu_item=menu_item,  # Pass the entire menu_item object
                         buttery=buttery)

#-----------------------------------------------------------------------

@app.route('/u_add_to_cart', methods=['POST'])
def u_add_to_cart():
    try:
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

        # Get current cart or initialize empty cart
        cart_cookie = request.cookies.get('cart')
        cart = json.loads(cart_cookie) if cart_cookie else []

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
        response = make_response(redirect(url_for('u_cart')))
        response.set_cookie('cart', json.dumps(cart))
        return response

    except Exception as e:
        return "Error adding item to cart", 500

#-----------------------------------------------------------------------

@app.route('/u_cart', methods=['GET'])
def u_cart():
    cart_cookie = request.cookies.get('cart')
    if cart_cookie:
        try:
            cart = json.loads(cart_cookie)
            # Filter out any invalid items from the cart
            valid_cart = []
            for item in cart:
                if isinstance(item, dict) and 'menu_item' in item and item['menu_item']:
                    valid_cart.append(item)
            cart = valid_cart
        except (json.JSONDecodeError, KeyError):
            cart = []
    else:
        cart = []
    
    return render_template('u_cart.html', cart=cart)

#-----------------------------------------------------------------------

@app.route('/u_remove_from_cart', methods=['POST'])
def u_remove_from_cart():
    index = int(request.form.get('index'))

    cart_cookie = request.cookies.get('cart')
    cart = json.loads(cart_cookie) if cart_cookie else []

    # remove item if index is valid
    if 0 <= index < len(cart):
        cart.pop(index)

    response = make_response(redirect(url_for('u_cart')))
    response.set_cookie('cart', json.dumps(cart))
    return response

#-----------------------------------------------------------------------

@app.route('/u_submit_order', methods=['POST'])
def u_submit_order():
    cart_cookie = request.cookies.get('cart')
    cart = json.loads(cart_cookie) if cart_cookie else []
    user_id = int(request.cookies.get('user_id'))
    
    if not cart:
        return redirect(url_for('u_cart'))
    
    # Create new order
    total_price = 0
    buttery_name = cart[0]['buttery']  # Assuming all items from same buttery
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    
    new_order = Order(
        user_id=user_id,
        buttery_id=buttery.buttery_id,
        total_price=0,  # Will update after adding items
        status='pending'
    )
    db.session.add(new_order)
    db.session.flush()  # Get order_id without committing
    
    # Add order items
    for item in cart:
        menu_item = MenuItem.query.filter_by(item_name=item['menu_item']['name']).first()
        order_item = OrderItem(
            order_id=new_order.order_id,
            menu_item_id=menu_item.menu_item_id,
            quantity=item['quantity'],
            item_price=item['menu_item']['price'],
            note=item.get('note', '')  # Add the note from cart item
        )
        total_price += item['menu_item']['price'] * item['quantity']
        db.session.add(order_item)
    
    new_order.total_price = total_price
    db.session.commit()
    
    response = make_response(redirect(url_for('u_ordersIP')))
    response.set_cookie('cart', '', expires=0)  # Clear cart
    return response

#-----------------------------------------------------------------------

@app.route('/u_ordersIP', methods=['GET'])  
def u_ordersIP():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('u_login'))
    
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

#-----------------------------------------------------------------------

@app.route('/u_account', methods=['GET'])  
def u_account():
    html = render_template('u_account.html', username=request.cookies.get('u_username'))
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------
# BUTTERY SIDE
#-----------------------------------------------------------------------

@app.route('/b_login', methods=['GET'])
def b_login():

    error_msg = request.cookies.get('error_msg')
    if error_msg is None:
        error_msg = ''

    # remember the user
    username = request.cookies.get('username')
    if username is None:
        username = ''

    password = request.cookies.get('password')
    if password is None:
        password = ''

    html = render_template('b_login.html', error_msg=error_msg,
                           username=username,
                           password=password)
    response = make_response(html)

    response.set_cookie('username', username)
    response.set_cookie('password', password)
    return response

#-----------------------------------------------------------------------

@app.route('/b_login_submit', methods=['GET'])  
def b_login_submit():
    username = request.args.get('uname')
    password = request.args.get('pword')

    username = username if username else ""
    password = password if password else ""

    if (username.strip() == '' or password.strip() == ''):
        response = redirect(url_for('b_login'))
        error_msg = 'Username or password empty.'
        response.set_cookie('error_msg', error_msg)

    else:
        # Query the Buttery from database instead of using BUTTERY_PASSWORD_DB
        buttery = Buttery.query.filter_by(buttery_name=username).first()

        if not buttery:
            response = redirect(url_for('b_login'))
            error_msg = 'Username not found. Create an account.'
            response.set_cookie('error_msg', error_msg)

        # TODO: Add proper password handling here
        elif password != 'temp_password':  # Temporary solution - should use proper password handling
            response = redirect(url_for('b_login'))
            error_msg = 'Password incorrect.'
            response.set_cookie('error_msg', error_msg)

        else:
            html = redirect(url_for('b_myButtery'))
            response = make_response(html)
            response.set_cookie('error_msg', '')

    response.set_cookie('username', username) 
    response.set_cookie('password', password)

    return response

#-----------------------------------------------------------------------

@app.route('/b_myButtery', methods=['GET'])  
def b_myButtery():
    # Get the buttery name from cookie
    buttery_name = request.cookies.get('username')
    
    # Get the buttery and its menu items from database
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    if not buttery:
        return redirect(url_for('b_login'))
    
    # Get all available menu items for this buttery
    menu_items = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id,
        is_available=True
    ).all()
    
    html = render_template('b_myButtery.html', 
                         buttery=buttery_name,
                         menuItems=[item.item_name for item in menu_items])
    response = make_response(html)

    return response

#-----------------------------------------------------------------------

@app.route('/b_display_item', methods=['GET'])
def b_display_item():
    menu_item_name = request.args.get('menu_item')
    buttery_name = request.cookies.get('username')
    
    # Get menu item from database
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    menu_item = MenuItem.query.filter_by(
        buttery_id=buttery.buttery_id,
        item_name=menu_item_name
    ).first()
    
    if not menu_item:
        return "Menu item not found", 404
    
    html = render_template('b_menuItem.html',
                         ingredients=[ing.ingredient_name for ing in menu_item.ingredients],
                         buttery=buttery_name,
                         menuItem=menu_item.item_name)
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------

@app.route('/b_orderQueue', methods=['GET']) 
def b_orderQueue():
    buttery_name = request.cookies.get('username')
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    
    if not buttery:
        return redirect(url_for('b_login'))
    
    # Get orders that are pending or ready (not picked up) # ! does this mean we keep all orders in history ever in our orders table? we could delete or we could recommend based on most frequently ordered
    orders = Order.query.filter_by(
        buttery_id=buttery.buttery_id
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
                'id': item.order_item_id,  # Need this for checkbox updates
                'name': menu_item.item_name,
                'quantity': item.quantity,
                'note': item.note,
                'checked': item.checked  # Include checked status
            })
        
        user = User.query.get(order.user_id)
        username = user.username if user else 'Unknown User'
        
        formatted_orders.append({
            'id': order.order_id,
            'username': username,
            'order_items': order_items,
            'status': order.status,
            'total_price': float(order.total_price)
        })
    
    return render_template('b_orderQueue.html', orders=formatted_orders)

async def send_email(user_email, buttery_name):
    asyncio.to_thread(
        yag.send,
        to=user_email,
        subject='[Butterrush] Your buttery order is ready!',
        contents=f"Your order from {buttery_name} buttery is ready!"
    ) # do not wait for result

@app.route('/b_update_order_status', methods=['POST'])
def b_update_order_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('status')

    order = Order.query.get(order_id)

    if order:

        # send email to user
        if new_status == "ready":

            user = User.query.get(order.user_id)
            buttery = Buttery.query.get(order.buttery_id)

            if user and buttery:
                asyncio.run(send_email(user.email, buttery.buttery_name)) 

        order.status = new_status
        # Don't reset the checked status of items when updating order status
        db.session.commit()
    
    return redirect(url_for('b_orderQueue'))

#-----------------------------------------------------------------------

@app.route('/b_account', methods=['GET']) 
def b_account():
    buttery_name = request.cookies.get('username')
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    
    if not buttery:
        return redirect(url_for('b_login'))
    
    html = render_template('b_account.html', 
                         username=buttery_name,
                         buttery=buttery)  # Pass the buttery object to template
    response = make_response(html)
    
    return response

@app.route('/b_update_hours', methods=['POST'])
def b_update_hours():
    buttery_name = request.cookies.get('username')
    buttery = Buttery.query.filter_by(buttery_name=buttery_name).first()
    
    if not buttery:
        return redirect(url_for('b_login'))
    
    new_hours = request.form.get('opening_hours')
    if new_hours:
        buttery.opening_hours = new_hours
        db.session.commit()
    
    return redirect(url_for('b_account'))

#-----------------------------------------------------------------------

@app.route('/logout', methods=['GET'])  # ! should we separate user and buttery logout
def logout():
    # clear cookies
    html = redirect(url_for("home"))
    response = make_response(html)
    response.set_cookie('username', '')
    response.set_cookie('password', '')
    
    return response


@app.route('/u_update_quantity', methods=['POST'])
def u_update_quantity():
    index = int(request.form.get('index'))
    new_quantity = int(request.form.get('quantity'))
    
    cart_cookie = request.cookies.get('cart')
    cart = json.loads(cart_cookie) if cart_cookie else []
    
    # Update quantity if index is valid
    if 0 <= index < len(cart):
        cart[index]['quantity'] = new_quantity
    
    response = make_response(redirect(url_for('u_cart')))
    response.set_cookie('cart', json.dumps(cart))
    return response

# allows checked items to persist when order status is updated
@app.route('/b_update_item_check', methods=['POST'])
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