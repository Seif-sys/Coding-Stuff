##decided to go with an apache2 server as it was better than minio for our use-case
sudo apt update
sudo apt install apache2

#enabling and starting the server
sudo systemctl enable apache2
sudo systemctl start apache2

#verifying the status
sudo systemctl status apache2

#creating the folder for the videos and adding the ogv file
sudo mkdir /var/www/html/videos
sudo cp /home/ubuntu/Downloads/the-blaze-territory-official-video-online-video-cuttercom-ppunp0.ogv /var/www/html/videos/

#setting permissions
sudo chown -R www-data:www-data /var/www/html/videos
sudo chmod -R 755 /var/www/html/videos

#enabling access from other devices (still on the same ip)
sudo ufw allow 'Apache Full'

##encountered an issue with ogv files being read as ogg

#verifying if its being read correctly
curl -I http://192.168.2.172/videos/the-blaze-territory-official-video-cuttercome-ppunp0.ogv

#changed config file to adapt
sudo nano /etc/apache2/sites-available/000-default.conf
#enabling mod_rewrite and restarting
sudo a2enmod rewrite
sudo systemctl restart apache2

#############################
#chunking the videos to enable streaming instead of download

#chunking the video with a keyframe and forcing a good quality
mkdir chunks3
ffmpeg -i input.ogv -c:v libtheora -q:v 7 -c:a libvorbis -q:a 5 -r 30 -map 0 -f segment -segment_time 5 -reset_timestamps 1 -force_key_frames "expr:gte(t,n_forced*5)" chunks/out%03d.ogv
sudo mv chunks3 /var/www/html/
