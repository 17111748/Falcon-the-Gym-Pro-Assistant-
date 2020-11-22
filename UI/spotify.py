import spotipy
import spotipy.util as util

scope = 'user-read-playback-state, user-modify-playback-state'

token = util.prompt_for_user_token("Venkata Vivek Thallam", scope,
client_id='31783ef36dc04e8589a58e30bbe327fe',
client_secret='2c03f9ea5fb44d05b7c44016dce2bdeb',
redirect_uri='http://localhost:8888/callback')

sp = spotipy.Spotify(auth=token)

device_id = sp.devices()['devices'][0]['id']

sp.start_playback(device_id)
