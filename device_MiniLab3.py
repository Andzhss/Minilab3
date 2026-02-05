# name= Arturia MiniLab 3
# supportedHardwareIds=00 20 6B 02 00 04 04
# url=https://forum.image-line.com/viewtopic.php?f=1994&t=289305

"""
[[
    Surface:    MiniLab3
    Developer:  Farès MEZDOUR
    Version:    1.0.8 (Modified)
]]
"""

import ui
import transport
import channels
import patterns
import plugins
import device

from MiniLab3Process import MiniLabMidiProcessor
from MiniLab3Return import MiniLabLightReturn
from MiniLab3Display import MiniLabDisplay
from MiniLab3Pages import MiniLabPagedDisplay
from MiniLab3Connexion import MiniLabConnexion
import ArturiaVCOL

## CONSTANT
PORT_MIDICC_ANALOGLAB = 10

class MidiControllerConfig :
    def __init__(self):
        self._lightReturn = MiniLabLightReturn()
        self._display = MiniLabDisplay()
        self._paged_display = MiniLabPagedDisplay(self._display)
        self._connexion = MiniLabConnexion()
        self._disp = 0

    def LightReturn(self) :
        return self._lightReturn
        
    def display(self):
        return self._display

    def paged_display(self):
        return self._paged_display
        
    def connexion(self) :
        return self._connexion
        
    def Idle(self):
        self._paged_display.Refresh()
        
    def Sync(self):
        # Update display
        active_index = channels.selectedChannel()
        channel_name = channels.getChannelName(active_index)
        
        # Handle special characters in names
        for i in range(len(channel_name)) :
            if (ord(channel_name[i]) not in range(0,127)) :
                str1 = channel_name[0:i]
                str2 = channel_name[i+1::]
                channel_name = str1 + '?' + str2
                
        pattern_number = patterns.patternNumber()
        pattern_name = patterns.getPatternName(pattern_number)    

        if active_index != -1 :  
            self._paged_display.SetPageLines(
                'main',
                10,
                line1='%d-%s' % (active_index + 1, channel_name),
                line2='%s' % pattern_name 
                )
            self.paged_display().SetActivePage('main', 1500)
        else :
            self._paged_display.SetPageLines(
                'main',
                10,
                line1='No Selection',
                line2='%s' % pattern_name 
                )
            self.paged_display().SetActivePage('main', 1500)


def OnMidiMsg(event) :
    # Pass event to the processor
    # Logic: If processor returns True, it means "I handled it internally" 
    # or "I want to influence handled state".
    # See MiniLab3Process.py for specific return values (False is used to force handled=True)
    if _processor.ProcessEvent(event):
        event.handled = False

def OnInit():
    print('Loaded MIDI script for Arturia MiniLab 3 (Custom)')
    init()
    _mk3.LightReturn().init()
    _mk3.Sync()
    _mk3.paged_display().SetPageLines('welcome', 10, line1=ui.getProgTitle(), line2="Connected")
    _mk3.paged_display().SetActivePage('welcome', expires=1500)
    _mk3.paged_display().SetActivePage('main')

def init() :
    global _mk3 
    _mk3 = MidiControllerConfig()
    global _processor
    _processor = MiniLabMidiProcessor(_mk3) 
    _mk3.connexion().DAWConnexion()
    
def OnDeInit():
    _mk3.connexion().DAWDisconnection()
    return
   
def OnUpdateBeatIndicator(value):
    _mk3.LightReturn().ProcessPlayBlink(value)
    _mk3.LightReturn().ProcessRecordBlink(value)
 
def OnRefresh(flags) :
    _mk3.LightReturn().RecordReturn()
    _mk3.LightReturn().PlayReturn()
    _mk3.LightReturn().LoopReturn()
    _mk3.LightReturn().PluginParamReturn()
    
    if plugins.isValid(channels.selectedChannel()) :
        string = plugins.getPluginName(channels.selectedChannel())
        if string in ArturiaVCOL.V_COL :
            if not ui.getFocused(5) :
                _mk3.connexion().ArturiaDisconnection()
            else :
                _mk3.connexion().ArturiaConnexion()
        else :
            _mk3.connexion().ArturiaDisconnection()
    else :
        _mk3.connexion().ArturiaDisconnection()

    if flags not in [4,256,260,4608,4096] :
        _mk3.Sync()

def OnIdle():
    _mk3.Idle()
