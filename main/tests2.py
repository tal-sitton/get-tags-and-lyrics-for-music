import os
import re
from urllib.request import urlopen

import GoogleScraper
import requests
from GoogleScraper import scrape_with_config, GoogleSearchError
from bs4 import BeautifulSoup
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import EasyMP3, MP3

from main import HEADERS_GET, SYNCED_LYRICS_SEARCH_RESULT_ATTRS, THE_SYNCED_LYRICS_ATTRS, FIRST_GOOGLE_PHOTOS_ATTRS, \
    searchInWiki, WIKI_COVER_ART_ATTR, WIKI_TABLE_ATTRS1, WIKI_TABLE_ATTRS2, GOOGLE_SONG_TAG_ATTRS, \
    GOOGLE_ARTISTS_TAG_ATTRS, searchForLength, GOOGLE_DATE_ATTRS, GOOGLE_GENRE_TAG_ATTRS, GOOGLE_GENRE2_TAG_ATTRS, \
    WIKI_SEARCH_RESULT_ATTRS, WIKI_ALBUM_ATTRS, WIKI_SEARCH_RESULT_DESCRIPTION_ATTRS, GOOGLE_COVER_ART_ATTR


def searchSyncedForLyrics(artist, title):
    query = "{title} {artist}".format(title=title, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://syair.info/search?q={query}".format(query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=SYNCED_LYRICS_SEARCH_RESULT_ATTRS)]
    items_hrefs = ['https://syair.info{}'.format(tag.find_next('a', href=True).get('href')) for tag in tags]
    theUrl = items_hrefs[0]
    for i in items_hrefs:
        if i.__contains__(title.replace(" ", "-")) and i.__contains__(artist):
            theUrl = i
            break
    test = theUrl[theUrl.find(str(artist)) + len(artist) + 1:]
    test = test[:test.find('/')]

    print("test= " + test)
    print(theUrl)
    res = requests.get(theUrl, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=THE_SYNCED_LYRICS_ATTRS)]
    lyric = str(tags[0])
    j = lyric.find('[00:')
    lyric = lyric[j:].replace("<br/>", "")
    n = lyric.find('<div')
    lyric = lyric[:n]
    print(lyric)


THE_LYRICS_ATTRS = {"class": "verse"}


def searchForLyrics(artist, title):
    query = "{title}-lyrics-{artist}".format(title=title, artist=artist).replace(" ", "-").replace("&", "and")
    search = "https://www.metrolyrics.com/{query}.html".format(query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    with open(r"C:\Users\talsi\Desktop\test2.html", 'w', encoding='utf-8') as f:
        f.write(res)
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=THE_LYRICS_ATTRS)]
    i = 0
    string = ""
    while i < len(tags):
        tags[i] = str(tags[i]).replace('<p class="verse">', "")
        tags[i] = str(tags[i]).replace('<br/>', "")
        tags[i] = str(tags[i]).replace('</p>', "")
        # print(tags[i])
        string += tags[i]
        i += 1
    print(string)


def searchPhoto(url,artist,title):
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
        query="{artist} {title} image".format(artist=artist,title=title).replace(" ","+")
        search="https://www.google.com/images?source=hp&q={query}".format(query=query)
        res = requests.get(search, headers=HEADERS_GET)
        soup = BeautifulSoup(res.content, 'html.parser')
        tags = [tag for tag in soup.find_all(attrs=GOOGLE_COVER_ART_ATTR)]
        if(tags):
            print("didnt found in wiki but found in google: "+str(tags[0]))
            return tags[0]
        return "https://music.uberchord.com/assets/images/png/placeholder-song.png"


def searchForPlaceInAlbumInWiki(title, url):
    found = False
    res = requests.get(url, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag.text for tag in soup.find_all(attrs=WIKI_TABLE_ATTRS1)]
    for i in tags:
        # print(i)
        if i.lower().__contains__(title.lower()) and (
                i.lower().__contains__("acoustic") == title.lower().__contains__("acoustic")):
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
            if i.lower().__contains__(title.lower()) and (
                    i.lower().__contains__("acoustic") == title.lower().__contains__("acoustic")):
                print("found i= " + str(i))
                j = i.find(".")
                newi = i[:j]
                print(newi)
                found = True
                return newi
    if (not found):
        print("sorry, didnt found the # for the song {song}".format(song=title))
        return 0


def printTags():
    for root, dirs, files, in os.walk(r"C:\Users\talsi\Desktop\Music\AJR\Neotheater (2019)\new"):
        for name in files:
            if name.endswith((".mp3", ".flac")):
                if name.endswith(".flac"):
                    print("it is .flac")
                    audio = FLAC(root + "\\" + name)
                    print(audio.pprint())
                else:
                    if name.endswith(".mp3"):
                        print("it is .mp3 and the name of the file is: " + name)
                        audio = ID3(root + "\\" + name)
                        print(audio.pprint())


def searchForArtist(title):
    query = "{title}".format(title=title).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+song".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    with open(r"C:\Users\talsi\Desktop\test.html", 'w', encoding='utf-8') as f:
        f.write(res)
    # try:
    text = res.split('Other recordings of this song')
    res = text[0]
    soup = BeautifulSoup(res, 'html.parser')
    i = 0
    songs = [tag.text for tag in soup.find_all(attrs=GOOGLE_SONG_TAG_ATTRS)]
    while i < len(songs):
        z = songs[i]
        if z.lower() != title.lower():
            print("z.lower= " + z.lower())
            print("title.lower= " + title.lower())
            print("what we going to del: " + songs[i])
            del songs[i]
            i -= 1
        else:
            print("we didnt delete: " + z.lower())
            print("cause we thought its: " + title.lower())
        i += 1
    print(songs)
    i = 0
    print("songs[0]= "+songs[0])
    print("soup.find({place0})= ".format(place0=songs[0])+soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=songs[0]).text)
    lastArt=soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=songs[0]).find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS).text
    artist=lastArt
    print("lastArt= "+lastArt)
    artists = []
    newSongs = []
    nextIsOK=True
    while i<len(songs):
        song=songs[i]
        lastSong=song
        if nextIsOK:
            newSongs.append(song)
            artists.append(artist)
        print(lastArt[:-7])
        print(soup.find_next(text=lastArt[:-7]))
        print(soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=lastSong).find_next(text=lastArt).text)
        if soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=lastSong).find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS,text=lastArt).find_next("span").find_next("span").text==soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=lastSong).find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS,text=lastArt).find_next("span").find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS).text:
            print("got in")
            nextIsOK=True
            artist=soup.find(attrs=GOOGLE_SONG_TAG_ATTRS,text=lastSong).find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS,text=lastArt).find_next("span").find_next(attrs=GOOGLE_ARTISTS_TAG_ATTRS).text
        else:
            nextIsOK=False
            artist=""




def searchReleaseYear(album, artist):
    query = "{album} {artist}".format(album=album, artist=artist).replace(" ", "-").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+release+date".format(lang='en', query=query)
    res = requests.get(search, headers=HEADERS_GET).text
    soup=BeautifulSoup(res, 'html.parser')
    date=[tag.text for tag in soup.find_all(attrs=GOOGLE_DATE_ATTRS)]
    if not date:
        return ""
    date=str(date[0])
    date=date[date.find(',')+1:]
    date=date.strip()
    print(date)
    return date

def searchForGenres(album, artist):
    query = "{album} {artist}".format(album=album, artist=artist).replace(" ", "+").replace("&", "and")
    search = "https://google.com/search?hl={lang}&q={query}+genre".format(lang='en', query=query)
    print(search)
    res = requests.get(search, headers=HEADERS_GET).text
    text=res.split('Songs')
    res=text[0]
    soup=BeautifulSoup(res, 'html.parser')
    genres=[tag.text for tag in soup.find_all(attrs=GOOGLE_GENRE_TAG_ATTRS)]
    print(genres)
    newGenre=[]
    if genres:
        for i in genres:
            i=str(i).split('/')
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
    genres=[tag.text for tag in soup.find_all(attrs=GOOGLE_GENRE2_TAG_ATTRS)]
    print(genres)
    if genres:
        for i in genres:
            i=str(i).split('/')
            newGenre.append(i[0])
            newGenre.append(i[1])
        return newGenre
    return ""

def askForDir():
    from tkinter.filedialog import askdirectory

    folder = askdirectory(title = "plz work",initialdir = r"C:\Users\User\Desktop", mustexist=True )
    print(folder)

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
            done=False
            newtags = [tag.text for tag in soup.find_all(attrs=WIKI_SEARCH_RESULT_DESCRIPTION_ATTRS)]
            print(str(newtags))
            try:
                if items_hrefs[2].__contains__("album") and not items_hrefs[0].__contains__("album") and not items_hrefs[1].__contains__("album") and str(newtags[2]).lower().__contains__(tempArtist.lower()):
                    print("4.1 found the song by {} in: {}".format(tempArtist, items_hrefs[2]))
                    trueURL.append(items_hrefs[2])
                    done=True
            except IndexError:
                print("there wa no other option")
            try:
                if not done and items_hrefs[0].lower().__contains__("band") and str(newtags[1]).lower().__contains__(tempArtist.lower()) or (items_hrefs[1].lower().__contains__("album") and not items_hrefs[0].lower().__contains__("album")):
                    print(str(newtags[1]).lower().__contains__(tempArtist))
                    print("4.5 found the song by {} in: {}".format(tempArtist, items_hrefs[1]))
                    trueURL.append(items_hrefs[1])
                    done=True
            except IndexError:
                print("there wa no other option")

            try:
                if not done and str(newtags[0]).lower().__contains__(tempArtist.lower()):
                    print("5 found the song by {} in: {}".format(tempArtist, items_hrefs[0]))
                    trueURL.append(items_hrefs[0])
                    done=True
            except IndexError:
                print("there is no option- no wiki pages found")
                trueURL.append(False)
            if not done:
                trueURL.append(False)
        i += 1
    return trueURL

def searchWikiForAlbum(title,artist):
    url=searchInWiki(title,[title],[artist])
    url=url[0]
    res = requests.get(url, headers=HEADERS_GET).text
    soup = BeautifulSoup(res, 'html.parser')
    tags = [tag for tag in soup.find_all(attrs=WIKI_ALBUM_ATTRS)]
    if tags:
        album=url[url.rfind('/')+1:]
        album=album.replace(artist,'')
        album=album.replace('album', '')
        album=album.replace('(','').replace(')','')
        album=album.replace("_"," ")
        album=album.replace("%3F","?")
        album=album.strip()
        print(album)
        return album
    else:
        return []

def main():
    print(str(searchPhoto(False,"as a stone","full trunk")))

if __name__ == "__main__":
    main()
