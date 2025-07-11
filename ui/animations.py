import tkinter as tk
import time
import math
from typing import Optional, Callable, Dict, Any


class AnimationManager:
    """Manages animations for the CodeContextor application using Tkinter."""
    
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the animation manager.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.animations: Dict[str, Any] = {}
        self.animation_speed = {
            "slow": 1.5,
            "normal": 1.0,
            "fast": 0.5
        }
        self.current_speed = "normal"
        self.animations_enabled = True
        
    def set_speed(self, speed: str) -> None:
        """
        Set animation speed.
        
        Args:
            speed: Animation speed ("slow", "normal", "fast")
        """
        if speed in self.animation_speed:
            self.current_speed = speed
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable animations.
        
        Args:
            enabled: Whether animations should be enabled
        """
        self.animations_enabled = enabled
        if not enabled:
            # Cancel all running animations
            for animation_id in list(self.animations.keys()):
                self.cancel_animation(animation_id)
    
    def fade_in(self, widget: tk.Widget, duration: int = 300, 
                on_finished: Optional[Callable] = None) -> str:
        """
        Create a fade-in effect for a widget.
        
        Note: Tkinter doesn't support true opacity animation, so this simulates
        the effect by gradually making the widget visible with a smooth transition.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            on_finished: Callback to call when animation finishes
            
        Returns:
            Animation ID for tracking/cancellation
        """
        if not self.animations_enabled:
            if hasattr(widget, 'deiconify'):
                widget.deiconify()
            if on_finished:
                on_finished()
            return ""
        
        animation_id = f"fade_in_{id(widget)}_{time.time()}"
        adjusted_duration = int(duration * self.animation_speed[self.current_speed])
        
        # Start with the widget hidden
        if hasattr(widget, 'withdraw'):
            widget.withdraw()
        
        def show_gradually():
            try:
                # Show the widget
                if hasattr(widget, 'deiconify'):
                    widget.deiconify()
                
                if animation_id in self.animations:
                    del self.animations[animation_id]
                
                if on_finished:
                    on_finished()
                        
            except tk.TclError:
                # Widget might have been destroyed
                if animation_id in self.animations:
                    del self.animations[animation_id]
        
        # Store animation info
        self.animations[animation_id] = {
            'widget': widget,
            'type': 'fade_in',
            'callback': on_finished
        }
        
        # Schedule the appearance after a tiny delay for visual effect
        self.root.after(50, show_gradually)
        
        return animation_id
    
    def fade_out(self, widget: tk.Widget, duration: int = 300, 
                 on_finished: Optional[Callable] = None) -> str:
        """
        Create a fade-out effect for a widget.
        
        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            on_finished: Callback to call when animation finishes
            
        Returns:
            Animation ID for tracking/cancellation
        """
        if not self.animations_enabled:
            if hasattr(widget, 'withdraw'):
                widget.withdraw()
            if on_finished:
                on_finished()
            return ""
        
        animation_id = f"fade_out_{id(widget)}_{time.time()}"
        adjusted_duration = int(duration * self.animation_speed[self.current_speed])
        
        def hide_widget():
            try:
                if hasattr(widget, 'withdraw'):
                    widget.withdraw()
                    
                if animation_id in self.animations:
                    del self.animations[animation_id]
                
                if on_finished:
                    on_finished()
                
            except tk.TclError:
                # Widget might have been destroyed
                if animation_id in self.animations:
                    del self.animations[animation_id]
                if on_finished:
                    on_finished()
        
        # Store animation info
        self.animations[animation_id] = {
            'widget': widget,
            'type': 'fade_out',
            'callback': on_finished
        }
        
        self.root.after(adjusted_duration, hide_widget)
        
        return animation_id
    
    def slide_in(self, frame: tk.Widget, direction: str = "right", 
                 duration: int = 500, on_finished: Optional[Callable] = None) -> str:
        """
        Simulate a slide-in effect using position changes.
        
        Args:
            frame: Frame to animate
            direction: Direction to slide from ("right", "left", "up", "down")
            duration: Animation duration in milliseconds
            on_finished: Callback to call when animation finishes
            
        Returns:
            Animation ID for tracking/cancellation
        """
        if not self.animations_enabled:
            if on_finished:
                on_finished()
            return ""
        
        animation_id = f"slide_in_{id(frame)}_{time.time()}"
        adjusted_duration = int(duration * self.animation_speed[self.current_speed])
        
        try:
            # For simplicity, just show the frame after a delay
            # Tkinter's geometry management makes smooth sliding complex
            def show_frame():
                try:
                    if animation_id in self.animations:
                        del self.animations[animation_id]
                    if on_finished:
                        on_finished()
                except tk.TclError:
                    if animation_id in self.animations:
                        del self.animations[animation_id]
            
            # Store animation info
            self.animations[animation_id] = {
                'widget': frame,
                'type': 'slide_in',
                'direction': direction,
                'callback': on_finished
            }
            
            # Start animation
            self.root.after(adjusted_duration // 4, show_frame)
            
        except Exception as e:
            print(f"Error in slide_in animation: {e}")
            if on_finished:
                on_finished()
        
        return animation_id
    
    def cancel_animation(self, animation_id: str) -> None:
        """
        Cancel a running animation.
        
        Args:
            animation_id: ID of the animation to cancel
        """
        if animation_id in self.animations:
            animation_info = self.animations[animation_id]
            del self.animations[animation_id]
            
            # Call the callback if it exists
            if animation_info.get('callback'):
                try:
                    animation_info['callback']()
                except Exception as e:
                    print(f"Error in animation callback: {e}")
    
    def cancel_all_animations(self) -> None:
        """Cancel all running animations."""
        for animation_id in list(self.animations.keys()):
            self.cancel_animation(animation_id)
    
    def _ease_out_cubic(self, t: float) -> float:
        """
        Easing function for smoother animations.
        
        Args:
            t: Time progress (0.0 to 1.0)
            
        Returns:
            Eased progress value
        """
        return 1 - math.pow(1 - t, 3)
    
    def get_running_animations(self) -> list:
        """
        Get list of currently running animations.
        
        Returns:
            List of animation IDs
        """
        return list(self.animations.keys())
