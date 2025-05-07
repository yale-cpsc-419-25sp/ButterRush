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
- EXTRA FEATURE: allow buttery to edit opening times 

Alpha Figma Wireframe: https://www.figma.com/design/uW76eWa8seOk0Rx3qsZXxy/ButterRush-Mockup?node-id=706-2&t=QNjWS0G9IW2NYc2R-1  

## What we’ve implemented (Beta): 
- Improved and more consistent UI using boostrap
- Added navbar to buttery side
- Implemented login sessions 
- Bug fixes: email, order queue
- Feature that allows butteries to mark ingredients as in or out of stock 

## What we’ve implemented (Final): 
- Improved and consistent UI through all parts of app
- Finishing touches, handling edge cases, and last minute bugs
Extra: 
- Hashing passwords
- Logo Creation
- Application hosted online via pythonanywhere.com

Final Project Presentation Slides: https://docs.google.com/presentation/d/1wnze7YMh7VBBpY97fzZGxTK5KZnztZYfot0HKYbvXh8/edit?usp=sharing 

## Implementation Instructions: 

ButterRush is hosted (https://butterrushyale.pythonanywhere.com/), but you can find instructions to run the application locally below: 

To run ButterRush locally, do `pip install -r requirements.txt`. 
Then, delete the current database if it is present (which would be named `butterrush.db`) and run `python init_db.py` to initalize the database.
Then, `python runserver.py [a valid port number]`.

Example Buttery Login: 
username: “Davenport” 
password: “temp_password”

Example User Login: 
username: “ayak” 
password: “12345678”
*NOTE: You may have to first create an account in order to login as a user.*

Issues to Address/Implement in the Future: 
- Implement an opt-in leaderboard to rank users with the most orders
- Updating tech stack for a more scalable application, as well as expanding to mobile
- Prevent user access to ordering outside of buttery hours
- Updating menus to reflect the unique menus of each residential buttery
- Switching from email notifications to text messaging!