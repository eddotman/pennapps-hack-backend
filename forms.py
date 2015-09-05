from spacy.en import English
from flask import jsonify

nlp = English()

def request_form(form): 
  txtform = None
  with open('txt/' + form + '.txt', 'rb') as f:
    txtform = f.read()

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

  u_txtform = unicode(str(txtform).decode('latin_1'))
  tokens = nlp(u_txtform)
  
  #this check should be last
  fill_verbs = set(['enter', 'fill', 'provide', 'list'])
  verbs = [t for t in tokens if (t.pos_ == 'VERB' and str(t.orth_).lower() in fill_verbs)]
  
  actions = []
  for verb in verbs:
    action = ' '.join([t.orth_ for t in verb.subtree])
    action = action.replace(u"\u2018", "").replace(u"\u2019", "").replace(u"\u201c","").replace(u"\u201d", "").replace(u"\u2014", "-")

    if len(list(verb.subtree)) > 1:
      actions.append(action)

  for action in actions:
    new_input = {
      "type": "text",
      "name": action,
      "value": None,
      "coordinates": [None, None]
    }
    ret_doc['inputs'].append(new_input)

  return jsonify(ret_doc)