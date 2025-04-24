# Note to TA's / Staff:
# For evaluation you can simply launch client.py in cs50.dev - it will offer to 
# also spawn the server for you.   Choose 'y' and you can begin using
# the application via command line with no other setup.

# If you wish to use server.py directly, you'll need to also launch client.py
# and decline the offer to start the server by pressing 'n'.

import json, sys, signal
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

# Allow config of team names.
HOME_TEAM_NAME = "Lancers"
VISITOR_TEAM_NAME = "Visitor"


# Define template names globally
template_dir = "templates/"
score_bug = template_dir+"score_bug.html" # corner graphic template
lower_third = template_dir+"lower_third.html" # Bottom graphic template
full_score = template_dir+"full_score.html" # Box score template

# Global application state.   Is not thread-safe, but client.py only
# communicates via API by design.
state = {
    "home": {
        "runs": [],
        "hits": [],
        "errors": [],
        "walks": [],
        "steals": [],
        "pitches": [],
        "name": HOME_TEAM_NAME
    },
    "away": {
        "runs": [0,], # Start in the top of the 1st inning at application launch.
        "hits": [],
        "errors": [],
        "walks": [],
        "steals": [],
        "pitches": [],
        "name": VISITOR_TEAM_NAME
    },
    "count": {
        "balls": 0,
        "strikes": 0,
        "outs": 0
    },
    "bases": {
        "first": False,
        "second": False,
        "third": False
    },
    "inning": 1,
    "bottom": False,
}

# Replaces all valid substitutions found in a provided template file
# Returns the rendered result as a string.
def render_template(template_file):

    # Load template from disk, or error.
    try:
        with open(template_file) as f:
            tmpl = f.read()
    except:
        return f"Error: Template {template_file} not found"

    # Some elements are rendered by setting element colors in the template.
    # This can be any valid HTML color.
    on_color = "gold"
    off_color = "white"

    # Pre-compute color-render vars for readability.
    ball1=on_color if state['count']['balls'] >= 1 else off_color
    ball2=on_color if state['count']['balls'] >= 2 else off_color
    ball3=on_color if state['count']['balls'] >= 3 else off_color

    base1=on_color if state['bases']['first'] else off_color
    base2=on_color if state['bases']['second'] else off_color
    base3=on_color if state['bases']['third'] else off_color

    strike1=on_color if state['count']['strikes'] >= 1 else off_color
    strike2=on_color if state['count']['strikes'] >= 2 else off_color

    out1=on_color if state['count']['outs'] >= 1 else off_color
    out2=on_color if state['count']['outs'] >= 2 else off_color

    # Build a dict of static substitutions.
    # The general format for template use is %VAR_NAME% (see example templates)
    replacements = {
        '%HOME_NAME%': HOME_TEAM_NAME,
        '%VISITOR_NAME%': VISITOR_TEAM_NAME,
        '%VISITOR_RUNS%': sum(state['away']['runs']),
        '%HOME_RUNS%': sum(state['home']['runs']),
        '%VISITOR_HITS%': sum(state['away']['hits']),
        '%HOME_HITS%': sum(state['home']['hits']),
        '%VISITOR_ERRORS%': sum(state['away']['errors']),
        '%HOME_ERRORS%': sum(state['home']['errors']),
        '%VISITOR_PITCHES%': sum(state['away']['pitches']),
        '%HOME_PITCHES%': sum(state['home']['pitches']),
        '%BALL1_COLOR%': ball1,
        '%BALL2_COLOR%': ball2,
        '%BALL3_COLOR%': ball3,
        '%FIRST_BASE_COLOR%': base1,
        '%SECOND_BASE_COLOR%': base2,
        '%THIRD_BASE_COLOR%': base3,
        '%BALLS%': state['count']['balls'],
        '%STRIKES%': state['count']['strikes'],
        '%OUTS%': state['count']['outs'],
        '%STRIKE1_COLOR%': strike1,
        '%STRIKE2_COLOR%': strike2,
        '%OUT1_COLOR%': out1,
        '%OUT2_COLOR%': out2,
        '%INNING%': state['inning'],
        '%TOP_COLOR%': on_color if not state['bottom'] else off_color,
        '%BOTTOM_COLOR%': on_color if state['bottom'] else off_color,
        '%TOP_BOTTOM%': "Top" if not state['bottom'] else 'Bottom',
    }

    # Programmatic addition of the runs, hits, and errors by inning.   Support for up to 8 innings for softball (7 + 1 extra inning)
    for i in range(8):

        # Some replacements render as "" unless the inning has occurred, since Box-score is populated progressively as the game goes on.
        replacements[f"%INNING_{i+1}_HOME_RUNS%"] = state['home']['runs'][i] if len(state['home']['runs'])>i else ""
        replacements[f"%INNING_{i+1}_VISITOR_RUNS%"] = state['away']['runs'][i] if len(state['away']['runs'])>i else ""

        replacements[f"%INNING_{i+1}_HOME_ERR%"] = state['home']['errors'][i] if len(state['home']['errors'])>i else ""
        replacements[f"%INNING_{i+1}_VISITOR_ERR%"] = state['away']['errors'][i] if len(state['away']['errors'])>i else ""

        replacements[f"%INNING_{i+1}_HOME_HITS%"] = state['home']['hits'][i] if len(state['home']['hits'])>i else ""
        replacements[f"%INNING_{i+1}_VISITOR_HITS%"] = state['away']['hits'][i] if len(state['away']['hits'])>i else ""


    # Do the substitutions.   If the key is not in the template, do nothing.
    for r in replacements:
        if r in tmpl:
            tmpl = tmpl.replace(r,str(replacements[r]))

    # Return the substituted template string.
    return tmpl
    

# The server class, extended from BaseHTTPRequestHandler per Python docs.
# This code was heavily influenced by the online documentation, but the implementation is unique and my own work.
class ScoreboardServer(BaseHTTPRequestHandler):

    # Handle GET requests using the basic http.server library.   Developed using http.server documentation.
    def do_GET(self):

        # We only handle HTTP/200 text responses, so send a static header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Build a payload by dispatching the request to our request handler.
        payload = self.dispatch()

        # For debug, print the payloads.
        #print("Payload:",payload)

        # Write the response per http.server docs.
        self.wfile.write(bytes(payload,'utf-8'))

    # Custom method to match path and generate responses.
    def dispatch(self):
        path = self.path
        global state 

        # Welcome page.
        if path=='/':
            payload = "Softball Scorekeeper - D. Yates (2025 - E7 Python Project)"
            return payload
    
        ## /ball - Increments the current ball count and returns the incremented count.
        ##          Also records a pitch for the current pitching team, depending on the inning state (top / bottom).
        ## If balls>3, rolls over to balls=0.
        elif path=='/ball':
            state['count']['balls']+=1
            if (state['count']['balls']>3):
                state['count']['balls']=0

            # Throwing a ball should also increment the pitch count automatically.
            team = "home" if not state['bottom'] else 'away'

            # Extend the pitches array if we've gone into a new inning.
            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            # Record the pitch for the appropriate team.
            state[team]['pitches'][state['inning']-1]+=1

            # Return the payload as the current balls count.
            return str(state['count']['balls'])
        
        elif path=='/ball_decrement':
            state['count']['balls']-=1
            if (state['count']['balls']<0):
                state['count']['balls']=0

            # Retracting a ball should also decrement the pitch count automatically.
            team = "home" if not state['bottom'] else 'away'

            # Extend the pitches array if we've gone into a new inning.
            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            # Record the pitch for the appropriate team.
            state[team]['pitches'][state['inning']-1]-=1
            if state[team]['pitches'][state['inning']-1]<0:
                state[team]['pitches'][state['inning']-1]=0

            # Return the payload as the current balls count.
            return str(state['count']['balls'])

        ## /strike - Increments the current strike count and returns the incremented count.
        ##          Also records a pitch for the current pitching team, depending on the inning state (top / bottom).
        ## If strikes > 2, rolls over to strike=0
        elif path=='/strike':
            state['count']['strikes']+=1
            if (state['count']['strikes']>2):
                state['count']['strikes']=0

            # Throwing a strike should increment the pitch count automatically.
            team = "home" if not state['bottom'] else 'away'

            # Make sure the pitches array is the proper length if we've gone into more innings.
            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            state[team]['pitches'][state['inning']-1]+=1

            return str(state['count']['strikes'])
        
        elif path=='/strike_decrement':
            state['count']['strikes']-=1
            if (state['count']['strikes']<0):
                state['count']['strikes']=0

            # Retracting a strike should decrement the pitch count automatically.
            team = "home" if not state['bottom'] else 'away'

            # Make sure the pitches array is the proper length if we've gone into more innings.
            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            state[team]['pitches'][state['inning']-1]-=1

            if state[team]['pitches'][state['inning']-1]<0:
                state[team]['pitches'][state['inning']-1]=0

            return str(state['count']['strikes'])
        

        ## /pitch_increment - Increments the current pitch count manually (for foul balls, corrections, etc).
        elif path=='/pitch_increment':
            team = "home" if not state['bottom'] else 'away'
            idx = state['inning']-1

            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            state[team]['pitches'][idx]+=1
            return str(sum(state[team]['pitches']))
        
        ## /pitch_decrement - Decrements the pitch count manually (for corrections).
        elif path=='/pitch_decrement':
            team = "home" if not state['bottom'] else 'away'
            idx = state['inning']-1

            while len(state[team]['pitches']) < state['inning']:
                state[team]['pitches'].append(0)

            state[team]['pitches'][idx]-=1

            # Pitches can not be negative for any inning.
            if state[team]['pitches'][idx]<0:
                state[team]['pitches'][idx]=0

            return str(sum(state[team]['pitches']))
        

        ## /out - Increments the current outs count and returns the incremented count.
        ## If outs > 2, rolls over to outs=0
        elif path=='/out':
            state['count']['outs']+=1
            if (state['count']['outs']>2):
                state['count']['outs']=0
            return str(state['count']['outs'])
        
        elif path=='/out_decrement':
            state['count']['outs']-=1
            if (state['count']['outs']<0):
                state['count']['outs']=0
            return str(state['count']['outs'])
        
        ## /reset_count - Resets the count to 0/0 without adding a pitch for the pitching team.
        elif path=='/reset_count':
            state['count']['strikes']=0
            state['count']['balls']=0
            return str(0)
        
        ## /hit - Records a hit for the current team at-bat in the current inning.
        ##          Also records a pitch for the current pitching team, depending on the inning state (top / bottom).
        elif path=='/hit' or path=='/hit_decrement':
            
            inning = state['inning']

            # Manage decrement by changing the direction of count.
            change_by = 1
            if path=='/hit_decrement':
                change_by=-1
            
            # The hit is for the batting team stats.   Home bats at the bottom, visitors at the top.
            batting_team = "home" if state['bottom'] else 'away'
            pitching_team = "home" if not state['bottom'] else 'away'

            # Make sure our array is of the proper length.
            while(len(state[batting_team]['hits'])<inning):
                state[batting_team]['hits'].append(0)


            # Increment / decrement the hit count for this inning.
            state[batting_team]['hits'][inning-1]+=change_by

            # Don't allow negative integers for hits.
            if state[batting_team]['hits'][inning-1]<0:
                state[batting_team]['hits'][inning-1]=0

            # A hit should also record a pitch for the fielding team.
            # Make sure the pitches array is the proper length if we've gone into more innings.
            while len(state[pitching_team]['pitches']) < state['inning']:
                state[pitching_team]['pitches'].append(0)

            state[pitching_team]['pitches'][state['inning']-1]+=1


            # Return the total hits for the game, as a string.
            return str(sum(state[batting_team]['hits']))
        

        ## /error - Records an error for the current field team in the current inning.
        elif path=='/error' or path=='/error_decrement':
            
            inning = state['inning']
            team = "away" if state['bottom'] else 'home'

            change_by = 1
            if path=='/error_decrement':
                change_by=-1
            
            # Make sure our array is of the proper length.
            while(len(state[team]['errors'])<inning):
                state[team]['errors'].append(0)
            
            # Increment / decrement the error count in this inning.
            state[team]['errors'][inning-1]+=change_by

            # Don't allow negative integers for errors.
            if state[team]['errors'][inning-1]<0:
                state[team]['errors'][inning-1]=0
            
            # Return the total errors for the current team, as a string.
            return str(sum(state[team]['errors']))
        
    
        ## /steal - Records a stolen base for the current batting team in the current inning.
        elif path=='/steal' or path=='/steal_decrement':
            
            inning = state['inning']
            team = "home" if state['bottom'] else 'away'

            change_by = 1
            if path=='/steal_decrement':
                change_by=-1
            
            # Make sure our array is of the proper length.
            while(len(state[team]['steals'])<inning):
                state[team]['steals'].append(0)
            
            # Increment / decrement the steals count in this inning.
            state[team]['steals'][inning-1]+=change_by

            # Don't allow negative integers for steals.
            if state[team]['steals'][inning-1]<0:
                state[team]['steals'][inning-1]=0
            
            # Return the total steals for the current team, as a string.
            return str(sum(state[team]['steals']))

        ## /walk - Records a walk for the current pitching team in the current inning.
        ##          A pitch is not recorded, as a ball should be recorded as well which will handle the pitch.
        elif path=='/walk' or path=='/walk_decrement':
            
            inning = state['inning']
            team = "away" if state['bottom'] else 'home' # Away team is pitching in the bottom of the inning.

            change_by = 1
            if path=='/walk_decrement':
                change_by=-1
            
            # Make sure our array is of the proper length.
            while(len(state[team]['walks'])<inning):
                state[team]['walks'].append(0)
            
            # Increment / decrement the walks count in this inning.
            state[team]['walks'][inning-1]+=change_by

            # Don't allow negative integers for walks.
            if state[team]['walks'][inning-1]<0:
                state[team]['walks'][inning-1]=0
            
            # Return the total walks for the current team, as a string.
            return str(sum(state[team]['walks']))
        
        ## /run - Records a run scored for the current pitching team in the current inning.
        elif path=='/run' or path=='/run_decrement':
            
            inning = state['inning']
            team = "home" if state['bottom'] else 'away' # Home team is batting at the bottom of the inning.

            change_by = 1
            if path=='/run_decrement':
                change_by=-1
            
            # Make sure our array is of the proper length.
            while(len(state[team]['runs'])<inning):
                state[team]['runs'].append(0)
            
            # Increment / decrement the runs count in this inning.
            state[team]['runs'][inning-1]+=change_by

            # Don't allow negative integers for runs.
            if state[team]['runs'][inning-1]<0:
                state[team]['runs'][inning-1]=0
            
            # Return the total runs for the current team, as a string.
            return str(sum(state[team]['runs']))
        
        ## /inning_plus or /inning_minus - Sets the current inning state.
        elif path=='/inning_plus' or path=='/inning_minus':
            
            if 'minus' in path:
                state['inning'] -=1
            else:
                state['inning'] +=1 

            if state['inning']<1:
                state['inning']=1
            
            return str(state['inning'])

        ## Toggles the top or bottom of the inning internal state without changing other variables.
        ## Returns the toggled value as a string.
        elif path=='/toggle_top_bottom':
            state['bottom']=not state['bottom']

            if state['bottom']:
                return "Bottom"
            else:
                return "Top"
        
        ## Advance game
        ## Used to progressively walk through the game.   Advancing toggles the top / bottom of an inning,
        ## moves to a new inning if it's currently bottom, and extends the scoring arrays to render box score
        ## properly.
        elif path=='/advance_inning':

            is_bottom = state['bottom']

            # In the bottom of an inning, we advance to the top of the next inning.
            if is_bottom:
                state['inning']+=1
                state['bottom']=False
                while len(state['away']['runs']) < state['inning']:
                      state['away']['runs'].append(0)
                
            # in the top of an inning, just advance to the bottom of the inning.
            else:
                state['bottom']=True
                while len(state['home']['runs']) < state['inning']:
                    state['home']['runs'].append(0)
            
            return "OK"

        ## Manage on-base state.   /toggle_base/1 toggles first base on and off, for example.
        ## used to set base state for rendering in templates - i.e. on first and third.
        elif '/toggle_base/' in path:
            base = int(path.split('/')[-1])

            ret = None
            if base==1:
                state['bases']['first'] = not state['bases']['first']
                ret = state['bases']['first']
            elif base==2:
                state['bases']['second'] = not state['bases']['second']
                ret = state['bases']['second']
            elif base==3:
                state['bases']['third'] = not state['bases']['third']
                ret = state['bases']['third']
            else:
                ret = "Error - unknown base."
            
            if ret==True:
                return "True"
            elif ret==False:
                return "False"
            else:
                return ret
            

        # Debug & integration endpoint.
        elif path=='/get_state':
            return json.dumps(state, indent=2)
        
        # Save state to disk, somewhat unsafely.
        elif path[0:5]=='/save':
            fname = path.split("?fname=")[-1]
            unwanted_chars = "/\\" # Don't allow arbitrary pathing
            for c in unwanted_chars:
                fname = fname.replace(c,"")
            
            fname.replace("/\\","")

            try:
                with open(fname,'w') as f:
                    f.write(json.dumps(state))
                    return "OK"
            except:
                    return "ERROR"

        # Load from disk, somewhat unsafely.
        elif path[0:5]=='/load':
            fname = path.split("?fname=")[-1]

            unwanted_chars = "/\\" # Don't allow arbitrary pathing
            for c in unwanted_chars:
                fname = fname.replace(c,"")

            try:
                with open(fname,'r') as f:
                    state = json.loads(f.read())
                    return("OK")
            except:
                return("ERROR")
        
        # Renders and returns a template for upper corner score-bug.
        elif path=='/scorebug' or path=='/score_bug':
            return render_template(score_bug)
        
        # Renders and returns a template for the lower-third screen.
        elif path=='/lower_third':
            return render_template(lower_third)
        
        # Renders and returns a template for the full scoreboard display.
        elif path=='/full_scoreboard' or path=='/box_score' or path=='/full_score':
            return render_template(full_score)
        

        # Endpoint to request exit of the program.   Added to allow
        # a clean exit when launched as sub-process from client.py
        elif path=='/terminate_thread':
            signal.raise_signal(signal.SIGTERM)
        
        # Getters that do not alter state.  Returns for the relevant team in the field or at-bat depending on the metric.
        # Used for live displays of current stats, and to sync with bitfocus companion app.
        elif path[0:5]=='/get?':
            var = path.split('?var=')[-1]

            if var=='balls':
                return str(state['count']['balls'])
            elif var=='strikes':
                return str(state['count']['strikes'])
            elif var=='outs':
                return str(state['count']['outs'])
            elif var=='hits':
                team = 'home' if state['bottom'] else 'away'
                return str(sum(state[team]['hits']))
            elif var=='steals':
                team = 'home' if state['bottom'] else 'away'
                return str(sum(state[team]['steals']))
            elif var=='errors':
                team = 'away' if state['bottom'] else 'home'
                return str(sum(state[team]['errors']))
            elif var=='walks':
                team = 'away' if state['bottom'] else 'home'
                return str(sum(state[team]['walks']))
            elif var=='inning':
                return str(state['inning'])
            elif var=='top_bottom':
                k = 'Bottom' if state['bottom'] else 'Top'
                return k
            elif var=='runs':
                team = 'home' if state['bottom'] else 'away'
                return str(sum(state[team]['runs']))
            elif var=='pitches':
                team = 'home' if not state['bottom'] else 'away'
                return str(sum(state[team]['pitches']))
            elif var=='home_team_name':
                return HOME_TEAM_NAME
            elif var=='visitor_team_name':
                return VISITOR_TEAM_NAME
            elif var=='batting_team':
                if state['bottom']:
                    return HOME_TEAM_NAME
                else:
                    return VISITOR_TEAM_NAME
        
            elif var=="fielding_team":
                if state['bottom']:
                    return VISITOR_TEAM_NAME
                else:
                    return HOME_TEAM_NAME
            else:
                return str("")
            
        # Handle undefined paths or unknown requests with a HTTP/200 and error text.
        else:
            return("Error - Not found.")
            

# Function to launch the server.   By default direct sys.stderr to server_log.txt
def run_server(quiet=True):

    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address,ScoreboardServer)

    # http.server logs every request to sys.stderr as default.
    # If launched as part of a module, redirect stderr to a file 
    # so it doesn't pollute the client.py output.
    if quiet:
        with open("server_log.txt",'w') as sys.stderr:
            httpd.serve_forever()
    else:
        httpd.serve_forever()

# If server is started directly, do not override sys.stderr
# This allows the usual server logs to print as expected in the console.
if __name__=="__main__":
    run_server(quiet=False)