from pywinauto.application import Application
app = Application(backend="win32").start(r"C:\Program Files\Bandicam\\bdcam.exe")
# Connect to Bandicam
app = Application(backend="win32").connect(title="Bandicam")

# Get the window
win = app.window(title="Bandicam")

# Click on the record button
#win.child_window(title="Record/Stop F12", control_type="Button").click_input()





win.print_control_identifiers()
#app.dlg.child_window(title="Add a device", auto_id="tasklink", control_type="Hyperlink").click()

