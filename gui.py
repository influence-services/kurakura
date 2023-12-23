import os
import tkinter as tk
from tkinter import ttk
import time
import sys
import zipfile
import requests as req
import shutil
from tkinter import filedialog
import urllib.request
import base64
import io
from PIL import Image, ImageTk
import os
from io import BytesIO
import win32gui, win32con

the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)

def themedMessageBox(title, message):
    window3 = tk.Tk()
    window3.title(title)
    window3.geometry("400x80")
    window3.tk.call("source", "azure/azure.tcl")
    window3.tk.call("set_theme", "dark")
    ttk.Label(window3, text="ⓘ", font=("Segoe UI", 20)).grid(column=0, row=0, sticky="W")
    ttk.Label(window3, justify="left", text=message, font=("Segoe UI", 12)).grid(column=1, row=0, sticky="W")
    ttk.Button(window3, text="Exit", command=lambda: window3.destroy()).grid(column=1, row=1, sticky="W")
    window3.mainloop()

def errorHook(type, value, traceback):
    themedMessageBox("Kurakura - Error", "An error occured:\n" + str(value))
    sys.__excepthook__(type, value, traceback)

sys.excepthook = errorHook

if not os.path.exists("azure/azure.tcl"):
    c = req.get("https://codeload.github.com/rdbende/Azure-ttk-theme/zip/refs/heads/main")
    with open("azure.zip", "wb") as f:
        f.write(c.content)
    with zipfile.ZipFile("azure.zip", "r") as zip_ref:
        zip_ref.extractall(".")
    shutil.move("Azure-ttk-theme-main", "azure")
    os.remove("azure.zip")

base_command = "py kurakura.py"

window = tk.Tk()
window.title("Kurakura")
window.geometry("1000x500")
window.tk.call("source", "azure/azure.tcl")
window.tk.call("set_theme", "dark")

def detectValidRootProjects():
    files_determining = ["kurakura.py", "beautify.exe", "plugins.json", "default.cfg", "main.py"]
    valid_root_projects = []
    for root, dirs, files in os.walk("."):
        if len(root.strip()) == 0:
            continue
        valid = True
        for file in files_determining:
            if not file in files:
                valid = False
                break
        if valid:
            valid_root_projects.append(root)
    return valid_root_projects

def drawNewProject():
    projectname = tk.StringVar()
    projectname.set("Project Name")
    projectnameentry = ttk.Entry(window, textvariable=projectname)
    projectnameentry.pack()
    ttk.Label(window, text="").pack()
    projectbutton = ttk.Button(window, text="Create Project", command=lambda: os.system(base_command + " new " + projectname.get()))
    projectbutton.pack()

def detectInstalledTextEditor():
    if os.path.exists("C:\\Program Files\\Sublime Text 3\\sublime_text.exe"):
        return "\"C:\\Program Files\\Sublime Text 3\\sublime_text.exe\""
    elif os.path.exists("C:\\Program Files\\Notepad++\\notepad++.exe"):
        return "\"C:\\Program Files\\Notepad++\\notepad++.exe\""
    elif os.path.exists(os.getenv("LOCALAPPDATA") + "\\Programs\\Microsoft VS Code\\Code.exe"):
        return "\"C:\\Program Files\\Microsoft VS Code\\Code.exe\""
    else:
        return "notepad.exe"

def detectUserName():
    return os.getenv("username") or os.getenv("USER")

def openProject(path):
    window2 = tk.Tk()
    window2.title("Kurakura - Project")
    window2.geometry("800x600")
    window2.tk.call("source", "azure/azure.tcl")
    window2.tk.call("set_theme", "dark")
    label = ttk.Label(window2, text="You are now exploring " + path, font=("Segoe UI", 12))
    label.pack()
    ttk.Label(window2, text="Project Operations", font=("Segoe UI", 20)).pack()
    origdir = os.getcwd()
    print(origdir)
    ttk.Button(window2, text="Build", command=lambda: drawDone(lambda: os.chdir(path) or (os.system("py kurakura.py main.py") and False) or os.chdir(origdir))).pack()
    ttk.Label(window2, text="", font=("Segoe UI", 10)).pack()
    ttk.Button(window2, text="Reveal in Explorer", command=lambda: os.system("START explorer.exe \"" + path + "\"")).pack()
    ttk.Label(window2, text="", font=("Segoe UI", 10)).pack()
    ttk.Button(window2, text="Remake Project", command=lambda: drawDone(lambda: os.system("py kurakura.py remake \"" + path + "\""))).pack()
    ttk.Label(window2, text="", font=("Segoe UI", 10)).pack()
    ttk.Button(window2, text="Clean project", command=lambda: drawDone(lambda: os.chdir(path) or (os.system("py kurakura.py clean .") and False) or os.chdir(origdir))).pack()
    ttk.Label(window2, text="", font=("Segoe UI", 10)).pack()
    ttk.Button(window2, text="DELETE PROJECT (DANGER)", command=lambda: drawDone(lambda: os.system("py kurakura.py del \"" + path + "\""))).pack()
    ttk.Label(window2, text="", font=("Segoe UI", 20)).pack()
    ttk.Button(window2, text="Exit", command=lambda: sys.exit(0)).pack()
    window2.mainloop()

def remakeProject():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "":
        return
    os.system("py kurakura.py remake \"" + folder_selected + '\"')
    for widget in window.winfo_children():
        widget.destroy()
    ttk.Label(window, text="").pack()
    ttk.Label(window, text="Welcome, " + detectUserName() + "!", font=("Segoe UI", 20)).pack()
    ttk.Label(window, text="").pack()
    drawNewProject()
    ttk.Label(window, text="").pack()
    ttk.Label(window, text="Open Project", font=("Segoe UI", 20)).pack()
    drawOpenValidProjects()
    ttk.Label(window, text="").pack()
    drawExit()
    return

def drawDone(func):
    func()
    themedMessageBox("Kurakura", "Operation completed successfully!")

def drawOpenValidProjects():
    valid_root_projects = detectValidRootProjects()
    if len(valid_root_projects) == 0:
        ttk.Label(window, text="Sorry, we couldn't find any projects.", font=("Segoe UI", 10)).pack()
        ttk.Label(window, text="Do you have an existing project you want to remake?", font=("Segoe UI", 10)).pack()
        projectbutton = ttk.Button(window, text="Remake Project", command=lambda: remakeProject())
        projectbutton.pack()
        return
    for project in valid_root_projects:
        projectbutton = ttk.Button(window, text=project, command=lambda: openProject(project))
        projectbutton.pack()
    ttk.Label(window, text="").pack()
    ttk.Label(window, text="Do you have an existing project you want to remake?", font=("Segoe UI", 10)).pack()
    projectbutton = ttk.Button(window, text="Remake Project", command=lambda: remakeProject())
    projectbutton.pack()

def drawExit():
    ttk.Button(window, text="Exit", command=lambda: sys.exit(0)).pack()

ttk.Label(window, text="").pack()
ttk.Label(window, text="Welcome, " + detectUserName() + "!", font=("Segoe UI", 20)).pack()
ttk.Label(window, text="").pack()
drawNewProject()
ttk.Label(window, text="").pack()
ttk.Label(window, text="Open Project", font=("Segoe UI", 20)).pack()
drawOpenValidProjects()
ttk.Label(window, text="").pack()
drawExit()

window.mainloop()