from flask import Flask
from flask_restful import reqparse, request, abort, Api, Resource
from flask.ext.cors import CORS
from forms import (request_form, save_form_json)
import os

app = Flask(__name__)
CORS(app)
api = Api(app)

class Form(Resource):
  def get(self, form, lang):
    return request_form(form, lang)

  def put(self, form):
    form_data = request.form['data']
    save_form_json(form, form_data)
    return 'Success!'

api.add_resource(Form, '/<form>', '/<form>/<lang>')

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)