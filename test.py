import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox
import re

print('launching passman')

#database and table
dbName='passwords.db'
tableName='users'

#db connection
conn=sqlite3.connect(dbName)
c=conn.cursor()

#table check
c.execute('''CREATE TABLE IF NOT EXISTS {} (username text, password text)'''.format(tableName))
conn.commit()

#function to check for valid emails using regex
def is_valid_email(email):
    pattern = r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$'
    return re.match(pattern, email) is not None

#function to check if email has already been registered
def is_email_used(email):
    c.execute('SELECT * FROM {} WHERE username=?'.format(tableName), (email,))
    return c.fetchone() is not None

#add new user and hash their password
def addUser(user, password):
    hashPass=hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO {} VALUES (?,?)'.format(tableName), (user, hashPass))
    conn.commit()

#simple user authentication
def authUser(user, password):
    hashPass=hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT * FROM {} WHERE username=? AND password =?'.format(tableName), (user, hashPass))
    result=c.fetchone()
    if result is not None:
        return True
    else:
        return False

#create gui
class Application(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)

        #some visual elements to the GUI
        self.master=master
        self.master.title('Pass Man 0.1')
        self.master.geometry('400x200')
        self.master.resizable(False,False)
        self.configure(bg='#f5f5f5')
        self.create_widgets()
        
        #buttons
    def create_widgets(self):
        # username display
        self.username_label = tk.Label(self, text='Username:', font=('Helvetica', 12), bg='#f5f5f5')
        self.username_label.pack(pady=(20, 0))

        self.username_entry = tk.Entry(self, font=('Helvetica', 12), bg='#ffffff')
        self.username_entry.pack()

        # password display
        self.password_label = tk.Label(self, text='Password:', font=('Helvetica', 12), bg='#f5f5f5')
        self.password_label.pack(pady=(10, 0))

        self.password_entry = tk.Entry(self, font=('Helvetica', 12), show='*', bg='#ffffff')
        self.password_entry.pack()

        # register button display
        self.button_frame=tk.Frame(self, bg='#f5f5f5')
        self.button_frame.pack(pady=(20,0))
        
        self.register_button = tk.Button(self, text='Register', font=('Helvetica', 12), bg='#007bff', fg='#ffffff', command=lambda: self.register_user())
        self.register_button.pack(side=tk.LEFT)

        #login button display
        self.login_button=tk.Button(self.button_frame,text='Login', font=('Helvetica',12), bg='#28a745', fg='#ffffff', command=lambda: self.login_user())
        self.login_button.pack(side=tk.LEFT,padx=(0,10))

    #register new user
    def register_user(self):
        user=self.username_entry.get()
        passw=self.password_entry.get()
        if user and passw:
            if is_valid_email(user)==False:
                tk.messagebox.showerror('error', 'invalid email address')
            elif is_email_used(user)==True:
                tk.messagebox.showerror('error', 'email already registered')
            else:
                addUser(user, passw)
                self.username_entry.delete(0,tk.END)
                self.password_entry.delete(0,tk.END)
                tk.messagebox.showinfo('success', 'registration successful')
        else:
            tk.messagebox.showerror('error', 'please enter both user and password')

    #login existing user
    def login_user(self):
        user=self.username_entry.get()
        passw=self.password_entry.get()
        if user and passw:
            if authUser(user,passw):
                tk.messagebox.showinfo('Success', 'Login Successful')
            else:
                tk.messagebox.showerror('error', 'incorrect combo')
        else:
            tk.messagebox.showerror('error', 'please enter user and passw')
        self.username_entry.delete(0,tk.END)
        self.password_entry.delete(0,tk.END)

#main
root=tk.Tk()
app=Application(master=root)
app.pack(fill='both',expand=True)
app.mainloop()
