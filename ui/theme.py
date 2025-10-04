"""集中管理应用配色、间距与字体."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import customtkinter as ctk


@dataclass(frozen=True)
class Theme:
    colors: Dict[str, str] = field(default_factory=lambda: {
        "background": "#F2F6FC",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FAFF",
        "surface_soft": "#EEF2FF",
        "surface_hover": "#E2E8F0",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "accent_muted": "#60A5FA",
        "text_primary": "#0F172A",
        "text_muted": "#64748B",
        "chip_bg": "#DBEAFE",
        "danger": "#EF4444",
        "success": "#16A34A",
    })
    radius: Dict[str, int] = field(default_factory=lambda: {
        "card": 18,
        "section": 16,
        "button": 12,
        "chip": 20,
    })
    spacing: Dict[str, int] = field(default_factory=lambda: {
        "page": 14,
        "section_gap": 12,
        "item": 10,
    })
    font_settings: Dict[str, Dict[str, object]] = field(default_factory=lambda: {
        "title": {"family": "Microsoft YaHei UI", "size": 25, "weight": "bold"},
        "subtitle": {"family": "Microsoft YaHei UI", "size": 17, "weight": "bold"},
        "button": {"family": "Microsoft YaHei UI", "size": 15, "weight": "bold"},
        "body": {"family": "Microsoft YaHei UI", "size": 14},
        "label": {"family": "Microsoft YaHei UI", "size": 13},
        "chip": {"family": "Microsoft YaHei UI", "size": 12, "weight": "bold"},
        "mono": {"family": "Consolas", "size": 12},
    })

    def create_fonts(self) -> Dict[str, ctk.CTkFont]:
        """为当前主题创建 CTkFont 实例."""
        return {name: ctk.CTkFont(**config) for name, config in self.font_settings.items()}


DEFAULT_THEME = Theme()


def apply_theme(root: ctk.CTk, theme: Theme = DEFAULT_THEME) -> Dict[str, ctk.CTkFont]:
    """应用基础主题设置并返回字体集合."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("dark-blue")
    ctk.set_widget_scaling(1.0)
    root.configure(fg_color=theme.colors["background"])
    return theme.create_fonts()
