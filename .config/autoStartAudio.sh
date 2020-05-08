#！/bin/sh
 
sleep 5
alsactl restore -f /home/pi/.config/asound.state
sleep 1
sh ~/.config/start_ec.sh
