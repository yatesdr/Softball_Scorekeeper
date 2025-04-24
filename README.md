
# Softball Scorekeeper

A simple python application developed for E-7-Introduction to Computer Science class, which keeps the score of a game and also generates a few different scoreboard overlays for use in a live video stream of the game.   The main goal was to have a low cognitive load for scoring and generating overlays from the press box while multi-tasking, and this utility adopts a unique context-based approach to scoring which is quite nice to use and easy to keep up with during a game.

## How to use
Download the project, and launch client.py.   This will start the command line client utility.   Type 'y' if you wish to start a server in another thread, or 'n' if you're running server.py separately or hosting it somewhere.  After that the client will load - type 'help' for help to see all supported command line client utilities.

<img width="702" alt="image" src="https://github.com/user-attachments/assets/0829f83a-4fda-49da-a7ea-50c6c7c7fbd9" />

Use the client to keep score, and load the overlays in a browser source in OBS to use them as part of your live stream.

See the docs/Submission.txt for more information regarding the philosophy of development and notes on usage.

## Using the overlays in a video stream


### Score Bug:  http://127.0.0.1/score_bug
<img width="282" alt="image" src="https://github.com/user-attachments/assets/f806e405-335d-47ee-a9b1-eec596b7d289" />

### Box Score:  http://127.0.0.1/box_score
<img width="881" alt="image" src="https://github.com/user-attachments/assets/1d9cc9fd-5d30-4c4b-95c7-ff7a10806200" />

### Lower Third:  http://127.0.0.1/lower_third
<img width="526" alt="image" src="https://github.com/user-attachments/assets/f72ed593-0c22-4da7-8d1e-91a4ee6590ee" />


This works well with OBS, just select the appropriate end-point and add it as a browser-source.

## Making new templates
The server serves a single file, so you'll need to include all content in the template file including images if desired, as base-64 encoded images.   See the example templates for basic design.

To include the server data, see the docs for supported template substitutions.


## Integrations with StreamDeck / Bitfocus Companion
The app works well with bitfocus Companion and a streamdeck.   Just map your keys to the appropriate http get() endpoints, or use the sample configuration provided for pre-mapped keys.   If you're using it with companion, I recommend running server.py independently of the command line client so you can see the log history.

## License
This was originally developed for the E-7 "Introduction to Computer Science in Python" course at Harvard Extension school as part of the final term project.  Upon course completion on May 18th, 2025 the license will be MIT license.   Prior to that, the license is proprietary and use is not permitted.



