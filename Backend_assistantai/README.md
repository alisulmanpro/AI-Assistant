# invocom_chatbot
This is a simple chatbot trained on some specific questions based on Educational and Travel Questions. We have use __nltk__ a python library for natural language processing in our code. We have also give multilanguge support in our chatbot.

## Requirements
You need to install following packages to run this code:-
* nltk
* numpy
* pandas
* keras
* tensorflow
* Flask-Cors
* flask

You can simply run following command to install all these packages:-
```
pip install -r requirements.txt
```
## Run Demo
You can simply run following command to quickly run the service.
```
python demo.py --message hello --language es
```
Here you will send message for which you want chatbot to answer. And in language you will send the language code for the language. By default it is set to english.

## Run server
You can run flask server by simply running following command:-
```
python app.py
```
This will start the server and then you can you this as an API to send requests on it.

## Logs
After running the above commands and sending requests on the endpoints you will see a log file where you can see logs of the code.
