from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from flask import Flask
from flask import request, render_template, flash
from flask import render_template


app = Flask(__name__)

@app.route('/<biz_code>')
def hello_world(biz_code):
	model = Word2Vec.load("word2vec.model")
	prediction = model.predict_output_word([str(biz_code)])
	print(prediction)
	return (str(prediction))





@app.route('/')

def hello(name=None):
    return render_template('hello.html', name=name)


