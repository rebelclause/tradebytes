### does not work, following terminal beep enabled on terminal profile
##import sys
##sys.stdout.write('\a')
##sys.stdout.flush()
import os
from time import sleep

##print('\a') # nope...
##print('\a\a\a')

# The Best
##http://manpages.ubuntu.com/manpages/jammy/en/man1/spd-say.1.html
##import os; os.system('say "Beer time."'); print('\a\a\a')

msg = {}
msg['enter'] = "enter"
msg['exit'] = "exit"
##
command = 'spd-say -t male3 -i -30 -r 0 -p -100'
stock="" #'ltc'
##enter =(f"'{command} \"{msg['enter']}\"{stock}'")
##
##print(msg['enter'])
##try:
##
##except:
##    pass
##sleep(1)
##os.system('spd-say "Close"')
##print(msg['exit'])

def buy():
    enter =(f"'{command} \"{msg['enter']}\"{stock}'")    
    os.system(f"'{enter}'")
    sleep(1)
    
def sell():
    ext =(f"'{command} \"{msg['exit']}\"'")
    os.system(f"'{ext}'")
    sleep(1)
    
def say(msg = 'top'):
        enter =(f"'{command} \"{msg}\"{stock}'")     
        os.system(f"'{enter}'")
        sleep(1)

if __name__ == '__main__':
    say('clink bee tea sea') #holy cow')
    buy()
    sell()
    
    

##os.system('spd-say -t female -i -30 -r -30 -p -100 "Enter or die"&')

##DESCRIPTION
##
##       send text-to-speech output request to speech-dispatcher
##
##OPTIONS
##
##       -r, --rate
##              Set the rate of the speech (between -100 and +100, default: 0)
##
##       -p, --pitch
##              Set the pitch of the speech (between -100 and +100, default: 0)
##
##       -R, --pitch-range
##              Set the pitch range of the speech (between -100 and +100, default: 0)
##
##       -i, --volume
##              Set the volume (intensity) of the speech (between -100 and +100, default: 0)
##
##       -o, --output-module
##              Set the output module
##
##       -O, --list-output-modules
##              Get the list of output modules
##
##       -I, --sound-icon
##              Play the sound icon
##
##       -l, --language
##              Set the language (ISO code)
##
##       -t, --voice-type
##              Set  the  preferred  voice  type  (male1,  male2,  male3, female1, female2 female3,
##              child_male, child_female)
##
##       -L, --list-synthesis-voices
##              Get the list of synthesis voices
##
##       -y, --synthesis-voice
##              Set the synthesis voice
##
##       -c, --character
##              Speak the character
##
##       -k, --key
##              Speak the key
##
##       -m, --punctuation-mode
##              Set the punctuation mode (none, some, most, all)
##
##       -s, --spelling
##              Spell the message
##
##       -x, --ssml
##              Set SSML mode on (default: off)
##
##       -e, --pipe-mode
##              Pipe from stdin to stdout plus Speech Dispatcher
##
##       -P, --priority
##              Set  priority   of   the   message   (important,   message,   text,   notification,
##              progress;default: text)
##
##       -N, --application-name
##              Set the application name used to establish the connection to specified string value
##              (default: spd-say)
##
##       -n, --connection-name
##              Set the connection name used to establish the connection to specified string  value
##              (default: main)
##
##       -w, --wait
##              Wait till the message is spoken or discarded
##
##       -S, --stop
##              Stop speaking the message being spoken
##
##       -C, --cancel
##              Cancel all messages
##
##       -v, --version
##              Print version and copyright info
##
##       -h, --help
##              Print this info
##
##       Please report bugs to speechd-discuss@nongnu.org
##



#### prefer to use the Google Text To Speech library because it has a more natural voice.
##
##from gtts import gTTS
##def speak(text):
##  tts = gTTS(text=text, lang="en")
##  filename = "voice.mp3"
##  tts.save(filename) 

####There is one limitation. gTTS can only convert text to speech and save. So you will have to find another module or function to play that file. (Ex: playsound)
##
####Playsound is a very simple module that has one function, which is to play sound.
##
##import playsound
##def play(filename):
##  playsound.playsound(filename)
##
####You can call playsound.playsound() directly after saving the mp3 file.

