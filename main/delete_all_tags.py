import os
import tkinter
from tkinter.filedialog import askdirectory

import requests
from bs4 import BeautifulSoup
from mutagen.flac import FLAC
import mutagen
from mutagen.mp3 import MP3

def main():
    print("start")
    tracks = []
    root = tkinter.Tk()
    root.withdraw()
    root.update()
    folder = askdirectory(title = "choose the dir u want to delete on tags in",initialdir = r"C:\Users\User\Desktop", mustexist=True )
    root.destroy()


    for root, dirs, files, in os.walk(folder):
        for name in files:
            if name.endswith((".mp3", ".flac")):
                print("the name= "+os.path.splitext(name)[0])
                print("the type= "+os.path.splitext(name)[1])
                if(name.endswith(".flac")):
                    print("its .flac")
                    audio=FLAC(root + "\\" + name)
                    audio.delete()
                    audio.clear_pictures()
                    audio.save()
                if(name.endswith(".mp3")):
                    print("its .mp3")
                    audio=MP3(root + "\\" + name)
                    audio.delete()
                    audio.clear()
                    audio.save()


if __name__ == "__main__":
    main()