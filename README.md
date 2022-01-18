# Youtube check and autopost

## Setting up:

1 - Install Python and Firefox

2 - Open CMD inside the folder that contain main.py and insert the following command: ```pip install -r requirements.txt```

3 - Open Firefox and login with account of the youtube channel

4 - Copy ```geckodriver.exe``` and paste where ```firefox.exe``` is

5 - Open ```main.py``` 

5.1 - Go to ```C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles``` and copy the path to your profile 
Example: ```C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\sm1g0yf3.default-1631840458096A```. Change the value of ```MOZILLA_PROFILE_PATH``` to the profile folder path and replace ```\``` to ```\\```

5.2 - Add the channel to download the videos in ```CHANNELS```

5.3 - Set the ```SECONDS_BETWEEN_CHECKS``` to as many seconds as you want

5.4 - Set ```INTRO_PATH``` to your introduction before each video or don't fill to not add intro before


## Run

Open CMD inside the folder and run ```main.py```