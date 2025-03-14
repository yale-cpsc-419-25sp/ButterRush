""" Module for our Flask app """

from flask import Flask, request, make_response, redirect, url_for, render_template
# import requests

# ! should there be 2 separate apps for user and buttery

app = Flask(__name__, template_folder='.')

# ! these should be in our eventual SQL DB
USERNAME_PASSWORD_DB = {"username": "password"}
BUTTERY_MENU_DB = {"Davenport" : ["Quesadilla 1", "Quesadilla 2"]}
MENU_ITEM_DB = {"Quesadilla 1" : ["Cheese", "Flour tortilla"], "Quesadilla 2" : ["Flour tortilla"]}

# we can probably store things like cart items and orders in progress in variables
cart = []
ordersIP = []
USERNAME = ""
PASSWORD = ""

#-----------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return "404 error."

#-----------------------------------------------------------------------

# ! apparently there is a Flask-Login extension that can handle this?
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

@app.route('/u_login_submit', methods=['GET'])  
def u_login_submit():

    username = request.args.get('uname')
    password = request.args.get('pword')

    username = username if username else ""
    password = password if password else ""

    if (username.strip() == '' or password.strip() == ''):
        response = redirect(url_for('u_login'))
        error_msg = 'Username or password empty.'
        response.set_cookie('error_msg', error_msg)

    elif username not in USERNAME_PASSWORD_DB:
        response = redirect(url_for('u_login'))
        error_msg = 'Username not found. Create an account.'
        response.set_cookie('error_msg', error_msg)

    elif USERNAME_PASSWORD_DB[username] != password:
        response = redirect(url_for('u_login'))
        error_msg = 'Password incorrect. You get [] more tries.'
        response.set_cookie('error_msg', error_msg)

    else:
        html = redirect(url_for('u_butteries'))

        response = make_response(html)
        response.set_cookie('error_msg', '')

    response.set_cookie('username', username)  # apparently this is how to do this?
    response.set_cookie('password', password)

    global USERNAME
    global PASSWORD
    USERNAME = username
    PASSWORD = password

    return response

#-----------------------------------------------------------------------

@app.route('/u_butteries', methods=['GET'])  
def u_butteries():
    html = render_template('u_butteries.html')
    response = make_response(html)

    return response
#-----------------------------------------------------------------------

# ! should take in as argument which buttery, but we are just doing DPORT for now
@app.route('/u_get_buttery_menu', methods=['GET'])  
def u_get_buttery_menu():
    html = render_template('u_butteryMenu.html', menuItems=BUTTERY_MENU_DB["Davenport"])
    response = make_response(html)

    return response

#-----------------------------------------------------------------------

@app.route('/u_display_item', methods=['GET'])  # ! or should we make the link have the menu item ID
def u_display_item():
    menu_item = request.args.get('menu_item')
    html = render_template('u_menuItem.html', ingredients=MENU_ITEM_DB[menu_item],
                           menuItem=menu_item)
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------

@app.route('/u_ordersIP', methods=['GET'])  
def u_ordersIP():
    html = render_template('u_ordersIP.html', orders=ordersIP)
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------

@app.route('/u_cart', methods=['GET'])  
def u_cart():
    html = render_template('u_cart.html')
    response = make_response(html)
    
    return response

#-----------------------------------------------------------------------

@app.route('/u_account', methods=['GET'])  
def u_account():
    html = render_template('u_account.html', username=USERNAME)
    response = make_response(html)
    
    return response
