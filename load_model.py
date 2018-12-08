from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from flask import Flask
from flask import request, render_template, flash
from flask import render_template
import io


app = Flask(__name__)


## Parse coordinate 



@app.route('/parse-coordinate', methods=['POST', 'GET'])
def show_user_profile():

    if request.method == 'POST':

    # checar si hay que parsear el request a texto

      coordinates = request.form['location']
      #coord2 = coordinates.replace("(","")
      #coord3 = coord2.replace(")","")
      #coord4 = coord3.replace(".","")
      #coord5 = coord4.replace(",","")
      #coord6 = coord5.replace(" ","")
      #url = "https://maps.googleapis.com/maps/api/staticmap?center=" + coord3 + "&zoom=18&size=600x300&maptype=satellite&format=jpg&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318&markers=color:red%7Clabel:C%7C40.718217,-73.998284&key=AIzaSyAEzAp00zKY3XiNRTBaNKaUz9k-_9caWLw"

      #image_location = "/Users/rodolfoocampo/Documents/Datalab/Proyectos/tensorflow-for-poets-2/real_images/" + coord6 + ".jpg"
      #urllib.urlretrieve(url, image_location)
      print(coordinates)
      output = coordinates
      resp = flask.Response(output)
      resp.headers['Access-Control-Allow-Origin'] = '*'
      return resp
    return

@app.route('/model?coordinate=<biz_code>')
def hello_world(biz_code):
	model = Word2Vec.load("word2vec.model")
	prediction = model.predict_output_word([str(biz_code)])
	print(prediction)
	return (str(prediction))





@app.route('/')

def hello(name=None):
    return render_template('form.html', name=name)





