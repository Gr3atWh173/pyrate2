#!/usr/bin/env python
# TODO: Make this work with platforms other than Windows lmao

import _thread as thread
import os

from tkinter import ttk
import tkinter as tk

import pafy
from pydub import AudioSegment


class Pyrate2(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)
    self.title("Pyrate 2 Copyleft 2018 GreatWhite")
    
    # hack to get a custom icon because tkinter's preferred method does not work
    self.tk.call('wm', 'iconphoto', self._w, tk.PhotoImage(file='icon.png'))  
    self.resizable(False, False)

    # some needed variables
    self.dl_audio_state = tk.IntVar() # if the 'download audio' checkbox is checked
    self.dl_video_state = tk.IntVar() # if the 'download video' checkbox is checked
    self.total_given    = False       # if the total amount of the file to be downloaded is given
    self.script_dirc    = os.getcwd() # the scripts current directory
    self.downloaded     = ''          # full path of the downloaded file
    
    # UI elements
    self.url = tk.Entry(width=50)
    self.download = tk.Button(text="Download", width=12, command=self.begin_download)
    self.output = tk.Text(height=15, width=52)
    self.dl_video = tk.Checkbutton(text="Video", variable=self.dl_video_state)
    self.dl_audio = tk.Checkbutton(text="Audio", variable=self.dl_audio_state)
    self.label_1 = tk.Label(text="Download: ")
    self.label_2 = tk.Label(text="Paste the URL below (ctrl + v): ")
    self.progress_bar = ttk.Progressbar(orient=tk.HORIZONTAL, length=420, mode="determinate")

    # place UI elements on the grid
    self.url.grid(column=1, ipadx=10, ipady=3, padx=10, pady=0, row=1, rowspan=2)
    self.download.grid(column=6, columnspan=33, row=1)
    self.output.grid(column=0, columnspan=50, row=5, padx=10, pady=5)
    self.dl_audio.grid(column=1, row=3, sticky="e", pady=10)
    self.dl_video.grid(column=0, row=3, columnspan=6, pady=10)
    self.label_1.grid(column=0, columnspan=2, row=3, sticky="w", padx=10, pady=10)
    self.label_2.grid(column=0, columnspan=4, row=0, sticky="w", padx=10)
    self.progress_bar.grid(column=0, columnspan=50, row=4)
  
  def begin_download(self):
    '''
    Callback of the 'download' button.
    Downloads audio, video or both depending on what
    is checked.
    '''
    url = self.url.get()

    # check if the url feild is empty
    if not url:
      self.output.insert(tk.END, "[*] Please give a valid URL")
      return

    # start downloads in new thread or else pafy
    # will block the current thread.
    if(self.dl_audio_state.get()):
      thread.start_new_thread(self.download_audio, (url,))
    if(self.dl_video_state.get()):
      thread.start_new_thread(self.download_video, (url,))
    
  def download_audio(self, url):
    '''
    Given a url as parameter, downloads the audio
    '''
    self.progress_bar["value"] = 0
    self.output.delete('1.0', tk.END)
    self.output.insert(tk.END, "[*] Download in progress...\n")

    try:
      os.chdir(os.environ['USERPROFILE'] + "/music")
      downloaded = pafy.new(url).getbestaudio().download(quiet=True, callback=self.handler)
      self.downloaded = os.path.realpath(downloaded)
      filename, extension = os.path.splitext(self.downloaded)
    except IOError:
      self.output.insert(tk.END, "[*] Sorry, but that video is not available")
      self.total_given = False
      return

    # mp3s are more compatible. Change the format to mp3
    os.chdir(self.script_dirc)
    if extension != "mp3": 
        self.output.insert(tk.END, "[*] Converting to mp3\n")
        AudioSegment.from_file(self.downloaded, extension[1:]).export(filename + ".mp3")
        self.output.insert(tk.END, "[*] Deleting original\n")
        os.remove(self.downloaded)

    self.output.insert(tk.END, "[*] Download Completed.\n")
    self.output.insert(tk.END, "[*] File saved at {}".format(os.environ['USERPROFILE']+"/music"))
    self.total_given = False
    self.downloaded = ''
  
  def download_video(self, url):
    '''
    Given a url in parameter, downloads video (With audio)
    '''
    self.progress_bar["value"] = 0
    self.output.delete('1.0', tk.END)
    self.output.insert(tk.END, "[*] Download in progress...\n")

    os.chdir(os.environ['USERPROFILE'] + "/videos")
    try:
      downloaded = pafy.new(url).getbest().download(quiet=True, callback=self.handler)
    except IOError:
      self.output.insert(tk.END, "[*] Sorry, but that video is not available")
      self.total_given = False
      return

    os.chdir(self.script_dirc)
    self.output.insert(tk.END, "[*] Download complete\n")
    self.output.insert(tk.END, "[*] File saved at {}".format(os.environ['USERPROFILE']+"/videos"))
    self.total_given = False

  def handler(self, total, recvd, ratio, rate, eta):
    '''
    Custom callback for pafy's download method.
    Makes the progressbar move.
    '''
    if not self.total_given:
      self.progress_bar["value"] = 0
      self.progress_bar["maximum"] = total
      self.total_given = True
    else:
      self.progress_bar["value"] = recvd

app = Pyrate2()
app.mainloop()
