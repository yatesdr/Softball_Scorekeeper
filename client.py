# Note to TA's / Staff:
# For evaluation you can simply launch this file - it will offer to 
# also spawn the server for you.   Choose 'y' and you can begin using
# the application via command line with no other setup.

import requests, json, threading, signal, sys
import server

# Assumes running on localhost / 127.0.0.1 on port 8081 (default)
base_url = "http://127.0.0.1:8081"

# The server can optionally run in another thread for cs50.dev, but doesn't have to.
# Track to know whether to terminate on exit or not.
started_server = False

def main():
    print(chr(27) + "[2J") # clear terminal.   Works for most.
    print("Welcome to scoreboard command-line client utility.  ('help' for help, 'q' to quit)")
    print_score()

    while True:

        cmd = input(" > ")
        print(chr(27) + "[2J") # clear terminal.
        cmd.strip()

        if cmd=='help':
            print("""
    ~~~~~~~ Normal Play ~~~~~~~
    b       ball            (b- to decrement)
    s       strike          (s- to decrement)
    o       out             (o- to decrement)
    c       clear count     
    h       hit             (h- to decrement)
    e       error           (e- to decrement)
    r       score a run     (r- to decrement)
    p       record pitch    (p- to decrement)
    w       record a walk   (w- to decrement)
    st      record a steal  (st- to decrement)
    a       advance game    moves to bottom of current, or top of next inning
    
    1       toggle runner on first base
    2       toggle runner on second base
    3       toggle runner on third base

    ~~~~~~~ Manual Adjustments ~~~~~~~
    +       Next inning
    -       Previous inning             
    top     set top of inning
    bot     set bottom of inning
    
    ~~~~~~~ View state ~~~~~~~
    score   print basic score
    box     print box score, also <enter> prints box score.
    state   print state dict directly
                  
    ~~~~~~~ File IO ~~~~~~~
    save <file>     save the game state to disk
    load <file>     load the game state from disk

                  """)
            
        elif cmd=='q':
            if started_server:
                print("Terminating server thread...")
                fetch("/terminate_thread") # Terminate server thread if started by client.py
            exit()
    
        elif cmd=='b':
            r = fetch("/ball")
            if r:
                print("\t\tRecorded pitch as ball")
                print_score()

        elif cmd=='b-':
            r = fetch("/ball_decrement")
            if r:
                print("\t\tReduced pitch and ball")
                print_score()

        elif cmd=='s':
            r = fetch("/strike")
            if r:
                print("\t\tRecorded pitch as strike")
                print_score()

        elif cmd=='s-':
            r = fetch("/strike_decrement")
            if r:
                print("\t\tReduced pitch and strike")
                print_score()

        elif cmd=='o':
            r = fetch("/out")
            if r:
                print("\t\tOut recorded.")
                print_score()

        elif cmd=='o-':
            r = fetch("/out_decrement")
            if r:
                print("\t\tOut removed.")
                print_score()

        elif cmd=='c':
            r = fetch("/reset_count")
            if r:
                print("\t\tCount cleared")
                print_score()

        elif cmd=='h':
            r = fetch('/hit')
            if r:
                print(f"\t\tPitch recorded as hit.")
                print_score()

        elif cmd=='h-':
            r = fetch('/hit_decrement')
            if r:
                print(f"\t\tHits and pitches reduced.")
                print_score()
        
        elif cmd=='e':
            r = fetch('/error')
            if r:
                print(f"\t\tError counted for the fielding team.")
                print_score()

        elif cmd=='e-':
            r = fetch('/error_decrement')
            if r:
                print(f"\t\tError reduced for the fielding team.")
                print_score()
        
        elif cmd=='r':
            r = fetch('/run')
            if r:
                print("\t\tRun scored for batting team.")
                print_score()

        elif cmd=='r-':
            r = fetch('/run_decrement')
            if r:
                print("\t\tRun reduced.")
                print_score()

        elif cmd=='p':
            r = fetch('/pitch_increment')
            if r:
                print(f"\t\tPitch counted for pitching team.")
                print_score()

        elif cmd=='p-':
            r = fetch('/pitch_decrement')
            if r:
                print(f"\t\tPitch reduced.")
                print_score()

        elif cmd=='st':
            r = fetch('/steal')
            if r:
                print(f"\t\tSteal counted for batting team.")
                print_score()

        elif cmd=='st-':
            r = fetch('/steal_decrement')
            if r:
                print(f"\t\tSteal reduced.")
                print_score()

        elif cmd=='w':
            r = fetch('/walk')
            if r:
                print(f"\t\tWalk counted for pitching team.")
                print_score()

        elif cmd=='w-':
            r = fetch('/walk_decrement')
            if r:
                print(f"\t\tWalk reduced.")
                print_score()
        
        # Handle placing / removing runners on base.
        elif cmd=='1' or cmd=='2' or cmd=='3':
            r = fetch(f"/toggle_base/{cmd}")
            if r=="True":
                print(f"\t\tRunner placed on {cmd}")
            else:
                print(f"\t\tRunner removed from {cmd}")
            print_score()

        # During normal gameplay, advance from top to bottom to next inning.
        elif cmd=='a':
            r = fetch('/advance_inning')
            if r:
                inning = fetch('/get?var=inning')
                top_bot = fetch('/get?var=top_bottom')
                print(f"\t\tGame advanced to {top_bot} of {inning}")
                print_score()
        
        # Manually adjust inning to correct mistakes.
        elif cmd=='+':
            r = fetch('/inning_plus')
            if r:
                print(f"\t\tInning set to {r}")
                print_score()
        
        # Manually adjust inning to correct mistakes.
        elif cmd=='-':
            r = fetch('/inning_minus')
            if r:
                print(f"\t\tInning set to {r}")
                print_score()
        
        # Manually adjust top or bottom of inning to correct mistakes if needed.
        elif cmd=='top' or cmd=='bot':
            top_bot = fetch('/get?var=top_bottom')
            inning = fetch('/get?var=inning')
            if top_bot.lower()[0:3]!=cmd:
                r = fetch('/toggle_top_bottom')
                if r:
                    print(f"\t\tSet to {r} of {inning}")
                    print_score()

            elif top_bot and inning:
                print(f"\t\tAlready {top_bot} of {inning} - no change made.")
                print_score()
            else:
                print(f" Unknown error.") # Shouldn't happen...
        
        # Print the box score
        elif cmd=='box' or cmd=='':
            print_score()

        # Print the standard scoreboard.
        elif cmd=="score":
            print_score(mode="simple")

        # Debug by examining state dict.
        elif cmd=="state":
            print_state()

        # Save the game state to disk.
        elif cmd[0:4]=="save":
            fname = cmd.split()[-1]
            res = fetch(f"/save?fname={fname}")
            print(f"\t\tSaved on server as {fname}: {res}")
            print_score()

        # Load the game state from disk.
        elif cmd[0:4]=="load":
            fname = cmd.split()[-1]
            res = fetch(f"/load?fname={fname}")
            print(f"\t\tLoaded {fname} from server: {res}")
            print_score()
        
        else:
            print("Unknown command - 'help' for help or 'q' to quit.")
            print_score()


# Safely fetch from the API.
def fetch(path):
    full_path = base_url+path

    try:
        resp = requests.get(full_path)
        return resp.text
    
    except:
        print(f"     Error: Unable to connect to server at {base_url} - is it running?")
        return False


def print_box_score():

    # Pull full state to render box score.
    state = json.loads(fetch("/get_state"))


    top_bot = "Top" if not state['bottom'] else "Bottom"
    suffix = None

    # Assign an ordinal indicator suffix to the inning number per english conventions.
    match state['inning']:
        case 1: suffix="st"
        case 2: suffix="nd"
        case 3: suffix="rd"
        case _: suffix="th"
    bso = f"Balls: {state['count']['balls']}   Strikes: {state['count']['strikes']}   Outs: {state['count']['outs']}"

    # Build string to show runner positions on base.
    runner1 = " 1 " if state['bases']['first'] else "   "
    runner2 = " 2 " if state['bases']['second'] else "   "
    runner3 = " 3 " if state['bases']['third'] else "   "
    runners = runner3+runner2+runner1

    str = f"""
    \t\t\t\t\t{top_bot} of {state['inning']}{suffix}

    \t\t\t\t{bso}

    \t\t\t\tRunners on [{runners}]

"""
    print(str)

    cols = ['P','1','2','3','4','5','6','7','(8)','R','|','H','E','W','Sts']
    rows = {"away": state['away']['name'], 'home': state['home']['name']}

    # Print headers
    print(f"{' ':>14}",end="")
    for c in cols:
        print(f"{c:^5}",end="")
    print()
    print(f"{' ':>14}",end="")
    for c in cols:
        if c=='|':
            print(f"{'|':^5}",end="")
        else:
            print(f"{'---':^5}",end="")
    print()

    # Print Visitor and Home stats.
    vbat = " " if state['bottom'] else "*"
    hbat = "*" if state['bottom'] else " "
    batting = {'home': hbat, 'away': vbat}

    for r in rows:
        print(f"{batting[r]}{rows[r]:>12}:", end="")
        print(f"{sum(state[r]['pitches']):^5}",end="")

        # Runs for innings 1-7 + 8
        for i in range(8):
            runs = state[r]['runs'][i] if len(state[r]['runs'])>i else ""
            print(f"{runs:^5}",end="")

        # Total Runs
        print("|",end="")
        print(f"{sum(state[r]['runs']):^3}",end="")
        print("|",end="")

        # Spacer
        print(f"{' | ':^5}",end="")

        # Hits, Errors, Walks, Steals
        print(f"{sum(state[r]['hits']):^5}",end="")
        print(f"{sum(state[r]['errors']):^5}",end="")
        print(f"{sum(state[r]['walks']):^5}",end="")
        print(f"{sum(state[r]['steals']):^5}",end="")

        print()



    print("\n\n\n")

# For debug, not documented.
def print_state():
    state = json.loads(fetch("/get_state"))
    print(json.dumps(state,indent=3))

# Prints the scoreboard, in simple or box mode.   Default changed to box mode.
def print_score(mode="box"):

    if mode=="box":
        print_box_score()
        return

    state = json.loads(fetch("/get_state"))

    if not state:
        return

    top_bot = "Top" if not state['bottom'] else "Bottom"
    suffix = None

    # Assign an ordinal indicator suffix to the inning number per english conventions.
    match state['inning']:
        case 1: suffix="st"
        case 2: suffix="nd"
        case 3: suffix="rd"
        case _: suffix="th"

    # Annotate the batting team with a star.
    vbatt = '* '+state['away']['name']+":" if not state['bottom'] else state['away']['name']+":"
    hbatt = '* '+state['home']['name']+":" if state['bottom'] else state['home']['name']+":"

    # Build string to show runner positions on base.
    runner1 = " 1 " if state['bases']['first'] else "   "
    runner2 = " 2 " if state['bases']['second'] else "   "
    runner3 = " 3 " if state['bases']['third'] else "   "
    runners = runner3+runner2+runner1
    
    bso = f"Balls: {state['count']['balls']}   Strikes: {state['count']['strikes']}   Outs: {state['count']['outs']}"
    str = f"""
        \t\t{top_bot} of {state['inning']}{suffix}

        {' ':^12}{'Runs':^8}{'Pitches':^8}{'Hits':^8}{'Errors':^8}{'Walks':^8}{'Steals':^8}
        {vbatt:>12}{sum(state['away']['runs']):^8}{sum(state['away']['pitches']):^8}{sum(state['away']['hits']):^8}{sum(state['away']['errors']):^8}{sum(state['away']['walks']):^8}{sum(state['away']['steals']):^8}
        {hbatt:>12}{sum(state['home']['runs']):^8}{sum(state['home']['pitches']):^8}{sum(state['home']['hits']):^8}{sum(state['home']['errors']):^8}{sum(state['home']['walks']):^8}{sum(state['home']['steals']):^8}
             
        \t{bso}

        \tRunners on [{runners}]

"""
    
    print(str)


def print_state():
    state = json.loads(fetch("/get_state"))
    print(json.dumps(state,indent=3))

# Need to intercept Ctrl-C to cleanly exit the server thread if needed.
# Install a signal handler for this purpose.
def sig_handler(sig,frame):
    
    # Only kill the server thread if we also started it.
    if started_server:
        print("\nCaught SIGINT - Exiting server thread before stopping...")
        fetch("/terminate_thread")
        print("Server terminated... Done.")

    print("Exiting client application...")
    exit(0)


#  This is a little more involved than the usual main() call, due to having server & client and needing to run on cs50.dev
#  When running this client, you'll be asked to start a server to help ease-of-use for whoever is grading this.
if __name__=="__main__":

    # Server will be started in another thread if requested.
    server_thread = None

    ui = None  # User input for choice to start server.
    while ui==None:
        ui = input("\nWould you like to start the server now? (y or n) ")
        if ui[0].lower()=='y':
            started_server=True
            print("Starting server on default port....")
            server_thread = threading.Thread(target=server.run_server)
            server_thread.start()

        elif ui[0].lower()=='n':
            break
        else:
            ui = None

    # Register our signal handler to clean up threads on ctrl-c if server is running.
    if server_thread is not None:
        signal.signal(signal.SIGINT,sig_handler)

    # Start the client thread.
    print("Starting client application...")
    client_thread = threading.Thread(target=main)
    client_thread.start()

    client_thread.join()
    server_thread.join()
    
