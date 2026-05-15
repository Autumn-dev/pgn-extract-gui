from enum import Enum

# Exclusive/clashing Flags

# special case, doesn't need a Disabled value, handled slightly differently in command builder.
class FileWriteMode(Enum):
    """File write mode options for command-line arguments.
    """
    Overwrite = "-o"
    Append = "-a"


class GameEndConditions(Enum):
    """Game end conditions for command-line arguments.
    """
    Disabled = ""
    Checkmate = "--checkmate"
    Stalemate = "--stalemate"
    Insufficient = "--insufficient"


class WinnerRating(Enum):
    """Winner rating options for command-line arguments.
    """
    Disabled = ""
    Higher = "--higherratedwinner"
    Lower = "--lowerratedwinner"


class Repetition(Enum):
    """Repetition options for command-line arguments.
    """
    Disabled = ""
    Three = "--repetition"
    Five = "--repetition5"


class NoCapture(Enum):
    """No capture options for command-line arguments.
    """
    Disabled = ""
    Fifty = "--fifty"
    SeventyFive = "--seventyfive"


class Duplicates(Enum):
    """Duplicate handling options for command-line arguments.
    """
    Disabled = ""
    SuppressDuplicates = "--noduplicates"
    SaveDuplicates = "--duplicates"


class SetUpTags(Enum):
    """Setup tag options for command-line arguments.
    """
    Disabled = ""
    OnlySetupTags = "--onlysetuptags"
    NoSetupTags = "--nosetuptags"


class Comments(Enum):
    """Comment handling options for command-line arguments.
    """
    Disabled = ""
    AtLeastOne = "--commented"
    NoComments = "--nocomments"


class ToMove(Enum):
    """To move options for command-line arguments.
    """
    Disabled = ""
    Black = "--btm"
    White = "--wtm"


class LogFile(Enum):
    """Log file options for command-line arguments.
    """
    Disabled = ""
    OverwriteLogFile = "-l"
    AppendLogFile = "-L"


class MaterialMatches(Enum):
    """Material matching options for command-line arguments.
    """
    Disabled = ""
    FileMaterialY = "-y"
    InlineMaterialY = "--materialy"
    FileMaterialZ = "-z"
    InlineMaterialZ = "--materialz"
    

class VariantHandling(Enum):
    """Variant handling options for command-line arguments.
    """
    Disabled = ""
    Split = "--splitvariants"
    Suppress = "--novars" # -V


class LowerBounds(Enum):
    """Lower bounds for command-line options.
    """
    Disabled = ""
    Ply = "--minply"
    Moves = "--minmoves"


class UpperBounds(Enum):
    """Upper bounds for command-line options.
    """
    Disabled = ""
    Ply = "--maxply"
    Moves = "--maxmoves"


# Non-exclusive flags

class BooleanFlags(Enum):
    """Boolean flags for command-line options.
    """    

    Underpromotion = "--underpromotion"
    StopAfter = "--stopafter"
    FENComments = "--fencomments"
    FENDescriptions = "-F"
    HashComments = "--hashcomments"
    Evaluation = "--evaluation"
    FuzzyDepth = "--fuzzydepth"
    MarkMatches = "--markmatches"
    FENCastling = "--addfencastling"
    NestedComments = "--nestedcomments"
    NoFauxEP = "--nofauxep"
    SelectOnly = "--selectonly"
    SkipMatching = "--skipmatching"
    AddMatchTag = "--addmatchtag"

    PlyLimit = "--plylimit"
    Quiescent = "--quiescent"
    DropPly = "--dropply"
    StartPly = "--startply"
    PlyCount = "--plycount"
    TotalPlyCount = "--totalplycount"
    LimitPlyDepth = "--matchplylimit"

    FirstGame = "--firstgame"
    DeleteSameSetup = "--deletesamesetup"
    Odds = "--odds"
    LineWidth = "-w"
    OutputFormat = "-W" # see OUTPUT_FORMATS in constants.py

    HashMatch = "-H"

    # Output to new file(s)
    NonMatch = "-n"
    ClassifyECO = "-E"
    SplitByChunk = "-#"

    # Tag matching
    TagMatch = "-t"
    MatchSubStr = "--tagsubstr"
    SuppressMatched = "--suppressmatched"
    SoundexMatching = "-S"

    # Tag/file output
    NoTags = "--notags"
    Seven = "-7"
    NoMoveNumbers = "--nomovenumbers"
    NoResults = "--noresults"
    TagOrder = "-R"
    Xroster = "--xroster"

    # Variations
    VariationsComplete = "-x"
    VariationsIncomplete = "-v"
    TextualPermutations = "-P"
    MatchAnywhere = "--vanywhere"

    # Fixes and misc
    KeepBroken = "--keepbroken"
    AllowNull = "--allownullmoves"
    LichessFix = "--lichesscommentfix"
    NoNags = "--nonags" # -N
    MallocOrDieFix = "-Z"

    # stdout tweaks
    ErrorsOnly = "-r"
    QuietMode = "--quiet"
    SilentMode = "-s"

    NoUnique = "--nounique"
    CheckFile = "--checkfile" # -c
    FixResultTags = "--fixresulttags"
    FixTagStrings = "--fixtagstrings"
    NoBadResults = "--nobadresults"
    DropBefore = "--dropbefore"
    CommentLines = "--commentlines"
    
    #t-flags
    Annotator = "-Ta"
    bPlayer = "-Tb"
    Date = "-Td"
    Eco = "-Te"
    FenPattern = "-Tf"
    HashCode = "-Th"
    Player = "-Tp"
    Result = "-Tr"
    wPlayer = "-Tw"