import Tkinter, Tkconstants, tkFileDialog
from Tkinter import *
import os
import glob
import shutil #untuk delete file dalam directory
import winsound #untuk play dan stop music
from splitterkit import readwave, writewave, split, merge, combine, split_s, slicewave_s #import semua fungsi di splitterkit.py

root = Tkinter.Tk()#membuat window baru

#create blank tabel
def blank(i,j):
        enter = Tkinter.Label(root)
        enter.grid(row=i,column=j)

#perhitungan durasi
def duration(file,string):
        wav_name = {}
        j = 0
        durasi = int(input_durasi.get())
        jeda_durasi = int(input_jeda_durasi.get())
        data = readwave(file)
        if jeda_durasi <= 0:
                splitted = split_s(data,durasi*2)
        else:
                splitted = split_s(data,jeda_durasi*2,durasi*2) #split dengan second dan overlap
        output = writewave("destination/"+"%s_Split_"%string,splitted) #output nama file.wav disimpan di folder destination
        for i in output:
                i = str(i)
                i = i.split("/") #mendapat nama file saja
                wav_name[j] = i[1]
                tabel_isi(j+8,j+1,wav_name[j],"","","","","")
                j = j+1
        
        
#fungsi untuk tombol browse
def browse():
        file_dialog = Tkinter.Tk()
        file_dialog.withdraw()
        global file_name #global variabel
        global string
        file_name = tkFileDialog.askopenfilename(initialdir = "/",title = "Select File",filetypes = (("wav file","*.wav"),("all files","*.*")))

        split_file_name = file_name.split("/")
        input_browse.insert(1,(split_file_name[len(split_file_name)-1]))
        string = split_file_name[len(split_file_name)-1].split(".wav")

#untuk mulai split
def go():
        if len(os.listdir("destination/")) != 0:
                shutil.rmtree("destination/") #delete all file in destination
                
        duration(file_name,string[0])


#fungsi untuk play music pada folder destination
def play_music(wav_name):
        winsound.PlaySound("destination/"+wav_name,winsound.SND_FILENAME|winsound.SND_ASYNC)

#fungsi untuk stop music pada folder destination
def stop_music(wav_name):
        winsound.PlaySound(None, winsound.SND_FILENAME|winsound.SND_ASYNC)

#create tabel
def tabel_isi(baris,no,filename,jpa,lpa,jpp,lpp,data):
        btn_play =  {} #array button play
        btn_stop =  {} #arrat button stop
        wav_name = {} #array nama lagu
        for i in range(baris,baris+1):
                for j in range(9):
                        if(j == 0):
                                string = str(no)
                        elif(j == 1):
                                string = str(filename)
                                wav_name[i] = str(string)
                        elif(j == 2):#membuat button play
                                btn_play[i] = Tkinter.Button(root, text = "PLAY", command=lambda: play_music(wav_name[i]))
                                btn_play[i].grid(row=i,column=j)
                        elif(j == 3):#membuat button stop
                                btn_stop[i] = Tkinter.Button(root, text = "STOP", command=lambda: stop_music(wav_name[i]))
                                btn_stop[i].grid(row=i,column=j)
                        elif(j == 4):
                                string = str(jpa)
                        elif(j == 5):
                                string = str(lpa)
                        elif(j == 6):
                                string = str(jpp)
                        elif(j == 7):
                                string = str(lpp)
                        else:
                                string = str(data)
                        if j < 2 or j > 3:#saat yang ditampilkan adalah bukan button
                                tabel = StringVar()
                                tabel = Entry(root,width=30, textvariable=tabel)
                                tabel.insert(1," %s"%(string))#insert data tabel
                                tabel.grid(row=i, column=j)

#menulis judul pada window
root.title("Browse Music")

baris = 0
#membuat inputan browse
input_browse = StringVar()
input_browse = Tkinter.Entry(root, textvariable=input_browse,width=30)
input_browse.grid(row=0,column=0)

#membuat tombol browse
btn_browse = Tkinter.Button(root, text = "BROWSE", command=browse)
btn_browse.grid(row=0,column=1)

blank(1,0)
#membuat label durasi
label_durasi = Tkinter.Label(root, text="JEDA SPLIT")
label_durasi.grid(row=baris+2,column=0)
#membuat inputan durasi
input_jeda_durasi = Spinbox(root,from_=0,to=3600,state="normal",width=28)
input_jeda_durasi.grid(row=baris+2,column=1)

blank(baris+3,0)
#membuat label durasi
label_durasi = Tkinter.Label(root, text="DURASI")
label_durasi.grid(row=baris+4,column=0)
#membuat inputan durasi
input_durasi = Spinbox(root,from_=0,to=3600,state="normal",width=28)
input_durasi.grid(row=baris+4,column=1)
#membuat tombol go
btn_split = Tkinter.Button(root, text = "SPLIT", command=go)
btn_split.grid(row=baris+4,column=2)

blank(baris+5,0)
#membuat tabel header
tabel = Tkinter.Label(root,text = "NO")
tabel.grid(row=baris+6, column=0)

tabel = Tkinter.Label(root,text = "FILENAME")
tabel.grid(row=baris+6, column=1)

tabel = Tkinter.Label(root,text = "PLAYER")
tabel.grid(row=baris+6, column=2)

tabel = Tkinter.Label(root,text = "MUSIC")
tabel.grid(row=baris+6, column=3)

tabel = Tkinter.Label(root,text = "JENIS PUPUH ASLI")
tabel.grid(row=baris+6, column=4)

tabel = Tkinter.Label(root,text = "LARAS PUPUH ASLI")
tabel.grid(row=baris+6, column=5)

tabel = Tkinter.Label(root,text = "JENIS PUPUH PENGENALAN")
tabel.grid(row=baris+6, column=6)

tabel = Tkinter.Label(root,text = "LARAS PUPUH PENGENALAN")
tabel.grid(row=baris+6, column=7)

tabel = Tkinter.Label(root,text = "DATA")
tabel.grid(row=baris+6, column=8)

tabel_isi(baris+8,"","","","","","","")#buat tabel pertama untuk display aja

root.mainloop()
