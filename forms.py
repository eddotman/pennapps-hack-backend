from flask import jsonify
from re import match, search

def request_form(form): 
  txtform = None
  with open('txt/' + form + '.txt', 'rb') as f:
    txtform = f.readlines()

  if txtform is None: return 1

  ret_doc = {
    "instructions": "",
    "inputs": [
      # {
      #   "type": "checkbox|text|textarea|radio|date|address|signature",
      #   "name": "text",
      #   "value": "text | boolean | number",
      #   "coordinates": ["float", "float"]
      # }
    ]
  }

  f_inputs = []

  for line in txtform:
    u_line = unicode(str(line).decode('latin_1').replace(u"\u2018", "").replace(u"\u2019", "").replace(u"\u201c","").replace(u"\u201d", "").replace(u"\u2014", "-"))

    if search('^([a-zA-Z]|\d)\.', u_line) is not None:
      f_inputs.append(u_line)
  
  for f_input in f_inputs:
    new_input = {
      "type": "text",
      "name": f_input,
      "value": None,
      "coordinates": [None, None]
    }
    ret_doc['inputs'].append(new_input)

  return jsonify(ret_doc)