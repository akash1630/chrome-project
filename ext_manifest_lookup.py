import os
import json
import io
import sys

from pprint import pprint

file_to_check = ''

if len(sys.argv) > 1:
  print("arguments passed" + str(sys.argv))
  file_to_check = str(sys.argv[1])

rootdir = './.config/google-chrome/Default/Extensions'
dir1 = './.config/google-chrome/'

name_path_map = {}
name_cs_map = {}
name_url_match_map = {}
changed = 0
restricted_permissions = ["webRequest", "webRequestBlocking", "cookies", "background"]
native_chrome_ext = []
sensitive_domains = ["https://mail.google.com", "https://*.citi.com", "https://github.com"]

def process_permissions(permissions):
  for perm in restricted_permissions:
    if perm in permissions:
      permissions.remove(perm)
  return permissions

def process_excludes(vals):
  for pattern in sensitive_domains:
    if pattern not in vals:
      vals.append(pattern)
  return vals

def file_traverse(fo, with_arg):
  global changed
  with fo as data_file:
    try:
      read_json_file = json.load(data_file)
    except:
      print("error loading json. Invalid JSON. skipping")
      return
    name = read_json_file["name"]
    if with_arg == 0:
      name_path_map[name] = os.path.join(subdir, file)
    if read_json_file.has_key("content_scripts"):
      name_cs_map[name] = read_json_file["content_scripts"]
      #print os.path.join(subdir, file)
      print "Content_scripts found. Searching for URL match patterns..... "
      for i in read_json_file["content_scripts"]:
        #print read_json_file["content_scripts"][i]
        add_exclude = 0
        print i["matches"]
        for j in i["matches"]:
          if j.find("http://*/*") >= 0 or j.find("https://*/*") >= 0:
            name_url_match_map[name] = i["matches"] 
            add_exclude = 1

        if add_exclude == 1:         
          if i.has_key("exclude_matches"):
            vals = i["exclude_matches"]
            i["exclude_matches"] = process_excludes(vals)
          else:
            i["exclude_matches"] = sensitive_domains
            changed = 1

    if read_json_file.has_key("permissions"):
      print("**** sanitizing permissions ****")
      permissions = read_json_file["permissions"]
      read_json_file["permissions"] = process_permissions(permissions)
      changed = 1

    if read_json_file.has_key("background"):
      print("*** removing background scripts ***")
      read_json_file["background"] = {}
      changed = 1

    if changed == 1:
      print "******rewriting the manifest file ****"
      fo.seek(0)
      json.dump(read_json_file, fo)
      fo.truncate()

if file_to_check == '':
  for subdir, dirs, files in os.walk(rootdir):
    for file in files:
      #print os.path.join(subdir, file)
      if file.find('manifest.json') >= 0 and not (file.find('.json.')) >= 0:
        fo = io.open(os.path.join(subdir,file), 'r+b')
        print os.path.join(subdir, file)
        file_traverse(fo, 0)
else:
  fo = io.open(file_to_check, 'r+b')
  file_traverse(fo, 1)   


for key in name_cs_map.keys():
  print key + " had content scripts enabled"

for key in name_url_match_map.keys():
  print key + " applied to all domains. exclude patterns added now to it"

