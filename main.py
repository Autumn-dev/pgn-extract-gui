import os
import sys
import urllib.request
import darkdetect
import platform
import subprocess
import shutil
import tempfile


from PyQt6.QtGui import QRegularExpressionValidator

from PyQt6.QtCore import (
    QThreadPool,
    Qt,
    QSettings,
    QRegularExpression,
    QTimer
)

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QScrollArea,
    QFrame,
    QFileDialog,
    QMessageBox,
    QTextBrowser,
    QCheckBox,
    QProgressBar,
    QPushButton
)

from utils import *
from extra_widgets import *


class MainWindow(QWidget):
    
    @log_execution_time
    def __init__(self):
        super().__init__()
        self._init_window()

        self.thread_pool = QThreadPool()
        self.command_builder = CommandBuilder()
        self.current_worker = None
        self.config_manager = ConfigManager(self)

        self._init_progress_bar()
        self._init_tabs()
        self._init_main_tab()
        self._init_output_tab()
        self._init_filters_tab()
        self._init_settings_tab()
        self._init_app_settings()


    def _init_window(self):
        self.setWindowTitle("PGN Extract GUI")
        self.resize(constants.min_window_size_w, constants.min_window_size_h)
        self.setMinimumSize(constants.min_window_size_w, constants.min_window_size_h)
        self.layout = QVBoxLayout(self)


    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.output_tab = QWidget()
        self.filters_tab = QWidget()
        self.settings_tab = QWidget()
        self.tabs.addTab(self.main_tab, "File")
        self.tabs.addTab(self.output_tab, "Output")
        self.tabs.addTab(self.filters_tab, "Filters")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.layout.addWidget(self.tabs)


    def _init_app_settings(self):
        """
        Initialize application settings.
        """
        self.settings = QSettings("UniversityOfKent", "pgn-extract-gui")
        self.settings_group = "MainWindow"

        theme_setting = self.settings.value("theme", defaultValue=None)
        if theme_setting == "dark":
            self.toggle_darkmode(True)
            self.darkmode_checkbox.setChecked(True)
        elif theme_setting == "light":
            self.toggle_darkmode(False)
            self.darkmode_checkbox.setChecked(False)
        else:
            # No saved setting – use system default
            is_dark = darkdetect.isDark()
            self.toggle_darkmode(is_dark)
            self.darkmode_checkbox.setChecked(is_dark)

        command_preview_setting = self.settings.value(f"{self.settings_group}/command_preview", defaultValue=False)
        if command_preview_setting is not None:
            preview_show = command_preview_setting == "true"
            self.command_preview_checkbox.setChecked(preview_show)
        else:
            self.command_preview_checkbox.setChecked(False)
        self.command_preview.setVisible(preview_show)

        self.restoreGeometry(self.settings.value("geometry", b""))


    def _init_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setEnabled(False)


    def _init_main_tab(self):
        """
        Build 'File' or main tab.
        Input and output handling, view: pgn input list, stdout, logs.
        """
        self.build_main_widgets()

        # Subcontainer for those elements
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.browse_btn)
        input_layout.addWidget(self.add_path_btn)
        input_layout.addWidget(self.pgn_input_field)
        input_layout.addWidget(self.add_filelist_checkbox)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.pgn_list_container)
        scroll_area.setObjectName("pgnInputs")

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)
        

        # Left panel
        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)
        # Push elements to the top
        left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Add subcontainers/widgets
        left_panel_layout.addLayout(input_layout)
        left_panel_layout.addWidget(self.add_filelist_area)
        left_panel_layout.addWidget(scroll_area)
        left_panel_layout.addWidget(self.clear_btn)
        left_panel_layout.addWidget(self.output_selector)
        left_panel_layout.addWidget(self.filewrite_checkbox)
        left_panel_layout.addWidget(self.extract_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_panel_layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_panel_layout.addLayout(progress_layout)

        # Right panel
        modes_layout = QHBoxLayout()
        modes_layout.addWidget(self.silent_mode_checkbox)
        modes_layout.addWidget(self.errors_only_checkbox)
        modes_layout.addWidget(self.quiet_mode_checkbox)

        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(right_panel_widget)
        right_panel_layout.addLayout(modes_layout)
        right_panel_layout.addWidget(self.output_display)

        panel_layout = QHBoxLayout()
        panel_layout.addWidget(left_panel_widget)
        panel_layout.addWidget(right_panel_widget)

        main_layout = QVBoxLayout()
        main_layout.addLayout(panel_layout)
        main_layout.addWidget(self.command_preview)
        self.main_tab.setLayout(main_layout)


    def build_main_widgets(self):
        """
        Build the main widgets for the application.
        """
        # Output path selector
        self.output_selector = PathInputBlock(placeholder_text="Output file name... e.g., games.pgn")
        self.output_selector.path_changed.connect(self.update_output)

        # -o / -a 
        self.filewrite_checkbox = QCheckBox()
        self.filewrite_checkbox.setObjectName("filewrite-checkbox")
        self.filewrite_checkbox.setChecked(True)
        self.filewrite_checkbox.setText(f"{self.command_builder.filewrite_mode.name} file")
        self.filewrite_checkbox.stateChanged.connect(self.update_filewrite_mode)
        self.filewrite_checkbox.setToolTip("Change filewrite mode - append: add to existing file, overwrite: clear file before writing")

        # Manual filename input and add button
        self.pgn_input_field = QLineEdit()
        self.pgn_input_field.setPlaceholderText("example.pgn...")
        self.pgn_input_field.setFixedSize(160, 25)
        # 'Enter' key can be used as shortcut
        self.pgn_input_field.returnPressed.connect(
            lambda: self.add_pgn() if self.pgn_input_field.text().strip() else None
        )
        self.pgn_input_field.textChanged.connect(
            lambda: self.add_path_btn.setEnabled(bool(self.pgn_input_field.text()))
        )

        # Add pgn filename to inputs
        self.add_path_btn = build_button(
            text="Add .pgn by name ->",
            width=130,
            height=30,
            callback=self.add_pgn,
            tooltip="Add a pgn file as an input"
        )
        self.add_path_btn.setEnabled(False)

        # Browse for file using file explorer button
        self.browse_btn = build_button(
            text="Browse for pgns",
            width=150,
            height=30,
            callback=self.browse_pgn
        )

        # Chosen file display list scroll area
        self.pgn_list_container = QWidget()
        self.pgn_list_layout = QVBoxLayout(self.pgn_list_container)
        self.pgn_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Extract button
        self.extract_btn = build_button(
            text="Extract",
            width=200,
            height=45,
            callback=self.run_extract
        )

        # pgn-extract output view
        self.output_display = OutputViewer()

        # build command preview
        self.command_preview = QTextBrowser()
        self.command_preview.setReadOnly(True)
        self.command_preview.setPlaceholderText("Command preview...")
        self.command_preview.setMaximumHeight(constants.min_command_preview_height)

        # Cancel button for mid-extract process
        #self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn = build_button(
            text="Cancel",
            width=200,
            height=45,
            callback=self.cancel_extract
        )
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self.cancel_extract)

        # --quiet, -s, and -r
        self.errors_only_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.ErrorsOnly,
            label_text="Check games but no output",
            tooltip_text="Does not extract, only report erorrs"
        )

        self.quiet_mode_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.QuietMode,
            label_text="Process but don’t report progress"
        )

        self.silent_mode_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.SilentMode,
            label_text="Report game count and errors",
            tooltip_text="Silent mode (don't report each game as it is extracted)"
        )

        self.clear_btn = build_button(
            text="Clear inputs files",
            width=150,
            height=30,
            callback=self.clear_pgn_inputs,
            tooltip="Clear all pgn inputs"
        )

        # Widgets for -f
        self.add_filelist_checkbox = QCheckBox("Add files from list")
        self.add_filelist_checkbox.setToolTip("-f replacement, Use list of files to add as inputs")
        self.add_filelist_checkbox.stateChanged.connect(
            lambda: self.add_filelist_area.setVisible(self.add_filelist_checkbox.isChecked())
        )
        
        self.add_filelist_entry = PathInputBlock(placeholder_text="fileslist.txt...", mode="select")
        self.add_filelist_entry.path_changed.connect(
            lambda: self.add_filelist_btn.setEnabled(bool(self.add_filelist_entry.text))
        )

        self.add_filelist_btn = build_button(
            text="Add",
            width=120,
            height=30,
            callback=self.add_filelist
        )
        self.add_filelist_btn.setEnabled(False)

        add_filelist_layout = QHBoxLayout()
        add_filelist_layout.addWidget(self.add_filelist_entry)
        add_filelist_layout.addWidget(self.add_filelist_btn)
        self.add_filelist_area = QWidget()
        self.add_filelist_area.setLayout(add_filelist_layout)
        self.add_filelist_area.hide()


    def _init_output_tab(self):
        """
        Build 'output handling tab'.
        Tag handling, other notations, game count control, etc.
        """
        panels = PanelLayout()
        self.build_output_widgets()

        # Variations section
        variations_section = CollapsibleSection("Variations")
        variations_section.add_widget(self.variations_handling_combobox)

        # Other files
        files_section = CollapsibleSection("Other files and Output options")
        files_section.add_widget(self.non_match_checkbox)
        files_section.add_widget(self.non_match_selector)
        files_section.add_widget(self.no_unique_checkbox)
        files_section.add_widget(self.split_by_chunk_widget)

        # Duplicates section
        duplicates_section = CollapsibleSection("Duplicates")
        duplicates_section.add_widget(self.duplicates_handling_combobox)
        duplicates_section.add_widget(self.duplicates_selector)
        duplicates_section.add_widget(self.malloc_fix_checkbox)
        duplicates_section.add_widget(self.checkfile_checkbox)
        duplicates_section.add_widget(self.checkfile_selector)

        # Tags section
        tags_section = CollapsibleSection("Tag output")
        tags_section.add_widget(self.tag_order_checkbox)
        tags_section.add_widget(self.tag_order_selector)
        tags_section.add_widget(self.xroster_checkbox)
        tags_section.add_widget(self.ply_count_checkbox)
        tags_section.add_widget(self.total_ply_count_checkbox)
        tags_section.add_widget(self.seven_tag_roster_checkbox)

        # Comments and info section
        comments_section = CollapsibleSection("Formatting and Comments")
        comments_section.add_widget(self.comments_combobox)
        comments_section.add_widget(self.comment_lines_checkbox)
        comments_section.add_widget(self.no_move_numbers_checkbox)
        comments_section.add_widget(self.no_results_checkbox)
        comments_section.add_widget(self.evaluation_checbox)
        comments_section.add_widget(self.delete_same_setup_checkbox)
        comments_section.add_widget(self.drop_before_entry)
        comments_section.add_widget(self.mark_matches_entry)

        # Limitation section
        limit_section = CollapsibleSection("Limitations")
        limit_section.add_widget(self.stopafter_entry)
        limit_section.add_widget(self.select_only_entry)
        limit_section.add_widget(self.skip_matching_entry)
        limit_section.add_widget(self.ply_limit_entry)
        limit_section.add_widget(self.quiescent_entry)
        limit_section.add_widget(self.first_game_entry)
        limit_section.add_widget(self.drop_ply_entry)
        limit_section.add_widget(self.line_width_entry)

        # Notation section
        notation_section = CollapsibleSection("Notation")
        notation_section.add_widget(self.output_format_widget) 
        notation_section.add_widget(self.fen_comments_checkbox)   
        notation_section.add_widget(self.fen_descriptions)
        notation_section.add_widget(self.hash_comments_checkbox)
        notation_section.add_widget(self.no_nags_checkbox)
        notation_section.add_widget(self.classify_eco_entry)

        panels.add_left(notation_section)
        panels.add_left(duplicates_section)
        panels.add_left(variations_section)
        panels.add_left(comments_section)
        panels.add_right(tags_section)
        panels.add_right(files_section)
        panels.add_right(limit_section)

        main_layout = QVBoxLayout()
        main_layout.addWidget(panels)
        self.output_tab.setLayout(main_layout)


    def build_output_widgets(self):
        """
        Make all the widgets for output tab
        """
        self.non_match_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NonMatch, 
            label_text="Save non-matches to file",
            state_changed_callback=self.update_non_match
        )

        self.non_match_selector = PathInputBlock(placeholder_text="rejects.pgn...", obj_name="nonmatch-pathinput")
        self.non_match_selector.path_changed.connect(self.update_non_match)
        self.non_match_selector.hide()

        self.stopafter_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.StopAfter, 
            label_text="Stop after matching N games",
            min_value=1,
        )

        self.fen_comments_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.FENComments,
            label_text="Enable FEN comments for every move",
            tooltip_text="enable FEN comment after each move"
        )

        self.fen_descriptions = self.build_enum_entryfield(
            flag_enum=BooleanFlags.FENDescriptions,
            label_text="Add FEN comment after comment",
            tooltip_text="Add FEN comments after a matching comment",
            placeholder_text="(Must be exact match)"
        )

        self.hash_comments_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.HashComments,
            label_text="Enable Zobrist Hash comments",
            tooltip_text="enable polyglot hashcode comment after each move"
        )

        self.classify_eco_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.ClassifyECO,
            label_text="Subdivide by ECO - *creates new file(s)*",
            tooltip_text="Normally takes a numeric argument of value 1, 2, or 3 to indicate level of subdivision",
            min_value=1
        )

        self.duplicates_handling_combobox = self.build_enum_combobox(
            flag_enum_group=Duplicates,
            label_text="Duplicate handling type",
            tooltip_text="Will duplicates be recognized, and will they be suppressed or saved.",
            item_names=["Disabled", "Suppress", "Save to file"],
            state_change_callback=self.update_duplicates
        )

        self.duplicates_selector = PathInputBlock(placeholder_text="dupes.pgn...", obj_name="duplicates-pathinput")
        self.duplicates_selector.path_changed.connect(self.update_duplicates)
        self.duplicates_selector.hide()

        self.malloc_fix_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.MallocOrDieFix,
            label_text="Use external temp file for duplicates",
            tooltip_text="Use virtual.tmp as an external hash table for duplicates.\n(Use when MallocOrDie)"
        )

        self.no_unique_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoUnique,
            label_text="Suppress first occurance of game",
            tooltip_text="Useful when combines with -d to identify duplicate games"
        )

        self.checkfile_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.CheckFile,
            label_text="Use file for duplicate detection (checkfile)",
            tooltip_text="Uses a file as source for checking duplicates",
            state_changed_callback=self.update_checkfile
        )

        self.checkfile_selector = PathInputBlock(placeholder_text="checkfile.pgn...", mode="select", obj_name="checkfile-pathinput")
        self.checkfile_selector.path_changed.connect(self.update_checkfile)
        self.checkfile_selector.hide()

        self.comments_combobox = self.build_enum_combobox(
            flag_enum_group=Comments,
            label_text="Comment output type",
            item_names=["No changes", "Only output games with comments", "Output all games without comments"]
        )

        self.no_move_numbers_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoMoveNumbers,
            label_text="Exclude move numbers"
        )

        self.no_results_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoResults,
            label_text="Exclude results and variations at end of game"
        )

        self.ply_limit_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.PlyLimit,
            label_text="Limit output plies",
            tooltip_text="Limit the number of plies (moves) per game in output",
            state_changed_callback=self.update_quiescent
        )

        self.quiescent_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.Quiescent,
            label_text="Quiescence Depth",
            tooltip_text="Defer termination of the output until the position has been quiescent for the given number of ply."
        )
        self.quiescent_entry.setEnabled(False)

        self.drop_ply_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.DropPly,
            label_text="Drop first plies from games",
            tooltip_text="(If less than 0, all but that number of plies are dropped at the end of the game)",
            min_value=-9999
        )

        self.first_game_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.FirstGame,
            label_text="Start matching from game number N",
            tooltip_text="start matching from specified game number, games before are skipped",
            min_value=1
        )

        self.delete_same_setup_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.DeleteSameSetup,
            label_text="Exclude games with seen starting positions",
            tooltip_text="Isolate the unique starting positions regardless of the games' moves"
        )

        self.seven_tag_roster_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.Seven,
            label_text="Only output tags in seven-tag roster",
            tooltip_text="tags: Event, Site, Date, Round, White, Black, and Result."
        )

        self.line_width_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.LineWidth,
            label_text="Limit line-width",
            tooltip_text="set width as an approximate line width for output",
            step=5
        )

        # Output format widgets (-W)
        self.output_format_widget = FormatWidget()
        self.output_format_widget.state_changed.connect(self.update_output_format)

        self.drop_before_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.DropBefore,
            label_text="Drop plies before matching comment",
            tooltip_text="output a game without the first few ply that occur before a matching comment string",
            placeholder_text="(Must be exact match)"
        )

        self.mark_matches_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.MarkMatches,
            label_text="Mark matches with a comment",
            tooltip_text="The text you enter will appear as a comment for any positional matches",
            placeholder_text="e.g., MATCH"
        )

        self.comment_lines_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.CommentLines,
            label_text="Comments on seperate lines",
            tooltip_text="Comments will appear on thier own line from game text"
        )

        self.evaluation_checbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.Evaluation,
            label_text="Add position evaluations",
            tooltip_text="Add a comment with an evaluation after each move"
        )

        self.no_nags_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoNags,
            label_text="Remove NAGs",
            tooltip_text="Disables NAGs (Numeric Annotation Glyphs) in the output."
        )

        self.ply_count_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.PlyCount,
            label_text="Include Ply Count tags",
            tooltip_text="Add the tag 'PlyCount' to the tags for extracted games"
        )

        self.total_ply_count_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.TotalPlyCount,
            label_text="Include Total Ply Count tags",
            tooltip_text="Add the tag TotalPlyCount to the tags. \n" \
            "This contains a count of the total number of ply present in the game being output \n" \
            "Unless variations have been suppressed this will include all moves in variations as well as the main line."
        )

        self.split_by_chunk_widget = ChunkWidget()
        self.split_by_chunk_widget.state_changed.connect(self.update_split_by_chunk)

        self.tag_order_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.TagOrder,
            label_text="Use tag-order file",
            state_changed_callback=self.update_tag_order
        )

        self.tag_order_selector = PathInputBlock(placeholder_text="roster.txt...", obj_name="roster-pathinput")
        self.tag_order_selector.path_changed.connect(self.update_tag_order)
        self.tag_order_selector.hide()

        self.xroster_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.Xroster,
            label_text="Exclude tags not included in tag order file"
        )

        self.select_only_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.SelectOnly,
            label_text="Select specific matches",
            tooltip_text="1:10,15 requests only the 1st up to 10th, and 15th matched games are output",
            placeholder_text="e.g., 1:10,15"
        )

        self.skip_matching_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.SkipMatching,
            label_text="Skip specific matches",
            tooltip_text="1:10,15 skips the 1st up to 10th, and 15th matched games in output",
            placeholder_text="e.g., 1:10,15"
        )

        self.variations_handling_combobox = self.build_enum_combobox(
            flag_enum_group=VariantHandling,
            label_text="Handle Variations",
            item_names=["...", "Split into separate games", "Suppress"]
        )

        select_validator = QRegularExpressionValidator(QRegularExpression(r"[0-9,:]*"))
        self.select_only_entry.entry_field.setValidator(select_validator)
        self.skip_matching_entry.entry_field.setValidator(select_validator)


    def _init_filters_tab(self):
        """
        Build 'filters' tab.
        Game matching critera.
        """
        self.build_filters_widgets()
        panels = PanelLayout()  

        # Subcontainer for tags file stuff
        tag_match_layout = QVBoxLayout()
        tag_match_layout.setContentsMargins(0, 3, 0, 3)
        tag_file_layout = QHBoxLayout()
        tag_file_layout.addWidget(self.tags_file_label)
        tag_file_layout.addWidget(self.tags_file_browse_btn)
        tag_file_layout.addWidget(self.tags_file_input)
        tag_file_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        tag_match_layout.addLayout(tag_file_layout)
        tag_match_layout.addWidget(self.build_tags_file_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.tag_match_widget = QWidget()
        self.tag_match_widget.setLayout(tag_match_layout)
        self.tag_match_widget.setVisible(False)

        # Material match section
        material_match_section = CollapsibleSection("Material matching")
        material_match_section.add_widget(self.material_match_widget)
        material_match_section.add_widget(self.add_match_tag_checkbox)

        # Variations section
        variations_section = CollapsibleSection("Variations")
        variations_section.add_widget(self.hash_match_entry)
        variations_section.add_widget(self.variation_complete_checkbox)
        variations_section.add_widget(self.variation_complete_selector)
        variations_section.add_widget(self.variation_incomplete_checkbox)
        variations_section.add_widget(self.variation_incomplete_selector)
        variations_section.add_widget(self.textual_permutations_checkbox)
        variations_section.add_widget(self.match_anywhere_checkbox)

        # Game info Section
        info_section = CollapsibleSection("Game/Player Information")
        info_section.add_widget(self.game_end_condition_combobox)
        info_section.add_widget(self.winner_rating_combobox)
        info_section.add_widget(self.bounds_widget)
        
        # Positions and moves Section
        moves_section = CollapsibleSection("Positional")
        moves_section.add_widget(self.to_move_combobox)
        moves_section.add_widget(self.repetition_combobox)
        moves_section.add_widget(self.no_capture_combobox)
        moves_section.add_widget(self.fuzzy_depth_entry)
        moves_section.add_widget(self.start_ply_entry)
        moves_section.add_widget(self.ply_depth_limit)
        moves_section.add_widget(self.contains_underpromotion_checkbox)

        # Filter by tags section
        tags_section = CollapsibleSection("Tag matching")
        tags_section.add_widget(self.tag_matching_checkbox)
        tags_section.add_widget(self.tag_match_widget)
        tags_section.add_widget(self.match_by_annotator_entry)
        tags_section.add_widget(self.match_by_player_entry)
        tags_section.add_widget(self.match_by_wPlayer_entry)
        tags_section.add_widget(self.match_by_bPlayer_entry)
        tags_section.add_widget(self.match_by_date_entry)
        tags_section.add_widget(self.match_by_eco_entry)
        tags_section.add_widget(self.match_by_fen_entry)
        tags_section.add_widget(self.match_by_hash_entry)
        tags_section.add_widget(self.match_by_result_entry)
        tags_section.add_widget(self.match_substring_checkbox)
        tags_section.add_widget(self.suppress_matched_checkbox)
        tags_section.add_widget(self.soundex_match_checkbox)
        tags_section.add_widget(self.setup_tags_combobox)

        # Add sections to panels
        panels.add_left(info_section)
        panels.add_left(moves_section)
        panels.add_left(variations_section)
        panels.add_right(tags_section)
        panels.add_right(material_match_section)

        main_layout = QVBoxLayout()
        main_layout.addWidget(panels)
        self.filters_tab.setLayout(main_layout)


    def build_filters_widgets(self):
        """
        Make all the widgets for filters tab
        """
        self.game_end_condition_combobox = self.build_enum_combobox(
            flag_enum_group=GameEndConditions, 
            label_text="Game end type"
        )

        self.winner_rating_combobox = self.build_enum_combobox(
            flag_enum_group=WinnerRating, 
            label_text="Winner rating difference"
        )

        self.contains_underpromotion_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.Underpromotion, 
            label_text="Contains Underpromotion"
        )
        
        self.repetition_combobox = self.build_enum_combobox(
            flag_enum_group=Repetition, 
            label_text="n-fold Repetition",
            item_names=["Disabled", "3", "5"]
        )

        self.no_capture_combobox = self.build_enum_combobox(
            flag_enum_group=NoCapture, 
            label_text="No-Capture count",
            item_names=["Disabled", "50", "75"]
        )

        # Tags
        self.tag_match_window = TagWindow()
        self.tag_match_window.tag_file_created.connect(lambda path: self.tags_file_input.setText(path))

        self.tag_matching_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.TagMatch, 
            label_text="Enable tag-matching by file",
            state_changed_callback=self.update_tag_match
        )

        self.tags_file_label = QLabel("Specify tags file: ")
        self.tags_file_input = QLineEdit()
        self.tags_file_input.setPlaceholderText("mytags.txt...")
        self.tags_file_input.setFixedSize(220, 25)
        self.tags_file_input.textChanged.connect(self.update_tag_match)

        self.tags_file_browse_btn = build_button(
            text="Browse",
            width=100,
            height=30,
            callback=self.browse_tags_file
        )

        self.build_tags_file_btn = build_button(
            text="Create a new tag match file",
            width=160,
            height=30,
            callback=self.tag_match_window.show
        )

        # tag flags
        self.match_substring_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.MatchSubStr,
            label_text="Match in any part of tag"
        )

        self.suppress_matched_checkbox = self.build_enum_checkbox(
            BooleanFlags.SuppressMatched,
            label_text="Don't output matched games"
        )

        self.soundex_match_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.SoundexMatching,
            label_text="Enable soundex matching",
            tooltip_text="perform soundex matches on White, Black, Site, Event, and Annotator tags"
        )
        
        self.match_by_annotator_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.Annotator,
            label_text="Extract games annotated by Annotator",
            tooltip_text="Find games based on who made the notes for the game",
            placeholder_text="e.g., chessAnnotator123"
        )

        self.match_by_bPlayer_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.bPlayer,
            label_text="Extract games where Player has the Black pieces",
            tooltip_text="Searches for games based on who is playing with black pieces",
            placeholder_text='e.g., chessPlayer333'
        )

        self.match_by_date_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.Date,
            label_text="Extract games by Date",
            tooltip_text="Find games based on their Date tag",
            placeholder_text="e.g., 2022.01.01"
        )

        validator = QRegularExpressionValidator(QRegularExpression(r"\d{4}\.(0[1-9]|1[0-2])(\.(0[1-9]|[12][0-9]|3[01]))"))
        self.match_by_date_entry.entry_field.setValidator(validator)

        self.match_by_eco_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.Eco,
            label_text="Extract games by ECO",
            tooltip_text="Find games based on their ECO tag",
            placeholder_text="e.g., A01",
        )
        validator = QRegularExpressionValidator(QRegularExpression(r"[A-E][0-9]{2}"))
        self.match_by_eco_entry.entry_field.setValidator(validator)

        self.match_by_fen_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.FenPattern,
            label_text="Extract games by FEN",
            tooltip_text="Find games based on FEN pattern",
            placeholder_text='e.g., */*/*/*/???PP???/*/*/*',
            quote_input=True,
        )

        self.match_by_hash_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.HashCode,
            label_text="Extract games by HashCode",
            tooltip_text="Extract games with HashCode designation HashCode",
            placeholder_text='e.g., 19b4aea499e0ba7c'
        )

        self.match_by_player_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.Player,
            label_text="Extract games where Player has either colour",
            tooltip_text="Find games based on Player of either side",
            placeholder_text='e.g., chessPlayer123'
        )

        self.match_by_result_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.Result,
            label_text="Extract games by Result",
            tooltip_text="Find games based on Result of the game",
            placeholder_text='e.g., 1-0'
        )
        validator = QRegularExpressionValidator(QRegularExpression(r"^(1-0|0-1|1/2)$"))
        self.match_by_result_entry.entry_field.setValidator(validator)
        
        self.match_by_wPlayer_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.wPlayer,
            label_text="Extract games where Player has the White pieces",
            tooltip_text="Find games based on Player with black pieces",
            placeholder_text='e.g., chessPlayer123'
        )

        self.fuzzy_depth_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.FuzzyDepth,
            label_text="Fuzzy-depth positional duplicates match",
            tooltip_text="Match on the basis of board position at the indicated number of plies or the end of the game."
        )

        self.setup_tags_combobox = self.build_enum_combobox(
            flag_enum_group=SetUpTags,
            label_text="Filter by setup tags",
            tooltip_text="Games with non-standard starting positions are indicated with a pair of tags",
            item_names=["Disabled", "Only setup tags", "No setup tags"]
        )

        self.to_move_combobox = self.build_enum_combobox(
            flag_enum_group=ToMove,
            label_text="Player to move"
        )

        self.start_ply_entry = self.build_enum_spinbox(
            flag_enum=BooleanFlags.StartPly,
            label_text="Start matching after Nth ply",
            tooltip_text="Defers match attempts until the move at the given ply is played each game."
        )

        self.ply_depth_limit = self.build_enum_spinbox(
            flag_enum=BooleanFlags.LimitPlyDepth,
            label_text="Limit ply depth",
            tooltip_text="Limits the number of ply to which matches are sought",
            min_value=1
        )

        self.material_match_widget = MaterialMatchWidget()
        self.material_match_widget.state_changed.connect(self.update_material_matches)

        self.add_match_tag_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.AddMatchTag,
            label_text="Add match tags",
            tooltip_text="add a MaterialMatch tag pair to a game"
        )
        self.add_match_tag_checkbox.setEnabled(False)

        self.hash_match_entry = self.build_enum_entryfield(
            flag_enum=BooleanFlags.HashMatch,
            label_text="Match by polyglot hashcode",
            tooltip_text="Positional matches are available by using a polyglot hashcode to specify the desired position",
            placeholder_text="e.g., 19b4aea499e0ba7c"
        )

        # Variations stuff
        self.variation_complete_checkbox = self.build_enum_checkbox(
            label_text="Identify variations (by complete sequence)",
            flag_enum=BooleanFlags.VariationsComplete,
            state_changed_callback=self.update_complete_variations
        )

        self.variation_complete_selector = PathInputBlock(placeholder_text="vars.txt...", obj_name="completevars-pathinput")
        self.variation_complete_selector.path_changed.connect(self.update_complete_variations)
        self.variation_complete_selector.hide()

        self.variation_incomplete_checkbox = self.build_enum_checkbox(
            label_text="Identify variations (by incomplete sequence)",
            flag_enum=BooleanFlags.VariationsIncomplete,
            state_changed_callback=self.update_incomplete_variations
        )

        self.variation_incomplete_selector = PathInputBlock(placeholder_text="vars.txt...", obj_name="incompletevars-pathinput")
        self.variation_incomplete_selector.path_changed.connect(self.update_incomplete_variations)
        self.variation_incomplete_selector.hide()

        self.textual_permutations_checkbox = self.build_enum_checkbox(
            label_text="Try all move order permutations",
            flag_enum=BooleanFlags.TextualPermutations,
            state_changed_callback=self.update_incomplete_variations
        )
        self.textual_permutations_checkbox.setEnabled(False)

        self.match_anywhere_checkbox = self.build_enum_checkbox(
            label_text="Apply variation matching through the whole game",
            flag_enum=BooleanFlags.MatchAnywhere,
            state_changed_callback=self.update_incomplete_variations
        )

        self.bounds_widget = BoundsWidget()
        self.bounds_widget.state_changed.connect(self.update_bounds)


    def _init_settings_tab(self):
        """
        Build 'settings' tab.
        Options relating to the UI, configs, logs, etc.
        """
        self.build_settings_widgets()
        panels = PanelLayout()

        app_section = CollapsibleSection("Application settings")
        app_section.add_widget(self.command_preview_checkbox)
        app_section.add_widget(self.darkmode_checkbox)
        app_section.add_widget(self.reset_settings_btn)
        app_section.add_widget(self.install_pgn_extract_btn)

        configs_section = CollapsibleSection("Config")
        configs_section.add_widget(self.save_config_btn)
        configs_section.add_widget(self.load_config_btn)

        fixes_section = CollapsibleSection("Fixes")
        fixes_section.add_widget(self.lichess_fix_checkbox)
        fixes_section.add_widget(self.fix_result_tags_checkbox)
        fixes_section.add_widget(self.fix_tag_strings_checkbox)
        fixes_section.add_widget(self.nested_comments_checkbox)
        fixes_section.add_widget(self.fen_castling_checkbox)
        fixes_section.add_widget(self.no_faux_ep_checkbox)

        logs_section = CollapsibleSection("Logs")
        logs_section.add_widget(self.save_logs_combobox)
        logs_section.add_widget(self.save_logs_selector)

        game_section = CollapsibleSection("Game settings")
        game_section.add_widget(self.keep_broken_checkbox)
        game_section.add_widget(self.allownull_checkbox)
        game_section.add_widget(self.no_bad_results_checkbox)
        game_section.add_widget(self.odds_checkbox)

        panels.add_left(app_section)
        panels.add_left(configs_section)
        panels.add_left(logs_section)
        panels.add_right(game_section)
        panels.add_right(fixes_section)

        main_layout = QVBoxLayout()
        main_layout.addWidget(panels)        
        self.settings_tab.setLayout(main_layout)


    def build_settings_widgets(self):
        """
        Make all the widgets for settings tab
        """
        self.command_preview_checkbox = QCheckBox("Preview commands")
        self.command_preview_checkbox.stateChanged.connect(self.update_command_viewer)
        self.command_preview_checkbox.setToolTip("Show command line args as text (shown in File tab)")

        # Initialize app theme
        self.darkmode_checkbox = QCheckBox("Enable Dark UI")
        self.darkmode_checkbox.stateChanged.connect(
            lambda: self.toggle_darkmode(self.darkmode_checkbox.isChecked())
        )

        self.install_pgn_extract_btn = build_button(
            text="Install pgn-extract",
            width=200,
            height=30,
            callback=self.install_pgn_extract,
            tooltip="Download and install the latest version of pgn-extract if not already installed."
        )

        self.reset_settings_btn = build_button(
            text="Reset App Settings",
            width=200,
            height=30,
            callback=self.reset_settings,
            tooltip="Doesn't affect pgn-extract related options"
        )

        self.keep_broken_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.KeepBroken,
            label_text="Keep broken games", 
            tooltip_text="Keeps games that have errors in the output, useful for debugging."
        )

        self.allownull_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.AllowNull,
            label_text="Allow NULL moves",
            tooltip_text="Allows null moves in the output."
        )

        self.lichess_fix_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.LichessFix,
            label_text="Lichess comment fix"
        )

        self.fix_result_tags_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.FixResultTags,
            label_text="Attempt to fix broken results",
            tooltip_text="Try correct games with conflicts in result and result tag"
        )

        self.no_bad_results_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoBadResults,
            label_text="Suppress broken results",
            tooltip_text="Suppresses games with conflicting result and result tag"
        )

        self.save_logs_combobox = self.build_enum_combobox(
            flag_enum_group=LogFile,
            label_text="Save Logs to file",
            item_names=["Don't save", "Overwrite", "Append"],
            state_change_callback=self.update_log_file
        )

        self.fix_tag_strings_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.FixTagStrings,
            label_text="Fix tag strings",
            tooltip_text="Tag strings sometimes contain extra, unescaped quote characters within them"
        )

        self.fen_castling_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.FENCastling,
            label_text="Add missing castling rights to FEN tags",
            tooltip_text="Warning: Not implemented for Chess 960 positions"
        )

        self.nested_comments_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NestedComments,
            label_text="Allow nested comments",
            tooltip_text="Nested comments are not usually allowed. " \
            "Avoid mismatched closing comment symbols for games with nested comments."
        )

        self.no_faux_ep_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.NoFauxEP,
            label_text="Exclude en-passant squares in FEN if no capture possible",
            tooltip_text="This makes it easier to compare identical FEN positions resulting from transpositions"
        )

        self.save_logs_selector = PathInputBlock(placeholder_text="logs.txt...", obj_name="logs-pathinput")
        self.save_logs_selector.path_changed.connect(self.update_log_file)
        self.save_logs_selector.setVisible(False)

        self.odds_checkbox = self.build_enum_checkbox(
            flag_enum=BooleanFlags.Odds,
            label_text="At Odds only",
            tooltip_text="Only match games starting with a material imbalance (handicap chess)"
        )

        self.save_config_btn = build_button(
            text="Create config",
            width=200,
            height=30,
            callback=self.save_config,
            tooltip="Save current UI state as config file"
        )

        self.load_config_btn = build_button(
            text="Load config from file",
            width=200,
            height=30,
            callback=self.load_config,
            tooltip="Load existing config file"
        )


    def add_filelist(self):
        """
        (Same as -f) but instead of the flag, upload all files as inputs
        """
        filelist = self.add_filelist_entry.text

        # Check for filename and filename.txt (in case they forgot)
        if not os.path.exists(filelist):
            if os.path.exists(CommandBuilder.auto_complete_filename(filelist, ext=".txt")):
                filelist += ".txt"
            else:
                self.display_error_message(message=f"Unable to find {filelist}")
                return
        
        dirname = os.path.dirname(filelist)

        # Loop through lines as pgn files, validate and add to inputs
        with open(filelist, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                pgn_path = os.path.join(dirname, line)
                if self.validate_pgn(pgn_path):
                    self.add_pgn(pgn_path)

        self.add_filelist_entry.text = ""


    def save_config(self):
        """
        Save current UI state and/or values into a file
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            self.config_manager.config_dir,  # start in configs folder
            "Config Files (*.json)"
        )

        if not filename: return

        if not filename.endswith(".json"):
            filename += ".json"

        config_name = os.path.splitext(os.path.basename(filename))[0]
        self.config_manager.save_config(config_name)


    def load_config(self):
        """
        Load config file into application
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            self.config_manager.config_dir,
            "Config Files (*.json)"
        )

        if not filename: return

        config_name = os.path.splitext(os.path.basename(filename))[0]
        self.config_manager.load_config(config_name)
        self.update_command_preview()


    def update_output(self):
        """
        Multiple checks/updates for the output file path changing
        """
        self.command_builder.set_output_path(self.output_selector.text)
        self.update_split_by_chunk()
        self.update_command_preview()


    def add_pgn(self, filename=False):
        """
        Add a pgn filename to the inputs list
        """
        # Catch no file input
        if filename is False:
            filename = self.pgn_input_field.text()
            # add .pgn if not already there
            if not filename.endswith(".pgn"):
                filename += ".pgn"

        # turn filename into full path 
        filename = os.path.abspath(filename)

        # check if pgn is valid
        if not self.validate_pgn(filename):
            return

        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)

        # show filename
        label = QLabel(os.path.basename(filename))

        # remove element from list
        remove_btn = build_button(
            img_name="x_icon.png",
            width=constants.remove_btn_size,
            height=constants.remove_btn_size,
            callback=lambda: self.remove_pgn(frame, filename)
        )

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(remove_btn)

        self.pgn_list_layout.addWidget(frame)
        self.command_builder.add_input_file(filename)
        self.pgn_input_field.clear()
        self.update_command_preview()


    def remove_pgn(self, frame, filename):
        """
        Remove a pgn from the inputs list
        """
        self.command_builder.remove_input_file(filename)
        frame.setParent(None)
        self.update_command_preview()


    def browse_pgn(self):
        """
        Open file explorer to find a pgn filename to add to inputs list.
        Calls 'self.add_pgn(filename)' on selection
        """
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "select .pgn file(s)",
            "",
            "PGN Files (*.pgn);;All files (*)"
        )

        for filename in filenames:
            filename = os.path.abspath(filename)
            if self.validate_pgn(filename):
                self.add_pgn(filename)
    

    def clear_pgn_inputs(self):
        """
        Clear all pgn inputs from the list after ftag input
        """
        for item in self.pgn_list_container.findChildren(QFrame):
            if type(item) == QFrame:
                item.setParent(None)

        self.command_builder.clear_inputs()
        self.update_command_preview()


    def validate_pgn(self, filename):
        """
        Check 'filename' is valid
        """
        # check empty filename
        if filename is None:
            self.display_error_message(message="Filename field is empty.")
            return False
        # check dupe
        if filename in self.command_builder.input_files:
            self.display_error_message(message=f"{filename} is already selected.")
            return False
        # check if pgn
        if not filename.endswith(".pgn"):
            self.display_error_message(message="Selcted file is not pgn.")
            return False
        # check it exists
        if not os.path.exists(filename):
            self.display_error_message(message=f"{filename} could not be found.")
            return False

        return True


    def display_error_message(self, title="Error", message="Something went wrong."):
        """
        Error messagebox pop-up
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()


    def update_filewrite_mode(self):
        """
        Update the filewrite mode pgn-extract uses.
        Flags: [-o, -a] <- [checked, unchecked]
        """
        self.command_builder.set_filewrite_mode(
            FileWriteMode.Overwrite if self.filewrite_checkbox.isChecked() else FileWriteMode.Append
        )
        self.filewrite_checkbox.setText(f"{self.command_builder.filewrite_mode.name} file")
        self.update_command_preview()


    def run_extract(self):
        """
        Trigger command execution through worker.py with current UI state as command line args
        """
        self.output_display.clear()

        #Validations
        if self.command_builder.is_input_list_empty():
            self.display_error_message(message="No input found. Please upload one or more pgn files.")
            self.extract_btn.setEnabled(True)
            return
        
        output_path = self.output_selector.text.replace("Current: ", "").strip()
        output_dir = os.path.dirname(output_path)

        if output_dir and not os.path.exists(output_dir):
            self.display_error_message(message=f"Output directory does not exist: {output_dir}")
            self.extract_btn.setEnabled(True)
            self.extract_btn.setText("Extract")
            return
        
        input_files = [os.path.abspath(f) for f in self.command_builder.input_files]
        output_file = os.path.abspath(self.command_builder.output_file)

        if output_file in input_files:
            self.display_error_message(message="Output file cannot be in input files.")
            self.reset_extract_widgets()
            return
        
        # Temporarily disable extract button until finished executing
        self.extract_btn.setEnabled(False)
        self.extract_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.extract_btn.setText("Please wait...")
        QApplication.processEvents()
        
        # Command executing
        self.command_builder.set_output_path(self.output_selector.text)
        cmdline = self.command_builder.build()
        worker = ExtractWorker(cmdline, output_path=self.command_builder.output_file)
        self.current_worker = worker

        # Progress bar
        line_count = self.command_builder.count_lines()
        self.progress_bar.setRange(0, line_count)
        self.progress_bar.setEnabled(True)

        # Output viewer update interval setup
        self._output_buffer = []
        self._output_timer = QTimer()
        self._output_timer.setInterval(150) # ms
        self._output_timer.timeout.connect(self.flush_output_buffer)
        self._output_timer.start()

        # Signals
        worker.signals.output.connect(lambda line: self.append_output_line(line))
        worker.signals.finished.connect(self.on_extract_finish)
        worker.signals.game_processed.connect(self.progress_bar_tick)
        self.thread_pool.start(worker)


    def progress_bar_tick(self):
        """
        Update the progress bar value by 1.
        """
        self.progress_bar.setValue(self.progress_bar.value() + 1)


    def append_output_line(self, line):
        """Append a line of output to the display.

        Args:
            line (str): The line of output to append.
        """
        self._output_buffer.append(line)


    def flush_output_buffer(self):
        """Flush the output buffer to the display.
        """
        if not self._output_buffer:
            return
        # Append all buffered lines joined by newline at once
        self.output_display.appendPlainText("\n".join(self._output_buffer))
        self._output_buffer.clear()

    
    def on_extract_finish(self):
        """Handle the completion of the extraction process.
        """
        self.reset_extract_widgets()
        self.append_output_line("Finished process...")
        self.flush_output_buffer()
        self.progress_bar.setEnabled(False)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)


    def reset_extract_widgets(self):
        """Reset extract and output field widgets.
        """
        self.extract_btn.setText("Extract")
        self.extract_btn.setEnabled(True)
        self.progress_bar.setEnabled(False)
        self.extract_btn.setVisible(True)
        self.cancel_btn.setVisible(False)


    def cancel_extract(self):
        if self.current_worker:
            self.current_worker.terminate()
            self.append_output_line("Extraction canceled.")
            self.reset_extract_widgets()


    def update_tag_order(self):
        """Update the -R flag and file selector.
        """
        flag_enabled = self.tag_order_checkbox.isChecked()
        self.tag_order_selector.setVisible(flag_enabled)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.TagOrder,
            enabled=flag_enabled and self.tag_order_selector.text,
            args=self.tag_order_selector.text
        )
        self.update_command_preview()


    def update_split_by_chunk(self):
        """Update the -# arg(s) using both spinboxes.
        Conflicts with -o and -a.
        """
        flag_enabled = self.split_by_chunk_widget.is_enabled
        has_output_path = bool(self.command_builder.output_file)

        first_value, second_value= self.split_by_chunk_widget.get_values()

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.SplitByChunk,
            enabled=flag_enabled and not has_output_path,
            args=f"{first_value},{second_value}"
        )
        self.update_command_preview()


    def update_duplicates(self):
        """Update duplicates file arg for --duplicates.
        """
        if self.duplicates_handling_combobox.current_index == 2:
            self.duplicates_selector.setVisible(True)
            new_flag = Duplicates.SaveDuplicates if bool(self.duplicates_selector.text) else Duplicates.Disabled
        else:
            self.duplicates_selector.setVisible(False)
            new_flag = self.duplicates_handling_combobox.current_data

        self.command_builder.update_flag_group(
            flag_enum_group=Duplicates,
            new_flag=new_flag,
            args=self.duplicates_selector.text,
            enabled=new_flag != Duplicates.Disabled
        )
        self.update_command_preview()


    def update_checkfile(self):
        """Update checkfile arg for --checkfile.
        """
        flag_enabled = self.checkfile_checkbox.isChecked()
        self.checkfile_selector.setVisible(flag_enabled)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.CheckFile,
            enabled=flag_enabled and self.checkfile_selector.text,
            args=self.checkfile_selector.text
        )
        self.update_command_preview()


    def update_output_format(self):
        """Update -W'format name'.
        """
        flag_enabled = self.output_format_widget.current_index() != 0
        arg = self.output_format_widget.current_data()
        san_suffix = self.output_format_widget.get_san_suffix() if arg == "san" else ""

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.OutputFormat,
            enabled=flag_enabled,
            args=arg + san_suffix
        )
        self.update_command_preview()


    def update_quiescent(self):
        """Update quiescent flag (relies on ply limit flag).
        """
        flag_enabled = self.ply_limit_entry.is_checked()
        self.quiescent_entry.setEnabled(flag_enabled)
        if not flag_enabled:
            self.quiescent_entry.checkbox.setChecked(False)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.PlyLimit,
            enabled=flag_enabled,
            args=self.ply_limit_entry.value()
        )
        self.update_command_preview()


    def update_complete_variations(self):
        """Update -x flag and file arg.
        """
        flag_enabled = self.variation_complete_checkbox.isChecked()

        self.variation_complete_selector.setVisible(flag_enabled)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.VariationsComplete,
            enabled=flag_enabled and self.variation_complete_selector.text,
            args=self.variation_complete_selector.text
        )
        self.update_command_preview()
        

    def update_incomplete_variations(self):
        """Update -v, -P, and --vanywhere.
        """
        flag_enabled = self.variation_incomplete_checkbox.isChecked()

        self.variation_incomplete_selector.setVisible(flag_enabled)

        self.textual_permutations_checkbox.setEnabled(flag_enabled and bool(self.variation_incomplete_selector.text))
        self.match_anywhere_checkbox.setEnabled(flag_enabled and bool(self.variation_incomplete_selector.text))

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.VariationsIncomplete,
            enabled=flag_enabled and self.variation_incomplete_selector.text,
            args = self.variation_incomplete_selector.text
        )

        enable_textual = self.textual_permutations_checkbox.isChecked() and self.textual_permutations_checkbox.isEnabled()
        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.TextualPermutations,
            enabled=flag_enabled and enable_textual and self.variation_incomplete_selector.text
        )

        enable_match_anywhere = self.match_anywhere_checkbox.isChecked() and self.match_anywhere_checkbox.isEnabled()
        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.MatchAnywhere,
            enabled=flag_enabled and enable_match_anywhere
        )
        self.update_command_preview()
        


    def update_material_matches(self):
        """Update -y, -z, --materialy/z based on material_match_widget.
        """
        using_file = self.material_match_widget.using_file
        mode = self.material_match_widget.mode

        if mode == "y":
            flag =  MaterialMatches.FileMaterialY if using_file else MaterialMatches.InlineMaterialY
        else:
            flag = MaterialMatches.FileMaterialZ if using_file else MaterialMatches.InlineMaterialZ
            self.add_match_tag_checkbox.setEnabled(bool(self.material_match_widget.contents))

        self.command_builder.update_flag_group(
            flag_enum_group=MaterialMatches,
            new_flag=flag,
            enabled=self.material_match_widget.flag_enabled and self.material_match_widget.contents,
            args=self.material_match_widget.contents
        )
        self.update_command_preview()


    def update_tag_match(self):
        """Toggle widgets assisiated with tag-matching.
        Based on the state of the checkbox and entryfield.
        """
        flag_enabled = self.tag_matching_checkbox.isChecked()
        has_text = bool(self.tags_file_input.text())

        self.tag_match_widget.setVisible(flag_enabled)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.TagMatch,
            enabled=flag_enabled and has_text,
            args=self.tags_file_input.text()
        )
        self.update_command_preview()


    def update_non_match(self):
        """Update the -n arg (Non-match)
        Called whenever the assisiated entry field is changed, or checkbox ticked/unticked
        """
        flag_enabled = self.non_match_checkbox.isChecked()
        self.non_match_selector.setVisible(flag_enabled)

        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.NonMatch,
            enabled=flag_enabled and self.non_match_selector.text,
            args=self.non_match_selector.text
        )
        self.update_command_preview()


    def update_bounds(self):
        """Update flags and args for --minply, --maxply, --minmoves, --maxmoves.
        """
        flag_enabled = self.bounds_widget.flag_enabled

        if self.bounds_widget.mode_combobox.currentText() == "Moves":
            new_flag_upper = UpperBounds.Moves
            new_flag_lower = LowerBounds.Moves
        elif self.bounds_widget.mode_combobox.currentText() == "Plies":
            new_flag_upper = UpperBounds.Ply
            new_flag_lower = LowerBounds.Ply
        else:
            new_flag_upper = UpperBounds.Disabled
            new_flag_lower = LowerBounds.Disabled

        self.command_builder.update_flag_group(
            flag_enum_group=UpperBounds,
            new_flag=new_flag_upper,
            enabled=flag_enabled,
            args=self.bounds_widget.max_spinbox.value()
        )

        self.command_builder.update_flag_group(
            flag_enum_group=LowerBounds,
            new_flag=new_flag_lower,
            enabled=flag_enabled,
            args=self.bounds_widget.min_spinbox.value()
        )
        self.update_command_preview()


    def browse_tags_file(self):
        """Use function browse_file() to set -t arg (Tag-matching).
        """
        filename = self.browse_file(allow_pgn=False)
        self.tags_file_input.setText(filename)
        self.command_builder.update_boolean_flag(
            flag_enum=BooleanFlags.TagMatch,
            enabled=True,
            args=filename
        )
        self.update_command_preview()
    

    def browse_file(self, allow_txt=True, allow_pgn=True, start_dir="") -> str:
        """Generic QFileDialog for singular file.

        Args:
            allow_txt (bool, optional): Whether to allow .txt files. Defaults to True.
            allow_pgn (bool, optional): Whether to allow .pgn files. Defaults to True.
            start_dir (str, optional): The starting directory for the file dialog. Defaults to "".

        Returns:
            str: The selected file path, or an empty string if no file was selected.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select tags file",
            start_dir,
            f"""
                {"PGN Files (*.pgn);;" if allow_pgn else ""}
                {"Text Files (*.txt);;" if allow_txt else ""}
                All files (*)
            """
        )
        if filename:
            filename = os.path.abspath(filename)
            if not os.path.isfile(filename):
                self.display_error_message(message=f"Selected path is not a file: {filename}")
                return ""
            if not os.path.exists(filename):
                self.display_error_message(message=f"File not found: {filename}")
                return ""
            
        return filename
        


    def build_enum_combobox(self, flag_enum_group, label_text="", tooltip_text="", item_names=[], state_change_callback=None) -> EnumCombobox:
        """Create a drop-down box for all options in a flag's enum. Includes a label.
        Returns a Horizontal layout.

        Args:
            flag_enum_group (_type_): The enum group to which the flag belongs.
            label_text (str, optional): The text to display as the label. Defaults to "".
            tooltip_text (str, optional): The text to display as a tooltip. Defaults to "".
            item_names (list, optional): The names of the items to display in the combobox. Defaults to [].
            state_change_callback (_type_, optional): A callback function to call when the state changes. Defaults to None.

        Returns:
            EnumCombobox: The created combobox widget.
        """
        widget = EnumCombobox(
            flag_enum_group=flag_enum_group,
            label_text=label_text,
            tooltip_text=tooltip_text,
            item_names=item_names
        )

        if not state_change_callback:
            # update flag on change of index if no defined callback
            widget.combobox.currentIndexChanged.connect(
                lambda: self.command_builder.update_flag_group(
                    flag_enum_group=flag_enum_group,
                    new_flag=widget.current_data,
                    enabled=widget.current_data.value != ""
                )
            )
            widget.combobox.currentIndexChanged.connect(self.update_command_preview)
        else:
            widget.combobox.currentIndexChanged.connect(state_change_callback)

        return widget
    

    def build_enum_checkbox(self, flag_enum, label_text="", default_state=False, tooltip_text="", state_changed_callback=None) -> QCheckBox:
        """Create a checkbox for enabling the addition of this flag to dict.

        Args:
            flag_enum (_type_): Which flag this checkbox controls.
            label_text (str, optional): The text to display as the label. Defaults to "".
            default_state (bool, optional): The default state of the checkbox. Defaults to False.
            tooltip_text (str, optional): The text to display as a tooltip. Defaults to "".
            state_changed_callback (_type_, optional): A callback function to call when the state changes. Defaults to None.

        Returns:
            QCheckBox: The created checkbox widget.
        """
        checkbox = EnumCheckbox(
            flag_enum=flag_enum,
            label_text=label_text,
            default_state=default_state,
            tooltip_text=tooltip_text
        )

        if not state_changed_callback:
            checkbox.stateChanged.connect(
                lambda: self.command_builder.update_boolean_flag(
                    flag_enum=flag_enum,
                    enabled=checkbox.isChecked()
                )
            )
            checkbox.stateChanged.connect(self.update_command_preview)
        else:
            checkbox.stateChanged.connect(state_changed_callback)

        return checkbox
    

    def build_enum_entryfield(self, flag_enum, label_text="", placeholder_text="", tooltip_text="", quote_input=False) -> EnumEntryField:
        """Create an entry field for a flag, if anything is there, enable flag with entry as arg, if empty, remove.

        Args:
            flag_enum (_type_): Which flag this entry field controls.
            label_text (str, optional): The text to display as the label. Defaults to "".
            placeholder_text (str, optional): The text to display as a placeholder. Defaults to "".
            tooltip_text (str, optional): The text to display as a tooltip. Defaults to "".

        Returns:
            EnumEntryField: The created entry field widget.
        """
        widget = EnumEntryField(flag_enum, label_text, placeholder_text, tooltip_text)

        # handle_flag_func = lambda: self.command_builder.update_boolean_flag(
        #     flag_enum=flag_enum,
        #     enabled=bool(widget.entry_field.text() and widget.checkbox.isChecked()),
        #     args=widget.entry_field.text()
        # )

        def handle_flag_func():
            raw_text = widget.entry_field.text().strip()
            arg_text = f'"{raw_text}"' if (raw_text and quote_input) else raw_text
            self.command_builder.update_boolean_flag(
                flag_enum=flag_enum,
                enabled=bool(raw_text and widget.checkbox.isChecked()),
                args=arg_text
            )

        widget.checkbox.stateChanged.connect(
            lambda: widget.entry_field.setEnabled(widget.checkbox.isChecked())
        )
        widget.checkbox.stateChanged.connect(handle_flag_func)
        widget.checkbox.stateChanged.connect(self.update_command_preview)

        widget.entry_field.textChanged.connect(handle_flag_func)
        widget.entry_field.textChanged.connect(self.update_command_preview)
        widget.entry_field.setEnabled(False)

        return widget
    

    def build_enum_spinbox(self, flag_enum, label_text="", min_value=0, max_value=9999999, 
                           step=1, width=100, tooltip_text="", state_changed_callback=None) -> EnumSpinbox:
        """Create a spinbox for a flag, enabling the flag when checked and passing the spinbox value as the argument.

        Args:
            flag_enum (_type_): Which flag this spinbox controls.
            label_text (str, optional): The text to display as the label. Defaults to "".
            min_value (int, optional): The minimum value for the spinbox. Defaults to 0.
            max_value (int, optional): The maximum value for the spinbox. Defaults to 9999999.
            step (int, optional): The step size for the spinbox. Defaults to 1.
            width (int, optional): The width of the spinbox. Defaults to 100.
            tooltip_text (str, optional): The text to display as a tooltip. Defaults to "".
            state_changed_callback (_type_, optional): A callback function to call when the state changes. Defaults to None.

        Returns:
            EnumSpinbox: The created spinbox widget.
        """
        widget = EnumSpinbox(
            flag_enum=flag_enum,
            label_text=label_text,
            min_value=min_value,
            max_value=max_value,
            step=step,
            tooltip_text=tooltip_text,
            width=width
        )

        widget.checkbox.stateChanged.connect(lambda: widget.spinbox.setEnabled(widget.checkbox.isChecked()))

        if not state_changed_callback:
            handle_flag_func = lambda: self.command_builder.update_boolean_flag(
                flag_enum=flag_enum,
                enabled=widget.checkbox.isChecked(),
                args=widget.spinbox.value()
            )
            widget.checkbox.stateChanged.connect(handle_flag_func)
            widget.spinbox.valueChanged.connect(handle_flag_func)
            widget.checkbox.stateChanged.connect(self.update_command_preview)
            widget.spinbox.valueChanged.connect(self.update_command_preview)

        else:
            widget.checkbox.stateChanged.connect(state_changed_callback)
            widget.spinbox.valueChanged.connect(state_changed_callback)

        widget.spinbox.setEnabled(False)

        return widget
    


    def update_command_viewer(self):
        """Update the command viewer to reflect the current state of the application.
        """
        self.command_preview.setVisible(self.command_preview_checkbox.isChecked())
        self.settings.setValue(f"{self.settings_group}/command_preview", "true" if self.command_preview_checkbox.isChecked() else "false")


    def update_log_file(self):
        """Update mode and directory of log file (-l or -L)
        """
        self.save_logs_selector.setVisible(self.save_logs_combobox.current_index != 0)
        new_flag = self.save_logs_combobox.current_data if self.save_logs_selector.text else LogFile.Disabled

        self.command_builder.update_flag_group(
            flag_enum_group=LogFile,
            new_flag=new_flag,
            args=self.save_logs_selector.text,
            enabled=new_flag != LogFile.Disabled
        )

        self.update_command_preview()


    def install_pgn_extract(self):
        """Install pgn-extract if not already installed.
        Downloads the latest version from the releases page.
        """

        if platform.system() == "Windows":
            print("Windows detected")
            urllib.request.urlretrieve("https://www.cs.kent.ac.uk/~djb/pgn-extract/pgn-extract.exe", "pgn-extract.exe")
            QMessageBox.information(self, "Installation", "pgn-extract has been installed successfully.")
        elif platform.system() == "Darwin":
            original_dir = os.path.abspath(".")
            tmp_script = os.path.join(tempfile.gettempdir(), "unix_install.sh")  # Assuming unix_install.sh is in the current directory
            shutil.copy("unix_install.sh", tmp_script)
            os.chmod(tmp_script, 0o755)  # Make the script executable
            print("macOS detected")
            apple_script = f'do shell script "bash \\"{tmp_script}\\" \\"{original_dir}\\"" with administrator privileges'
            shell = subprocess.run(['osascript','-e', apple_script]) # Assuming unix_install.sh is in the current directory
        elif platform.system() == "Linux":
            print("Linux detected")


    def toggle_darkmode(self, enabled: bool):
        """Toggle dark mode.

        Args:
            enabled (bool): Whether to enable dark mode.
        """        
        if enabled:
            stylesheet_path = "stylesheets/darkmode.qss"
            self.settings.setValue("theme", "dark")     
        else:
            stylesheet_path = "stylesheets/lightmode.qss"    
            self.settings.setValue("theme", "light") 

        with open(stylesheet_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())


    def update_command_preview(self):
        """
        Update command preview widget to match app state.
        Represents what will be executed by pgn-extract.
        """
        cmdline = self.command_builder.build()
        self.command_preview.setText(" ".join(cmdline))


    def closeEvent(self, event):
        """Handle application close event.

        Args:
            event (QCloseEvent): The close event.
        """        
        if self.tag_match_window and self.tag_match_window.isVisible():
            self.tag_match_window.close()

        self.settings.setValue(f"{self.settings_group}/geometry", self.saveGeometry())

        if self.current_worker:
            self.current_worker.terminate()

        super().closeEvent(event)


    def reset_settings(self):
        """
        Clear QSettings and re-initialise settings to get to 'default' state.
        """
        reply = QMessageBox.question(
        self,
        "Confirm Reset",
        "Are you sure you want to reset all application settings?\n" \
            "(will not affect pgn-extract options)",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.__init_app_settings()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(app.exec())
