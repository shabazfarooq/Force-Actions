import sublime, sublime_plugin, subprocess, os, sys, datetime
from io import StringIO

class EventDump(sublime_plugin.EventListener):
  def on_post_save_async(self, view):

    # view.window().new_file().insert(null, 0, "hello")



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
      # query = EventDump.readSoqlFile(file_path)
      # query = "'SELECT id FROM Account'"
      # action = "force query " + query
      # action = 'force query "SELECT id FROM Account"'
      action = "force query \"select id from account\""
      print(action)


    # If it is an SFDC action proceed
    if action != "":
      # Get workspace directory
      # assuming the parent dir is 3 directories up from file being saved
      workspace_dir = file_split[:5]
      workspace_dir = '/'.join(workspace_dir)
      workspace_dir = workspace_dir + '/'


      # Generate shell commands
      # Login, cd into workspace dir, execute force cli action
      commands = ["cd " + workspace_dir, "./login"]
      command = " && ".join(commands)


      # Show console window and return focus to current view
      sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
      view.window().focus_group(view.window().active_group())


      # Execute bash command
      proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

      while proc.poll() is None:
        print("OUT:" + proc.stdout.readline())
        print("ERR:" + proc.stderr.readline())

        line = proc.stdout.readline()
        lineToString = line.strip().decode("utf-8")
        if lineToString:
          print("     " + lineToString)
        # else:
        #   if proc.stderr:
        #     errLine = proc.stderr.readline()
        #     errLineToString = errLine.strip().decode("utf-8")
        #     if errLineToString:
        #       print("     " + errLineToString)


      # Something to do with the panel
      sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": False})
      view.window().focus_group(view.window().active_group())


  def readSoqlFile(soqlFilePath):
    with open(soqlFilePath) as f:
      content = f.readlines()

    query = []
    queryFound = False

    for line in content:
      if line.startswith('['):
        queryFound = True
      if queryFound == True:
        query += line.rstrip('\n')
      if line.rstrip('\n').endswith(']'):
        break;
    
    query.pop(0)
    query.pop(-1)
    
    return ''.join(query);
