
Template Construction Documentation:

The below placeholders are tested to work with the HTML templates, as demonstrated in the provided samples.
If creating a new template, you can use these magic strings to retrieve the associated data during render.

Aggregate variables - returns the sum of all innings as a string.
    %VISITOR_RUNS%
    %HOME_RUNS%
    %VISITOR_HITS% 
    %HOME_HITS%
    %VISITOR_ERRORS%
    %HOME_ERRORS%
    %VISITOR_PITCHES%
    %HOME_PITCHES%

State variables - Returns a text representation of the relevant field.
    %HOME_NAME% - Name of the home team
    %VISITOR_NAME% - Name of the visiting team
    %BALLS%
    %STRIKES%
    %OUTS%
    %INNING%
    %TOP_BOTTOM%    "Top" or "Bottom"

Color rendering variables - Returns the on_color or off_color depending whether set or unset.
    %BALL1_COLOR%
    %BALL2_COLOR%
    %BALL3_COLOR%
    %STRIKE1_COLOR%
    %STRIKE2_COLOR%
    %OUT1_COLOR%
    %OUT2_COLOR%
    %FIRST_BASE_COLOR%
    %SECOND_BASE_COLOR%
    %THIRD_BASE_COLOR%
    %TOP_COLOR%         on if top of inning
    %BOTTOM_COLOR%      on if bottom of inning


Inning-specific variables - Used for rendering box scores or stats for innings N=1 through N=8
    Home team Runs, Hits, Errors for inning N:
    %INNING_N_HOME_RUNS%
    %INNING_N_HOME_ERR%
    %INNING_N_HOME_HITS%

    Visitor team Runs, Hits, Errors for inning N:
    %INNING_N_VISITOR_RUNS%
    %INNING_N_VISITOR_ERR%
    %INNING_N_VISITOR_HITS%