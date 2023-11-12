# Social Connections Website

#### General idea of the project:

The General idea of this project is to create a dating website for open realationships but by creating such a website i created a normal dating website and as a feture it had the main idea of a couple being able to search for another male/female to join their couple and vise versa.

## Templates:

### Apology.html

Here i used your method of apology you gave us in the finance exercise but i changed the image into a funnier one.

### FirstRegister.html

This is the first thing you see after you register (Create a valid account) in this template you are forced to enter a nickname (The name the other users will see), what type of gender are you or if you are a couple , your age and if you are a couple its reccomended to put the oldest one and finaly what you are looking for male/female/couple. Also the user has the option to enter a image for themselfs but if they dont their profile pic gets set to the defualt one named "none.jpg" which is stored in the static folder.

### FirstLiking.html

As soon as you finish with the "FirstRegister.html" page you press a button named continue and it promts you here. This template shows you all the available likings in the app. Using javascript once the user clicks one or more of the likings they will change color so they know which one they selected, also they must at least select 3 different likings or else they will get a alert error which will tell them to selected 3 or more likings. At the bottom of the template will be a button called Create Profile and that will finaly create their profile and uploading it into our FireStore database.

### Index.html

This is the main page where you will see on the navbar the logo of the app and all the things you can access on the app which are Swipe, Profile, Message and i will explain each one latter on. Also in this template you will see a welcoming message with your nickname , a table which will show the Updates/Maintenence Logs (Which is used only for a example purpuse since the app is not going to get published any time soon.) and on the bottom of the template a Contact us table containing the companys email and a About us table which is a small descripiton for the user to know about.

### Login.html

A basic login template which checks if everything is correct and if yes allows the user to login to their account

### Messages.html

This template uses the FireStore database to display the users like the session user and which the session user liked back, if so the critirias are met then the profile picture of the user which their nickname, the session user is able to press on which user they wish to chat with and when the user will be pressed the chat will appear with their past messages (if they had any) the chat is supported by the Firebase realtime database.

### Profile.html

This template will access all the users information from the FireStore database and will display their profile picture, nickname, gender, looking for, age and likings which they are able to change anything they want from there if they want to, also their likings will be displayed with a blue color and the other of the likings where they didnt select before will be displayed in a grey color so the users knows what they had selected in the past.

### Register.html

This is a default register page where the user will input his username, password and again confirm the password. An error will be displayed if the user enters a username that was already registered in the database or if his/her password dosnt match the confirm password.

### Swiping.html

This page displayes to the user all the possible matches for him with a null values in 'users_option' (which means he still hasnt viewed them) and the user can eigther press accept or decline an a corresponding value will be passed to the databases 'users_option' value to be able to understand if the user liked or didnt like the other user.

## Routes:

### "/"

This is the main page getting displayed and it checks if theres a user session active and if not it will render the "idex.html" if there is a user session active it will check if the users profile and likings exist and something dosnt exist it will render the "FirstRegister.html" or "firstLikings.html" correspondingly. Finally if everything it check is correct it will render the home page when you log in.

### "/login"

This Checks if the user didnt leave anything blank and if the username and password is correct and if everything is correct the users id will be connected to the session["user_id"] value and then the user will be redirected to the "/" route.

### "/register"

Firstly we clear the previous session so we can store new values, next we check for any error the user can do and if the usernamer the user has entered hasnt been used already and we check if the password matches the confirmation password. If everything is correct the users info gets stored into the FireStore database, also the session["user_id"] gets the users id   and then the user get redirected to "/".

### "/profile"

This route gets the users information and displayes it so the user is able to change it if needed.

### "/upload_info"

This route firstly checks if the user has left behind any important information and if yes it will render the apology template, next it checks if the users age is valid and also if it checks if the user has a folder of his in the programs data and if not it creates one (so the user can later on place his profile picture), next it checks if the user has inputed a picture and if yes it places it in the folder we created previously and save the location in a value names file_path so we can access it later on also it checks if the usrProfile exist and if not it creates one, finaly the user gets redirected to the home page.

### "/logout"

This route simply clears all the session data and then redirects the user to the "/" route.

### "/firstLikings"

This route will show the user all the possible likings that are availble by rendering the template "firstLikings.html" and passing the likings array so it can be displayed in the html.

### "/likings"

This route gets passed all the likings the users has selected and checks if the user has selected at least 3 and if not he gets redirected again to "/firstLikings" so he can select again and if he selected at least 3 the likings get stored in the database.

### "/update_profile"

This route checks if all the values entered are valid and if yes it updates the FireStore database based on which values have changed.

### "/update_likings"

This route checks if the likings are 3 or more and if not a error pops and then gets redirected to "/profile" but if everythng is correct the code will update the users likings.

### "/swipe"

This route create and stores into a dictionary all the people with at least one common liking as the user and then renders and send the information to the "swiping.html" template.

### "/updateUserOption"

This route gets the a values from a html template which shows what the users option is for the specific other user and so the users option gets updated in the FireStore database.

### "/messages" and "/messages/<selected_user>"

This route checks which users have liked back the user of which the user likes too and if the match they get displayed in the "messages.html" template.

### "/send_message"

This route uses the function send_messages with some values that could be obtained by the "messages.html" template to be able to send a message (the message is getting stored in a realtime database).

### "/select_user"

This route is used to diplay in the "message.html" the correct chat of the user with the selceted user.
