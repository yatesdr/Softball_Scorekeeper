
# Softball Scorekeeper

A simple python application developed for E-7 class, which keeps the score of a game and also generates a few different scoreboard overlays for use in a live video stream of the game.

# How to use
Download the project, and launch client.py.   This will start the command line client utility.   Type 'help' for help.

See the docs/Submission.txt for more information regarding the philosophy of development and notes on usage.

# Using the overlays in a video
This works well with OBS, just select the appropriate end-point and add it as a browser-source.   The endpoints are:
 /score_bug     Upper corner mini scoreboard.
 /full_score    Box-score, for between innings
 /lower_third   A lower left simple graphic

# Making new templates
The server serves a single file, so you'll need to include all content in the template file including images if desired, as base-64 encoded images.   See the example templates for basic design.

To include the server data, see the docs for supported template substitutions.


# License
This was developed for E-7, Introduction to Computer Science, by myself.  Upon course completion on May 18th, 2025 the license will be MIT license.   Prior to that, the license is proprietary.


