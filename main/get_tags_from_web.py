import datetime
import logging
import os
import re
import tkinter
from tkinter.filedialog import askdirectory
from urllib.request import urlopen

import mutagen
from mutagen import id3
from mutagen.id3 import USLT, ID3, TRCK, APIC, ID3NoHeaderError, TPE1, TALB, TIT2, SYLT, TORY, TYER, TPE2, TCON
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3, EasyMP3
import requests
from bs4 import BeautifulSoup

HEADERS_GET = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

WIKI_SEARCH_RESULT_ATTRS = {"class": "mw-search-result-heading"}
WIKI_SEARCH_RESULT_DESCRIPTION_ATTRS = {"class": "searchresult"}
WIKI_TABLE_ATTRS1 = {"style": "background-color:#fff"}
WIKI_TABLE_ATTRS2 = {"style": "background-color:#f7f7f7"}
GOOGLE_ARTISTS_TAG_ATTRS = {"class": "uDMnUc"}
ANOTHER_GOOGLE_ARTISTS_TAG_ATTRS = {"class": "LrzXr kno-fv"}
GOOGLE_SONG_TAG_ATTRS = {"class": "title"}
GOOGLE_ALBUM_TAG_ATTRS = {"class": "FLP8od"}
GOOGLE_ARTIST_TAG_ATTRS = {"class": "FLP8od"}
SYNCED_LYRICS_SEARCH_RESULT_ATTRS = {"class": "li"}
THE_SYNCED_LYRICS_ATTRS = {"class": "entry"}
THE_LYRICS_ATTRS = {"jsname": "YS01Ge"}
FIRST_GOOGLE_PHOTOS_ATTRS = {"class": "wXeWr islib nfEiy mM5pbd"}
WIKI_COVER_ART_ATTR = {"class": "image"}
GOOGLE_DATE_ATTRS = {"class": "Z0LcW"}
GOOGLE_GENRE_TAG_ATTRS = {"class": "title"}
GOOGLE_GENRE2_TAG_ATTRS = {"class": "FLP8od"}
GOOGLE_GENRE3_TAG_ATTRS = {"class": "Z0LcW"}
WIKI_ALBUM_ATTRS = {"title": "Album"}


# WIKI_TABLE_ATTRS = {"class": "tlheader"}

def is_number(n):
    try:
        float(n)  # Type-casting the string to `float`.
        # If string is not a valid `float`,
        # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True


def searchPhoto(url):
    if url:
        res = requests.get(url, headers=HEADERS_GET)
        soup = BeautifulSoup(res.content, 'html.parser')
        tags = [tag for tag in soup.find_all(attrs=WIKI_COVER_ART_ATTR)]
        if tags:
            tag = tags[0]
            tag = str(tag)[str(tag).find("src") + 5:]
            tag = str(tag)[:str(tag).find(" ") - 1]
            newtag = "https:"
            newtag += tag
            print(newtag)
            return newtag
        else:
            return "https://music.uberchord.com/assets/images/png/placeholder-song.png"
    else:
        return "https://music.uberchord.com/assets/images/png/placeholder-song.png"


def searchInWiki(title, albums, artists):
    i = 0
    trueURL = []
    while i < len(artists):
        found = False
        tempAlbum = albums[i]
        print("tempAlbum= " + str(tempAlbum))
        tempArtist = artists[i]
        print("tempArtist= " + str(tempArtist))
        if (albums[i] == False):
            tempAlbum = str(title)
            print("new tempAlbum= " + tempAlbum)

        query = "{title} {art}".format(art=tempArtist, title=tempAlbum).replace(" ", "+").replace("&", "and")
        search = "https://en.wikipedia.org/w/index.php?cirrusUserTesting=glent_m0&sort=relevance&search={query}&title=Special:Search&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1".format(
            query=query)
        res = requests.get(search, headers=HEADERS_GET).text
        soup = BeautifulSoup(res, 'html.parser')
        tags = [tag for tag in soup.find_all(attrs=WIKI_SEARCH_RESULT_ATTRS)]
        items_hrefs = ['https://en.wikipedia.org/{}'.format(tag.find_next('a', href=True).get('href')) for tag in tags]
        print("item_hrefs= {}".format(items_hrefs))
        for j in items_hrefs:
            # print("j= "+j)
            if (j.lower().__contains__(tempArtist.lower())) and j.lower().__contains__(
                    tempAlbum.lower()) and j.lower().__contains__("album"):
                print("1 found the song by {} in: {}".format(tempArtist, j))
                trueURL.append(j)
                found = True
                break
            else:
                if (j.lower().__contains__(tempAlbum.lower())) and j.lower().__contains__(tempArtist.lower()):
                    print("2 found the song by {} in: {}".format(tempArtist, j))
                    trueURL.append(j)
                    found = True
                    break
                else:
                    if (j.lower().__contains__(tempAlbum.lower())) and j.lower().__contains__("album"):
                        print("3 found the song by {} in: {}".format(tempArtist, j))
                        trueURL.append(j)
                        found = True
                        break
                    else:
                        if tempAlbum != title:
                            if j.lower().__contains__(tempAlbum.lower()):
                                print("4 found the song by {} in: {}".format(tempArtist, j))
                                trueURL.append(j)
                                found = True
                                break
        if not found:
            done = False
            newtags = [tag.text for tag in soup.find_all(attrs=WIKI_SEARCH_RESULT_DESCRIPTION_ATTRS)]
            print(str(newtags))
            try:
                if items_hrefs[2].__contains__("album") and not items_hrefs[0].__contains__("album") and not \
                items_hrefs[1].__contains__("album") and str(newtags[2]).lower().__contains__(tempArtist.lower()):
                    print("4.1 found the song by {} in: {}".format(tempArtist, items_hrefs[2]))
                    trueURL.append(items_hrefs[2])
                    done = True
            except IndexError:
                print("there wa no other option")
            try:
                if not done and items_hrefs[0].lower().__contains__("band") and str(newtags[1]).lower().__contains__(
                        tempArtist.lower()) or (
                        items_hrefs[1].lower().__contains__("album") and not items_hrefs[0].lower().__contains__(
                        "album")):
                    print(str(newtags[1]).lower().__contains__(tempArtist))
                    print("4.5 found the song by {} in: {}".format(tempArtist, items_hrefs[1]))
                    trueURL.append(items_hrefs[1])
                    done = True
            except IndexError:
                print("there wa no other option")

            try:
                if not done and str(newtags[0]).lower().__contains__(tempArtist.lower()):
                    print("5 found the song by {} in: {}".format(tempArtist, items_hrefs[0]))
                    trueURL.append(items_hrefs[0])
                    done = True
            except IndexError:
                print("there is no option- no wiki pages found")
                trueURL.append(False)
            if not done:
                trueURL.append(False)
        i += 1
    return trueURL


def searchWikiForAlbum(title, artist):
    url = searchInWiki(title, [title], [artist])
    url = url[0]
    if (url):
        res = requests.get(url, headers=HEADERS_GET).text
        soup = BeautifulSoup(res, 'html.parser')
        tags = [tag for tag in soup.find_all(attrs=WIKI_ALBUM_ATTRS)]
        if tags:
            album = url[url.rfind('/') + 1:]
            album = album.replace(artist, '')
            album = album.replace('album', '')
            album = album.replace('(', '').replace(')', '')
            album = album.replace("_", " ")
            album = album.replace("%3F", "?")
            album = album.replace("%27", "`")
            album = album.strip()
            print(album)
            return album
        else:
            return False
    else:
        return False


def searchForLength(trueUrl, title, artists):
    lengths = []
    j = 0
    while j < len(trueUrl):
        found = False
        tempUrl = trueUrl[j]
        if tempUrl:
            res = requests.get(tempUrl, headers=HEADERS_GET).text
            soup = BeautifulSoup(res, 'html.parser')
            tags = [tag.text for tag in soup.find_all(attrs=WIKI_TABLE_ATTRS1)]
            for i in tags:
                # print(i)
                if i.__contains__(title) and not i.__contains__("acoustic") and not i.__contains__("live"):
                    print(i)
                    newi = i[-5:]
                    if not is_number(newi[0]):
                        newi = '0' + newi[-4:]
                        print("{artist}'s song length: ".format(artist=artists[j]) + newi)
                    lengths.append(newi)
                    found = True
                    break

            if not found:
                tags = [tag.text for tag in soup.find_all(attrs=WIKI_TABLE_ATTRS2)]
                for i in tags:
                    # print(i)
                    if i.__contains__(title) and not i.__contains__("acoustic"):
                        # print(i)
                        newi = i[-5:]
                        if not is_number(newi[0]):
                            newi = '0' + newi[-4:]
                            print("{artist}'s song length: ".format(artist=artists[j]) + newi)
                        lengths.append(newi)
                        found = True
                        break
            if (not found):
                print("sorry, didnt found the length for the song {song} by {art}".format(song=title, art=artists[j]))
                lengths.append(False)
        else:
            lengths.append(False)
        j += 1
    return lengths


def searchForAnArtist(title):
    query = "{title}".format(title=title).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+artist".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    artist = [tag.text for tag in soup.find_all(attrs=GOOGLE_ARTIST_TAG_ATTRS)]
    if artist:
        return artist[0]

    query = "{title}".format(title=title).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+song".format(lang='en', query=query)
    print(search)
    res = requests.get(search, headers=HEADERS_GET).text
    with open(r"C:\Users\talsi\Desktop\test10.html", 'w', encoding='utf-8') as f:
        f.write(res)
    soup = BeautifulSoup(res, 'html.parser')
    artist = [tag.text for tag in soup.find_all(attrs=ANOTHER_GOOGLE_ARTISTS_TAG_ATTRS)]
    if artist:
        return artist[0]
    return []


def searchForAnAlbum(title, artist):
    query = "{title} by {artist}".format(title=title, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+album".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    temp_albums = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
    if not temp_albums:
        query = "{title} {artist}".format(title=title, artist=artist).replace(" ", "+").replace("&", "and")
        search = "https://google.com/search?hl={lang}&q={query}+album".format(lang='en', query=query)
        res = requests.get(search, headers=HEADERS_GET).text
        soup = BeautifulSoup(res, 'html.parser')
        album = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
        if album:
            print("the album for the song {title} by {artist} is: ".format(title=title, artist=artist) + album[0])
            return album[0]
        query = "{title} by {artist}".format(title=title, artist=artist).replace(" ", "+").replace("&", "and")
        search = "https://google.com/search?hl={lang}&q={query}+song+album".format(lang='en', query=query)
        res = requests.get(search, headers=HEADERS_GET).text
        with open(r"C:\Users\talsi\Desktop\test4.html", 'w', encoding='utf-8') as f:
            f.write(res)
        soup = BeautifulSoup(res, 'html.parser')
        temp_albums2 = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
        if temp_albums2:
            return temp_albums2[0]
        temp_albums3 = searchWikiForAlbum(title, artist)
        if (temp_albums3):
            return temp_albums3[0]
        print("didnt find album to {title} by {artist}".format(title=title, artist=artist))
        return title
    else:
        if temp_albums:
            temp_albums = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
            print("the album for the song {title} by {artist} is: ".format(title=title, artist=artist) + temp_albums[0])
            return temp_albums[0]


def searchForArtist(title):
    query = "{title}".format(title=title).replace(" ", "+").replace("&", "and")
    # search = "https://www.google.com/search?q={query}+song&ie=utf-8&oe=utf-8'".format(query=query) //doesnt work (
    # its hebrew)
    search = "https://google.com/search?hl={lang}&q={query}+song".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    with open(r"C:\Users\talsi\Desktop\test.html", 'w', encoding='utf-8') as f:
        f.write(res)
    # try:
    text = res.split('Other recordings of this song')
    res = text[0]
    soup = BeautifulSoup(res, 'html.parser')
    songs = [tag.text for tag in soup.find_all(attrs=GOOGLE_SONG_TAG_ATTRS)]
    songs = songs[:round(len(songs) / 2)]
    artists = [tag.text for tag in soup.find_all(attrs=GOOGLE_ARTISTS_TAG_ATTRS)][:len(songs)]
    i = 0
    # print("list length= "+ str(len(songs)))
    if (not artists):
        return []
    while i < len(songs):
        z = songs[i]
        if z.lower() != title.lower():
            print("z.lower= " + z.lower())
            print("title.lower= " + title.lower())
            print("what we going to del: " + songs[i])
            del songs[i]
            del artists[i]
            i -= 1
        else:
            print("we didnt delete: " + z.lower())
            print("cause we thought its: " + title.lower())
        i += 1

    # print("i= "+ str(i))
    # print("list length after delete= "+ str(len(songs)))
    # for i in songs:
    #      print("songs:" + i)
    #      print("artist: "+str(artists[songs.index(i)]))
    #      print("artists[-7:] "+str(artists[songs.index(i)][:-7]))

    i = 0
    while i < len(artists):
        artists[i] = artists[i][:-7]
        print("the song {name} by {art}".format(name=songs[i], art=artists[i]))
        i += 1
    return artists


def searchForPlaceInAlbumInWiki(title, url):
    found = False
    print(url)
    if (url):
        res = requests.get(url, headers=HEADERS_GET).text
        soup = BeautifulSoup(res, 'html.parser')
        tags = [tag.text for tag in soup.find_all(attrs=WIKI_TABLE_ATTRS1)]
        print("we serch for place to the song: " + title.lower())
        for i in tags:
            print("searchong for place... i= " + str(i.lower()))
            if i.lower().__contains__(title.lower()):
                # and (i.lower().__contains__("acoustic") == title.lower().__contains__("acoustic")):
                print("found i= " + str(i))
                j = i.find(".")
                newi = i[:j]
                print(newi)
                found = True
                return newi

        if not found:
            tags = [tag.text for tag in soup.find_all(attrs=WIKI_TABLE_ATTRS2)]
            for i in tags:
                # print(i)
                if i.lower().__contains__(title.lower()):
                    # and (i.lower().__contains__("acoustic") == title.lower().__contains__("acoustic")):
                    print("found i= " + str(i))
                    j = i.find(".")
                    newi = i[:j]
                    print(newi)
                    found = True
                    return newi
    if not found:
        print("sorry, didnt found the # for the song {song}".format(song=title))
        return 0


def searchForAlbum(title, artists):
    albums = []
    for i in artists:
        query = "{title} by {artist}".format(title=title, artist=i).replace(" ", "+").replace("&", "and")
        search = "https://google.com/search?hl={lang}&q={query}+album".format(lang='en', query=query)
        res = requests.get(search, headers=HEADERS_GET).text
        soup = BeautifulSoup(res, 'html.parser')
        temp_albums = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
        if not temp_albums or str(temp_albums).lower().__contains__("remix"):
            query = "{title} by {artist}".format(title=title, artist=i).replace(" ", "+").replace("&", "and")
            search = "https://google.com/search?hl={lang}&q={query}+song+album".format(lang='en', query=query)
            res = requests.get(search, headers=HEADERS_GET).text
            with open(r"C:\Users\talsi\Desktop\test3.html", 'w', encoding='utf-8') as f:
                f.write(res)
            soup = BeautifulSoup(res, 'html.parser')
            temp_albums2 = [tag.text for tag in soup.find_all(attrs=GOOGLE_ALBUM_TAG_ATTRS)]
            if temp_albums2 and not str(temp_albums2).lower().__contains__("remix"):
                albums.append(temp_albums2[0])
            else:
                print("didnt find album to {title} by {artist}".format(title=title, artist=i))
                albums.append(False)
        else:
            if temp_albums:
                print("the album for the song {title} by {artist} is: ".format(title=title, artist=i) + temp_albums[0])
                albums.append(temp_albums[0])
    return albums


def searchForSyncedLyrics(artist, title):
    query = "{title} {artist}".format(title=title, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://syair.info/search?q={query}".format(query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=SYNCED_LYRICS_SEARCH_RESULT_ATTRS)]
    items_hrefs = ['https://syair.info{}'.format(tag.find_next('a', href=True).get('href')) for tag in tags]
    theUrl = items_hrefs[0]
    for i in items_hrefs:
        if i.lower().__contains__(title.replace(" ", "-").lower()) and i.lower().__contains__(str(artist).lower()):
            theUrl = i
            break

    print(theUrl)
    nameFromUrl = theUrl[theUrl.find(str(artist).lower().replace("/", "-")) + len(artist) + 1:]
    nameFromUrl = nameFromUrl[:nameFromUrl.find('/')]
    print("the name from the url= " + nameFromUrl)
    if (not nameFromUrl.lower().__contains__(title.lower())):
        print("didnt find the synced lyrics")
        return ""
    res = requests.get(theUrl, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=THE_SYNCED_LYRICS_ATTRS)]
    lyric = str(tags[0])
    j = lyric.find('[00:')
    lyric = lyric[j:].replace("<br/>", "")
    n = lyric.find('<div')
    lyric = lyric[:n]
    # print(lyric)
    return lyric


def searchForLyrics(artist, title):
    query = "{title} {artist}".format(title=title, artist=artist).replace(" ", "-").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+lyrics".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    with open(r"C:\Users\talsi\Desktop\test2.html", 'w', encoding='utf-8') as f:
        f.write(res)
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=THE_LYRICS_ATTRS)]
    i = 0
    string = ""
    while i < len(tags):
        tags[i] = str(tags[i]).replace('<span jsname="YS01Ge">', "")
        tags[i] = str(tags[i]).replace('</span>', "")
        # print(tags[i])
        string += tags[i]
        string += "\n"
        i += 1
    # print(string)
    return string


def albumFromWiki(title, album, artist, url):
    print("now searching for album via the url")
    length = searchForLength([url], title, [artist])
    length = length[0]
    if length:
        newUrl = url.replace("_", " ").replace("%3F", "?").replace("%27", "'")
        if not newUrl.lower().__contains__(album.lower()) and length:
            print("the album was wrong, fixing it now")
            album = newUrl[newUrl.rfind('/') + 1:]
            album = album.replace(artist, '')
            if album.lower().__contains__("edition") or album.lower().__contains__("delux"):
                album = album.replace('(', '').replace(')', '')
            album = album.replace('album', '')
            album = album.strip()
        print(album)
        return album
    return album


def searchReleaseYear(album, artist):
    query = "{album} {artist}".format(album=album, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+release+date".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    date = [tag.text for tag in soup.find_all(attrs=GOOGLE_DATE_ATTRS)]
    if not date:
        return ""
    date = str(date[0])
    date = date[date.find(',') + 1:]
    date = date.strip()
    print(date)
    return date


def searchForGenres(album, artist):
    query = "{album} {artist}".format(album=album, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+genre".format(lang='en', query=query)
    print(search)
    res = requests.get(search, headers=HEADERS_GET).text
    text = res.split('Songs')
    res = text[0]
    soup = BeautifulSoup(res, 'html.parser')
    for i in range(3):
        if(i==0):
            genres = [tag.text for tag in soup.find_all(attrs=GOOGLE_GENRE_TAG_ATTRS)]
        elif(i==1):
            genres = [tag.text for tag in soup.find_all(attrs=GOOGLE_GENRE2_TAG_ATTRS)]
        elif(i==2):
            genres = [tag.text for tag in soup.find_all(attrs=GOOGLE_GENRE3_TAG_ATTRS)]
        print(genres)
        newGenre = []
        if genres:
            for i in genres:
                i = str(i).split('/')
                newGenre.append(i[0])
                try:
                    newGenre.append(i[1])
                    try:
                        newGenre.append(i[2])
                    except IndexError:
                        continue
                except IndexError:
                    continue
            return newGenre


def main():
    open(r'C:\Users\talsi\Desktop\log for mp3 tagging program.log', 'w').close()
    LOG_FILENAME = r'C:\Users\talsi\Desktop\log for mp3 tagging program.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger("THIS IS IMPORTANT!")
    printing = logging.getLogger("")
    printing.debug('this is the start of the program')
    printing.debug("")
    print("start")
    tracks = []
    root = tkinter.Tk()
    root.withdraw()
    root.update()
    folder = askdirectory(title="choose the dir u want get tags to", initialdir=r"C:\Users\User\Desktop",
                          mustexist=True)
    root.destroy()
    printing.debug("the dir is " + folder)
    printing.debug("")

    for root, dirs, files, in os.walk(folder):
        for name in files:
            if name.endswith((".mp3", ".flac")):
                fileType = os.path.splitext(name)[1]
                if (fileType == ".mp3"):
                    audio = MP3(root + "\\" + name)
                    ezAudio = EasyMP3(root + "\\" + name)
                    # print("length using mutagen MP3: "+str(audio.info.length))
                    # print("title using mutagen ezMP3: "+ezAudio["title"][0])
                if (fileType == ".flac"):
                    audio = FLAC(root + "\\" + name)
                    ezAudio = audio
                    # print("length using mutagen FLAC: "+str(audio.info.length))
                    # print("title using mutagen FLAC: "+audio["title"][0])
                print(root)
                tracks.append(name)
                print(audio.info.length)
                try:
                    print("found title in file: " + ezAudio["title"][0])
                    title = ezAudio["title"][0]
                except KeyError:
                    print("didnt found title in file, title of file= " + os.path.splitext(name)[0])
                    title = os.path.splitext(name)[0]
                title = str(title)
                title = title.strip()
                print(title)
                print(fileType)
                print("audio.info.length= " + str(audio.info.length))
                duration = round(audio.info.length)
                print("duration= " + str(duration))
                formattedDuration = str(datetime.timedelta(seconds=duration))
                formattedDuration = formattedDuration[-5:]
                print("formattedDuration= " + str(formattedDuration))

                artists = searchForArtist(title)
                print("len(artists)= " + str(len(artists)))
                if len(artists) >= 2:
                    print("len(artists) >= 2")
                    temp_title = title
                    if ("delux" in title or "edition" in title or "edit" in title or "version" in title):
                        temp_title = re.sub(r'\([^()]*\)', '', title)
                    albums = searchForAlbum(temp_title, artists)
                    wikialbums = []
                    for i in albums:
                        if "(" in str(i) and (
                                "edition" in str(i) or "delux" in str(i) or "edit" in str(i) or "version" in str(i)):
                            wikialbums.append(re.sub(r'\([^()]*\)', '', i))
                        else:
                            wikialbums.append(i)
                    wikipidiaUrls = searchInWiki(temp_title, wikialbums, artists)
                    print("wiki urls len= " + str(len(wikipidiaUrls)))
                    print("artists len= " + str(len(artists)))
                    print("albums len= " + str(len(albums)))

                    foundedLengths = searchForLength(wikipidiaUrls, temp_title, artists)

                    i = 0
                    needToDoLengthAgian = False
                    while i < len(artists):
                        if (foundedLengths[i] == False):
                            albums[i] = searchWikiForAlbum(temp_title, artists[i])
                            needToDoLengthAgian = True
                        i += 1

                    if (needToDoLengthAgian):
                        wikialbums = []
                        for i in albums:
                            if str(temp_album).__contains__("(") and (
                                    str(temp_album).lower().__contains__("edition") or str(
                                    temp_album).lower().__contains__("delux")):
                                wikialbums.append(re.sub(r'\([^()]*\)', '', i))
                            else:
                                wikialbums.append(i)
                        wikipidiaUrls = searchInWiki(temp_title, wikialbums, artists)
                        foundedLengths = searchForLength(wikipidiaUrls, temp_title, artists)

                    eliminationMatch = foundedLengths
                    durationMinutes = formattedDuration[:-3]
                    durationSeconds = int(formattedDuration[-2:])

                    i = 0
                    while i < len(eliminationMatch):
                        if eliminationMatch[i] and durationMinutes == eliminationMatch[i][:-3]:
                            print("correct minute!")
                        else:
                            print(
                                "time to eliminate {song} by {artist}, because their was {length} and the right is {trueLength}".format(
                                    song=temp_title, artist=artists[i], length=eliminationMatch[i],
                                    trueLength=durationMinutes))
                            del artists[i]
                            del albums[i]
                            del eliminationMatch[i]
                            i -= 1
                        i += 1

                    i = 1
                    try:
                        rightOne = eliminationMatch[0]
                    except IndexError:
                        logger.error("didnt found the right artist to the song " + title)
                        logging.debug("")
                        continue
                    rightOneSecs = int(rightOne[-2:])
                    while i < len(eliminationMatch):
                        temp_duration = int(eliminationMatch[i][-2:])
                        print("temp duration= " + str(temp_duration) + " durationSeconds= " + str(
                            durationSeconds) + " rightOneSecs= " + str(rightOneSecs))
                        print("abs(temp_duration - durationSeconds) " + str(
                            abs(temp_duration - durationSeconds)) + " abs(rightOneSecs - durationSeconds)= " + str(
                            abs(rightOneSecs - durationSeconds)))
                        if abs(temp_duration - durationSeconds) < abs(rightOneSecs - durationSeconds):
                            print("the previous was {previous} and the new is {new}".format(
                                previous=abs(rightOneSecs - durationSeconds), new=abs(temp_duration - durationSeconds)))
                            rightOne = eliminationMatch[i]
                            rightOneSecs = temp_duration
                        i += 1
                    print("the right one= " + rightOne + " and the file is: " + formattedDuration)

                    rightArtist = artists[eliminationMatch.index(rightOne)]
                    rightAlbum = albums[eliminationMatch.index(rightOne)]

                    # print("before format: {}".format(duration))
                    # print("what we got: {}".format(formattedDuration))
                    # print("what we found: {}".format(foundedLengths))
                else:
                    if len(artists) < 2:
                        if (artists):
                            rightArtist = artists[0]
                        else:
                            rightArtist = searchForAnArtist(title)
                            print(rightArtist)
                            if (not rightArtist):
                                logger.error(
                                    "didnt found the right atrist using the 'searchForAnArtist()' function with the title " + title)
                                logging.debug("")
                                continue
                        print("artists<2 and found the right one:" + rightArtist)
                        temp_title = title
                        if "delux" in title.lower() or "edition" in title.lower() or "edit" in title.lower() or "version" in title.lower():
                            temp_title = re.sub(r'\([^()]*\)', '', title)
                        print("temp_title= " + temp_title)
                        rightAlbum = searchForAnAlbum(temp_title, rightArtist)
                        print("right album= " + rightAlbum)

                        wikipidiaUrls = searchInWiki(temp_title, [rightAlbum], [rightArtist])
                        length = searchForLength(wikipidiaUrls, temp_title, [rightArtist])
                        length = length[0]

                        i = 0
                        needToDoLengthAgian = False
                        temp_album = False
                        foundedLengths = False

                        if (length == False):
                            temp_album = searchWikiForAlbum(temp_title, rightArtist)
                            needToDoLengthAgian = True

                        if (needToDoLengthAgian and temp_album):
                            if str(temp_album).__contains__("(") and (
                                    str(temp_album).lower().__contains__("edition") or str(
                                    temp_album).lower().__contains__("delux")):
                                wikialbums = re.sub(r'\([^()]*\)', '', temp_album)
                            else:
                                wikialbums = temp_album

                            wikipidiaUrls = searchInWiki(temp_title, [wikialbums], [rightArtist])
                            print("wikiUrls= " + str(wikipidiaUrls))
                            foundedLengths = searchForLength(wikipidiaUrls, temp_title, [rightArtist])

                        if foundedLengths:
                            rightAlbum = temp_album
                            rightOne = foundedLengths[0]
                        else:
                            rightOne = formattedDuration

                syncedLyrics = searchForSyncedLyrics(rightArtist,
                                                     title)  # dosent work with the any music player i came across with
                syncedLyrics
                if str(rightAlbum).lower().__contains__("edition") or str(rightAlbum).lower().__contains__("delux"):
                    url = searchInWiki(temp_title, [re.sub(r'\([^()]*\)', '', rightAlbum)], [rightArtist])
                else:
                    url = searchInWiki(temp_title, [rightAlbum], [rightArtist])
                print("url= " + str(url))
                url = url[0]
                print("url[0]= " + url)
                lyrics = searchForLyrics(rightArtist, title)
                number = searchForPlaceInAlbumInWiki(temp_title, url)
                photo = searchPhoto(url)
                rightAlbum = albumFromWiki(temp_title, rightAlbum, rightArtist, url)
                yearOfRelease = searchReleaseYear(rightAlbum, rightArtist)
                genres = searchForGenres(rightAlbum, rightArtist)
                print("artist is {art}, album is {album}, length is {length}".format(art=rightArtist, album=rightAlbum,
                                                                                     length=rightOne))
                if fileType == ".flac":
                    print("its .flac")
                    audio = FLAC(root + "\\" + name)
                    audio["title"] = title
                    audio["album"] = rightAlbum
                    audio["artist"] = rightArtist
                    cover = Picture()
                    cover.type = mutagen.flac.Picture
                    cover.type = id3.PictureType.COVER_FRONT
                    cover.mime = 'image/jpg'
                    cover.width = 500
                    cover.height = 500
                    cover.depth = 16
                    cover.data = urlopen(photo).read()
                    audio.add_picture(cover)
                    # audio["SYLT"] = syncedLyrics  # SYLT = synchronized syncedLyrics transcription #USLT = unsynchronized syncedLyrics transcription
                    # audio["USLT"] = lyrics
                    audio["Lyrics"] = lyrics
                    audio["DATE"] = str(yearOfRelease)
                    audio["TRACKNUMBER"] = number
                    audio["ALBUMARTIST"] = rightArtist
                    audio["GENRE"] = genres
                    audio.save()
                else:
                    if fileType == ".mp3":
                        photoType = photo[photo.rfind(".") + 1:]
                        print("its .mp3")
                        try:
                            audio = ID3(root + "\\" + name)
                        except ID3NoHeaderError:
                            tags = ID3()
                        if (photo != ''):
                            audio['APIC'] = APIC(
                                encoding=3,
                                mime='image/' + str(photoType),
                                type=3, desc=u'Cover',
                                data=urlopen(photo).read()
                            )
                        trackNumber = str(number) + '/' + '30'
                        audio['TPE1'] = TPE1(encoding=3, text=rightArtist)
                        print("TPE1= " + str(TPE1(encoding=3, text=rightArtist)))
                        audio['TIT2'] = TIT2(encoding=3, text=title)
                        audio['TPE2'] = TPE2(encoding=3, text=rightArtist)
                        print("TIT2= " + str(TIT2(encoding=3, text=title)))
                        audio['TRCK'] = TRCK(encoding=3, text=trackNumber)
                        print("TRCK= " + str(TRCK(encoding=3, text=trackNumber)))
                        audio['TALB'] = TALB(encoding=3, text=rightAlbum)
                        print("TALB= " + str(TALB(encoding=3, text=rightAlbum)))
                        audio['TORY'] = TORY(encoding=3, text=str(yearOfRelease))
                        audio['TYER'] = TYER(encoding=3, text=str(yearOfRelease))
                        audio['TCON'] = TCON(encoding=3, text=genres)
                        # audio['SYLT'] = SYLT(encoding=3,lang='eng',desc=u'desc',text=syncedLyrics)
                        # print("SYLT= "+str(SYLT(encoding=3,lang='eng',desc=u'desc',text=syncedLyrics)))
                        uslt_output = USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics)
                        audio["USLT::'eng'"] = uslt_output
                        # print("USLT::'eng'= "+str(uslt_output))
                        audio.save(root + "\\" + name)


if __name__ == "__main__":
    main()
