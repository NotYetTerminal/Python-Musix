from pynput import keyboard, mouse
import threading
import time
from tkinter import *
from tkinter import simpledialog
import pygame
from tkinter import filedialog
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
import random
#import pafy
import os
from moviepy.editor import *
#from youtubesearchpython import SearchVideos
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip, ffmpeg_extract_audio
#import spotipy
from shutil import copyfile

# changed _get_user_input in oauth2.py
# form raw_input(prompt)
# to pyautogui.prompt(text=prompt)

# game listener
def on_release(key):
    global actionsPerMinute
    actionsPerMinute += 1
    if (key == keyboard.Key.space):
        add_in_actions_list('win')
    
def on_click(x, y, button, pressed):
    if pressed:
        global actionsPerMinute
        actionsPerMinute += 1
        
def stop_listening():
    global appIsRunning
    if appIsRunning:
        klistener.stop()
        mlistener.stop()
        appIsRunning = False
        print("Shutting down")
        
        start_btn["state"] = NORMAL
        stop_btn["state"] = DISABLED
        
        change_label("Pick a song")
        pygame.mixer.music.unload()
        refresh_file_lists()
        
        fail_radio_btn["state"] = NORMAL
        confused_radio_btn["state"] = NORMAL
        win_radio_btn["state"] = NORMAL
            
def check_actions():
    if appIsRunning:
        global actionsPerMinute
        #print(actionsPerMinute)
        
        # time up
        #if pygame.mixer.music.get_pos() > playing_time:
        #    pygame.mixer.music.fadeout(1000)
        
        last_20_actions.pop(0)
        last_20_actions.append(actionsPerMinute)
        
        if pygame.mixer.music.get_busy() == 0:
            if actionsPerMinute > 8:
                play_effect_from('win')
            #elif actionsPerMinute == 0:
                #play_effect_from('fail')
            else:
                start_spotify()
                
        actionsPerMinute = 0
        time.sleep(2)
        threading.Thread(target=check_actions).start()
        
def play_effect_from(this_category):
    files = os.listdir('./effects/' + this_category)
    
    if len(files) != 0:
        stop_spotify()
        song_name_playing = files[random.randint(0, len(files) - 1)]
        pygame.mixer.music.load(f"./effects/{this_category}/{song_name_playing}")
        pygame.mixer.music.play()
        
'''    
def play_effect_from(this_category):
    global playing_time
    song_name_playing = random.choice(list(this_category.keys()))
    song_part = random.randint(0, len(this_category[song_name_playing]) - 1)
    
    #print(this_category[song_name_playing][song_part])
    the_string = this_category[song_name_playing][song_part].split("|")[1].split("-->")
    
    start_point = minutes_to_seconds(the_string[0])
    end_point = minutes_to_seconds(the_string[1])
    
    playing_time = (end_point - start_point) * 1000
    
    pygame.mixer.music.load(f"./audio/{song_name_playing}.mp3")
    pygame.mixer.music.play(start=start_point, fade_ms=1000)
    
    change_label(song_name_playing)
    '''
def minutes_to_seconds(minutes):
    return int(minutes.split(":")[0]) * 60 + int(minutes.split(":")[1])
    
def start_listening():
    global appIsRunning
    global klistener
    global mlistener
    global actionsPerMinute
    global paused
    
    klistener = keyboard.Listener(on_release=on_release)
    mlistener = mouse.Listener(on_click=on_click)
    
    actionsPerMinute = 0
    appIsRunning = True
        
    klistener.start()
    mlistener.start()
    
    threading.Thread(target=check_actions).start()
    
    start_btn["state"] = DISABLED
    stop_btn["state"] = NORMAL
    
    play_pause_btn["state"] = DISABLED
    trim_part_btn["state"] = DISABLED
    remove_effect_btn["state"] = DISABLED
    #save_btn["state"] = DISABLED
    music_slider["state"] = DISABLED
    
    unload_current_song()
    #save_time_stamps()

# tkinter from now on
def on_closing_main():
    pygame.mixer.music.stop()
    stop_listening()
    #save_time_stamps()
    #root.destroy()
    quit()

def play_pause():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True
        
def ask_for_local():
    global song
    song = filedialog.askopenfilename(initialdir="audio/", title="Choose A Song",filetype=(("MP3 files", "*.mp3"), ))
    add_song()
    
def add_song():
    if song != "":
        global paused
        
        name_of_song = song.split("/")[-1].replace(".mp3", "")
        change_label(name_of_song)
        
        #time_stamp_list = search_for_song(name_of_song)
        #markers_clear_and_add(time_stamp_list)
        
        '''for numbers in time_stamp_list:
            if numbers != [""]:
                for nums in numbers:
                    selections_box.insert(END, nums)'''
        
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        paused = False
        
        global song_length
        global converted_song_length
        song_length = MP3(song).info.length
        converted_song_length = time.strftime("%M:%S", time.gmtime(song_length))
        
        music_slider.config(to=int(song_length), value=0)
        music_slider["state"] = NORMAL
        
        play_pause_btn["state"] = NORMAL
        trim_part_btn["state"] = NORMAL
        save_whole_effect["state"] = NORMAL
        
        if selections_box.size() != 0:
            remove_effect_btn["state"] = NORMAL
            #save_btn["state"] = NORMAL
        
        if not play_time_started:
            play_time()

def get_marker_for_trim():
    global last_marker
    
    if last_marker == -1:
        last_marker = int(music_slider.get())
        
        save_whole_effect["state"] = DISABLED
        remove_effect_btn["state"] = DISABLED
        start_btn["state"] = DISABLED
        
        fail_radio_btn["state"] = DISABLED
        confused_radio_btn["state"] = DISABLED
        win_radio_btn["state"] = DISABLED
        
    else:
        bigger = int(music_slider.get())
        if bigger < last_marker:
            temp = bigger
            bigger = last_marker
            last_marker = temp
            
        trim_audio(song, last_marker, bigger)
        last_marker = -1
        
        save_whole_effect["state"] = NORMAL        
        remove_effect_btn["state"] = NORMAL
        start_btn["state"] = NORMAL
        
        fail_radio_btn["state"] = NORMAL
        confused_radio_btn["state"] = NORMAL
        win_radio_btn["state"] = NORMAL
'''
def add_in_marker():
    global last_marker
    marker = option.get() + "|" + str(time.strftime("%M:%S", time.gmtime(int(music_slider.get())))) + "-->"
    selections_box.insert(END, marker)
    
    last_marker = int(music_slider.get())
    
    trim_part_btn["state"] = DISABLED
    save_whole_effect["state"] = NORMAL
    remove_effect_btn["state"] = DISABLED
    save_btn["state"] = DISABLED
    start_btn["state"] = DISABLED
    
    fail_radio_btn["state"] = DISABLED
    confused_radio_btn["state"] = DISABLED
    win_radio_btn["state"] = DISABLED


def add_out_marker():
    global last_marker
    if music_slider.get() > last_marker:
        marker = selections_box.get(END) + str(time.strftime("%M:%S", time.gmtime(int(music_slider.get()))))
        
        selections_box.delete(END)
        selections_box.insert(END, marker)
        
        trim_audio(song_label.get(), last_marker, int(music_slider.get()))
        
        last_marker = 0
        
        trim_part_btn["state"] = NORMAL
        save_whole_effect["state"] = DISABLED
        remove_effect_btn["state"] = NORMAL
        save_btn["state"] = NORMAL
        start_btn["state"] = NORMAL
        
        fail_radio_btn["state"] = NORMAL
        confused_radio_btn["state"] = NORMAL
        win_radio_btn["state"] = NORMAL
        
def remove_marker():
    if selections_box.get(ANCHOR) != "":
        markers_dict[selections_box.get(ANCHOR)[0]].remove(selections_box.get(ANCHOR))
    
    selections_box.delete(ANCHOR)
    if selections_box.size() == 0:
        remove_effect_btn["state"] = DISABLED
        save_btn["state"] = DISABLED'''

def save_whole_effect():
    copyfile(song, f'./effects/{option.get()}/{song.split("/")[-1]}')
    refresh_file_lists()

def remove_effect():
    os.remove(f'./effects/{option.get()}/{selections_box.get(ANCHOR)}.mp3')
    selections_box.delete(ANCHOR)
    if selections_box.size() == 0:
        remove_effect_btn["state"] = DISABLED

def trim_audio(path, start_time, end_time):
    name_of_file = path.split("/")[-1]
    if name_of_file[-1] == '4':
        name_of_file.replace('4', '3')
    
    print(start_time, end_time)
    ffmpeg_extract_subclip(path, start_time, end_time, targetname=f'./effects/{option.get()}/{name_of_file}')
    refresh_file_lists()

def play_time():
    #print(markers_dict)
    
    global play_time_started
    play_time_started = True
    
    if int(music_slider.get()) < int(song_length) and not paused:
        converted_time = time.strftime("%M:%S", time.gmtime(music_slider.get()))
        status_bar.config(text=f"{converted_time} of {converted_song_length} ")

        next_time = int(music_slider.get()) + 1
        music_slider.config(value=next_time)
        
    status_bar.after(1000, play_time)

def slide(x):
    global paused
    
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0, start=int(music_slider.get()))
    paused = False
    
def volume(x):
    pygame.mixer.music.set_volume(volume_slider.get() / 100)
    
def unload_current_song():
    global paused
    pygame.mixer.music.pause()
    pygame.mixer.music.unload()
    paused = True
    
    play_pause_btn["state"] = DISABLED
    trim_part_btn["state"] = DISABLED
    #save_btn["state"] = DISABLED
    music_slider["state"] = DISABLED
    
    #selections_box.delete(0, END)
    status_bar.config(text="")
    
    change_label("Pick a song")
    
def change_label(text_in):
    song_label.config(text=text_in)
    
    '''
def save_time_stamps():
    global song
    unload_current_song()
    
    low_list = markers_dict["L"]
    medium_list = markers_dict["M"]
    high_list = markers_dict["H"]
    
    song_name = song.split("/")[-1].replace(".mp3", "")
    
    if len(low_list) != 0:
        if song_name not in low_contents.keys():
            low_contents[song_name] = []
            
        low_contents[song_name] = low_list
        
    if len(medium_list) != 0:
        if song_name not in medium_contents.keys():
            medium_contents[song_name] = []
            
        medium_contents[song_name] = medium_list
        
    if len(high_list) != 0:
        if song_name not in low_contents.keys():
            high_contents[song_name] = []
            
        high_contents[song_name] = high_list
        
    export_to_txt()
    
def export_to_txt():
    open_file_export('./timestamps/low.txt', contents_to_string(low_contents))
    open_file_export('./timestamps/medium.txt', contents_to_string(medium_contents))
    open_file_export('./timestamps/high.txt', contents_to_string(high_contents))

def contents_to_string(a_contents):
    ouput = []
    for key, value in a_contents.items():
        temp = key + "!" + ",".join(value)
        ouput.append(temp)
        
    return ";".join(ouput)

def open_file_export(file, export_list):
    with open(file, "w", encoding="utf-8") as file_open:
        file_open.write(export_list)
    

def open_file_list(file, list_in):
    with open(file, "r", encoding="utf-8") as file_open:
        contents = file_open.read().split(";")
        
        for songs in contents:
            if len(songs) != 0:
                both = songs.split("!")
                list_in[both[0]] = both[1].split(",")
                
    for items in list_in.keys():
        for bits in list_in[items]:
            if bits == "":
                list_in[items].remove(bits)

def import_lists():
    global low_contents
    global medium_contents
    global high_contents
    
    open_file_list('./timestamps/low.txt', low_contents)
    open_file_list('./timestamps/medium.txt', medium_contents)
    open_file_list('./timestamps/high.txt', high_contents)
    
def search_for_song(song_name):
    output = []
    
    if song_name in low_contents.keys():
        output.append(low_contents[song_name])
    else:
        output.append([])
        
    if song_name in medium_contents.keys():
        output.append(medium_contents[song_name])
    else:
        output.append([])
        
    if song_name in high_contents.keys():
        output.append(high_contents[song_name])
    else:
        output.append([])
    
    return output

def markers_clear_and_add(add_these):
    global markers_dict
    
    markers_dict = {"L":add_these[0], "M":add_these[1], "H":add_these[2]}'''
    
def refresh_file_lists():
    selections_box.delete(0, END)
    path = './effects/' + option.get()
    for file in os.listdir(path):
        selections_box.insert(END, file.replace('.mp3', ''))
    if selections_box.size() == 0:
        remove_effect_btn["state"] = DISABLED
    else:
        remove_effect_btn['state'] = NORMAL

def ask_and_download():
    video_link = simpledialog.askstring("Video Source", "Youtube link", parent=root)
    download_threading(video_link)

def download_audio(url):
    if url is not None:
        try:
            videos = pafy.new(url)
            title_of = videos.title.replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            
            audiostreams = videos.getbest(preftype="mp4")
            audiostreams.download()
            
            try:
                global song
                ffmpeg_extract_audio("./" + title_of + ".mp4", "./audio/" + title_of + ".mp3")
                
                song = "./audio/" + title_of + ".mp3"
                add_song()
                #os.remove("./" + title_of + ".mp4")
            except:
                change_label("Conversion error")
                
            finally:
                os.remove("./" + title_of + ".mp4")
        except:
            change_label("Video not found")
            
def download_threading(url):
    change_label('Working...')
    threading.Thread(target=download_audio, args=(url,)).start()
        
def search_youtube():
    search = simpledialog.askstring("Video Source", "Youtube Search", parent=root)
    
    search_result = SearchVideos(search, offset = 1, mode = "dict", max_results = 1)
    
    video_link = search_result.result()["search_result"][0]["link"]
    download_threading(video_link)
    
def start_spotify(trackSelectionList):
    global spotify_paused
    if loaded_creds and spotify_paused:
        spotifyObject.shuffle(True)
        spotifyObject.start_playback(deviceID, None, trackSelectionList)
        change_label('Playing Spotify')
        spotify_paused = False
        
def start_spotify():
    global spotify_paused
    if loaded_creds and spotify_paused:
        spotifyObject.shuffle(True)
        spotifyObject.start_playback(deviceID)
        change_label('Playing Spotify')
        spotify_paused = False

def stop_spotify():
    if loaded_creds:
        try:
            spotifyObject.pause_playback(deviceID)
        except:
            pass
        finally:
            global spotify_paused
            spotify_paused = True
            

def play_spotify_playlist():
    if not loaded_creds:
        authenticate_spotify()
    else:
        searchQuery = simpledialog.askstring("Playlist", "Name", parent=root)
        
        if searchQuery is not None:
            searchResults = spotifyObject.search(searchQuery,1,0,'playlist')
            
            playlistID = searchResults['playlists']['items'][0]['id']
            items_in_it = spotifyObject.playlist_items(playlistID, additional_types=("track",))['items']

            list_of_songs = []

            for item in items_in_it:
                list_of_songs.append(item['track']['uri'])
                
            start_spotify(list_of_songs)

def play_spotify_album():
    if not loaded_creds:
        authenticate_spotify()
    else:
        searchQuery = simpledialog.askstring("Album", "Name", parent=root)
        
        if searchQuery is not None:
            searchResults = spotifyObject.search(searchQuery,1,0,'album')
        
            albumID = searchResults['albums']['items'][0]['id']
            trackResults = spotifyObject.album_tracks(albumID)['items']
            
            play_list = []
            
            for item in trackResults:
                play_list.append(item['uri'])
                
            start_spotify(play_list)
        
        
def add_song_to_queue():
    if not loaded_creds:
        authenticate_spotify()
    else:
        searchQuery = simpledialog.askstring("Song", "Name", parent=root)
        
        if searchQuery is not None:
            searchResults = spotifyObject.search(searchQuery,1,0)
            
            songID = searchResults['tracks']['items'][0]['uri']
            
            spotifyObject.add_to_queue(songID)
            
def search_playlist_and_add():
    if not loaded_creds:
        authenticate_spotify()
    else:
        searchResults = spotifyObject.search(input('Search playlist: '),1,0,'playlist')
        
        playlistID = searchResults['playlists']['items'][0]['id']
        items_in_it = spotifyObject.playlist_items(playlistID, additional_types=("track",))['items']

        list_of_songs = []

        for item in items_in_it:
            list_of_songs.append(item['track']['uri'])
        
        spotifyObject.user_playlist_create('timetraveller01', 'test')
        
        for songs in list_of_songs:
            print(songs)

def authenticate_spotify():
    a_window = Toplevel(root)
    a_window.geometry("200x300")
    
    id_frame = LabelFrame(a_window, text='Client Id')
    id_frame.pack(pady=10)
    id_entry = Entry(id_frame)
    id_entry.grid(padx=10, pady=10)
    
    secret_frame = LabelFrame(a_window, text='Client Secret')
    secret_frame.pack(pady=10)
    secret_entry = Entry(secret_frame)
    secret_entry.grid(padx=10, pady=10)
    
    uri_frame = LabelFrame(a_window, text='Redirect Uri')
    uri_frame.pack(pady=10)
    uri_entry = Entry(uri_frame)
    uri_entry.grid(padx=10, pady=10)
    
    confirm_btn = Button(a_window, text='Confirm', command=lambda:delete_window_and_auth(id_entry.get(), secret_entry.get(), uri_entry.get(), a_window))
    confirm_btn.pack(pady=10)
    
def delete_window_and_auth(client_id, client_secret, redirect_uri, window):
    window.destroy()
    confirm_spotify(client_id, client_secret, redirect_uri)

def confirm_spotify(client_id, client_secret, redirect_uri):
    try:
        global spotifyObject
        global deviceID
        scope = 'user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public'

        auth_manager = spotipy.SpotifyOAuth(scope=scope,
                                            client_id=client_id,
                                            client_secret=client_secret,
                                            redirect_uri=redirect_uri
                                            )
        
        spotifyObject = spotipy.Spotify(auth_manager=auth_manager)
        
        cred_dict['client_id'] = client_id
        cred_dict['client_secret'] = client_secret
        cred_dict['redirect_uri'] = redirect_uri
        
        try:
            deviceID = spotifyObject.devices()['devices'][0]['id']
        except:
            #pass
            change_label('No spotify open')
        
        save_creds()
        stop_spotify()
        
    except:
        change_label('Failed to authenticate')
        
def save_creds():
    message = f'client_id={cred_dict["client_id"]};client_secret={cred_dict["client_secret"]};redirect_uri={cred_dict["redirect_uri"]}'
    with open('spotify_creds.txt', 'w') as f:
        f.write(message)
        
def load_spotify_credentials():
    if 'spotify_creds.txt' in os.listdir():
        global loaded_creds
        with open('spotify_creds.txt', 'r+') as f:
            text = f.read()
            if len(text) < 39:
                f.write('client_id=;client_secret=;redirect_uri=')
                text = 'client_id=;client_secret=;redirect_uri='
            
        splitted = text.split(';')
        
        for item in splitted:
            item = item.split('=')
            cred_dict[item[0]] = item[1]
            
        #print(cred_dict)
        loaded_creds = True
        
        for value in cred_dict.values():
            if value == '':
                loaded_creds = False
                break
        
    else:
        with open('spotify_creds.txt', 'w') as f:
            f.write('client_id=;client_secret=;redirect_uri=')

def load_actions_file():
    if 'actions_file.txt' in os.listdir():
        with open('actions_file.txt', 'r+') as f:
            text = f.read()
        
        splitted = text.split('.')
        
        fail_list = splitted[0].split(';')
        fail_list = do_list(fail_list)
            
        confused_list = splitted[1].split(';')
        confused_list = do_list(confused_list)
        
        win_list = splitted[2].split(';')
        win_list = do_list(win_list)
        
        actions_list_dict['fail'] = fail_list
        actions_list_dict['confused'] = confused_list
        actions_list_dict['win'] = win_list
        
        print(actions_list_dict)
        
    else:
        with open('actions_file.txt', 'w') as f:
            f.write('23;1,2,3,4.1;2,6,7.34;2,3,4,5,6')

def do_list(in_list):
    try:
        out_list = [int(in_list[0])]
    except:
        out_list = [0]
    
    '''
    for items in in_list:
        temp_list = items.split(',')
        temp_list2 = []
        for not_number_number in temp_list:
            try:
                temp_list2.append(int(not_number_number))
            except:
                pass
        if len(temp_list2) != 0:
            out_list.append(temp_list2)
    '''
    tlist = in_list[1].split(',')
    print(tlist)
    temp_list = []
    
    for items in tlist:
        try:
            temp_list.append(int(items))
        except:
            pass
    
    out_list.append(temp_list)
        
    print(out_list)
    return out_list
    
def save_actions_file():
    message = f'actions_list_dict["fail"].actions_list_dict["confused"].actions_list_dict["win"]'
    with open('actions_file.txt', 'w') as f:
        f.write(message)

'''
def get_average_list():
    only need list and number {list:number}
    not list, list, list, list
    fix
'''

def add_in_actions_list(category):
    things = actions_list_dict[category]
    things
        
def clear_downloads():
    for file in os.listdir('./audio'):
        os.remove('./audio/' + file)

def open_downloads():
    os.system('start audio')

# global variables
global spotifyObject
global deviceID
global spotify_paused

# declaring and start
actionsPerMinute = 0
appIsRunning = False
paused = False
play_time_started = False
song_length = 100
song=""
loaded_creds = False
last_marker = -1
last_20_actions = []

for i in range(0, 20):
    last_20_actions.append(0)
    
cred_dict = {}

actions_list_dict = {'fail':[], 'confused':[], 'win':[]}
#load_actions_file()

pygame.mixer.init()

root = Tk()
root.title("Song Player")
#root.iconbitmap()
root.geometry("650x300")

top_menu = Menu(root)
root.config(menu=top_menu)

config_menu = Menu(top_menu, tearoff=0)
top_menu.add_cascade(label="Config", menu=config_menu)
config_menu.add_command(label="Open Downloads", command=open_downloads)
config_menu.add_command(label="Clear Downloads", command=clear_downloads)

add_song_menu = Menu(top_menu, tearoff=0)
top_menu.add_cascade(label="Import For Effect", menu=add_song_menu)
add_song_menu.add_command(label="Local Song", command=ask_for_local)
add_song_menu.add_command(label="Youtube Link", command=ask_and_download)
add_song_menu.add_command(label="Youtube Search", command=search_youtube)

spotify_menu = Menu(top_menu, tearoff=0)
top_menu.add_cascade(label="Spotify", menu=spotify_menu)
spotify_menu.add_command(label="Authenticate", command=authenticate_spotify)
spotify_menu.add_command(label="Play Playlist", command=play_spotify_playlist)
spotify_menu.add_command(label="Play Album", command=play_spotify_album)
spotify_menu.add_command(label="Add Song To Queue", command=add_song_to_queue)


both_frame = Frame(root)
both_frame.pack()

left_frame = Frame(both_frame)
left_frame.grid(row=0, column=0, padx=20)

radio_frame = Frame(left_frame)
radio_frame.grid(row=0, column=0, pady=10)

#low, medium, high
option = StringVar()
option.set("fail")

fail_radio_btn = Radiobutton(radio_frame, text="Fail", variable=option, value="fail", command=refresh_file_lists)
confused_radio_btn = Radiobutton(radio_frame, text="Confused", variable=option, value="confused", command=refresh_file_lists)
win_radio_btn = Radiobutton(radio_frame, text="Win", variable=option, value="win", command=refresh_file_lists)

fail_radio_btn.grid(row=0, column=0, padx=10)
confused_radio_btn.grid(row=0, column=1, padx=10)
win_radio_btn.grid(row=0, column=2, padx=10)

song_label = Label(left_frame, text="Pick a song")
song_label.grid(row=1, column=0, pady=10)


load_spotify_credentials()
if loaded_creds:
    confirm_spotify(cred_dict['client_id'], cred_dict['client_secret'], cred_dict['redirect_uri'])

#search_playlist_and_add()


music_slider = ttk.Scale(left_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=300)
music_slider["state"] = DISABLED
music_slider.grid(row=2, column=0, pady=10)

controls_frame = Frame(left_frame)
controls_frame.grid(row=4, column=0, pady=10)

play_pause_btn = Button(controls_frame, text="Play/Pause", command=play_pause)
trim_part_btn = Button(controls_frame, text="Trim Part", command=get_marker_for_trim)
save_whole_effect = Button(controls_frame, text="Save Whole Effect", command=save_whole_effect)
remove_effect_btn = Button(controls_frame, text="Delete Effect", command=remove_effect)
#save_btn = Button(controls_frame, text="Save", command=save_time_stamps)

play_pause_btn["state"] = DISABLED
trim_part_btn["state"] = DISABLED
save_whole_effect["state"] = DISABLED
remove_effect_btn["state"] = DISABLED
#save_btn["state"] = DISABLED

play_pause_btn.grid(row=0, column=0, padx=10)
trim_part_btn.grid(row=0, column=1, padx=10)
save_whole_effect.grid(row=0, column=2, padx=10)
remove_effect_btn.grid(row=0, column=3, padx=10)
#save_btn.grid(row=0, column=4, padx=10)


selection_frame = Frame(both_frame)
selection_frame.grid(row=0, column=1, pady=10)

yscrollbar = Scrollbar(selection_frame)
yscrollbar.pack(side="right", fill="y")

xscrollbar = Scrollbar(selection_frame, orient='horizontal')
xscrollbar.pack(side="bottom", fill="x")

selections_box = Listbox(selection_frame, width=30)
selections_box.pack(side="left", fill="y")

xscrollbar.config(command=selections_box.xview)
yscrollbar.config(command=selections_box.yview)
selections_box.config(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)


refresh_file_lists()


bottom_frame = Frame(root)
bottom_frame.pack()

volume_frame = LabelFrame(bottom_frame, text="Volume")
volume_frame.grid(row=0, column=0, padx=10)

volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient=HORIZONTAL, value=50, command=volume, length=200)
volume_slider.grid(row=0, column=0, padx=10, pady=6)

start_btn = Button(bottom_frame, text="Start", command=start_listening)
start_btn.grid(row=0, column=1, padx=10)

stop_btn = Button(bottom_frame, text="Stop", command=stop_listening)
stop_btn.grid(row=0, column=2, padx=10)
stop_btn["state"] = DISABLED

status_bar = Label(root, text="", bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)


volume(50)

root.protocol("WM_DELETE_WINDOW", on_closing_main)
root.mainloop()
