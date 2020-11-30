import spotipy
import spotipy.util as util

scope = 'user-read-playback-state user-modify-playback-state'

token = util.prompt_for_user_token("Venkata Vivek Thallam", scope,
client_id='31783ef36dc04e8589a58e30bbe327fe',
client_secret='2c03f9ea5fb44d05b7c44016dce2bdeb',
redirect_uri='http://localhost:8888/callback')

sp = spotipy.Spotify(auth=token)

devices = sp.devices()['devices']
device_id = None
for i in range(len(devices)):
    if(devices[i]['is_active']):
        device_id = devices[i]['id']

if device_id == None and len(devices) != 0:
    device_id = devices[0]['id']

if device_id != None:
    if(sp.current_playback()['is_playing']):
        sp.pause_playback(device_id)
    else:
        sp.start_playback(device_id)
else:
    print("Nothing playing!")

# print(sp.current_playback())