class NullConsole():
    def __init__(self):
        pass
    def error(self,text):
        print (text)
    def log(self,text):
        print (text)
    def warn(self,text):
        print (text)
CONSOLE = NullConsole()