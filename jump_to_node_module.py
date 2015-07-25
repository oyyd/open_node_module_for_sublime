import sublime, sublime_plugin
import re, json
from os import path

# NOTE: do not support dynamic requiring

# TODO: is the json handler correct?
# TODO: check comments syntax
# TODO: if more than one sentence ...
path_reg = re.compile('require\([\"\'](.*)[\"\']\)')

def alert_file_not_found():
  sublime.error_message('Node module not found.')

def try_directory_module(possible_dir):
  if not path.isdir(possible_dir):
    return None

  main_file = 'index'
  package_path = path.join(possible_dir, 'package.json')
  if path.isfile(package_path):
    try:
      with open(package_path) as content:
        data = json.load(content)
        main_file = data['main']
    except:
      pass
  try_file = path.join(possible_dir, main_file)
  return try_ext(try_file)

# trail_path = ['index.js']
# def try_file(dir_path):
#   for trial in trail_path:
#     try_path = path.join(dir_path, trial)
#     print(try_path)
#     if(path.isfile(try_path)):
#       return  try_path
#   return None

trial_ext = ['js', 'json']
def try_ext(dir_path):
  dot_index = None
  try:
    dot_index = dir_path.rindex('.')
  except:
    pass

  if dot_index != None:
    if path.isfile(dir_path):
      return dir_path
    else:
      return None

  for ext in trial_ext:
    try_path = dir_path + '.' + ext
    if path.isfile(try_path):
      return try_path
  return None

def walk_node_modules(current_file_name, require_text):
  current_dir = current_file_name[:current_file_name.rindex('/')]
  while current_dir != '':
    possible_dir = path.join(current_dir, 'node_modules', require_text)
    possible_file = try_directory_module(possible_dir)
    # possible_file = try_file(possible_dir)
    if possible_file:
      return possible_file
    current_dir = current_dir[:current_dir.rindex('/')]

  # try global module
  return None

def get_file_path(current_file_name, require_text):
  # TODO: also consider json, jsx, es ...
  # TODO: package json extension
  if require_text[0] == '.':
    file_path = path.realpath(path.join(current_file_name, '../', require_text))
  # TODO: window '\'
  # TODO: test absolute
  elif require_text[0] == '/':
    file_path = path.realpath(require_text)

  return try_ext(file_path)

class OpenRequiredFileCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    window = sublime.active_window()
    view = window.active_view()
    current_file_name = view.file_name()

    line = view.line(view.sel()[0])
    line_text = view.substr(line)
    require_text = re.search(path_reg, line_text).group(1)
    if require_text == None:
      alert_file_not_found()
      return

    file_path = None
    if require_text[0] == '.' or require_text[0] == '/':
      # relative path or absolute path
      file_path = get_file_path(current_file_name, require_text)
    else:
      # core module or node_modules
      file_path = walk_node_modules(current_file_name, require_text)

    if file_path:
      window.open_file(file_path)
    else:
      alert_file_not_found()
