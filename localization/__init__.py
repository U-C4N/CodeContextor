"""
Localization module for CodeContextor.

This module provides multi-language support for the application,
supporting 10 languages: EN, TR, RU, ES, PT, FR, IT, UA, DE, NL.
"""

from .translations import TRANSLATIONS, get_translation

__all__ = ['TRANSLATIONS', 'get_translation'] 