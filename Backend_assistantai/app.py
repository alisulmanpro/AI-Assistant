from flask import Flask
from flask_cors import CORS
from utils import *
from flask import request
import traceback
import wget
import os
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods = ['POST'])
def get_response():
    try:
        conf = 0.55
        print("Request object prediction=======>\n", request.json)

        if request.json["audio"]:
            conf = 0.8
            try:
                url = request.json["audio"]
            except Exception as e:
                url = "" 

            if not os.path.exists("Audio"):
                os.mkdir("Audio")

            message = convert_audio_to_text(url)
        else:
            try:
                message = request.json["message"]
            except Exception as e:
                message = ""

        try:
            language = request.json["language"]
            language = language.capitalize()
        except:
            language = ""

        try:
            bot_name = request.json["bot_name"]
        except:
            bot_name = ""
        
        res, sentiments = chatbot_response(conf, message, language, bot_name)
            
        return {"message": res, "error": False, "sentiments": sentiments}
    except Exception as e:
        print(traceback.format_exc())
        return {"message": "Oops! Couldn't get that, am a new bot in town and learning with time. You can try rephrasing your question!", "error": True, "sentiments": "Neutral"}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5600, debug=True)
