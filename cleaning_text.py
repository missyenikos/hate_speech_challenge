from flask import Flask,jsonify,request
import pandas as pd
import string
import re
import sqlite3
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

app = Flask(__name__)
DB_NAME = "binar.db" #this called CONSTANTS
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
info = {
    'title': LazyString(lambda: 'cleansing text'),
    'version': LazyString(lambda: '1'),
    'description': LazyString(lambda: 'api swagger for cleansing text'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


def remove_emoji_csv (data):
    return re.sub(r"\\x[A-Za-z0-9./]+"," ",data)

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

def remove_enter(data):
    return data.replace('\\n',' ')

def insert_db1(dirty_text,clean_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tweet (dirty_text,clean_text) values (?,?)",(dirty_text,clean_text))
    conn.commit()
    conn.close()

def insert_db2(df):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql('tweet_csv_1',con = conn,index =False, if_exists = 'append')
    conn.close()

@swag_from("swagger_config_post.yml", methods=['POST'])
@app.route('/clean_body/v1',methods = ['POST'])

def clean_tweet():
    s = request.get_json()
    s = s['text']
    clean_tweet = remove_emojis(s)
    clean_tweet = remove_punc(clean_tweet)
    clean_tweet = clean_new_line_and_spaces(clean_tweet)
    insert_db1(s,clean_tweet)
    return jsonify({"clean_version" : clean_tweet})


@swag_from("swagger_config_file.yml", methods=['POST'])
@app.route('/clean_file/v1',methods = ['POST'])
def post_csv():
    f = request.files['file']
    df = pd.read_csv(f,encoding = "latin")
    df['clean_tweet'] = df.Tweet.apply(remove_emoji_csv)
    df['clean_tweet'] = df.Tweet.apply(remove_enter)
    df['clean_tweet'] = df.Tweet.apply(remove_punc)
    insert_db2(df)
    return jsonify({"clean_version" : 'success'})

if __name__ == "__main__":
    app.run(debug = True,port = 1234)
