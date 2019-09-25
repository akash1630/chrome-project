import os
import pyinotify
import shutil
from threading import Timer

class EventHandler(pyinotify.ProcessEvent):
  
  running_modify = 0
  modify_eventpath = []
  create_eventpath = []
  running_create = 0 

  def reset_create(self, *args):
    path = args[0]   
    print("resetting create event " + path)
    #self.running_create = 0
    if path.find("Bookmarks.bak") >= 0:
      self.edit_bookmarks()
    self.create_eventpath.remove(path)

  def reset_modify(self, *args):
    path = args[0]
    print("resetting modify event" + path)
    #self.running_modify = 0
    if path.find("Bookmarks.bak") >= 0:
      self.edit_bookmarks()
    self.modify_eventpath.remove(path)

  def edit_bookmarks(self):
    print("--------removing bookmarks-----------------")
    os.remove('/home/akash/.config/google-chrome/Default/Bookmarks')
    print("+++++++++++++copying back up to bookmarks++++++++++")
    #os.rename('/home/akash/.config/google-chrome/Default/Bookmarks.bak', '/home/akash/.config/google-chrome/Default/Bookmarks')
    shutil.copyfile('/home/akash/.config/google-chrome/Default/Bookmarks.bak', '/home/akash/.config/google-chrome/Default/Bookmarks')
    #os.system('cp /home/akash/.config/google-chrome/Default/Bookmarks.bak /home/akash/.config/google-chrome/Default/Bookmarks')

  def process_IN_CREATE(self, event):
    print("Create event handler. event :  ", event.pathname)
    if (event.pathname).find("Bookmarks") >= 0 and not (event.pathname).find(".sw") >= 0:
      if event.pathname not in self.create_eventpath: 
        print "Bookmarks file created"
        self.create_eventpath.append(str(event.pathname))
        #self.handler_running = 1
        #os.system('python bookmarks_lookup.py')
        os.system('python bookmarks_lookup.py '+ str(event.pathname))
        t = Timer(2.0, self.reset_create, [str(event.pathname)])
        t.start()

  def process_IN_MODIFY(self, event):
    print("Modify event handler. event : ", event.pathname)
    if (event.pathname).find("Bookmarks") >= 0 and not (event.pathname).find(".sw") >= 0:
      if event.pathname not in self.modify_eventpath: 
        print "Bookmarks file has been modified"
        self.modify_eventpath.append(str(event.pathname))
        #self.handler_running = 1
        #os.system('python bookmarks_lookup.py')
        os.system('python bookmarks_lookup.py '+ str(event.pathname))
        t = Timer(2.0, self.reset_modify, [str(event.pathname)])
        t.start()

mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE
handler = EventHandler()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch('./.config/google-chrome/Default', mask, rec=True)

notifier.loop()
