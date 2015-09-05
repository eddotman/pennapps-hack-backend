from flask import jsonify
from requests import post
from os import environ
from re import match, search
from json import loads

def request_form(form, lang): 
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
  refs = []

  for line in txtform:
    u_line = unicode(str(line).decode('latin_1').replace(u"\u2018", "").replace(u"\u2019", "").replace(u"\u201c","").replace(u"\u201d", "").replace(u"\u2014", "-"))

    if search('^([a-zA-Z]|\d)\.', u_line):
      if search('(\$|\%|[aA]dd|[sS]ubtract|[mM]ultiply|[iI]ncome|[sS]alary|[wW]ages|[dD]ivid(e|end)|[iI]nterest|less|more|equal)', u_line):
        f_types.append('currency')
      elif search('\[*\]', u_line):
        f_types.append('checkbox')
      else:
        f_types.append('text')
      
      if search('\:', u_line):
        u_line = u_line[:u_line.index(":")+1]

      if search('^\d+\.\s*', u_line[:3]):
        refs.append(u_line[:3])
        u_line = u_line[3:]
      else:
        refs.append(None)

      f_inputs.append(u_line)


  translated_inputs = translate_text(f_inputs, lang)
  
  for f_input, f_type, ref in zip(translated_inputs, f_types, refs):
    new_input = {
      "type": f_type,
      "name": f_input,
      "ref": ref,
      "value": None,
      "coordinates": [None, None]
    }
    ret_doc['inputs'].append(new_input)

  return jsonify(ret_doc)


def translate_text(text, lang):
  data = {
    'key': environ.get('YANDEX_API'), 
    'lang': lang,
    'text': text
  }
  r = post('https://translate.yandex.net/api/v1.5/tr.json/translate', data=data)
  return loads(r.text)['text']

# request_form('f1120w15', 'en-ko')