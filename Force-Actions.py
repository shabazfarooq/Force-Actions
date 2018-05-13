import sublime, sublime_plugin, subprocess, os, sys, datetime
from io import StringIO

class ExampleCommand(sublime_plugin.TextCommand):
  def run(self, edit, args):
    self.view.insert(edit, 0, args.get("text"))


class EventDump(sublime_plugin.EventListener):
  def on_post_save_async(self, view):
    prefix = "   "

    # Extract file extension from currently saved file
    file_path         = view.file_name()
    file_split        = file_path.split("/")
    length            = len(file_split)
    file              = file_split[length-1]
    lastDot           = file.rfind(".")
    file_extension    = file[lastDot+1:]
    file_wo_extension = file[:lastDot]


    # Determine if this is a SFDC type
    action=""
    if file_extension == "apex":
      action = "force apex " + file
    elif file_extension == "soql":
      query = EventDump.readSoqlFile(file_path)
      action = "force query " + query


    # If it is an SFDC action proceed
    if action != "":
      print('\n' * 50)
      print(prefix + "Executing: ")
      print(prefix + action + "\n")


      # Get workspace directory
      # assuming the parent dir is 3 directories up from file being saved
      workspace_dir = file_split[:5]
      workspace_dir = '/'.join(workspace_dir)
      workspace_dir = workspace_dir + '/'


      # Generate shell commands
      # Login, cd into workspace dir, execute force cli action
      commands = ["cd " + workspace_dir, "./login", "echo -e '\n\n'", action]
      command = " && ".join(commands)


      # Show console window and return focus to current view
      sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
      view.window().active_panel()


      # Execute bash command
      proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

      # logStdout = ""

      while proc.poll() is None:
        lineOut = proc.stdout.readline()
        lineOutToString = lineOut.strip().decode("utf-8")
        lineOutToString = lineOutToString.replace("];", "").replace("-e", "")
        # logStdout = logStdout + lineOutToString + "\n"
        print(prefix + lineOutToString)

      # #createNewWindow(view, logStdout)

      # Something to do with the panel
      sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": False})
      view.window().focus_group(view.window().active_group())


  def readSoqlFile(soqlFilePath):
    with open(soqlFilePath) as f:
      content = f.readlines()

    query      = []
    queryFound = False
    query_str  = ""

    for line in content:
      if line.startswith('['):
        queryFound = True
      if queryFound == True:
        query += line
        if line.rstrip('\n').endswith(']'):
          break;
    
    lenOfQuery = len(query)

    if lenOfQuery > 1:
      query[0] = "\""

      if query[lenOfQuery-1] == "]":
        query[lenOfQuery-1] = "\""
      elif query[lenOfQuery-2] == "]":
        query[lenOfQuery-2] = "\""


      for element in query:
         if element == "\n":
            query[query.index(element)] = " "

      query_str = ''.join(query)    

    return query_str;


def createNewWindow(view, textToApply):
  newFileView = view.window().new_file()
  newFileView.run_command("example", {"args":{"text":textToApply}})


