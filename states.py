import voicetotext
from voicetotext import *

global ready
ready =False

# welcoming state
def welcome():
    #trigger welcome video and music, are you ready
    print("now playing welcome video and music")
    global ready
    ready = True
    return ready

def Ready():
    if ready == True:
        #trigger listening
        voicetotext()
        r = False
        readyText(r)
        
        