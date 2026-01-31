import os
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
import json
import pickle
import logging
import random
import numpy as np
from keras.models import load_model
from tinydb import TinyDB, Query
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
from gensim.parsing.preprocessing import remove_stopwords

import warnings
warnings.filterwarnings("ignore")

# import gtts
# import boto3
# import time
# import base64

# import speech_recognition as sr
# import librosa
# import soundfile as sf
from fuzzywuzzy import process
from pydub import AudioSegment
import glob
from gensim.parsing.preprocessing import remove_stopwords
from operator import itemgetter

# import openai

from flair.models import TextClassifier
from flair.data import Sentence
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
flair_sentiment = TextClassifier.load('sentiment-fast')

import sys
sys.path.append('google_trans_updated')
from google_trans_updated.constant import *
from google_trans_updated.google_trans_updated import google_translator

translator = google_translator()
db = TinyDB('wrong_answers_record.json')
count = Query()

logging.basicConfig(filename='./example.log', level=logging.DEBUG)
lemmatizer = WordNetLemmatizer()
dirname = os.path.dirname(__file__)

def clean_up_sentence(sentence):
    """
    Description:
    This function is used to tokenize and then lemmatize the sentence. With nltk.word_tokenize we are able to extract tokens
    from the string of characters. It actually returns the syllables from single word. Then lemmatizer.lemmatize is a process
    of grouping together the inflected forms of a word so they can be analysed as a single item.

    Input Parameters:
    sentence => Complete sentece sent by user.

    Output Parameters:
    sentence_words => list of lemmatized token of the sentence.
    """
    # extracting syllables from the string
    sentence_words = nltk.word_tokenize(sentence)
    # grouping together the inflected forms of a word in a single item.
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    """
    Description:
    This function basically returns a bag of words array. It contains 0 for each word which does not exists in the sentence
    and 1 for those words which exists in the sentence.

    Input Parameters:
    sentence => Complete sentece sent by user.
    words => bag of words of training data.
    show_details => a boolean parameter for logging.

    Output Parameters:
    bag => bag of words array.
    """
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model, words, classes):
    """
    Description:
    This function makes prediction based on the array of bag of words and filter out the results below a threshold. Then it
    sort the results and get the predicted class from the classes file.

    Input Parameters:
    sentence => Complete sentece sent by user.
    model => model that will predict the results.

    Output Parameters:
    return_list => a dictionary which contains the predicted class along with the probability.
    """
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.2
    results = [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    """
    Description:
    This functions get the response from the json file based on the predicted class.

    Input Parameters:
    ints => dictionary returned by predict_class function.
    intents_json => json file of dataset that contains the responses against the classes.

    Output Parameter:
    result => It is the answer for the question that user has asked.
    """
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def translate(string, lang_tgt='en'):
    """
    Description:
    This funtion is used for the translation of the questions and answers in the required language.

    Input Parameters:
    string => this is the text.
    lang_tgt => this is the target language in which string will be translated.

    Output Parameters:
    translate_text => translated text in the required language.
    """
    try:
        translate_text = translator.translate(string, lang_tgt=lang_tgt)
        return translate_text
    except:
        pass

def check_status(db_object, user_id, bot_id):
    smart_assign = False
    if db.contains(db_object.user_id == str(user_id) + "_" + str(bot_id)):
        user_count = db.get(db_object.user_id == str(user_id) + "_" + str(bot_id))
        if user_count['count'] < 3:
            db.update({'count': user_count['count'] + 1}, db_object.user_id == str(user_id) + "_" + str(bot_id))
        else:
            smart_assign = True
            db.remove(db_object.user_id == str(user_id) + "_" + str(bot_id))
    else:
        db.insert({"user_id":str(user_id) + "_" + str(bot_id), "count":1})
            
    return smart_assign

def get_sentiment_analysis(sentence):
    """
    This function is basically detect the emotions of person's message,
    either it is Positive or negative and returns True if it is Negative.

    Two Advanced pretrained techniques are used in this function.
    i- Flair sentiment analysis.
    ii- Vader sentiment analysis.
    """
    sentiments = 'POSITIVE'
    response = Sentence(sentence.lower())
    flair_sentiment.predict(response)
    total_sentiment = response.labels
    
    if total_sentiment[0].value == 'NEGATIVE' and total_sentiment[0].score > 0.7:
        sentiments = 'NEGATIVE'
        
    sid_obj = SentimentIntensityAnalyzer()
    sid_obj_score = sid_obj.polarity_scores(sentence.lower())
    if sid_obj_score['compound'] < 0.3 and sid_obj_score['neu'] != 1.0:
        sentiments = 'NEGATIVE'
        
    return sentiments

def chatbot_response(conf, msg, lang, bot_name):
    """
    This function is the main function which call all the above functions and get together the results. It basically take message
    and language as input and return the response of bot in the required language.

    Input Paramers:
    msg => The message sent by the user.
    lang => selected language by the user.

    Output Parameters:
    res => Response by the chatboot in selected language.
    """
    # Loaded the model file
    model = load_model(dirname + '/weights/' + str(bot_name) + '/model.h5')
    # This file contains all the dataset. It is used to get the response
    intents = json.loads(open(dirname + '/weights/' + str(bot_name) + '/data.json').read())
    # This file is bag of words for the model to predict
    words = pickle.load(open(dirname + '/weights/' + str(bot_name) + '/words.pkl','rb'))
    # This file contains all the classes of questions
    classes = pickle.load(open(dirname + '/weights/' + str(bot_name) + '/classes.pkl','rb'))
        
        
    logging.debug("selected_language=====>{}".format(lang))
    lang = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(lang.lower())]
    logging.debug("language_code=====>{}".format(lang))
    logging.debug("original_message=====>{}".format(msg))
    if lang != "en":
        msg = translate(msg)
        logging.debug("tranlated msg to english======>{}".format(msg))
    ints = predict_class(msg, model, words, classes)
    logging.debug("predictions=====>{}".format(ints))

    # This will return True or False according to the users sentiments.
    if ints[0]['intent'] != 'unknown' and float(ints[0]['probability']) < 0.7:
        sentiment_analysis = get_sentiment_analysis(msg)
        logging.debug("sentiment_analysis unknown probability=====>{}".format(sentiment_analysis))

    if float(ints[0]['probability']) < conf or len(ints) != 1:
        sentiment_analysis = get_sentiment_analysis(msg)
        if lang != "en":
            return translate("Oops! Couldn't get that, am a new bot in town and learning with time. You can try rephrasing your question!", lang), sentiment_analysis
        return "Oops! Couldn't get that, am a new bot in town and learning with time. You can try rephrasing your question!", sentiment_analysis
    sentiment_analysis = get_sentiment_analysis(msg)
    res = getResponse(ints, intents)
    if lang != "en":
        res = translate(res, lang)
    logging.debug("response=======>{}".format(res))
    return res, sentiment_analysis


##################################################   AUDIO TO TEXT   ##################################################

# def convert_audio_to_text(src):
#     try:
#         import pdb;pdb.set_trace()
#         _format = src.split('.')[-1]
#         sound = AudioSegment.from_file(src,  format= _format)
#         sound.export("Audio/file.wav", format="wav")
#         file_path = "Audio/file.wav"
#         x,_ = librosa.load(file_path, sr=16000)
#         sf.write(file_path, x, 16000)

#         r = sr.Recognizer()

#         with sr.AudioFile(file_path) as source:
#             audio_data = r.record(source)
#             text = r.recognize_google(audio_data)#, language='en-USA')
        
#         files = glob.glob('Audio/*')
#         for f in files:
#             os.remove(f)

#         return text
#     except:
#         return "Oops! Couldn't get that, am a new bot in town and learning with time. You can try rephrasing your question!"

