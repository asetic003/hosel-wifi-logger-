import requests
from lxml import etree
from customtkinter import *
import customtkinter
import json
from PIL import Image
import subprocess
import time
import threading  
import requests
import psutil


#payload variable 
a= int(time.time() * 1000)

def payload_entry(username, password):
   
    try:
        with open('payload.json', 'r') as file:
            payload_lib = json.load(file)
    except FileNotFoundError:
        payload_lib = {}

   
    payload_lib[username] = {
        "date": username,
        "data-usage":0,
        "password": password,
    }

    
    with open("payload.json", "w") as outfile:
        json.dump(payload_lib, outfile, indent=4)
        username_label.configure(text=f"Account added \n pls restart to see changes") 
        username_label.place(relx=0.5,rely=0.33,anchor="center")


def check_wifi_login():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, check=True)
        output = result.stdout
        if "BH5" in output:
            request_sender() 
        else:
            username_label.configure(text="Not connected to BH5")
    except subprocess.CalledProcessError as e:
        username_label.configure(text=f"Error:{e} ")


def check_wifi_logout():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, check=True)
        output = result.stdout()
        if "BH5" in output:
            logout(comboBox.get())
        else:
            username_label.configure(text="Not connected to BH5")
    except subprocess.CalledProcessError as e:
        username_label.configure(text=f"Error:{e} ")



def request_sender():
    current_id = str(comboBox.get())
    url = "http://172.16.1.1:8090/login.xml"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    # Load payload data from the file
    with open('payload.json', 'r') as file:
        payload_lib = json.load(file)
    
    # Check if the username exists in the payload library
    if current_id in payload_lib:
        payload = payload_maker(current_id ,payload_lib[current_id]["password"])
        response = requests.post(url, data=payload, headers=headers)
        status = response.text
        output_printer(status,current_id)
      
    else:
        return f"No payload found for username: {current_id}"





def stay_logged_in_thread():
    global stay_logged_in
    global login_counter
    login_counter=0

    
    while stay_logged_in:
      
       
        time.sleep(180)
        if login_counter<6:
            login_counter+=1
        else:
            login_counter=0
            logout(comboBox.get())
            check_wifi_login()
            break
    


a= int(time.time() * 1000)




def start_stay_logged_in_thread():
    global stay_logged_in
    stay_logged_in = True
    stay_logged_in_thread_handler = threading.Thread(target=stay_logged_in_thread)
    stay_logged_in_thread_handler.daemon = True  # Set as a daemon thread to exit with the main program
    stay_logged_in_thread_handler.start()

def stop_stay_logged_in_thread():
    global stay_logged_in
    stay_logged_in = False

def payload_maker(username,password):
    log_in_payload={
       
        "mode": 191,
        "username": username,
        "password": password,
        "a":int(time.time() * 1000),
        "producttype": 0
    }
    return log_in_payload



def output_printer(status,username):
    
    doc = etree.XML(status.strip())
    code_1 = doc.findtext("message")
    

    if code_1=="You are signed in as {username}":
        username_label.configure(text="login succesful")
       
        username_label.place(relx=0.5,rely=0.33,anchor="center")
        button.configure(text="Logout")
        button.configure(command=lambda:logout(comboBox.get()))
        comboBox.place_forget()
        userid_details.configure(text=f"Id:{username}")
        userid_details.place(relx=0.5,rely=0.4,anchor="center")
        connectedimage.place(relx=0.5,rely=0.23,anchor="center")
        start_stay_logged_in_thread()
      
       

    elif code_1=="Your data transfer has been exceeded, Please contact the administrator":
        username_label.configure(text= "Data transfer for this Id exceeded")
        username_label.place(relx=0.5,rely=0.33,anchor="center")
        app.after(3000, username_label.configure(text="User-id") )
    elif code_1=="Login failed. Invalid user name/password. Please contact the administrator. ":
        username_label.configure(text="invalid username/password")
        username_label.place(relx=0.5,rely=0.33,anchor="center")
    elif code_1=="Login failed. You have reached the maximum login limit.":
        username_label.configure(text="Already using in another device" )  
        username_label.place(relx=0.5,rely=0.33,anchor="center")
    else :
        username_label.configure(text="server not responding at this moment" ) 
   


def logout(user):
    url = "http://172.16.1.1:8090/login.xml"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    payload={
    "mode":193,
    "username":user,
    "a":a,
    "producttype":0
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    status=(response.text)
    doc = etree.XML(status.strip())
    code_1 = doc.findtext("message")
    if code_1=="You&#39;ve signed out":
        username_label.configure(text = "Logged out")
        connectedimage.place_forget()
        username_label.place(relx=0.5,rely=0.3, anchor="center")
        comboBox.place(relx=0.5,rely=0.4, anchor="center")
        button.configure(command =  request_sender)
        button.configure(text="Login")
        userid_details.place_forget()
        stop_stay_logged_in_thread()
        
    else:
        username_label.configure(text = "not logged out correctly")
        

def get_usernames_from_json():
    with open('payload.json', 'r') as file:
        payload_data = json.load(file)
    return list(payload_data.keys())

def open_popup():
    if hasattr(app, "_popup") and app._popup.winfo_exists():
        app._popup.focus()
    else:
        top = customtkinter.CTkToplevel(app)
        top.geometry("500x250")
        top.title("Add account")
        usr = CTkLabel(master=top, text="User-Id")
        usr.pack()
        entry = CTkEntry(top, placeholder_text="Username", text_color="white")
        entry.pack()
        password = CTkLabel(master=top, text="password:")
        password.pack()
        pass_entry = CTkEntry(top, placeholder_text="password", text_color="white")
        pass_entry.pack()
        add_button=CTkButton(master=top,text="Add",border_color="blue",corner_radius=50,command=lambda: add_account(entry.get(),pass_entry.get()))
        add_button.pack(pady=10)
        app._popup = top

        def add_account(usrnamr,passwor):
            payload_entry(usrnamr, passwor)
            top.destroy()
            top.update()

def open_funny():
        funny_popup = customtkinter.CTkToplevel(app)
        funny_popup.geometry("250x250")
        funny_popup.title("secrect")
        ulabel = CTkLabel(master=funny_popup, text="\"Yes ,this tick sign is stolen from the website,\n your dont have to click it \"")
        ulabel.pack(pady=50)
        add_button=CTkButton(master=funny_popup,text="this button does noting ",border_color="blue",corner_radius=50)
        add_button.pack(pady=10)
       
  
 

    
  



app=CTk()
app.geometry("250x500")
app.title("WifiLogger")
app.configure(fg_color="#31263e")
img=Image.open("connected.png")
customtkinter.set_appearance_mode("Dark")
app.iconbitmap("app_icon.ico")
connectedimage=CTkButton(master=app,
                         height=55,
                         width=53,
                         text="",
                         border_color="#31263e",
                         fg_color="transparent",
                         hover_color="#31263e",
                         image=CTkImage(light_image=img,dark_image=img),
                         command=open_funny)
connectedimage.place_forget()


username_label=CTkLabel(master=app,font=("Helvetica",15),text="User-id:",text_color="white")
username_label.place(relx=0.38,rely=0.33,anchor="center")
comboBox=CTkComboBox(master=app,
                     values=get_usernames_from_json(),
                     fg_color="black",
                     dropdown_fg_color="#221e22",
                     dropdown_hover_color="#eca72c",
                     bg_color="#221e22",
                     border_color="#de9e36",
                     dropdown_text_color="#f0eff4",
                     button_color="#de9e36",
                     button_hover_color="white",
                     height=35
                    )
comboBox.place(relx=0.5,rely=0.4, anchor="center")
userid_details=CTkLabel(master=app,font=("Helvetica",15),
                        text="User-id:",
                        text_color="white")
userid_details.place_forget()

button=CTkButton(master=app,text="login",
                 border_color="#3f7d20",
                 fg_color="#3f7d20",
                 corner_radius=50,
                 hover_color="#eca72c",
                 command= check_wifi_login)
button.place(relx=0.5,rely=0.5,anchor="center")

img_dark=Image.open("dark_plus.png")
img_light=Image.open("light_plus.png")
add_button=CTkButton(master=app,text="",
                     width=5,
                     corner_radius=100,
                     fg_color="#f0eff4",
                     hover_color="#eca72c",
                     border_width=0,
                     image=CTkImage(dark_image=img_dark,
                                    light_image=img_light),
                     command=open_popup)
add_button.place(relx=0.95,rely=0.95,anchor="se")

app.mainloop()