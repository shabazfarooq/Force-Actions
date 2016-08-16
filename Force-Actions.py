import sublime, sublime_plugin, subprocess, os, sys, datetime
from io import StringIO

# TODO:
# fix query reading to handle edge cases
# open new window and pipe terminal output there
# get error printing to work with standard out printing
# run terminal commands seperately (one at a time, not sure if this will even work tho?
# -and only if the out/err printing isnt solved because it is right now mis matching errors

class EventDump(sublime_plugin.EventListener):
  def on_post_save_async(self, view):

    # view.window().new_file().insert(null, 0, "hello")

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
      commands = ["cd " + workspace_dir, "./login", action]
      # commands = ["cd " + workspace_dir, "./login", "echo -e '\n\n'", action]
      command = " && ".join(commands)


      # Show console window and return focus to current view
      sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
      view.window().active_panel()

      print(command)

      # Execute bash command
      proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

      while proc.poll() is None:
        lineOut = proc.stdout.readline()
        lineOutToString = lineOut.strip().decode("utf-8")
        print(prefix + lineOutToString)

        
        # print(proc.stdout.readline());
        # print(proc.stderr.readline());

        # printline = ""

        # _stdout = proc.stdout.readline()
        # if _stdout:
        #   printLine = _stdout
        # else:
        # _stderr = proc.stderr.readline()
        # if _stderr:
        #   printLine = _stderr
        
        # print(printLine)




        # print(proc.stderr.readline())
        # lineOut = proc.stdout.readline()
        # lineOutToString = lineOut.strip().decode("utf-8")
        # print(prefix + lineOutToString)

        # lineErr = proc.stderr.readline()
        # lineErrToString = lineErr.strip().decode("utf-8")
        # print(prefix + lineErrToString)


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
