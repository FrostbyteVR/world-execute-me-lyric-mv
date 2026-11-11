"""Manim configuration for the display: 960 x 320 px, a 19.2 x 6.4 unit frame (100 virtual px per unit)."""
from manim import config


def configure(width=960, height=320, fps=None):
    config.pixel_width = width
    config.pixel_height = height
    config.frame_width = 19.2
    config.frame_height = 19.2 * height / width
    if fps:
        config.frame_rate = fps
    config.background_color = '#000000'
    from .fonts import register
    register()
