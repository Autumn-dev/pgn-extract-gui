import os
from enum import Enum

from utils.flags import FileWriteMode, BooleanFlags
from utils.constants import IGNORE_FLAGS, PRIORITY_FLAGS

class CommandBuilder:
    def __init__(self):
        """Build command-line arguments for the pgn-extract tool.
        """        
        self.input_files = []
        self.output_file = ""
        self.filewrite_mode = FileWriteMode.Overwrite
        self.flags = {}


    def build(self):
        """Build the command-line arguments for the pgn-extract tool.

        Returns:
            list: The list of command-line arguments.
        """        
        commands = ["pgn-extract"]
        commands.extend(f"{f}" for f in self.input_files)

        # Place Priority flags before others before looping through
        sorted_flags = sorted(
            self.flags.keys(),
            key=lambda group: (group not in PRIORITY_FLAGS, list(PRIORITY_FLAGS).index(group) if group in PRIORITY_FLAGS else "")
        )

        for group in sorted_flags:
            flag = self.flags[group]["flag"]
            args = self.flags[group]["args"]

            # Only need the arg, flag is just for code recognition
            if flag not in IGNORE_FLAGS:
                commands.append(flag.value)
                if args:
                    commands.extend([args])
            
            else:
                # e.g. -W san becomes -Wsan (for flags that need to have no spaces between arg)
                commands.append(flag.value + args)

        # add filewrite mode and path if path specified
        if self.output_file:
            commands.append(self.filewrite_mode.value)
            commands.append(self.output_file)
            
        print(" ".join(str(command) for command in commands))
        return commands
    

    def add_input_file(self, filename):
        """Add an input file to the command builder.

        Args:
            filename (str): The name of the input file to add.
        """        
        self.input_files.append(filename)
    

    def remove_input_file(self, filename):
        """Remove an input file from the command builder.

        Args:
            filename (str): The name of the input file to remove.
        """        
        self.input_files.remove(filename)


    def clear_inputs(self):
        """Clear all input files from the command builder.
        """        
        self.input_files = []


    def set_output_path(self, filename):
        """Set the output file path for the command builder.

        Args:
            filename (str): The path of the output file + name.
        """        
        self.output_file = self.auto_complete_filename(filename)


    @classmethod
    def auto_complete_filename(self, filename, ext=".pgn"):
        """Automatically complete the filename with the given extension.

        Args:
            filename (str): The name of the file to complete.
            ext (str, optional): The file extension to add. Defaults to ".pgn".

        Returns:
            str: The completed filename.
        """        
        # Check for any file extension, default add .pgn
        if filename and not os.path.splitext(filename)[1]:
            filename += ext
        return filename


    def is_input_list_empty(self):
        """Check if the input file list is empty.

        Returns:
            bool: True if the input file list is empty, False otherwise.
        """        
        return False if self.input_files else True
    

    def set_filewrite_mode(self, mode: FileWriteMode):
        """Set the file write mode for the command builder.

        Args:
            mode (FileWriteMode): The file write mode to set.

        Flags: 
            [-o, -a]
        """
        self.filewrite_mode = mode


    def update_boolean_flag(self, flag_enum: Enum, enabled: bool, args=""):
        """
        Update a boolean flag in the command builder.

        Args:
            flag_enum (Enum): The flag enum to update.
            enabled (bool): Whether to enable or disable the flag.
            args (str, optional): Additional arguments for the flag.
        """
        if enabled:
            self.flags[flag_enum] = {"flag": flag_enum, "args": str(args)}
        else:
            self.flags.pop(flag_enum, None)


    def update_flag_group(self, flag_enum_group: Enum, new_flag, enabled:bool=True, args=""):
        """Update flag group (only for exclusive flags), reference by enum name in dict.

        Args:
            flag_enum_group (Enum): The flag enum group to update.
            new_flag (Enum): The new flag to set.
            enabled (bool, optional): Whether to enable or disable the flag group. Defaults to True.
            args (str, optional): Additional arguments for the flag group. Defaults to "".
        """
        if enabled:
            self.flags[flag_enum_group] = {
                "flag": new_flag,
                "args": str(args)
            }
        else:
            self.flags.pop(flag_enum_group, None)


    def count_lines(self):
        """Count total lines in all input files.

        Returns:
            int: The total number of lines in all input files.
        """        
        count = 0
        for pgn in self.input_files:
            with open(pgn, "r", encoding="utf-8", errors="ignore") as f:
                count+= sum(1 for line in f)

        return count


