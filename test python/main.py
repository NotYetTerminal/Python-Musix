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
import pafy
import os
from moviepy.editor import *
from youtubesearchpython import SearchVideos

# game listener
def on_release(key):
    global actionsPerMinute
    actionsPerMinute += 1
    if (key == keyboard.Key.esc):
        stop_listening()
    
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
            
def check_actions():
    if appIsRunning:
        global playing_time
        global actionsPerMinute
        print(actionsPerMinute)
        print(playing_time)
        print(pygame.mixer.music.get_pos())
        print(pygame.mixer.music.get_busy())
        
        # time up
        if pygame.mixer.music.get_pos() > playing_time:
            pygame.mixer.music.fadeout(1000)
        
        if pygame.mixer.music.get_busy() == 0:
            '''
            if actionsPerMinute < 3:
                play_music_from(low_contents)
            elif actionsPerMinute > 8:
                play_music_from(high_contents)
            else:
                play_music_from(medium_contents)
            '''
        elif pygame.mixer.music.get_busy() == 1:
            play_music_from(music_list)
                
        actionsPerMinute = 0
        time.sleep(2)
        threading.Thread(target=check_actions).start()
        
def play_music_from(this_category):
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
    add_in_marker_btn["state"] = DISABLED
    remove_marker_btn["state"] = DISABLED
    save_btn["state"] = DISABLED
    music_slider["state"] = DISABLED
    low_btn["state"] = DISABLED
    medium_btn["state"] = DISABLED
    high_btn["state"] = DISABLED
    
    save_time_stamps()

# tkinter from now on
def on_closing_main():
    pygame.mixer.music.stop()
    stop_listening()
    save_time_stamps()
    root.destroy()
    #quit()

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
        song_label.config(text=name_of_song)
        
        time_stamp_list = search_for_song(name_of_song)
        markers_clear_and_add(time_stamp_list)
        
        for numbers in time_stamp_list:
            if numbers != [""]:
                for nums in numbers:
                    selections_box.insert(END, nums)
        
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
        add_in_marker_btn["state"] = NORMAL
        low_btn["state"] = NORMAL
        medium_btn["state"] = NORMAL
        high_btn["state"] = NORMAL
        
        if selections_box.size() != 0:
            remove_marker_btn["state"] = NORMAL
            save_btn["state"] = NORMAL
        
        if not play_time_started:
            play_time()

def add_in_marker():
    marker = option.get() + "|" + str(time.strftime("%M:%S", time.gmtime(int(music_slider.get())))) + "-->"
    selections_box.insert(END, marker)
    
    markers_dict[option.get()].append(int(music_slider.get()))
    
    add_in_marker_btn["state"] = DISABLED
    add_out_marker_btn["state"] = NORMAL
    remove_marker_btn["state"] = DISABLED
    save_btn["state"] = DISABLED
    start_btn["state"] = DISABLED
    
    low_btn["state"] = DISABLED
    medium_btn["state"] = DISABLED
    high_btn["state"] = DISABLED


def add_out_marker():
    if music_slider.get() > markers_dict[option.get()][-1]:
        marker = selections_box.get(END) + str(time.strftime("%M:%S", time.gmtime(int(music_slider.get()))))
        
        selections_box.delete(END)
        selections_box.insert(END, marker)
        
        markers_dict[option.get()].pop(-1)
        markers_dict[option.get()].append(marker)
        
        add_in_marker_btn["state"] = NORMAL
        add_out_marker_btn["state"] = DISABLED
        remove_marker_btn["state"] = NORMAL
        save_btn["state"] = NORMAL
        start_btn["state"] = NORMAL
        
        low_btn["state"] = NORMAL
        medium_btn["state"] = NORMAL
        high_btn["state"] = NORMAL

def remove_marker():
    if selections_box.get(ANCHOR) != "":
        markers_dict[selections_box.get(ANCHOR)[0]].remove(selections_box.get(ANCHOR))
    
    selections_box.delete(ANCHOR)
    if selections_box.size() == 0:
        remove_marker_btn["state"] = DISABLED
        save_btn["state"] = DISABLED


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
    add_in_marker_btn["state"] = DISABLED
    remove_marker_btn["state"] = DISABLED
    save_btn["state"] = DISABLED
    music_slider["state"] = DISABLED
    low_btn["state"] = DISABLED
    medium_btn["state"] = DISABLED
    high_btn["state"] = DISABLED
    
    selections_box.delete(0, END)
    status_bar.config(text="")
    
    change_label("Pick a song")
    
def change_label(text_in):
    song_label.config(text=text_in)
    
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
    
    markers_dict = {"L":add_these[0], "M":add_these[1], "H":add_these[2]}

# use spotify instead of youtube
'''
def ask_and_download():
    video_link = simpledialog.askstring("Video Source", "Youtube link", parent=root)
    download_audio(video_link)

    
def download_audio(url):
    if url is not None:
        try:
            videos = pafy.new(url)
            title_of = videos.title.replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("|", "_")
            
            audiostreams = videos.getbest(preftype="mp4")
            audiostreams.download()
            
            try:
                global song
                video = VideoFileClip("./" + title_of + ".mp4")
                video.audio.write_audiofile("./audio/" + title_of + ".mp3")
                
                video.close()
                song = "./audio/" + title_of + ".mp3"
                add_song()
            except:
                change_label("Conversion error")
                
            finally:
                os.remove("./" + title_of + ".mp4")
        except:
            change_label("Video not found")
        
        

def search_youtube():
    search = simpledialog.askstring("Video Source", "Youtube Search", parent=root)
    
    search_result = SearchVideos(search, offset = 1, mode = "dict", max_results = 1)
    
    video_link = search_result.result()["search_result"][0]["link"]
    download_audio(video_link)
'''

# declaring and start
actionsPerMinute = 0
appIsRunning = False
paused = False
play_time_started = False
song_length = 100
markers_dict = {"L":[], "M":[], "H":[]}
song=""
playing_time = 1000

low_contents = {}
medium_contents = {}
high_contents = {}

import_lists()

pygame.mixer.init()

root = Tk()
root.title("Song Player")
#root.iconbitmap()
root.geometry("550x300")

top_menu = Menu(root)
root.config(menu=top_menu)

add_song_menu = Menu(top_menu, tearoff=0)
top_menu.add_cascade(label="Import", menu=add_song_menu)
add_song_menu.add_command(label="Local Song", command=ask_for_local)


# use spotify instead
'''
online_song_menu = Menu(top_menu, tearoff=0)
top_menu.add_cascade(label="Online", menu=online_song_menu)
online_song_menu.add_command(label="Youtube Link", command=ask_and_download)
online_song_menu.add_command(label="Search Youtube", command=search_youtube)
'''

both_frame = Frame(root)
both_frame.pack()

left_frame = Frame(both_frame)
left_frame.grid(row=0, column=0, padx=20)

radio_frame = Frame(left_frame)
radio_frame.grid(row=0, column=0, pady=10)

#low, medium, high
option = StringVar()
option.set("L")

low_btn = Radiobutton(radio_frame, text="Low", variable=option, value="L")
medium_btn = Radiobutton(radio_frame, text="Medium", variable=option, value="M")
high_btn = Radiobutton(radio_frame, text="High", variable=option, value="H")

low_btn.grid(row=0, column=0, padx=10)
medium_btn.grid(row=0, column=1, padx=10)
high_btn.grid(row=0, column=2, padx=10)

song_label = Label(left_frame, text="Pick a song")
song_label.grid(row=1, column=0, pady=10)

music_slider = ttk.Scale(left_frame, from_=0, to=100, orient=HORIZONTAL, value=0, command=slide, length=300)
music_slider["state"] = DISABLED
music_slider.grid(row=2, column=0, pady=10)

controls_frame = Frame(left_frame)
controls_frame.grid(row=4, column=0, pady=10)

play_pause_btn = Button(controls_frame, text="Play/Pause", command=play_pause)
add_in_marker_btn = Button(controls_frame, text="Add In", command=add_in_marker)
add_out_marker_btn = Button(controls_frame, text="Add Out", command=add_out_marker)
remove_marker_btn = Button(controls_frame, text="Remove", command=remove_marker)
save_btn = Button(controls_frame, text="Save", command=save_time_stamps)

play_pause_btn["state"] = DISABLED
add_in_marker_btn["state"] = DISABLED
add_out_marker_btn["state"] = DISABLED
remove_marker_btn["state"] = DISABLED
save_btn["state"] = DISABLED

play_pause_btn.grid(row=0, column=0, padx=10)
add_in_marker_btn.grid(row=0, column=1, padx=10)
add_out_marker_btn.grid(row=0, column=2, padx=10)
remove_marker_btn.grid(row=0, column=3, padx=10)
save_btn.grid(row=0, column=4, padx=10)

selections_box = Listbox(both_frame)
selections_box.grid(row=0, column=1, pady=10)

#show current sections

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

