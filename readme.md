# How to setup 
1. install Squish IDE 7.0.1 squish-7.0.1-qt515x-win64-msvc142.exe
2. in the edit server setting, to add an aut with name, gx1, localhost, 3520
3. login qt.io to register and request a trial license for 14 days
4. enabled open-ssh-authenticator in the window services
5. request the mti private key and copy the key and cert to the .ssh of home directory
6. use ssh-add ~/.ssh/xxx to add your key and give the password when prompt
7. clone the GX1Automation and set the python venv with python38, this python38 should be the same
version as Squish, you can use the python under squish installation folder python38.
8. use pip install -r requirement.txt to install all the packages
9. install virtual com port vsp to create a pair of com ports, let say com1 and com2
10. startup the application of gx1 with squish in the vm and change the com port from pipe to com2
11. start the main.py in the sim_desk
12. create a project in the sim_desk and click the project to set the com port 
13. select the squish names to set the squish hooker's ip and aut, the ip is the virtual machine ip 
where the application is running, normally check vmnet8, and it will start from 128 at last section
14. start the sim_desk with start button on the toolbar
# How to robotframe work
1. under you venv, go to the Scripts find the ride.py, run it.
2. set the output dir in the run setting 
3. start running you test 