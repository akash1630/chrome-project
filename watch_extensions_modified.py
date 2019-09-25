import os
import pyinotify
from threading import Timer

class EventHandler(pyinotify.ProcessEvent):

  running_modify = 0
  modify_eventpath = []
  create_eventpath = []
  running_create = 0

  def reset(self):
    print("resetting event handler")
    self.running_modify = 0

  def reset_create(self, *args):
    path = args[0]   
    print("resetting create event " + path)
    #self.running_create = 0
    self.create_eventpath.remove(path)

  def reset_modify(self, *args):
    path = args[0]
    print("resetting modify event" + path)
    #self.running_modify = 0
    self.modify_eventpath.remove(path)

  def process_IN_CREATE(self, event):
    print "Create event handler. event :  " + event.pathname
    if self.running_modify == 0: 
      print "new extension added as manifest file added"
      self.create_eventpath.append(str(event.pathname))
      #os.system('python /home/akash/CSC705_project/code/ext_manifest_lookup.py '+ str(event.pathname))
      os.system('python /home/akash/CSC705_project/code/ext_manifest_lookup.py ')
      self.running_modify = 1
      #t = Timer(2.0, self.reset_open, [str(event.pathname)])
      t = Timer(5.0, self.reset)
      t.start()
        

  def process_IN_MODIFY(self, event):
    print "Modify event handler. event : " + event.pathname
    if self.running_modify == 0: 
      print "new extension added as manifest file added"
      self.create_eventpath.append(str(event.pathname))
      #os.system('python /home/akash/CSC705_project/code/ext_manifest_lookup.py '+ str(event.pathname))
      os.system('python /home/akash/CSC705_project/code/ext_manifest_lookup.py ')
      self.running_modify = 1
      #t = Timer(2.0, self.reset_open, [str(event.pathname)])
      t = Timer(5.0, self.reset)
      t.start()

mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE
handler = EventHandler()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch('./.config/google-chrome/Default/Extensions', mask, rec=True)

notifier.loop()
