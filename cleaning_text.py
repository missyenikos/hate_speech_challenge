from flask import Flask,jsonify,request
import string
import re

app = Flask(__name__)


def remove_emojis(data):
    emoj = re.compile("["
        u"\U00002700-\U000027BF"  # Dingbats
        u"\U0001F600-\U0001F64F"  # Emoticons
        u"\U00002600-\U000026FF"  # Miscellaneous Symbols
        u"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols And Pictographs
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def remove_punc(data):
    return data.translate(str.maketrans('', '', string.punctuation))

def clean_new_line_and_spaces(data):
    return ' '.join(data.split())



@app.route('/clean_body/v1',methods = ['POST'])

def clean_tweet():
    s = request.get_json()
    s = s['text']
    clean_tweet = remove_emojis(s)
    clean_tweet = remove_punc(clean_tweet)
    clean_tweet = clean_new_line_and_spaces(clean_tweet)
    return jsonify({"clean_version" : clean_tweet})




if __name__ == "__main__":
    app.run(debug = True,port = 1234)
