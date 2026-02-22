import os
import sys
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from colorama import Fore
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn, TextColumn, TimeRemainingColumn

from core.ui import clear_console, error, success, info, status, display_banner
from core.utils import load_file_lines

class KrakenModule(ABC):
    """Abstract Base Class for all KRAKEN brute force modules."""

    def __init__(self, name: str, default_port: Optional[int] = None):
        self.name: str = name
        self.default_port: Optional[int] = default_port
        self.script_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.results_dir: str = os.path.join(self.script_dir, '..', 'Results')
        self.logs_dir: str = os.path.join(self.script_dir, '..', 'Logs')
        
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def setup_ui(self) -> None:
        """Initializes the UI elements for the module."""
        clear_console()
        display_banner(f"Kraken {self.name} Brute-Force")
        info("\n" + "="*80 + "\n")

    def _get_wordlist(self, arg_file: Optional[str], default_filename: str, input_prompt: str, is_user: bool = False) -> List[str]:
        """Helper to get and load a wordlist safely."""
        wordlist_path = arg_file
        
        # Interactive fallback
        if not wordlist_path:
            default_path = os.path.join(self.script_dir, "..", "wordlists", default_filename)
            wordlist_path = input(Fore.WHITE + f"{input_prompt} (default: {default_filename}): ").strip() or default_path
            
        items = load_file_lines(wordlist_path)
        
        if not items and not is_user:  # Password lists can't be empty
             error(f"Error: The list '{wordlist_path}' is empty or could not be found.")
             sys.exit(1)
             
        return items

    def create_progress_bar(self) -> Progress:
        """Creates and returns a rich progress bar instance."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            "|",
            TimeRemainingColumn(),
            TextColumn("[cyan]{task.fields[current_attempt]}")
        )

    @abstractmethod
    def check_target(self, target: str, port: Optional[int] = None) -> bool:
        """Verifies if the target is reachable/valid before attacking."""
        pass

    @abstractmethod
    def attempt_login(self, *args, **kwargs) -> Any:
        """Core logic to attempt a single login."""
        pass

    @abstractmethod
    def execute_brute(self, *args, **kwargs) -> None:
        """The main loop handling concurrency and thread pools."""
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> None:
        """CLI Entry point."""
        pass

    @abstractmethod
    def run_interactive(self) -> None:
        """Interactive Menu Entry point."""
        pass
