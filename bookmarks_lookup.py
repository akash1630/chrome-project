import os
import json
import io
import pprint as pp

fname = './.config/google-chrome/Default/Bookmarks'
name_url_map = {}
bkmarklets_count = 0
bookmarklets_url_map = {}
bookmarklets_id_map = {}
is_changed = 0

fo = io.open(fname, 'r+b')

def print_parse_results():
  print("Total number of bookmarklets : ", bkmarklets_count)
 
  for key in bookmarklets_url_map.keys():
    print(key + " has a javascript bookmarklet")
    print("Javascript content  :   "+ bookmarklets_url_map[key])

  for key in bookmarklets_id_map.keys():
    print(" id name mapping  -  " + key + " : " + bookmarklets_id_map[key])



def traverse_children(node):
  global bkmarklets_count
  global is_changed
  #pp.pprint(node1)
  #node = node1.json()
  #pp.pprint(node)
  if isinstance(node, dict):
    children = node.get("children")
  else:
    children = node
  for child in children:
    if child.has_key("url"):
      if child["url"].find("javascript:(function()") >= 0:
        bkmarklets_count = bkmarklets_count + 1
        bookmarklets_url_map[child["name"]] = child["url"]
        bookmarklets_id_map[child["id"]] = child["name"]
	child["url"] = "javascript:(function(){alert(\"You are trying to run external scripts on this page which can lead to security issues and is not allowed by policy\");})();"
	is_changed = 1
    if child.has_key("children"):
      traverse_children(child["children"])
  print_parse_results()
  return  

with fo as data_file:
  try:
    read_json = json.load(data_file)
  except:
    print(" *** Error reading json. Invalid JSON input")
    quit()
  roots = read_json["roots"]
  if roots.has_key("bookmark_bar"):
    bkm_bar = roots["bookmark_bar"]
    traverse_children(bkm_bar)
  if roots.has_key("other"):
    other = roots["other"]
    traverse_children(other)
  if is_changed == 1:
    print "******rewriting the Bookmarks configuration file ****"
    fo.seek(0)
    json.dump(read_json, fo)
    fo.truncate()


