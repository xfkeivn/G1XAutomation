# How to setup 
1. install Squish IDE 7.0.1 squish-7.0.1-qt515x-win64-msvc142.exe
2. in the edit server setting, to add an aut with name, gx1, localhost, 3520
3. login qt.io to register and request a trial license for 14 days
4. add the squish bin folder to the env path.
5. update the squish_lib.py the first 2 lines according to your squish installation folder, python library
6. enabled open-ssh-authenticator in the window services if not starting the service.
7. request the mti private key and copy the key and cert to the .ssh of home directory
8. use ssh-add ~/.ssh/xxx to add your key and give the password when prompt
9. clone the GX1Automation and set the python venv with python38, this python38 should be the same
version as Squish, you can use the python under squish installation folder python38.
10. use pip install -r requirement.txt to install all the packages
11. install virtual com port vsp to create a pair of com ports, let say com1 and com2
12. start the SquishProxyServer.py, before startin update the IP and the private key file information in the file. (Line 88)
13. startup the application of gx1 with startaut to start the GX1 application in the vm and change the com port from pipe to com2
14. start the main.py in the sim_desk
15. create a project in the sim_desk and click the project to set the com port 
16. select the squish names to set the squish hooker's ip and aut, the ip is the virtual machine ip 
where the application is running, normally check vmnet8, and it will start from 128 at last section
17. start the sim_desk with start button on the toolbar

# OCR
1. install the tessacert OCR in the tool folder and make sure download the language file you need 
2. set the installation dir to the environment
3. 
# How to robotframework
1. Click the robot toolbar on the SimDesk can start the application
2. Set the report and log output directory in the run setting of RIDE
3. add the lib GX1Testlib.py, pay attention, use // not / for directory seperator.
4. start running you test 
5. install visual code extension robotframework server extension if you want to use text editor
