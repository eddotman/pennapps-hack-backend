from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from forms import (request_form)
import os

app = Flask(__name__)
api = Api(app)

class Form(Resource):
  def get(self, form, lang):
    return request_form(form, lang)

api.add_resource(Form, '/<form>/<lang>')

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)