from flask import Flask
from forms import (request_form)
import os

app = Flask(__name__)

@app.route('/<form>')
def app_request_form(form):
  return request_form(form)

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)