# Firebase Integration


With this guide, you will learn how to create a project in Firebase and link it to the PriceHunter script


### 1. Login to firebase platform
Go to [firebase platform](https://firebase.google.com/) site and log in.

### 2. Create new project
- in the right upper corner click on ```Go to console```
- click ```Add project```
- enter a name for your project
- then you will be asked about Google Analytics - leave it as enable
- click create project

### 3. Generate firebase private key
When you already have created project next step is to generate your own private key.

- in the upper left corner find gear icon, click it and select project settings
  ![1](https://user-images.githubusercontent.com/64009728/107626354-f4d09200-6c5d-11eb-916b-4c9f0d76fcaa.png)
- then select a bookmark ```Service accounts```
  ![2](https://user-images.githubusercontent.com/64009728/107626419-0c0f7f80-6c5e-11eb-997c-fd72aea6edb2.png)

- click ```Generate new private key```
- your downloaded key put to the same folder as ```main.py``` file
- change name of downloaded file to ```firebase_config.json```

### 4. Create realtime-database 
Now it's time to create realtime-database on the firebase platform

- open your project site
- on the left site in build tab click ```Realtime Database``` and ```Create Database```
- select location
- select ```Start in test mode```
- enter to realtime database tab
  - copy url to your database (you will need it later)
![3](https://user-images.githubusercontent.com/64009728/107626456-19c50500-6c5e-11eb-9cc7-eed04edfd662.png)  
- select rules ant set it to:
  ```
  {
    "rules": {
      ".read": "true",  
      ".write": "true",
    }
  }
  ```
  ![4](https://user-images.githubusercontent.com/64009728/107626589-5264de80-6c5e-11eb-99b8-a405adca9f98.png)
  - you will get many notification that this rules are insecure, if u are only one who will be using it, its fine
    - if u want to disable this notification:\
      Click bell icon in the upper-right corner of the Firebase console.
Choose the project for which you want to disable alerts.
  

_if you want to set your own secure rules, u can read more about it [here](https://firebase.google.com/docs/rules)_

### 5. Set config values
The last step is to set config to use the created key

- open ```main.py``` with your favorite text editor
- find ```FIREBASE_INTEGRATION``` and change ```False``` to ```True```
- find ```FIREBASE_DATABASE_URL``` and change url to yours (you copy this url in step 4)

_Now PriceHunter is connected to firebase, run it and check if new records appears in your realtime-database_

### 6. Mobile App
It is possible to use [Android app](https://github.com/Rejfin/PriceHunter_Android) to see a list of your products and get notification about lower than usual price

- [download](https://github.com/Rejfin/PriceHunter_Android/releases/download/v1.0/PriceHunter.apk) Android app and install it
- generate config file adapted to mobile applications (it differs from the key used for the python script)
    - go to your firebase project website
    - in the upper left corner find gear icon, click it and select project settings
    - then select a bookmark ```General```
    - at section ```Your apps``` click ```Add app``` and select android OS
    - in the field ```Android package name``` type ```com.rejfin.pricehunter``` and click register app
    - click ```download google-service.json``` button, and save downloaded file in your phone
    - go to the next step several times until the registration of the application is completed
    - if the application has been registered correctly, it will appear in the project site at section ```Your apps``` (the place where we started)

#### Now edit PriceHunter script config value
- open ```main.py``` with your favorite text editor
- find ```FIREBASE_REMOTE_CONTROL``` and change ```False``` to ```True```
- find ```FCM_ENABLED``` and change ```False``` to ```True```
- find ```FIREBASE_SEND_LAST``` and change ```False``` to ```True```
- now PriceHunter is ready to work with the mobile app