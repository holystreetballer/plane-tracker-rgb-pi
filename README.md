# planefinal
Hello.
So the basis of this project came from https://github.com/ColinWaddell/its-a-plane-python and his instructions are way better than mine. Mine is running on a Pi3A+ with adafruit bonnet (not hat)
I just added and changed his layout to include scrolling of the full airline name instead of code ie Airline Name 1234 instead of aln1234 and added the matching logo in the corner. If there is no logo than it defaults to a blank plane. Also now displays the distance and direction from your location to the airplane.
I also added a 3 day forecast, well today and the next two days with the high and low temp. 
You'll have to make it executable by running chmod +x /home/path/its-a-plane-python/its-a-plane.py
Although to get it to run on boot youll have to do a crontab -e and do @reboot sleep 60 && sudo ./its-a-plane.py

When you use git to pull these files you'll have to move everything into a folder up. logos and files must be in the main folder ie /home/xxx/ not /home/xxx/plane-tracker-rgb-pi

I'm on reddit under this name if you have any questions or let me know if you make this. youll have to fill out the config file though
![PXL_20230323_000203495](https://user-images.githubusercontent.com/127139588/227799263-05bafba3-a847-4832-8635-f495ca50358b.jpg)
![PXL_20230323_000207446](https://user-images.githubusercontent.com/127139588/227799264-3d6b1132-a177-4c56-ae65-a33387daacf2.jpg)
![PXL_20230323_003309032](https://user-images.githubusercontent.com/127139588/227799265-e80bd531-704b-440d-8b6f-0e2a6b373294.jpg)


