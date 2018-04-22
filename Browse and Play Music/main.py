import Tkinter
from Tkinter import *
import glob
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
	data = readwave(file)
	splitted = split_s(data,durasi,durasi*durasi) #split dengan second dan overlap
	output = writewave("destination/"+"%s_Split_"%string,splitted) #output nama file.wav disimpan di folder destination
	for i in output:
		i = str(i)
		i = i.split("/") #mendapat nama file saja
		wav_name[j] = i[1]
		tabel_isi(j+5,j+1,wav_name[j],"","")
		j = j+1

#fungsi untuk tombol browse
def browse():
	string = str(input_browse.get())
	for file in glob.glob("source/"+string+".wav"): #read file dari folder source
		duration(file,string)

#fungsi untuk play music pada folder destination
def play_music(wav_name):
	winsound.PlaySound("destination/"+wav_name,winsound.SND_FILENAME|winsound.SND_ASYNC)

#fungsi untuk stop music pada folder destination
def stop_music(wav_name):
	winsound.PlaySound(None, winsound.SND_FILENAME)

#create tabel
def tabel_isi(baris,no,filename,pengenalan,data):
	btn_play =  {} #array button play
	btn_stop =  {} #arrat button stop
	wav_name = {} #array nama lagu
	for i in range(baris,baris+1):
		for j in range(6):
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
				string = str(pengenalan)
			else:
				string = str(data)
			if j < 2 or j > 3:#saat yang ditampilkan adalah bukan button
				tabel = StringVar()
				tabel = Entry(root,width=22, textvariable=tabel)
				tabel.insert(1," %s"%(string))#insert data tabel
				tabel.grid(row=i, column=j)

#menulis judul pada window
root.title("Browse Music")

#membuat tombol browse
btn_browse = Tkinter.Button(root, text = "BROWSE", command=browse)
btn_browse.grid(row=0,column=1)
#membuat inputan browse
input_browse = StringVar()
input_browse = Tkinter.Entry(root, textvariable=input_browse)
#input_browse.insert(1,"asdfgh")
input_browse.grid(row=0,column=0)

blank(1,0)
#membuat label durasi
label_durasi = Tkinter.Label(root, text="DURASI")
label_durasi.grid(row=2,column=0)
#membuat inputan durasi
input_durasi = Spinbox(root,from_=0,to=3600,state="normal")
input_durasi.grid(row=2,column=1)

blank(3,0)
#membuat tabel header
tabel = Tkinter.Label(root,text = "NO")
tabel.grid(row=4, column=0)

tabel = Tkinter.Label(root,text = "FILENAME")
tabel.grid(row=4, column=1)

tabel = Tkinter.Label(root,text = "PLAYER")
tabel.grid(row=4, column=2)

tabel = Tkinter.Label(root,text = "MUSIC")
tabel.grid(row=4, column=3)

tabel = Tkinter.Label(root,text = "PENGENALAN")
tabel.grid(row=4, column=4)

tabel = Tkinter.Label(root,text = "DATA")
tabel.grid(row=4, column=5)

tabel_isi(5,"","","","")#buat tabel pertama untuk display aja

root.mainloop()
