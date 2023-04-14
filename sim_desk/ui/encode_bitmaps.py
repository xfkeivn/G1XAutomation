
"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys
from wx.tools import img2py


command_lines = [
    "   -F -i -n AppImage icons/alt_window_16.gif images.py",
    "-a -F -n NewProject icons/newprj.gif images.py",
    "-a -F -n DBC icons/dbc.png images.py",
    "-a -F -n DIAG icons/diagnostic.png images.py",
    "-a -F -n DID icons/did.png images.py",
    "-a -F -n DTC icons/dtc.png images.py",
    "-a -F -n Delete icons/delete.png images.py",
    "-a -F -n Import icons/import_wiz.png images.py",
    "-a -F -n Export icons/export_wiz.png images.py",
    "-a -F -n viewproject icons/delete.png images.py",
    "-a -F -n viewprop icons/delete.png images.py",
    "-a -F -n viewconsole icons/delete.png images.py",
    "-a -F -n viewcontrol icons/delete.png images.py",
    "-a -F -n saveperspective icons/PerspectiveStack.gif images.py",
    "-a -F -n openperspective icons/saveall_edit_memory.png images.py",
    "-a -F -n nested_projects icons/Project.gif images.py",
    "-a -F -n folder_expand icons/folder_expand.gif images.py",
    "-a -F -n folder_collapse icons/folder_collapse.gif images.py",
    "-a -F -n wizard icons/wizard.png images.py",
    "-a -F -n message icons/message.png images.py",
    "-a -F -n save_edit icons/save_edit.png images.py",
    "-a -F -n service icons/service-16.png images.py",
    "-a -F -n request icons/request.png images.py",
    "-a -F -n presponse icons/positive_response.png images.py",
    "-a -F -n nresponse icons/negative_response.png images.py",
    "-a -F -n datafield icons/parameter.png images.py",
    "-a -F -n dtc icons/dtc.png images.py",
    "-a -F -n did icons/did.png images.py",
    "-a -F -n driverinstall icons/package_obj.gif images.py",
    "-a -F -n adddriver icons/list-add-32.png images.py",
    "-a -F -n removedriver icons/remove-sign-32.png images.py",
    "-a -F -n refreshdriver icons/view-refresh-32.png images.py",
    "-a -F -n device icons/device.gif images.py",
    "-a -F -n resource icons/hardware.png images.py",
    "-a -F -n device_no_exist icons/device_no_exist.png images.py",
    "-a -F -n panel icons/panel.png images.py",
    "-a -F -n viewproj icons/packagefolder_obj.gif images.py",
    "-a -F -n viewconsole icons/console.gif images.py",
    "-a -F -n viewprop icons/property.gif images.py",
    "-a -F -n viewcontrols icons/panel.png images.py",
    "-a -F -n widget icons/jar_obj.gif images.py",
    "-a -F -n run icons/run.png images.py",    
    "-a -F -n stop icons/stop.png images.py",    
    "-a -F -n robot icons/robot.png images.py", 
    "-a -F -n script icons/python2.png images.py",           
    "-a -F -n callback icons/callback.gif images.py", 
    "-a -F -n func icons/func.gif images.py", 
    "-a -F -n edit icons/edit.png images.py", 
    "-a -F -n testrun icons/testrun.png images.py", 
    "-a -F -n timer icons/XSDDateAndTimeTypes.gif images.py", 
    "-a -F -n signal icons/msg_signal.png images.py", 
    "-a -F -n list icons/list.png images.py",   
    "-a -F -n splashscreen icons/splashscreen.jpg images.py",     
    "-a -F -n message_go icons/message_go.png images.py",     
    "-a -F -n message_reply icons/message_reply.png images.py",     
    "-a -F -n msg_signal icons/msg_signal.png images.py",     
    "-a -F -n node icons/node.gif images.py",     
    "-a -F -n main icons/MAIN.png images.py",     
    "-a -F -n ldf icons/ldf.bmp images.py",   
    "-a -F -n table icons/table.png images.py",   
    "-a -F -n slot icons/slot.png images.py",     
    "-a -F -n flex icons/flex.ico images.py",
    "-a -F -n array icons/array.png images.py",
    "-a -F -n camera icons/icons8-camera-24.png images.py",

    ]


if __name__ == "__main__":
    for line in command_lines:
        args = line.split()
        img2py.main(args)

