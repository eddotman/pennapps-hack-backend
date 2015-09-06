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
  print "FIELDS"
  print fields
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
  # print raw_output_groups

  reference = {}
  fields = []

  for group in raw_output_groups:
    # print "------"
    # print "GROUP"
    # print group
    if len(group) > 1:
      if 'FieldNameAlt' in group and 'FieldName' in group:
        temp_alt = group[group.index('FieldNameAlt: ')+14:]
        # print "TEMP_ALT"
        # print temp_alt
        fieldnamealt = temp_alt[:temp_alt.index('\nField')]
        # print "FIELD_ALT"
        # print fieldnamealt
        temp_name = group[group.index('FieldName: ')+11:]
        # print "TEMPNAME"
        # print temp_name
        fieldname = temp_name[:temp_name.index('\nField')]
        # print "FIELDNAME"
        # print fieldname
        reference[fieldnamealt] = fieldname
        # print "REFERENCE"
        # print reference

  # print "INPUTS"
  # print inputs
  raw_output = result.split('\n')
  print "RAW_OUTPUT"
  print raw_output
  print "-----------------------"

  print "IOASNDLK"
  print inputs.keys()

  for line in raw_output:
    if 'FieldNameAlt' in line:
        fieldnamealt = line[line.index('FieldNameAlt: ')+14:]
        

        for key in inputs.keys():
          if "[name]" in key:
            # print "----------------------------------"
            # print "FIELDNAMEALT"
            # print fieldnamealt

            # print "KEY"
            # print key

            value = inputs[key]
            # print "VALUE"
            # print value

            key_num = key[7:9]
            # print "KEYNUM"
            # print key_num
            if key_num[1] == ']':
              key_num = key_num[0]

            val_first_word = value.split(" ")[0]
            # print "VAL FISRT"
            # print val_first_word

            # print "TEIDSAJL"
            # print val_first_word in fieldnamealt

            if val_first_word in fieldnamealt:
              fields.append((reference[fieldnamealt], inputs['inputs['+str(key_num)+'][value]']))
              print "Success!"
              continue

            
              

          
  print "FIELDS"
  print fields
  
  return fields
