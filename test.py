import os
import sqlite3
import hashlib
import tkinter as tk
import re
import random
import string
from tkinter import messagebox
from tkinter import simpledialog
from urllib.parse import urlparse
print('launching passman')

#database and table
dbName='passwords.db'
tableName='users'

#db connection
main_conn=sqlite3.connect(dbName)
main_c=main_conn.cursor()

#table check
main_c.execute('''CREATE TABLE IF NOT EXISTS {} (username text, password text)'''.format(tableName))
main_conn.commit()

#create new database for the user
def create_database(user):
    #create a directory folder for the user tables
    database_dir='data'
    os.makedirs(database_dir,exist_ok=True)
    user_db= os.path.join(database_dir,f'{user}_db.db')
    #checks for duplicate files
    if os.path.exists(user_db):
        print('database file already exists')
        print(os.path.abspath(user_db))
        return False
    try:
        #file creation
        with open(user_db, 'w'):
            print('file created')
            print(os.path.abspath(user_db))
            return True
    except IOError:
        print('error occured')
        return None
    
#function to create a table in the users db file, store new entry input into table
def create_table(website,user,password):
    database_dir='data'
    db_file=os.path.join(database_dir,f'{user}_db.db')
    conn=sqlite3.connect(db_file)
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS userdata
                 (website TEXT, user TEXT, password TEXT)''')
    hashed_pass=hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO userdata VALUES (?,?,?)',(website,user,hashed_pass))
    conn.commit()
    conn.close()

#function to check for valid emails using regex
def is_valid_email(email):
    pattern = r'^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$'
    return re.match(pattern, email) is not None

#function to check if email has already been registered
def is_email_used(email):
    main_c.execute('SELECT * FROM {} WHERE username=?'.format(tableName), (email,))
    return main_c.fetchone() is not None

#add new user and hash their password
def addUser(user, password):
    hashPass=hashlib.sha256(password.encode()).hexdigest()
    main_c.execute('INSERT INTO {} VALUES (?,?)'.format(tableName), (user, hashPass))
    main_conn.commit()

#simple user authentication
def authUser(user, password):
    hashPass=hashlib.sha256(password.encode()).hexdigest()
    main_c.execute('SELECT * FROM {} WHERE username=? AND password =?'.format(tableName), (user, hashPass))
    result=main_c.fetchone()
    if result is not None:
        return True
    else:
        return False

#checks a string for valid url    
def valid_url(url):
    pattern = re.compile(r"^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
    return bool(pattern.match(url))

#create  login gui
class Login(tk.Frame):
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
        self.username_label = tk.Label(self, text='Email:', font=('Helvetica', 12), bg='#f5f5f5')
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
        self.register_button.pack(side=tk.LEFT, anchor=tk.SW)
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

        #check for both fields to have data
        if user and passw:
            #call authUser to validate login info in passwords.db
            if authUser(user,passw):
                tk.messagebox.showinfo('Success', 'Login Successful')
                create_database(user)
                self.destroy()
                #load home page
                home= HomePage(self.master)
                home.pack(fill='both',expand=True)
                return
            
            else:
                tk.messagebox.showerror('error', 'incorrect combo')

        else:
            tk.messagebox.showerror('error', 'please enter user and passw')
        self.username_entry.delete(0,tk.END)
        self.password_entry.delete(0,tk.END)

#home page screen
class HomePage(tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master=master
        self.master.title('PassMan')
        self.master.geometry('400x200')
        self.master.resizable(False,False)
        self.configure(bg='#f5f5f5')
        self.create_widgets()
        self.get_clipboard()

    #function to init clipboard
    def get_clipboard(self):
        self.clipboard=self.clipboard_get()

    def create_widgets(self):
        #welcome label
        self.welcome=tk.Label(self, text='Home Page')
        self.welcome.pack()
        button_frame=tk.Frame(self)
        button_frame.pack(side=tk.LEFT)
        
        #new entry button
        self.entry=tk.Button(self,text='Add a New Password',command=self.entry_page)
        self.entry.pack(side=tk.TOP,anchor=tk.NW)

        #generate password button
        self.entry=tk.Button(self,text='Generate A New Password',command=self.generate_page)
        self.entry.pack(side=tk.TOP,anchor=tk.W)

        #logout button
        self.logout=tk.Button(self,text='Logout', command=self.logout_page)
        self.logout.pack(side=tk.BOTTOM,anchor=tk.SW)

        #initializing clipboard
        self.master.after(0, self.get_clipboard)

    #logout function
    def logout_page(self):
        self.destroy()
        login_page=Login(self.master)
        login_page.pack(fill='both', expand=True)

    #generate password popup
    def generate_page(self):
        uppers=string.ascii_uppercase
        lowers=string.ascii_lowercase
        digits=string.digits
        spchars=string.punctuation
        totalchar=uppers+lowers+digits+spchars
        length=12
        secpass=''.join(random.choices(totalchar,k=length))

        def copy_selected_text():
            selected_text = popup_text.get("sel.first", "sel.last")
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)

        popup_window = tk.Toplevel(self)
        popup_window.title('New Password')

        popup_text = tk.Text(popup_window,height=3,width=30)
        popup_text.insert("1.0", secpass)
        popup_text.pack(fill='both', expand=True,padx=1,pady=1)
        popup_text.configure(state="disabled")

        context_menu = tk.Menu(popup_text, tearoff=0)
        context_menu.add_command(label="Copy", command=copy_selected_text)

        def show_context_menu(event):
            context_menu.post(event.x_root, event.y_root)

        popup_text.bind("<Button-3>", show_context_menu)

    #new entry popup 
    def entry_page(self):
        entry_input=tk.Toplevel(self)
        entry_input.title('New Entry')

        #paste command handling
        def paste_entry(entry):
            entry.delete(0,tk.END)
            entry.insert(tk.END,entry.clipboard_get())

        # Website
        website_label = tk.Label(entry_input, text='Website:')
        website_label.grid(row=0, column=0, sticky=tk.E)
        website_entry = tk.Entry(entry_input)
        website_entry.grid(row=0, column=1, padx=5,pady=5)
        website_entry.bind('<Button-3>', lambda event: context_menu.post(event.x_root, event.y_root))
        
        # Username
        user_label = tk.Label(entry_input, text='Username:')
        user_label.grid(row=1, column=0, sticky=tk.E)
        user_entry = tk.Entry(entry_input)
        user_entry.grid(row=1, column=1, padx=5, pady=5)
        user_entry.bind('<Button-3>', lambda event: context_menu.post(event.x_root, event.y_root))
        
        # Password
        pass_label = tk.Label(entry_input, text='Password:')
        pass_label.grid(row=2, column=0, sticky=tk.E)
        pass_entry = tk.Entry(entry_input, show='*')
        pass_entry.grid(row=2, column=1, padx=5,pady=5)
        pass_entry.bind('<Button-3>', lambda event: context_menu.post(event.x_root, event.y_root))

        #context menu keybind
        def show_context(event):
            context_menu.post(event.x_root,event.y_root)

        #context menu with paste option
        context_menu=tk.Menu(entry_input,tearoff=0)
        context_menu.add_command(label='Paste',command=lambda: paste_entry(entry_input.focus_get()))

        # Submit button
        submit_button = tk.Button(entry_input, text='Submit New Entry', command=lambda: self.submit_page(website_entry.get(), user_entry.get(), pass_entry.get()))
        submit_button.grid(row=3, column=0, columnspan=2,padx=5,pady=10)

    def submit_page(self, website, user, password):
        if website and user and password:
            if is_valid_email(user)==False:
                tk.messagebox.showerror('error', 'invalid email address')
                return
            if valid_url(website) == False:
                tk.messagebox.showerror('error', 'invalid URL')
                return
            user_db=f'{user}_db.db'
            create_table(website,user,password)
            tk.messagebox.showinfo('Success', 'Entry added to db')
            self.destroy()
            home=HomePage(self.master)
            home.pack(fill='both',expand=True)
        else:
            tk.messagebox.showerror('error','please fill in all fields')


#main
root=tk.Tk()
app=Login(root)
app.pack(fill='both',expand=True)
app.mainloop()