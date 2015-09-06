from flask import Flask, send_from_directory
from flask_restful import reqparse, request, abort, Api, Resource
from flask.ext.cors import CORS
from forms import (request_form, save_form_json, fill_w10)
import os
import json

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.route('/pdfs/<path:path>')
def pdfs(path):
    return send_from_directory('pdfs', path)

class Form(Resource):
  def get(self, form, lang):
    return request_form(form, lang)

  def post(self, form):
    form_data = json.loads(request.form)
    save_form_json(form, form_data)
    return 'SUCCESS:' + str(form_data)

api.add_resource(Form, '/<form>', '/<form>/<lang>')

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)