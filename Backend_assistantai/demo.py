from utils import *
import traceback
import argparse



def run(message, language, bot_name):
    try:  
        res, sentiments = chatbot_response(message, language, bot_name)
        return {"message": res, "error": False, "sentiments": sentiments}
    except Exception as e:
        print(traceback.format_exc())
        return {"message": "Oops! Couldn't get that. You can try rephrasing your question.", "error": True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--message')
    parser.add_argument('--language', default='english')
    parser.add_argument('--bot_name', default='education_bot')
    args = parser.parse_args()
    result = run(args.message, args.language, args.bot_name)
    print(result)
