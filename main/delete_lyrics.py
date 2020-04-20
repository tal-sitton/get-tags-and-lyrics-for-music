import os
import tkinter
from tkinter.filedialog import askdirectory

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import EasyMP3, MP3


def main():
    root = tkinter.Tk()
    root.withdraw()
    root.update()
    folder = askdirectory(title = "choose the dir u want get tags to",initialdir = r"C:\Users\User\Desktop", mustexist=True )
    root.destroy()
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name.endswith((".mp3", ".flac")):
                fileType = os.path.splitext(name)[1]
                if fileType== ".mp3":
                    audio = ID3(root + "\\" + name)
                    # audio["USLT::'eng'"] = ""
                    audio.delall(u"USLT")
                    audio.save(root + "\\" + name)
                    print("deleted lyrics from the file "+name)

                elif fileType==".flac":
                    audio=FLAC(root + "\\" + name)
                    audio["Lyrics"]=""
                    audio["ALBUMARTIST"] = ""
                    audio.save()
                    print("deleted lyrics from the file "+name)


if __name__ == '__main__':
    main()
