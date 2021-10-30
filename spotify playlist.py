import spotipy

def get_playlist_tracks(playlist_id):
    results = spotifyObject.playlist_tracks(playlist_id)
    tracks = {}
    index = 0
    
    for songs in results['items']:
        if index not in tracks.keys():
            tracks[index] = []
        tracks[index].append(songs['track'])
        
    while results['next']:
        index += 1
        results = spotifyObject.next(results)
        for songs in results['items']:
            if index not in tracks.keys():
                tracks[index] = []
            tracks[index].append(songs['track'])
            
    return tracks

def make_complete_list(in_dict):
    output = []
    
    for value in in_dict.values():
        for ids in value:
            output.append(ids)
    
    return output

def make_some_list(in_list, some):
    output = []
    
    for value in in_list:
        output.append(value[some])
    
    return output

def lowering(in_list):
    output = []
    
    for items in in_list:
        output.append(items.lower())
    
    return output

def search_playlist_and_add():
    searchResults = spotifyObject.search(input('Search playlist: '),1,0,'playlist')
    
    playlistID = searchResults['playlists']['items'][0]['id']
    #items_in_it = spotifyObject.playlist_items(playlistID, additional_types=("track",))['items']
    
    items_in_it = get_playlist_tracks(playlistID)
    
    #new_playlist = spotifyObject.user_playlist_create(spotifyObject.current_user()['id'], 'test')
    
    playlists = spotifyObject.current_user_playlists()
    
    searching_name = input('Playlist to add to: ')
    
    current_playlist = 0
    
    for items in playlists['items']:
        if items['name'] == searching_name:
            current_playlist = items['id']
    
    if current_playlist != 0:
        
        own_in_it = get_playlist_tracks(current_playlist)
        complete_list = make_complete_list(own_in_it)
        #print(len(complete_list))
        
        id_list = make_some_list(complete_list, 'id')
        #print(len(id_list))
        name_list = make_some_list(complete_list, 'name')
        name_list = lowering(name_list)
        #print(len(name_list))
        
        outing = []
        for item in items_in_it.values():
            list_of_songs = []
            
            for item_songs in item:
                if item_songs['id'] not in id_list and item_songs['name'].lower() not in name_list:
                    outing.append([item_songs['name'], item_songs['id']])
                    list_of_songs.append(item_songs['id'])
                    id_list.append(item_songs['id'])
                    name_list.append(item_songs['name'])
            
            if len(list_of_songs) != 0:
                spotifyObject.playlist_add_items(current_playlist, list_of_songs)
        
        print(outing)
        print(sorted(id_list))
        print(sorted(name_list))
        
    else:
        print('no')
        
        

client_id = ''
client_secret = ''
redirect_uri = ''

scope = 'user-read-private playlist-modify-private playlist-modify-public'

auth_manager = spotipy.SpotifyOAuth(scope=scope,
                                    client_id=client_id,
                                    client_secret=client_secret,
                                    redirect_uri=redirect_uri
                                    )

spotifyObject = spotipy.Spotify(auth_manager=auth_manager)

search_playlist_and_add()
#deviceID = spotifyObject.devices()['devices'][0]['id']


