import subprocess
import time
from pywinauto import Desktop, Application


app = Application(backend='uia').start(r"cmd.exe /c start shell:appsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App", create_new_console=True, wait_for_idle=False)
app = Application(backend='uia').connect(title_re=".*WhatsApp.*") # Replace with the actual path
time.sleep(1)
while True:
    try:
        time.sleep(2)
        app.WhatsAppDialog.VideoCallButton.click() 
        break
    except:
        time.sleep(1)
        continue
time.sleep(5)
dialog = app.window(title="Video call ‎- WhatsApp")
time.sleep(30)
dialog.print_control_identifiers()
app.WhatsAppDialog.TitleBar.EndCallButton.click()