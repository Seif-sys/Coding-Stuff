###
This is a mixed reality project that i worked on last summer with my uni in the context of SEP (Software Entwicklung Praktikum)
Nothing fancy just an app that you can run from your android headset (tested only on the meta quest 3 back in the time, but should work fine with any android headset)

###
The main idea of the app is to connect multiple people through the headset to watch a movie. Of course these movies were blender open-source videos, but the app itself in expandable as a streaming service like "Prime Video" and "Netflix". 

After launching the app the user/-s would be in a menu in an augmented reality environment where they can enter a lobby with other users and chose a movie with a basic voting system (majority takes it, in case of a tie random movie). When all viewers are ready they can chose a map from a list. The current state of the app offers 3 possible environments (also expandable), 2 fully virtual (either a living room or a movie theatre) and 3rd mixed reality one. The "screening" in both headsets is synchronized leaving a realistic experience for the viewers.

###
We also set up an apache server were we stored the movies. The folder "streaming-backend" contains all the scripts from the setup, the chunking of the videos, and even testing before integrating in the main app.