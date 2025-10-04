"""封装 CustomTkinter 组件以统一外观与交互."""
from __future__ import annotations

from typing import Callable, Dict, Optional

import customtkinter as ctk

from .theme import DEFAULT_THEME, Theme


class Card(ctk.CTkFrame):
    """统一样式的卡片容器."""

    def __init__(
        self,
        master,
        *,
        theme: Theme = DEFAULT_THEME,
        variant: str = "surface",
        padding: Optional[tuple[int, int]] = (18, 18),
        **kwargs,
    ) -> None:
        bg_map = {
            "surface": theme.colors["surface"],
            "surface-alt": theme.colors["surface_alt"],
            "surface-soft": theme.colors["surface_soft"],
        }
        base_kwargs = {
            "fg_color": bg_map.get(variant, theme.colors["surface"]),
            "corner_radius": theme.radius["card"],
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)
        if padding:
            inner = ctk.CTkFrame(self, fg_color="transparent")
            inner.grid(row=0, column=0, sticky="nsew", padx=padding[0], pady=padding[1])
            inner.grid_columnconfigure(0, weight=1)
            inner.grid_rowconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
            self.content = inner
        else:
            self.content = self


class SectionHeader(ctk.CTkFrame):
    """包含标题与描述文本的区段标题."""

    def __init__(
        self,
        master,
        *,
        title: str,
        description: Optional[str] = None,
        fonts: Dict[str, ctk.CTkFont],
        theme: Theme = DEFAULT_THEME,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=fonts["subtitle"],
            text_color=theme.colors["text_primary"],
        )
        title_label.grid(row=0, column=0, sticky="w")
        if description:
            desc = ctk.CTkLabel(
                self,
                text=description,
                font=fonts["label"],
                text_color=theme.colors["text_muted"],
            )
            desc.grid(row=1, column=0, sticky="w", pady=(4, 0))


class _BaseButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        *,
        fonts: Dict[str, ctk.CTkFont],
        theme: Theme = DEFAULT_THEME,
        **kwargs,
    ) -> None:
        base_kwargs = {
            "height": 40,
            "corner_radius": theme.radius["button"],
            "font": fonts["button"],
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class PrimaryButton(_BaseButton):
    def __init__(self, master, *, fonts, theme: Theme = DEFAULT_THEME, **kwargs):
        colors = {
            "fg_color": theme.colors["accent"],
            "hover_color": theme.colors["accent_hover"],
            "text_color": "white",
        }
        colors.update(kwargs)
        super().__init__(master, fonts=fonts, theme=theme, **colors)


class SecondaryButton(_BaseButton):
    def __init__(self, master, *, fonts, theme: Theme = DEFAULT_THEME, **kwargs):
        colors = {
            "fg_color": theme.colors["surface_soft"],
            "hover_color": theme.colors["surface_hover"],
            "text_color": theme.colors["text_primary"],
        }
        colors.update(kwargs)
        super().__init__(master, fonts=fonts, theme=theme, **colors)


class TertiaryButton(_BaseButton):
    def __init__(self, master, *, fonts, theme: Theme = DEFAULT_THEME, **kwargs):
        colors = {
            "fg_color": "transparent",
            "hover_color": theme.colors["surface_hover"],
            "text_color": theme.colors["text_primary"],
            "border_width": 0,
        }
        colors.update(kwargs)
        super().__init__(master, fonts=fonts, theme=theme, **colors)


class StatusChip(ctk.CTkLabel):
    def __init__(self, master, *, text: str, fonts, theme: Theme = DEFAULT_THEME):
        super().__init__(
            master,
            text=text,
            font=fonts["chip"],
            text_color=theme.colors["text_primary"],
            fg_color=theme.colors["chip_bg"],
            corner_radius=theme.radius["chip"],
            padx=14,
            pady=6,
        )


class InfoTextBox(ctk.CTkTextbox):
    def __init__(
        self,
        master,
        *,
        fonts,
        theme: Theme = DEFAULT_THEME,
        height: int = 160,
        wrap: str = "word",
        **kwargs,
    ):
        base_kwargs = {
            "fg_color": theme.colors["surface_soft"],
            "text_color": theme.colors["text_primary"],
            "border_width": 0,
            "corner_radius": theme.radius["section"],
            "font": fonts["body"],
            "height": height,
            "wrap": wrap,
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class ScrollSection(ctk.CTkScrollableFrame):
    def __init__(self, master, *, theme: Theme = DEFAULT_THEME, **kwargs):
        base_kwargs = {
            "fg_color": theme.colors["surface_soft"],
            "corner_radius": theme.radius["section"],
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class NavigationRail(ctk.CTkFrame):
    """侧边导航栏，支持选中态切换."""

    def __init__(self, master, *, fonts, theme: Theme = DEFAULT_THEME):
        super().__init__(master, fg_color=theme.colors["surface"], corner_radius=0)
        self._theme = theme
        self._fonts = fonts
        self._buttons: Dict[str, ctk.CTkButton] = {}
        self.grid_rowconfigure("all", weight=0)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self,
            text="设置",
            font=fonts["subtitle"],
            text_color=theme.colors["text_primary"],
        )
        title.grid(row=0, column=0, padx=18, pady=(18, 12), sticky="w")

    def add_item(self, key: str, text: str, command: Callable[[], None]) -> None:
        button = ctk.CTkButton(
            self,
            text=text,
            command=lambda k=key, cmd=command: (self.select(k), cmd()),
            corner_radius=0,
            height=42,
            fg_color="transparent",
            hover_color=self._theme.colors["surface_hover"],
            text_color=self._theme.colors["text_primary"],
            anchor="w",
            font=self._fonts["label"],
            border_width=0,
        )
        row_index = len(self._buttons) + 1
        button.grid(row=row_index, column=0, sticky="ew", padx=0, pady=2)
        self._buttons[key] = button

    def select(self, key: Optional[str]) -> None:
        for name, button in self._buttons.items():
            if name == key:
                button.configure(
                    fg_color=self._theme.colors["surface_soft"],
                    text_color=self._theme.colors["accent"],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=self._theme.colors["text_primary"],
                )


class LabeledInput(ctk.CTkFrame):
    """带标题的输入区域，支持自定义控件."""

    def __init__(self, master, *, label: str, fonts, theme: Theme = DEFAULT_THEME):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=fonts["label"],
            text_color=theme.colors["text_muted"],
        )
        label_widget.grid(row=0, column=0, sticky="w")
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.body.grid_columnconfigure(0, weight=1)

    def mount(self, widget, *, column: int = 0, sticky: str = "ew") -> None:
        widget.grid(row=0, column=column, sticky=sticky)
