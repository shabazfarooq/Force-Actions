import sublime, sublime_plugin, subprocess, os, sys, datetime
from io import StringIO

class EventDump(sublime_plugin.EventListener):
    def on_post_save_async(self, view):

# class Force_saveCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         print("hit")

        # Extract file extension from currently saved file
        file_split = view.file_name().split("/")
        length = len(file_split)
        file = file_split[length-1]
        lastDot = file.rfind(".")
        file_extension = file[lastDot+1:]
        file_wo_extension = file[:lastDot]


        # Determine if this is a SFDC type
        sfdc_meta_type=""
        if file_extension == "resource":
            sfdc_meta_type = "StaticResource"
        elif file_extension == "component":
            sfdc_meta_type = "ApexComponent"
        elif file_extension == "apex":
            sfdc_meta_type = "__execute_anon__"

        # If it is an SFDC type proceed to save
        if sfdc_meta_type != "":
            # Get workspace directory
            # assuming the parent dir is 3 directories up from file being saved
            # workspace_dir = file_split[:-3]
            workspace_dir = file_split[:5]
            workspace_dir = '/'.join(workspace_dir)
            workspace_dir = workspace_dir + '/'
            
            # Generate shell commands
            # Login, cd into workspace dir, execute force cli save
            commands = ["cd " + workspace_dir,
                        "./login",
                        "force push -type " + sfdc_meta_type + " -name " + file_wo_extension]

            # Override FORCE command to execute phantomjs save 
            # if sfdc_meta_type == "ApexClass":
            #     commands[2] = "phantomjs phantomsave.js"

            # Override FORCE command to execute anon apex call instead of push
            if sfdc_meta_type == "__execute_anon__":
                commands[2] = "force apex " + file

            command = " && ".join(commands)


            # Show console window and return focus to current view
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
            view.window().focus_group(view.window().active_group())

            startTime = datetime.datetime.now()
            print("")
            print("SFDC Action started: " + file + " @ " + datetime.datetime.strftime(startTime, '%-I:%M:%S %p'))
            print("")

            print(command)

            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            while proc.poll() is None:
                line = proc.stdout.readline()
                lineToString = line.strip().decode("utf-8")
                if lineToString:
                    print("     " + lineToString)


            endTime = datetime.datetime.now()
            print("")
            print("SFDC Action ended: " + file + " @ " + datetime.datetime.strftime(endTime, '%-I:%M:%S %p'))
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": False})
            view.window().focus_group(view.window().active_group())
