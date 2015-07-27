import sublime, sublime_plugin
import re, json
from os import path

# NOTE: static requiring

# TODO: core module and global module
# TODO: a more accurate `import` assertion
# TODO: check comments syntax
# TODO: if more than one sentence ...
path_regs = [
  re.compile('require\([\"\'](.*)[\"\']\)'),
  re.compile('import.*[\"\'](.*)[\"\']'),
  re.compile('from.*[\"\'](.*)[\"\']'),
]

def alert_file_not_found():
  sublime.error_message('File not found.')

def get_require_text(line_text):
  for reg in path_regs:
    result = re.search(reg, line_text)
    if result != None:
      return result.group(1)
  return None

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

trial_exts = ['js', 'json', 'jsx', 'es', 'es6']
def try_ext(dir_path):
  dot_index = None
  try:
    dot_index = dir_path.rindex('.')
  except:
    pass

  if dot_index != None:
    ext = dir_path[dot_index+1:]
    if ext in trial_exts and path.isfile(dir_path):
      return dir_path

  for ext in trial_exts:
    try_path = dir_path + '.' + ext
    if path.isfile(try_path):
      return try_path
  return None

def walk_node_modules(current_file_name, require_text):
  current_dir = current_file_name[:current_file_name.rindex('/')]
  while current_dir != '':
    possible_dir = path.join(current_dir, 'node_modules', require_text)
    possible_file = try_directory_module(possible_dir)
    if possible_file:
      return possible_file
    current_dir = current_dir[:current_dir.rindex('/')]

  # try global module
  return None

def get_file_path(current_file_name, require_text):
  if require_text[0] == '.':
    file_path = path.realpath(path.join(current_file_name, '../', require_text))
  elif require_text[0] == '/':
    file_path = path.realpath(require_text)

  result = try_ext(file_path)
  if result == None:
    result = try_directory_module(file_path)
  return result

class OpenRequiredFileCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    window = sublime.active_window()
    view = window.active_view()
    current_file_name = view.file_name()

    line = view.line(view.sel()[0])
    line_text = view.substr(line)
    require_text = get_require_text(line_text)
    print(require_text)
    if require_text == None:
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
