####
The server is now up and running, its a minio-server that still has to be filled with a bucket and streaming files.
It is accessible through http://"ip-adress-of-my-virtual-machine":9001 and the username and password are "seifsep" and "sep12345678" respectfully.

####
Decided to go instead with an apache2 server, I already added a couple of videos to test streaming in Godot.

TODO: set up a scene in godot where a mesh instance can get a streamline from the apache2 server and play said video.

####
As mentioned in my last commit, the server is now able to streamline .ogv files to the godot app.
