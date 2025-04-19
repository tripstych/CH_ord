from itertools import cycle, islice
from tkinter import *
from math import *
import numpy as np
import keyboard
import json
import time
import os
# event_type = None
# scan_code = None
# name = None
# time = None
# device = None
# modifiers = None
# is_keypad = None

'''

1516a1517,1518
> {
>    WinSet, ExStyle, -0x20, ahk_id %actwinid%
1517a1520,1524
> }
> Else
> {
>    WinSet, ExStyle, +0x80020, ahk_id %actwinid%
> }
'''

settings = { 'width':320,'height':80 } 

# Create object
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{settings['width']}x{settings['height']}+{screen_width//2}+{screen_height//2}")
root.configure(bg='white')

# Create transparent window
#root.attributes('-alpha',0.5)
root.attributes('-topmost', True)

root.overrideredirect(True)

class chordUtil:
    def __init__(self):
        #hooks
        self.chordKeys = {}

        try:
            if os.stat("config.json"):
                fp = open("config.json")
                self.chordKeys = json.load(fp)
                print(self.chordKeys,"loaded")
                fp.close()
        except:
            print()
        
 
        keyboard.hook(self.keyhook,suppress=True)
        self.record_next_stroke = False
        self.recorded_key = ""
        self.count_keydown = 0
        self.count_keyup = 0
        self.keySeq = []
        self.chord = [0,0,0,0,0]
        self.recording = False
        self.recording_readkey = False
        self.setBackground = "black"
        self.ctrl_keydown = False
        self.displaykey = ""
        self.last_key = ""
        self.last_key_time = 0
        self.f=0
        self.stop = False
        canvas = Canvas(root, width = settings['width'], height = settings['height'])
        canvas.configure(bd=0, highlightthickness=0)
        canvas.pack()
        self.canvas = canvas
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.create_rectangle(0,0,settings['width'],settings['height'],fill='black')
        self.canvas.create_text(settings['width']/2,40,fill="white",justify=CENTER,font="Console 12 bold",text="VIRTUAL CHORDER\nCONFIGURE & TEST\nUSE ASDFG")
        #pause for 1 second 
        self.canvas.update()
        time.sleep(1)
        self.redraw()
        


    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None
    def quit(self):
        keyboard.unhook_all()
        self.stop = True
        #root.destroy()
    def save(self):
        fp = open("config.json","w")
        json.dump(self.chordKeys,fp)
        fp.close()

    def panic(self):
        self.count_keydown = 0
        self.count_keyup = 0
        self.chord = [0,0,0,0,0]
        self.canvas.create_rectangle(0,0,settings['width'],settings['height'],fill='white')

    def keyhook(self,e):
        KEY_UP = e.event_type == keyboard.KEY_UP
        KEY_DOWN = e.event_type == keyboard.KEY_DOWN
        
        if self.record_next_stroke:
            self.recorded_key = e.name
            self.record_next_stroke = False
            #chordKey = base5to10(int(''.join(self.keySeq)))
            chordKey = str(int(''.join(self.keySeq)))
            self.chordKeys[chordKey] = e.name
            self.count_keyup = 0
            self.count_keydown = 0
            self.chord = [0,0,0,0,0]
            self.keySeq=[]
            self.redraw()

        if e.scan_code==29:
            self.ctrl_keydown=KEY_DOWN
            
        if KEY_UP and self.ctrl_keydown:
            if e.name=="q":
                self.canvas = None
                keyboard.unhook_all()
                root.destroy()
                return
            if e.name=="s":
                self.save()
                return
            if e.name=="p":
                self.panic()
                return
            if e.name=="r":
                self.toggleRecord()
                self.redraw()
                return
        
        if KEY_UP:
            self.last_key = ""
        if e.scan_code>29 and e.scan_code<35:
            kordkeynum = 34-e.scan_code     
            #prevent repeats
            if KEY_DOWN and self.last_key==e.name:
                return
            if KEY_DOWN:
                #print("up")
                self.last_key = e.name
                self.last_key_time = time.time()
                self.count_keydown = self.count_keydown + 1
                self.chord[kordkeynum] += self.count_keydown
                self.keySeq.append(str(kordkeynum))
                self.redraw()
                # if self.chord[kordkeynum]>8:
                #     self.panic()
            #print(self.chord)    
            if KEY_UP:               
               self.count_keyup = self.count_keyup + 1
            
            if self.count_keydown>0 and self.count_keydown==self.count_keyup:

                if self.recording:
                    self.record_next_stroke = True
                else:
                    #chord = self.sum_chord(self.chord)
                    keySeq = ''.join(self.keySeq)
                    self.keySeq = []
                    self.chord=[0,0,0,0,0]
                    
                    self.count_keydown = 0
                    self.count_keyup = 0 
                    
                    chord = str(keySeq)
                    #print(chord,self.chordKeys.get(chord),"*"*80)
                    
                    if self.chordKeys.get(chord):
                        #print(".")
                        key = self.chordKeys[chord]
                        self.displaykey = key
                        keyboard.unhook_all()
                        keyboard.press_and_release(key)
                        #print(key)
                        keyboard.hook(self.keyhook,suppress=True)
                    else:
                        self.displaykey = "¿"
                        #print("unknown")
                    self.redraw()
                            
    def toggleRecord(self):
        self.recording = not self.recording

    countDown = 0
    def redraw(self):
        Q=120
        pl = []
        if not self.canvas:
            return

        self.canvas.create_rectangle(0,0,settings['width'],settings['height'],fill='black')
        self.canvas.create_text(130,settings['height']-20,fill="green",font="Serif 10 bold",text="CTRL-s: Save | CTRL-r: Toggle record")
            
        if self.recorded_key:
            self.canvas.create_text(280,45,fill="red",font="Serif 30 bold",text=self.recorded_key)
            self.recorded_key = ""
            self.record_next_stroke = False
            self.countDown = 1000
        if (self.countDown>0):
            self.canvas.create_text(280,45,fill="red",font="Serif 30 bold",text=self.recorded_key)
            self.countDown -=1
            
        # if self.record_next_stroke:
        #     self.canvas.create_rectangle(180,0,240,40,fill="red")
        # else:
        #     self.canvas.create_rectangle(180,0,240,40,fill="white")
 
        keys = ['A','S','D','F','G']
        keys.reverse()
        for n,c in enumerate(self.chord):
            self.canvas.create_rectangle( 260-48*n, 5, 260-48*(n+1),40,outline="white",width=2,fill="blue"),
            self.canvas.create_rectangle( 260-48*n, 40, 260-48*(n+1), 40-c*3  ,outline="white",width=2,fill="white"),
            self.canvas.create_text( 260-48*n-24, 25,fill="white",font="Serif 10 bold",text=keys[n])

        if self.recording:
            self.canvas.create_text(290,20,fill="red",font="Serif 12 bold",text="[ ⏺ ]")
        else:
            self.canvas.create_text(290,20,fill="red",font="Serif 12 bold",text="[ ⏵ ]")
        self.canvas.update()
        if self.displaykey and not self.recording:
            self.canvas.create_text(290,settings['height']-35,fill="green",font="Serif 40 bold",text=self.displaykey)
        #self.canvas.after(10,self.redraw)

#def keyhook(e):
cu = chordUtil()
cu.chordKeys
# Execute tkinter

root.mainloop()