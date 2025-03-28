# Butterrush
Sophia Zhou, Aya Kasim, Sivan Almogy, Sebastian Orozco, Emma Slagle

## Project Description:

Our web app ButterRush, allows individuals to order ahead from the Yale buttery locations and receive a notification when their order is ready for pick-up. Our application is composed of both a user side and a buttery side. Users are able to create an account, can browse buttery menus, add menu items to cart, place orders, see the status of their order (if ready for pick-up), and log out. On the buttery side, buttery workers can log-into their buttery account, can edit their buttery menu, see their order queue from customers, mark orders as ready for pick-up, and log out. When a user’s order is ready for pick-up, users make their way to the respective buttery to pay there. 

## What we’ve implemented: 

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

## Implementation Instructions: 

To run ButterRush, do `pip install -r requirements.txt`. Then, `flask run`.

Example Buttery Login: 
username: “Davenport” 
password: “temp_password”

Example User Login: 
username: “ayak” 
password: “12345678”

Issues to Address/Implement in the Future: 

- Notification (through email or messages) for buttery order pick-up
- Multiple orders (multiple separate orders of the same item?)
