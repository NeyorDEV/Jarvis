import win32com.client
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortcut(r"C:\Users\mylan\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar\Deezer.lnk")
print("Target:", shortcut.TargetPath)
print("Arguments:", shortcut.Arguments)
