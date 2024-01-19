from customtkinter import *
from tkinter import *
from tkinter import messagebox,ttk
from PIL import Image,ImageTk
from ultralytics import YOLO
from tracker import *
import cv2
import os

file=""
violations=""
total=""

video_playing = False

class ObjectDetector:
    def __init__(self, filename):

        # Initializing the user input video using opencv
        self.cap = cv2.VideoCapture(filename)
        self.model = YOLO(r"assets\yolov8s.pt")

        # self.tracker makes sure that the detected object isnt detected as a new object again
        self.tracker = EuclideanDistTracker()
        
        # Initializing the counters for RED mode and GREEN mode 
        self.counter_red = 0
        self.counter_green = 0

        # Creating the window that contains the canvas and buttons
        self.root = CTkToplevel(app)
        self.root.after(201, lambda :self.root.iconbitmap(r'assets\trfx.ico'))
        self.root.title("Object Detection")
        self.root.resizable(width=False,height=False)
        self.root.protocol("WM_DELETE_WINDOW",self.nextButton)

        # Creating the style object to modify the button apearences
        self.green_button_style = ttk.Style()
        self.green_button_style.configure(
            "Green.TRadiobutton", 
            background = 'GRAY', 
            foreground = 'GREEN')

        self.red_button_style = ttk.Style()
        self.red_button_style.configure(
            "Red.TRadiobutton", 
            background = 'GRAY', 
            foreground = 'RED')
        
        # Creating the canvas that holds the processed frame
        self.canvas = Canvas(self.root, width=640, height=480,highlightthickness=0)
        self.canvas.pack(side=LEFT,padx=10,pady=10)

        # Creating the frame to store the RED, GREEN and NEXT buttons
        self.radio_frame = CTkFrame(self.root)
        self.radio_frame.pack(side=RIGHT, padx=20,ipadx=5,ipady=5)

        # Creating the RED, GREEN and NEXT buttons
        self.radio_var = IntVar()
        self.radio_button1 = CTkRadioButton(self.radio_frame, text="Red", variable=self.radio_var, value=1,fg_color="#C70039",hover_color="#9d002d",text_color="#C70039",font=("Sofachrome Rg",9))
        self.radio_button2 = CTkRadioButton(self.radio_frame, text="Green", variable=self.radio_var, value=0,fg_color="#1D8348",hover_color="#14562f",text_color="#1D8348",font=("Sofachrome Rg",9))
        self.next_button = CTkButton(self.radio_frame, text="Next",command=self.nextButton,corner_radius=100,font=("Sofachrome Rg",7),fg_color="#C70039",hover_color="#9d002d")
        self.radio_button1.pack(anchor=W)
        self.radio_button2.pack(anchor=W)
        self.next_button.pack(anchor=W)

    def detect(self):
        global violations,total
        self.id_index = []
        _,self.first_frame = self.cap.read()
        self.frame_width = self.first_frame.shape[1]
        print(self.frame_width)
        while True:
            detections = []
            self.ret, frame = self.cap.read()
            if self.ret:
                roi = frame[340:720, :]
                results = self.model.predict(roi)
                result = results[0]
                cv2.line(frame, (0, 600), (self.frame_width, 600), color=(0, 255, 0), thickness=2)
                cv2.putText(frame, str(self.counter_red), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, str(self.counter_green), (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                for box in result.boxes:
                    conf = round(box.conf.item(), 2)
                    class_id = result.names[box.cls[0].item()]
                    if conf > 0.40 and class_id in ['car', 'truck','bike']:
                        cords = box.xyxy[0].tolist()
                        cords = [round(x) for x in cords]
                        detections.append(cords)

                detections_with_ids = self.tracker.update(detections)

                for detection in detections_with_ids:
                    cx = ((detection[0] + detection[2]) // 2)
                    cy = ((detection[1] + detection[3]) // 2) + 350

                    cv2.circle(frame, (cx, cy), color=(255, 0, 0), thickness=10, radius=5)
                    cv2.rectangle(frame, (detection[0], detection[1] + 350), (detection[2], detection[3] + 350),
                                  color=(0, 0, 0), thickness=2)
                    cv2.putText(frame, str(detection[-1]), (detection[0], detection[1] + 350), cv2.FONT_HERSHEY_COMPLEX,
                                1, (0, 0, 255), 1)
                    if cy > 600 and detection[-1] not in self.id_index and cy < 610:
                        if self.radio_var.get() == 0:
                            self.counter_green += 1
                        else:
                            self.counter_red += 1
                        self.id_index.append(detection[-1])

                # Convert the OpenCV frame to a PhotoImage object for displaying on the canvas
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (640,480))
                img = ImageTk.PhotoImage(master=self.root,image=Image.fromarray(img))
                self.canvas.create_image(0, 0, anchor=NW, image=img)
                #self.canvas.photo = img
                self.root.update()

            else:
                self.cap.release()
                cv2.destroyAllWindows()
                self.root.destroy()
                new_win(self.counter_red,(self.counter_red+self.counter_green))
    
    def nextButton(self):
        self.cap.release()



# FINAL WINDOW
def new_win(count_red,count_total):
    global roof,file
    roof = CTk()
    roof.after(201, lambda :roof.iconbitmap(r'assets\trfx.ico'))
    roof.title("Traffix™")

    width = 1280
    height = 720 
    screen_width = app.winfo_screenwidth()  
    screen_height = app.winfo_screenheight() 

    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    roof.geometry('%dx%d+%d+%d' % (width, height, x, y))

    f=CTkFrame(roof)
    f_=CTkFrame(f,corner_radius=25)
    T=CTkLabel(f,text="Traffix™",font=("Sofachrome Rg",70))
    S=CTkLabel(f,text="")
    L1=CTkLabel(f_,text=file.split("/")[-1],font=("Sofachrome Rg",30),fg_color="#C70039",corner_radius=100)
    L2=CTkLabel(f_,text="TOTAL VEHICLES:  "+str(count_total),font=("Sofachrome Rg",15),text_color="#1D8348")
    L3=CTkLabel(f_,text="NO. OF VIOLATIONS:  "+str(count_red),font=("Sofachrome Rg",15),text_color="#C70039")
    n=CTkButton(roof,text="Return",hover=True,corner_radius=1000,font=("Sofachrome Rg",9),fg_color="#C70039",hover_color="#9d002d",command=next)
    f.pack(fill=BOTH,expand=True,pady=45,padx=20)
    T.pack(anchor=CENTER,padx=10,pady=5)
    S.pack(pady=100)
    f_.pack(ipadx=100,ipady=10)
    L1.pack(anchor=CENTER,padx=10,pady=10)
    L2.pack(anchor=W,padx=10,pady=5)
    L3.pack(anchor=W,padx=10,pady=5)

    n.place(relx=0.885,rely=0.95)
    
    roof.resizable(width=False,height=False)
    roof.protocol("WM_DELETE_WINDOW", next)
    roof.mainloop()

def main():
    global app
    app=CTk()
    app.title("Traffix™")
    app.after(201, lambda :app.iconbitmap(r'assets\trfx.ico'))

    width = 1280
    height = 720 
    screen_width = app.winfo_screenwidth()  
    screen_height = app.winfo_screenheight() 

    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    app.geometry('%dx%d+%d+%d' % (width, height, x, y))


    #WIDGETS

    global srch    
    f=CTkFrame(app,corner_radius=17)
    spc=CTkLabel(app,text="")
    l1=CTkLabel(app,text='Traffix™',font=("Sofachrome Rg",90))
    l2=CTkLabel(app,text='Red Light. Brake Right.',font=("Sofachrome Rg",20),fg_color="#C70039",corner_radius=17)
    b1=CTkButton(f,text="Browse",corner_radius=1000,command=opf2,font=("Sofachrome Rg",9),fg_color="#CEAC35",hover_color="#a4892e")
    srch=CTkEntry(f,placeholder_text="Paste the file path here or press the browse button...",width=700,corner_radius=1000,font=("Sofachrome Rg",10))
    b2=CTkButton(f,text="Exit",corner_radius=1000,command=close,font=("Sofachrome Rg",9),fg_color="#1D8348",hover_color="#14562f")
    b3=CTkButton(f,text="Open",corner_radius=1000,command=opf1,font=("Sofachrome Rg",9),fg_color="#C70039",hover_color="#9d002d")

    #WIDGET POSITION

    f.grid(row=3,column=0,columnspan=3,ipadx=5,ipady=5,padx=8,sticky="N")
    l1.grid(row=0,pady=10)
    l2.grid(row=1,pady=10)
    spc.grid(row=2,pady=100)
    b3.grid(row=0,column=1,pady=5)
    srch.grid(row=0,column=0,padx=10,pady=5)
    b1.grid(row=1,column=1)
    b2.grid(row=2,column=1,pady=5)
   
    app.resizable(width=False,height=False)
    app.grid_columnconfigure(0,weight=1)
    app.mainloop()

#BUTTON COMMANDS

def opf1():
    global file
    file_path = srch.get()
    file=file_path
    if os.path.exists(file_path):
        app.withdraw()
        obj = ObjectDetector(file_path)
        obj.detect()
    else:
        nofile=messagebox.showerror(title="Error",message="File Not Found")    

def opf2():
    global file
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
    file=file_path
    if os.path.exists(file_path):
        app.withdraw()
        obj = ObjectDetector(file_path)
        obj.detect()
    else:
        nofile=messagebox.showerror(title="Error",message="File Not Found")

def close():
    global video_playing
    video_playing = False
    app.destroy()

def next():
    roof.destroy()
    app.deiconify()

main()