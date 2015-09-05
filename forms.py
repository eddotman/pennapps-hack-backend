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
  f_types = []

  for line in txtform:
    u_line = unicode(str(line).decode('latin_1').replace(u"\u2018", "").replace(u"\u2019", "").replace(u"\u201c","").replace(u"\u201d", "").replace(u"\u2014", "-"))

    if search('^([a-zA-Z]|\d)\.', u_line) is not None:
      if search('(\$|\%|[aA]dd|[sS]ubtract|[mM]ultiply|[iI]ncome|[sS]alary|[wW]ages|[dD]ivid(e|end)|[iI]nterest|less|more|equal)', u_line) is not None:
        f_types.append('currency')
      elif search('\[*\]', u_line) is not None:
        f_types.append('checkbox')
      else:
        f_types.append('text')
      
      if search('\:', u_line) is not None:
        u_line = u_line[:u_line.index(":")+1]
      
      f_inputs.append(u_line)

  
  for f_input, f_type in zip(f_inputs, f_types):
    new_input = {
      "type": f_type,
      "name": f_input,
      "value": None,
      "coordinates": [None, None]
    }
    ret_doc['inputs'].append(new_input)

  return jsonify(ret_doc)