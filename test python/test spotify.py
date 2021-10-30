import spotipy
# https://dev.to/arvindmehairjan/how-to-play-spotify-songs-and-show-the-album-art-using-spotipy-library-and-python-5eki#:~:text=Go%20to%20Python%20Foundation%20and,the%20page%20and%20install%20it.&text=After%20you%20have%20installed%20the,login%20with%20your%20Spotify%20account.
# changed _get_user_input in oauth2.py
# form raw_input(prompt)
# to pyautogui.prompt(text=prompt)
#username = sys.argv[1]
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
'''
token = spotipy.util.prompt_for_user_token(scope=scope,
                                   client_id='',
                                   client_secret='',
                                   redirect_uri=''
                                   )

spotifyObject = spotipy.Spotify(auth=token)'''

ID = ''
secret = ''
uri = ''

auth_manager = spotipy.SpotifyOAuth(scope=scope,
                                   client_id=ID,
                                   client_secret=secret,
                                   redirect_uri=uri
                                   )

spotifyObject = spotipy.Spotify(auth_manager=auth_manager)


devices = spotifyObject.devices()
deviceID = devices['devices'][0]['id']


track = spotifyObject.current_user_playing_track()
artist = track['item']['artists'][0]['name']
track = track['item']['name']

if artist !="":
    print("Currently playing " + artist + " - " + track)
    
#user = spotifyObject.current_user()
#displayName = user['display_name']
#follower = user['followers']['total']

playlists = spotifyObject.current_user_playlists()

for plays in playlists['items']:
    print(plays['name'])

while True:

    name_of_playlist = input("Which playlist to play? ")
    
    if name_of_playlist == 'x':
        break
    
    for plays in playlists['items']:
        if name_of_playlist in plays['name']:
            play_id = plays['id']
            break

    items_in_it = spotifyObject.playlist_items(playlist_id=play_id, additional_types=("track",))

    list_of_songs = []

    for i in items_in_it['items']:
        list_of_songs.append(i['track']['uri'])

    spotifyObject.shuffle(True)
    spotifyObject.start_playback(deviceID, None, list_of_songs)
    spotifyObject.pause_playback(deviceID)

while True:

    print()
    #print(">>> Welcome to Spotify " + displayName + " :)")
    #print(">>> You have " + str(follower) + " followers.")
    print()
    print("0 - Search for an artist")
    print("1 - exit")
    print()
    choice = input("Enter your choice: ")
    
    
    if choice == "0":
        print()
        searchQuery = input("Ok, what's their name?: ")
        print()
        
        searchResults = spotifyObject.search(searchQuery,1,0,"artist")
        
        artist = searchResults['artists']['items'][0]
        print(artist['name'])
        print(str(artist['followers']['total']) + " followers")
        print(artist['genres'][0])
        print()
        #webbrowser.open(artist['images'][0]['url'])
        artistID = artist['id']
        
        trackURIs = []
        trackArt = []
        z = 0
        
        albumResults = spotifyObject.artist_albums(artistID)
        albumResults = albumResults['items']

        for item in albumResults:
            print("ALBUM: " + item['name'])
            albumID = item['id']
            albumArt = item['images'][0]['url']

            # Extract track data
            trackResults = spotifyObject.album_tracks(albumID)
            trackResults = trackResults['items']

            for item in trackResults:
                print(str(z) + ": " + item['name'])
                trackURIs.append(item['uri'])
                trackArt.append(albumArt)
                z+=1
            print()
        
        while True:
            songSelection = input("Enter a song number to see the album art: ")
            if songSelection == "x":
                break
            trackSelectionList = []
            trackSelectionList.append(trackURIs[int(songSelection)])
            spotifyObject.start_playback(deviceID, None, trackSelectionList)
            #webbrowser.open(trackArt[int(songSelection)])
        
    if choice == "1":
        break