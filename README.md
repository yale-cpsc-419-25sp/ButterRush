# Butterrush
Sophia Zhou, Aya Kasim, Sivan Almogy, Sebastian Orozco, Emma Slagle

## Project Description:

Our web app ButterRush, allows individuals to order ahead from the Yale buttery locations and receive a notification when their order is ready for pick-up. Our application is composed of both a user side and a buttery side. Users are able to create an account, can browse buttery menus, add menu items to cart, place orders, see the status of their order (if ready for pick-up), and log out. On the buttery side, buttery workers can log-into their buttery account, can edit their buttery menu, see their order queue from customers, mark orders as ready for pick-up, and log out. When a user’s order is ready for pick-up, users make their way to the respective buttery to pay there. 

## What we’ve implemented (MVP): 

- Simple User UI: Butteries, Orders In Progress, Cart, Account
- Order items off of a fixed menu + optional descriptional notes for each menu item
- Simple Buttery UI: My Buttery, Order Queue, Account
- User creates account
- Butteries able to log into their Buttery account
- User submits single-item order(s) (payment in-person when picking up food)
- User UI shows orders(s) in progress
- Buttery worker receives order which is put into order queue
- Buttery worker checks off order when done, and order status on User side changes to ready (for pick-up)
- Buttery worker acknowledges that user received their food which deletes order from queue & user orders in progress
- Techstack used: Flask, SQLite

MVP Figma Wireframe: https://www.figma.com/design/LjKQgS0H2t7sxeloq0wsxY/Butterrush-Wireframe-MVP-v0?m=auto&t=9HOD9R9hE286vW7k-6 

## What we’ve implemented (Alpha): 
- Buttery menus can be edited by buttery workers
- User can submit multi-item order(s)
- Users can add items to / delete from a cart before ordering
- Buttery workers can mark an order as “in progress” or “done”*, shows on user page and notifies them through email
- EXTRA FEATURE: allow buttery to edit opening times – maybe this should be limited to within regular hours?

Alpha Figma Wireframe: https://www.figma.com/design/uW76eWa8seOk0Rx3qsZXxy/ButterRush-Mockup?node-id=706-2&t=QNjWS0G9IW2NYc2R-1  

## Implementation Instructions: 

*NOTE: This is optional, but in order to send emails you must set `MAIL_USERNAME` and `MAIL_PASSWORD` in your terminal. This requires setting up an app password to login to your email account. To do this, please follow the instructions from your email service provider (likely found within the "Security" section of your email account settings). After accomplishing this, please run `export MAIL_USERNAME="[your_email]"` and `export MAIL_PASSWORD="[your_email_app_password]"` to set the necessary environment variables. In the future, we will use a standard ButterRush address from which to send emails, so this is a temporary solution.*

To run ButterRush, do `pip install -r requirements.txt`. 
Then, delete the current database if it is present (which would be named `butterrush.db`) and run `python3 init_db.py` to initalize the database.
Then, `flask run`.


Example Buttery Login: 
username: “Davenport” 
password: “temp_password”

Example User Login: 
username: “ayak” 
password: “12345678”
*NOTE: You may have to first create an account in order to login as a student.*

Changing opening hours is a feature available in the Account tab on the buttery side

Issues to Address/Implement in the Future: 

- Somewhere along our branch merging, the funtionality of the Buttery Order queue broke. Currently, when the buttery marks an item as Ready, the order disapears from the queue rather than remain on the queue with a "Mark as Picked Up" option. We will fix this in the next version!
