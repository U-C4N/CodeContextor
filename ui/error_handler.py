import tkinter as tk
from tkinter import messagebox
import logging
import traceback
from typing import Optional, Any
from localization import get_translation


class ErrorHandler:
    """Handles errors and displays user-friendly messages with localization support."""
    
    def __init__(self, parent: Optional[tk.Widget] = None, language: str = "EN") -> None:
        """
        Initialize the error handler.
        
        Args:
            parent: Parent widget for dialog boxes
            language: Current language code for translations
        """
        self.parent = parent
        self.language = language
        self.logger = logging.getLogger(__name__)
        
        # Set up logging if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.ERROR)
    
    def set_language(self, language: str) -> None:
        """
        Set the language for error messages.
        
        Args:
            language: Language code (e.g., "EN", "TR", "ES")
        """
        self.language = language
    
    def show_error(self, error_code: str, exception: Optional[Exception] = None, 
                   details: Optional[str] = None, show_details: bool = False) -> None:
        """
        Display a user-friendly error message based on error code.
        
        Args:
            error_code: Error code for message lookup
            exception: The original exception (optional)
            details: Additional details to show (optional)
            show_details: Whether to show technical details
        """
        try:
            # Get localized error messages
            error_messages = self._get_error_messages()
            
            title = get_translation(self.language, "error_title")
            message = error_messages.get(error_code, error_messages["UNKNOWN_ERROR"])
            
            # Log the error with full details
            if exception:
                self.logger.error(f"{error_code}: {str(exception)}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
            else:
                self.logger.error(f"{error_code}: {details or 'No details provided'}")
            
            # Prepare the full message
            full_message = message
            
            if show_details and (details or exception):
                full_message += "\n\n" + get_translation(self.language, "details_label") + "\n"
                if details:
                    full_message += details
                elif exception:
                    full_message += str(exception)
            
            # Show the error dialog
            messagebox.showerror(title, full_message, parent=self.parent)
            
        except Exception as e:
            # Fallback error handling
            print(f"Error in error handler: {e}")
            messagebox.showerror("Error", f"An error occurred: {error_code}", parent=self.parent)
    
    def show_warning(self, warning_code: str, details: Optional[str] = None) -> None:
        """
        Display a user-friendly warning message.
        
        Args:
            warning_code: Warning code for message lookup
            details: Additional details to show (optional)
        """
        try:
            warning_messages = self._get_warning_messages()
            
            title = get_translation(self.language, "warning_title")
            message = warning_messages.get(warning_code, warning_messages["UNKNOWN_WARNING"])
            
            # Log the warning
            self.logger.warning(f"{warning_code}: {details or 'No details provided'}")
            
            full_message = message
            if details:
                full_message += f"\n\n{details}"
            
            messagebox.showwarning(title, full_message, parent=self.parent)
            
        except Exception as e:
            print(f"Error in warning handler: {e}")
            messagebox.showwarning("Warning", f"Warning: {warning_code}", parent=self.parent)
    
    def show_info(self, info_code: str, details: Optional[str] = None) -> None:
        """
        Display an informational message.
        
        Args:
            info_code: Information code for message lookup
            details: Additional details to show (optional)
        """
        try:
            info_messages = self._get_info_messages()
            
            title = get_translation(self.language, "info_title")
            message = info_messages.get(info_code, info_messages["UNKNOWN_INFO"])
            
            full_message = message
            if details:
                full_message += f"\n\n{details}"
            
            messagebox.showinfo(title, full_message, parent=self.parent)
            
        except Exception as e:
            print(f"Error in info handler: {e}")
            messagebox.showinfo("Info", f"Info: {info_code}", parent=self.parent)
    
    def ask_yes_no(self, question_code: str, details: Optional[str] = None) -> bool:
        """
        Ask a yes/no question to the user.
        
        Args:
            question_code: Question code for message lookup
            details: Additional details to show (optional)
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        try:
            question_messages = self._get_question_messages()
            
            title = get_translation(self.language, "question_title")
            message = question_messages.get(question_code, question_messages["UNKNOWN_QUESTION"])
            
            full_message = message
            if details:
                full_message += f"\n\n{details}"
            
            return messagebox.askyesno(title, full_message, parent=self.parent)
            
        except Exception as e:
            print(f"Error in question handler: {e}")
            return messagebox.askyesno("Question", f"Question: {question_code}", parent=self.parent)
    
    def _get_error_messages(self) -> dict:
        """Get localized error messages."""
        return {
            "FILE_NOT_FOUND": get_translation(self.language, "error_file_not_found"),
            "PERMISSION_DENIED": get_translation(self.language, "error_permission_denied"),
            "NETWORK_ERROR": get_translation(self.language, "error_network_connection"),
            "PROCESSING_ERROR": get_translation(self.language, "error_processing_failed"),
            "INVALID_PATH": get_translation(self.language, "error_invalid_path"),
            "DISK_FULL": get_translation(self.language, "error_disk_full"),
            "MEMORY_ERROR": get_translation(self.language, "error_memory"),
            "TIMEOUT_ERROR": get_translation(self.language, "error_timeout"),
            "UNKNOWN_ERROR": get_translation(self.language, "error_unknown")
        }
    
    def _get_warning_messages(self) -> dict:
        """Get localized warning messages."""
        return {
            "LARGE_FILE": get_translation(self.language, "warning_large_file"),
            "MANY_FILES": get_translation(self.language, "warning_many_files"),
            "UNSUPPORTED_FORMAT": get_translation(self.language, "warning_unsupported_format"),
            "UNKNOWN_WARNING": get_translation(self.language, "warning_unknown")
        }
    
    def _get_info_messages(self) -> dict:
        """Get localized info messages."""
        return {
            "OPERATION_COMPLETE": get_translation(self.language, "info_operation_complete"),
            "FILE_SAVED": get_translation(self.language, "info_file_saved"),
            "COPIED_TO_CLIPBOARD": get_translation(self.language, "info_copied_clipboard"),
            "UNKNOWN_INFO": get_translation(self.language, "info_unknown")
        }
    
    def _get_question_messages(self) -> dict:
        """Get localized question messages."""
        return {
            "CONFIRM_OVERWRITE": get_translation(self.language, "question_confirm_overwrite"),
            "CONFIRM_DELETE": get_translation(self.language, "question_confirm_delete"),
            "SAVE_CHANGES": get_translation(self.language, "question_save_changes"),
            "UNKNOWN_QUESTION": get_translation(self.language, "question_unknown")
        }
    
    def handle_exception(self, exception: Exception, context: str = "") -> None:
        """
        Handle an exception by determining the appropriate error code and showing a user-friendly message.
        
        Args:
            exception: The exception to handle
            context: Additional context about where the error occurred
        """
        # Map common exceptions to error codes
        error_code = "UNKNOWN_ERROR"
        
        if isinstance(exception, FileNotFoundError):
            error_code = "FILE_NOT_FOUND"
        elif isinstance(exception, PermissionError):
            error_code = "PERMISSION_DENIED"
        elif isinstance(exception, MemoryError):
            error_code = "MEMORY_ERROR"
        elif isinstance(exception, TimeoutError):
            error_code = "TIMEOUT_ERROR"
        elif isinstance(exception, (OSError, IOError)):
            if "No space left on device" in str(exception):
                error_code = "DISK_FULL"
            else:
                error_code = "PROCESSING_ERROR"
        
        # Show the error
        details = f"{context}\n{str(exception)}" if context else str(exception)
        self.show_error(error_code, exception, details, show_details=True) 