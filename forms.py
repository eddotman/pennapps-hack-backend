from flask import jsonify
from requests import post
from os import environ
from re import match, search
from json import loads, dumps
from fdfgen import forge_fdf
from subprocess import call
import formencode
import subprocess

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

    if search('\-\-\-\-', u_line):
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

def save_form_json(form, data):
  if form == 'fw10':
    fill_w10(form, data)
  else:
    with open('jsons/' + str(form) + '.json', 'wb') as f:
      f.write(dumps(data, indent=2, sort_keys=True))
  
  return True

def fill_w10(form, data):
  # print "data", data
  inputs = formencode.variabledecode.variable_decode(data)
  # print "inputs", inputs
  fields = populate_fields(form, inputs)
  # fields = [
  #   ('topmostSubform[0].Page1[0].p1-t1[0]', inputs['inputs[0][value]']),
  #   ('topmostSubform[0].Page1[0].p1-t2[0]', inputs['inputs[1][value]']),
  #   ('topmostSubform[0].Page1[0].p1-t3[0]', inputs['inputs[2][value]']),
  #   ('topmostSubform[0].Page1[0].p1-cb1[0]', inputs['inputs[3][value]']),
  #   ('topmostSubform[0].Page1[0].p1-t4[0]', inputs['inputs[4][value]']),
  #   ('topmostSubform[0].Page1[0].p1-t5[0]', inputs['inputs[5][value]']),
  # ]
  fdf = forge_fdf("",fields,[],[],[])
  fdf_file = open("data.fdf","wb")
  fdf_file.write(fdf)
  fdf_file.close()
  call(['pdftk pdfs/' + form + '.pdf fill_form data.fdf output pdfs/output.pdf flatten'], shell=True)


def populate_fields(pdfname, inputs):
  pdf_url = 'pdftk pdfs/' + pdfname +  '.pdf dump_data_fields'
  result = subprocess.check_output(pdf_url, shell=True)
  raw_output_groups = result.split('---')
  print raw_output_groups

  reference = {}
  fields = []

  for group in raw_output_groups:
    if len(group) > 1:
      if bool(group.index('FieldNameAlt') is not None) and bool(group.index('FieldName') is not None):
        temp_alt = group[group.index('FieldNameAlt: ')+14:]
        print "TEMP_ALT"
        print temp_alt
        fieldnamealt = temp_alt[:temp_alt.index('\nField')]
        print "FIELD_ALT"
        print fieldnamealt
        temp_name = group[group.index('FieldName: ')+11:]
        print "TEMPNAME"
        print temp_name
        fieldname = temp_name[:temp_name.index('\nField')]
        print "FIELDNAME"
        print fieldname
        reference[fieldnamealt] = fieldname
        print "REFERENCE"
        print reference


  print "REFERECE"
  print reference
  raw_output = result.split('\n')

  for line in raw_output:
    try:
      matched = bool(line.index('FieldNameAlt') is not None)
      if matched:
        fieldnamealt = line[line.index('FieldNameAlt: ')+14:]
        for key, value in inputs.items():
          if value in fieldnamealt or fieldnamealt in value:
            fields.append((reference[fieldnamealt], key))
            break
    except:
      pass



  # # i = 0

  
  # #line_type = None

  # for line in raw_output:
  #   try:
  #     fieldnamealt = line[line.index('FieldNameAlt: ')+14:]
  #     #line_type = 'field_name_alt'
  #     #for each key, check if fieldnamealt matches its value (decoded from unicode)
  #     #if it is, get its inputs[
  #     for key, value in inputs.items():
  #       if value in fieldnamealt or fieldnamealt in value:
  #         name_alt_sets.append((fieldnamalt, key))
  # for line in raw_output:
  #   try:
  #     matched =  bool(line.index('FieldName: ') is not None)
  #     if matched:
  #       #line_type = 'field_name'


  #   except:
  #     pass

    


    
  #   if(matched):
      

  #     new_set = (line[11:], inputs['inputs['+str(i)+'][value]'])
  #     fields.append(new_set)
  #     i += 1

  return fields


# request_form('f1120w15', 'en-ko')
# fill_w10('fw10_accessible', {
#   'inputs': [
#     {'value': 'test'},
#     {'value': 'test'},
#     {'value': 'test'},
#     {'value': 'test'},
#     {'value': 'test'},
#     {'value': 'test'}
#   ]
#   })
