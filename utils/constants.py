from utils.flags import *

# UI
min_window_size_w = 1200
min_window_size_h = 650
min_combobox_width = 100
min_command_preview_height = 60
remove_btn_size = 20
san_arg_length = 6

COMMON_TAGS = [
    "Event", "Site", "Date", "Round", "White", "Black", 
    "Result", "ECO", "Opening", "Annotator", "Difficulty",
    "TimeControl", "Elo", "WhiteElo", "BlackElo", "FEN", "SetUp",
    
]

TAG_OPERATORS = [
    "", "=", "<>", "<", ">", "<=", ">=", "=~"
]

# Data : User-friendly name
OUTPUT_FORMATS = {
    "": "Default", 
    "san": "SAN",
    "epd": "EPD", 
    "fen": "FEN",  
    "halg": "Hyphenated Long Algebraic",  
    "lalg": "Long Algebraic", 
    "elalg": "Enhanced Long Algebraic",  
    "xlalg": "Enhanced Long Algebraic with Hyphens/X",  
    "xolalg": "Enhanced Long Algebraic with O-O/O-O-O",    
    "uci": "UCI", 
    "cm": "ChessMaster"
}

"""
Flags to ignore and only use thier arg (flag just for locating in commands list)
Useful for flags like -H or -W where the arg cannot have a space in between 
"""
IGNORE_FLAGS = [
    BooleanFlags.OutputFormat,  # -W
    BooleanFlags.HashMatch, # -H
    BooleanFlags.FENDescriptions, # -F
    
    # -T flags
    BooleanFlags.Annotator,
    BooleanFlags.bPlayer,
    BooleanFlags.Date,
    BooleanFlags.Eco,
    BooleanFlags.FenPattern,
    BooleanFlags.HashCode,
    BooleanFlags.Player,
    BooleanFlags.Result,
    BooleanFlags.wPlayer
]

# Simple solution for -S (and potential future implemented flags) to be first in order of commands
PRIORITY_FLAGS = [
    BooleanFlags.SoundexMatching
]