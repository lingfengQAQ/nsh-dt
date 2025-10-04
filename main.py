import customtkinter as ctk
from tkinter import messagebox
import threading
import json
import re
import os
import logging
import sys
import ctypes

from ui import (
    DEFAULT_THEME,
    Card,
    InfoTextBox,
    PrimaryButton,
    ScrollSection,
    SectionHeader,
    SecondaryButton,
    StatusChip,
    TertiaryButton,
    apply_theme,
)

# 应用配置常量
APP_CONFIG = {
    'WINDOW_SIZE': '1080x720',
    'MAX_AI_CONCURRENT': 2,
    'MAX_POEM_RESULTS': 5,
    'MAX_DISPLAYED_ANSWERS': 2,
    'MAX_DISPLAYED_POEMS': 2,
    'LOG_FILENAME': 'app.log',
    'SETTINGS_FILENAME': 'settings.json'
}

# --- DPI Awareness ---
# Add this block to make the application DPI-aware
if sys.platform == "win32":
    try:
        # This tells Windows that the process is DPI-aware, preventing blurring on high-DPI displays.
        # It should be called before any GUI elements are created.
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        # Log the error if setting DPI awareness fails.
        logging.warning(f"Could not set DPI awareness: {e}")
# --- End of DPI Awareness Block ---

from screenshot_tool import ScreenshotTool
from ai_manager import AIManager
from ocr_manager import OCRManager
from settings_window import SettingsWindow
from knowledge_base_manager import KnowledgeBaseManager

class QuestionAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("逆水寒殿试答题器")
        self.geometry(APP_CONFIG['WINDOW_SIZE'])
        self.minsize(1080, 720)
        self.resizable(True, True)
        self.base_height = 720  # 基准高度用于字体缩放

        self.setup_logging()

        self.theme = DEFAULT_THEME
        # 初始化字体需在根窗口创建后执行
        self.fonts = apply_theme(self, self.theme)

        self.screenshot_tool = ScreenshotTool(self)
        self.ai_manager = AIManager()
        self.ocr_manager = OCRManager()
        self.kb_manager = KnowledgeBaseManager()
        
        self.answer_widgets = {}
        self.highlight_populated = False

        self.load_settings()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 绑定窗口大小变化事件
        self.bind("<Configure>", self.on_window_resize)
        self._last_height = 720  # 避免频繁更新

        # Start loading the knowledge base in a background thread
        threading.Thread(target=self._load_kb_background, daemon=True).start()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_card = Card(self, theme=self.theme, padding=(10, 10))
        header_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        header_card.content.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_card.content,
            text="逆水寒殿试答题器",
            font=self.fonts["title"],
            text_color=self.theme.colors["text_primary"],
        )
        title_label.grid(row=0, column=0, sticky="w")

        self.header_status_label = StatusChip(
            header_card.content,
            text="就绪",
            fonts=self.fonts,
            theme=self.theme,
        )
        self.header_status_label.grid(row=0, column=1, sticky="e")

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        content_frame.grid_columnconfigure(0, weight=0, minsize=260)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        control_card = Card(content_frame, theme=self.theme, padding=(10, 10))
        control_card.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        control = control_card.content
        control.grid_columnconfigure(0, weight=1)

        SectionHeader(
            control,
            title="控制中心",
            description="快速操作与服务状态",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        self.screenshot_btn = PrimaryButton(
            control,
            text="打开截图区域",
            command=self.toggle_screenshot_area,
            fonts=self.fonts,
            theme=self.theme,
        )
        self.screenshot_btn.grid(row=1, column=0, sticky="ew", pady=(12, 8))

        self.capture_btn = SecondaryButton(
            control,
            text="截图并识别",
            command=self.capture_and_recognize,
            state="disabled",
            fonts=self.fonts,
            theme=self.theme,
        )
        self.capture_btn.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        settings_btn = TertiaryButton(
            control,
            text="打开设置",
            command=self.open_settings,
            fonts=self.fonts,
            theme=self.theme,
            anchor="center",
        )
        settings_btn.grid(row=3, column=0, sticky="ew")

        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 题目卡片（标题嵌入，2行高度）
        question_card = Card(right_frame, theme=self.theme, padding=(6, 6))
        question_card.grid(row=0, column=0, sticky="ew")
        question = question_card.content
        question.grid_columnconfigure(0, weight=1)

        self.question_text = InfoTextBox(
            question,
            fonts=self.fonts,
            theme=self.theme,
            height=36,  # 约2行文字高度
        )
        self.question_text.grid(row=0, column=0, sticky="ew")

        # 本地知识库卡片（标题嵌入，3行高度）
        local_card = Card(right_frame, theme=self.theme, padding=(6, 6))
        local_card.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        local = local_card.content
        local.grid_columnconfigure(0, weight=1)

        self.local_results_frame = InfoTextBox(
            local,
            fonts=self.fonts,
            theme=self.theme,
            height=54,  # 约3行文字高度
        )
        self.local_results_frame.grid(row=0, column=0, sticky="ew")

        # AI回答卡片（标题嵌入，无额外标题）
        answers_card = Card(right_frame, theme=self.theme, padding=(6, 6))
        answers_card.grid(row=2, column=0, sticky="nsew", pady=(6, 0))
        answers = answers_card.content
        answers.grid_columnconfigure(0, weight=1)
        answers.grid_rowconfigure(0, weight=1)

        self.answers_frame = ScrollSection(answers, theme=self.theme)
        self.answers_frame.grid(row=0, column=0, sticky="nsew")
        self.answers_frame.grid_columnconfigure(0, weight=1)

        status_card = Card(self, theme=self.theme, padding=(8, 8))
        status_card.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        status = status_card.content
        status.grid_columnconfigure(0, weight=1)
        status.grid_columnconfigure(1, weight=0)

        self.status_var = ctk.StringVar(value="就绪")
        status_label = ctk.CTkLabel(
            status,
            textvariable=self.status_var,
            font=self.fonts["label"],
            text_color=self.theme.colors["text_muted"],
        )
        status_label.grid(row=0, column=0, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(
            status,
            mode="indeterminate",
            progress_color=self.theme.colors["accent"],
            fg_color=self.theme.colors["surface_soft"],
            height=6,
        )
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=(16, 0))
        self.progress_bar.grid_remove()

        self.clear_ai_answers()

    def _load_kb_background(self):
        """Load the knowledge base in the background and manage the progress bar."""
        self.after(0, self.progress_bar.grid) # Show progress bar
        self.after(0, self.progress_bar.start)

        self.kb_manager.ensure_loaded() # This is the blocking call

        # 立即构建索引（后台异步）
        self.after(0, self.status_var.set, "知识库加载完毕，正在构建索引...")
        self.kb_manager._build_index()  # 构建倒排索引

        self.after(0, self.progress_bar.stop)
        self.after(0, self.progress_bar.grid_remove) # Hide progress bar
        self.after(0, self.status_var.set, "就绪，索引已优化。")
        self.after(0, lambda: self.header_status_label.configure(text="已优化"))

    def toggle_screenshot_area(self):
        if self.screenshot_tool.is_active:
            self.screenshot_tool.hide_overlay()
            self.screenshot_btn.configure(
                text="打开截图区域",
                fg_color=self.theme.colors["accent"],
                hover_color=self.theme.colors["accent_hover"],
                text_color="white"
            )
            self.capture_btn.configure(
                state="disabled",
                fg_color=self.theme.colors["surface_hover"],
                text_color=self.theme.colors["text_primary"]
            )
            self.header_status_label.configure(text="就绪")
        else:
            self.screenshot_tool.show_overlay()
            self.screenshot_btn.configure(
                text="隐藏截图区域",
                fg_color=self.theme.colors["surface_soft"],
                hover_color=self.theme.colors["surface_hover"],
                text_color=self.theme.colors["text_primary"]
            )
            self.capture_btn.configure(
                state="normal",
                fg_color=self.theme.colors["accent"],
                hover_color=self.theme.colors["accent_hover"],
                text_color="white"
            )
            self.header_status_label.configure(text="截图模式")

    def capture_and_recognize(self):
        self.status_var.set("正在截图...")
        self.update()
        threading.Thread(target=self._capture_and_recognize_thread, daemon=True).start()


    def _format_question_text(self, text):
        if not text:
            return ""

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""

        stop_words = {"确定", "取消", "确认", "返回", "完成", "提交", "关闭", "继续", "重试", "下一题", "上一题"}
        while lines and (lines[-1] in stop_words or re.fullmatch(r"[0-9A-Za-z]+", lines[-1])):
            lines.pop()
        if not lines:
            return ""

        single_char_count = sum(1 for line in lines if len(line) <= 2)
        if single_char_count >= max(1, int(len(lines) * 0.6)):
            return ''.join(lines)

        merged = []
        buffer = []
        for line in lines:
            if len(line) <= 2 and not re.search(r"[。！？?！]", line):
                buffer.append(line)
            else:
                if buffer:
                    merged.append(''.join(buffer))
                    buffer = []
                merged.append(line)
        if buffer:
            merged.append(''.join(buffer))

        return "\n".join(merged)


    def _capture_and_recognize_thread(self):
        try:
            image = self.screenshot_tool.capture_area()
            if image is None:
                self.after(0, lambda: self.status_var.set("截图失败或取消"))
                return

            # On successful capture, toggle the button state and hide the overlay
            self.after(0, self.toggle_screenshot_area)

            self.after(0, lambda: self.status_var.set("正在识别文字..."))
            self.after(0, lambda: self.header_status_label.configure(text="识别中"))
            ocr_thread = threading.Thread(target=self._ocr_thread, args=(image,), daemon=True)
            ocr_thread.start()
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in capture and recognize thread: {e}", exc_info=True)
            self.after(0, lambda: self.status_var.set(f"错误: {error_msg}"))
            self.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误:\n{error_msg}"))

    def _ocr_thread(self, image):
        try:
            raw_text = self.ocr_manager.extract_text(image)
            question_text = self._format_question_text(raw_text)

            # 记录识别到的题目
            logging.info(f"=" * 60)
            logging.info(f"OCR识别结果: {question_text}")

            if not question_text.strip():
                self.after(0, lambda: self.status_var.set("未识别到文字"))
                logging.warning("OCR未识别到任何文字")
                question_text = ""
            self.after(0, lambda: self.update_question_text(question_text))
            self.after(0, self.clear_ai_answers)
            # 支持多种诗词问题格式
            trigger_phrases = [
                "请从以下字中选出一句诗词",
                "请从下列字中选出一句诗词",
                "从以下字中选出一句诗词",
                "从下列字中选出一句诗词",
                "用这些字组成一句诗",
                "用下面的字组成诗句",
                "这些字能组成什么诗句"
            ]
            is_poem_task = any(phrase in question_text for phrase in trigger_phrases)
            self.after(0, lambda: self.status_var.set("正在获取AI及本地回答..."))
            self.after(0, lambda: self.header_status_label.configure(text="生成答案"))
            self.get_all_answers_parallel(question_text, image, is_poem_task)
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in OCR thread: {e}", exc_info=True)
            self.after(0, lambda: self.status_var.set(f"错误: {error_msg}"))
            self.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误:\n{error_msg}"))

    def get_all_answers_parallel(self, question_text, image, is_poem_task):
        self.clear_ai_answers()

        if is_poem_task and hasattr(self, "local_results_frame"):
            import re
            chars_to_find = question_text

            # 找到"诗词"的位置，提取其后的内容
            if "诗词" in question_text:
                idx = question_text.find("诗词")
                chars_to_find = question_text[idx + 2:].strip()  # +2跳过"诗词"两个字

            # 去除尾部的按钮文字（确定、取消等）
            chars_to_find = re.sub(r'(确定|取消|选择|提交|重置).*$', '', chars_to_find)
            chars_to_find = chars_to_find.strip()

            logging.info(f"本地知识库 - 提取字符: {chars_to_find}")

            self.local_results_frame.configure(state="normal")
            self.local_results_frame.delete("1.0", "end")
            self.local_results_frame.insert("end", "正在匹配本地诗词...\n")
            self.local_results_frame.configure(state="disabled")
            threading.Thread(
                target=self._find_poem_locally,
                args=(chars_to_find, self.local_results_frame),
                daemon=True
            ).start()
        elif hasattr(self, "local_results_frame"):
            self.local_results_frame.configure(state="normal")
            self.local_results_frame.delete("1.0", "end")
            self.local_results_frame.insert("end", "本地匹配仅适用于诗词组字类题目。")
            self.local_results_frame.configure(state="disabled")

        enabled_ais = self.ai_manager.get_enabled_ais()
        ai_to_process = dict(list(enabled_ais.items())[:APP_CONFIG['MAX_AI_CONCURRENT']])

        if not ai_to_process and not is_poem_task:
            self.after(0, lambda: self.status_var.set("未配置或启用任何服务"))
            self.after(0, lambda: messagebox.showwarning("警告", "请先在设置中启用至少一个AI服务"))
            return

        def create_answer_card(name):
            # 极简卡片：标题嵌入内容，1行高度
            card = Card(self.answers_frame, theme=self.theme, padding=(8, 8))
            card.pack(fill="x", expand=False, padx=6, pady=4)
            card.content.grid_columnconfigure(0, weight=1)

            body = InfoTextBox(
                card.content,
                fonts=self.fonts,
                theme=self.theme,
                height=24,  # 约1行文字高度
            )
            body.grid(row=0, column=0, sticky="ew")

            # 在文本框内添加标题前缀（标题颜色高亮）
            body.insert("1.0", f"{name}：")
            body.tag_add("ai_name", "1.0", f"1.{len(name)+1}")
            body.tag_config("ai_name", foreground=self.theme.colors["accent"])

            return body

        for ai_name, config in ai_to_process.items():
            body_widget = create_answer_card(ai_name)
            self.answer_widgets[ai_name] = body_widget
            threading.Thread(
                target=self._get_single_ai_answer,
                args=(ai_name, config, question_text, image, body_widget),
                daemon=True
            ).start()

    def _search_locally(self, query, widget):
        """普通搜索方法"""
        try:
            results = self.kb_manager.search(query, limit=10)

            self.after(0, widget.delete, "1.0", "end")
            if results:
                # 显示搜索结果（移除font配置，CustomTkinter不支持）
                widget.tag_config("title", foreground=self.theme.colors["accent"])
                widget.tag_config("author", foreground="#FBBF24")
                widget.tag_config("content", foreground=self.theme.colors["text_primary"])

                self.after(0, widget.insert, "end", f"【搜索结果】找到 {len(results)} 首相关诗词\n\n", "title")

                for i, poem in enumerate(results[:5]):  # 只显示前5个结果
                    title = poem.get('title', '无题')
                    author = poem.get('author', '佚名')
                    content = poem.get('content', [])

                    self.after(0, widget.insert, "end", f"{i+1}. ", "title")
                    self.after(0, widget.insert, "end", f"《{title}》", "title")
                    self.after(0, widget.insert, "end", f" - {author}\n", "author")

                    # 显示内容片段
                    if isinstance(content, list) and content:
                        preview = content[0][:50] + "..." if len(content[0]) > 50 else content[0]
                        self.after(0, widget.insert, "end", f"   {preview}\n\n", "content")
            else:
                self.after(0, widget.insert, "end", "未找到相关诗词内容")

        except Exception as e:
            error_msg = f"本地搜索出错: {str(e)}"
            logging.error(f"Error in local search: {e}", exc_info=True)
            self.after(0, widget.delete, "1.0", "end")
            self.after(0, widget.insert, "end", error_msg)

    def _find_poem_locally(self, chars, widget):
        try:
            # This will block until the background loading is complete
            results = self.kb_manager.find_poem_from_chars(chars)

            # 记录本地知识库结果
            if results:
                poems_info = []
                for poem, matched_clauses in results:
                    poems_info.append(f"《{poem.get('title', '未知')}》- {poem.get('author', '未知')}: {matched_clauses}")
                logging.info(f"本地知识库 - 找到结果: {'; '.join(poems_info)}")
            else:
                logging.info(f"本地知识库 - 未找到匹配")

            # Clear the widget (either the loading message or old results) before showing new results
            self.after(0, widget.delete, "1.0", "end")
            self.after(0, self._update_poem_widget, widget, results)
        except Exception as e:
            error_msg = f"本地搜索出错: {str(e)}"
            logging.error(f"本地知识库错误: {e}", exc_info=True)
            self.after(0, widget.delete, "1.0", "end")
            self.after(0, widget.insert, "end", error_msg)

    def _update_poem_widget(self, widget, answer):
        widget.configure(state="normal")
        widget.delete("1.0", "end")

        # 添加标题前缀（标题颜色高亮）
        widget.insert("1.0", "本地：")
        widget.tag_add("title", "1.0", "1.3")
        widget.tag_config("title", foreground=self.theme.colors["accent"])

        # Configure a tag for highlighting once per widget
        widget.tag_config("highlight", foreground=self.theme.colors["accent"])
        widget.tag_config("answer", foreground="#F97316")

        if not answer:
            widget.insert("end", "未找到匹配的诗词")
        else:
            widget.insert("end", "【答案】", "answer")

            # 首先显示所有匹配的诗句（答案）
            all_matched = []
            for i, (poem, matched_clauses) in enumerate(answer):
                for clause in matched_clauses:
                    if clause not in all_matched:
                        all_matched.append(clause)

            if all_matched:
                cols = 3
                rows = (len(all_matched) + cols - 1) // cols
                for r in range(rows):
                    items = []
                    for c in range(cols):
                        idx = r + c * rows
                        if idx < len(all_matched):
                            items.append(f"• {all_matched[idx]}")
                    if items:
                        widget.insert("end", "    ".join(items) + "\n", "answer")
                widget.insert("end", "\n")

            widget.insert("end", "【出处】\n", "highlight")
            # 然后简化显示诗词信息
            for i, (poem, matched_clauses) in enumerate(answer[:APP_CONFIG['MAX_DISPLAYED_POEMS']]):
                title = poem.get('title', '无题')
                author = poem.get('author', '佚名')
                widget.insert("end", f"{i+1}. 《{title}》 - {author}\n")

                if i < len(answer) - 1:
                    widget.insert("end", "\n")

        widget.configure(state="disabled")
        self.after(100, lambda w=widget: self._adjust_widget_height(w))


    def _get_single_ai_answer(self, ai_name, config, question_text, image, widget):
        try:
            logging.info(f"AI({ai_name}) - 开始请求")
            stream = self.ai_manager.get_answer(ai_name, config, question_text, image)
            buffer = []
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if not content:
                    continue
                buffer.append(content)
                self.after(0, widget.insert, "end", content)
                if not self.highlight_populated:
                    preview = "".join(buffer)
                    if preview.strip():
                        self.after(0, lambda text=preview: self._update_highlight_preview(ai_name, text))

            # 记录完整的AI回答
            full_answer = "".join(buffer)
            if full_answer.strip():
                # 限制日志长度，只记录前500字符
                log_answer = full_answer[:500] + "..." if len(full_answer) > 500 else full_answer
                logging.info(f"AI({ai_name}) - 回答: {log_answer}")
            else:
                logging.warning(f"AI({ai_name}) - 回答为空")

            self.after(100, lambda w=widget: self._adjust_widget_height(w))
            self.after(0, lambda: self.header_status_label.configure(text="完成"))
            if not self.highlight_populated:
                joined = "".join(buffer)
                if joined.strip():
                    self.after(0, lambda text=joined: self._update_highlight_preview(ai_name, text))
        except Exception as e:
            error_msg = f"获取{ai_name}回答时出错: {str(e)}"
            logging.error(f"AI({ai_name})错误: {e}", exc_info=True)
            self.after(0, widget.insert, "end", error_msg)
            self.after(0, lambda: self.header_status_label.configure(text="服务异常"))

    def _adjust_widget_height(self, widget):
        # Adjust height of the textbox to fit its content
        # A small delay is sometimes needed for the widget to update its layout
        def _resize():
            requested = widget.winfo_reqheight()
            widget.configure(height=max(requested, 120))

        self.after(80, _resize)

    def _update_highlight_preview(self, ai_name: str, text: str) -> None:
        # AI预览区已移除，保留此方法以避免错误
        pass


    def clear_ai_answers(self):
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
        self.answer_widgets = {}
        self.highlight_populated = False
        if hasattr(self, "local_results_frame"):
            self.local_results_frame.configure(state="normal")
            self.local_results_frame.delete("1.0", "end")
            self.local_results_frame.insert("1.0", "本地：")
            self.local_results_frame.tag_add("title", "1.0", "1.3")
            self.local_results_frame.tag_config("title", foreground=self.theme.colors["accent"])
            self.local_results_frame.insert("end", "等待识别...")
            self.local_results_frame.configure(state="disabled")

    def update_question_text(self, text):
        self.question_text.delete(1.0, "end")
        # 添加标题前缀（标题颜色高亮）
        self.question_text.insert("1.0", "题目：")
        self.question_text.tag_add("title", "1.0", "1.3")
        self.question_text.tag_config("title", foreground=self.theme.colors["accent"])
        self.question_text.insert("end", text)

    def open_settings(self):
        if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
            self.settings_win.focus()
        else:
            self.settings_win = SettingsWindow(
                self,
                self.ai_manager,
                self.ocr_manager,
                self.save_settings,
                self.fonts,
                self.theme,
            )

    def load_settings(self):
        if os.path.exists(APP_CONFIG['SETTINGS_FILENAME']):
            try:
                with open(APP_CONFIG['SETTINGS_FILENAME'], "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.ai_manager.load_settings(settings.get("ai", {}))
                    self.ocr_manager.load_settings(settings.get("ocr", {}))
            except Exception as e:
                logging.error(f"Failed to load settings: {e}", exc_info=True)
                messagebox.showerror("错误", f"加载设置失败: {str(e)}")

    def save_settings(self):
        try:
            settings = {
                "ai": self.ai_manager.get_settings(),
                "ocr": self.ocr_manager.get_settings()
            }
            with open(APP_CONFIG['SETTINGS_FILENAME'], "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}", exc_info=True)
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def on_closing(self):
        try:
            self.progress_bar.stop()
        except Exception:
            pass
        self.screenshot_tool.cleanup()
        release = getattr(self.kb_manager, "release", None)
        if callable(release):
            release()
        self.answer_widgets.clear()
        self.destroy()

    def on_window_resize(self, event):
        """窗口大小变化时动态调整字体"""
        if event.widget != self:
            return

        current_height = self.winfo_height()
        if current_height < 100:  # 忽略初始化阶段
            return

        # 防抖：只有高度变化超过 50px 才更新字体
        if abs(current_height - self._last_height) > 50:
            scale = current_height / self.base_height
            self.update_fonts(scale)
            self._last_height = current_height

    def update_fonts(self, scale):
        """根据缩放因子更新字体"""
        try:
            self.fonts["title"].configure(size=int(25 * scale))
            self.fonts["subtitle"].configure(size=int(17 * scale))
            self.fonts["body"].configure(size=int(14 * scale))
            self.fonts["label"].configure(size=int(13 * scale))
            self.fonts["button"].configure(size=int(15 * scale))
            self.fonts["chip"].configure(size=int(12 * scale))
        except Exception as e:
            logging.warning(f"更新字体失败: {e}")

    def setup_logging(self):
        # 清除已有的handlers，确保配置生效
        logger = logging.getLogger()
        logger.handlers.clear()
        logger.setLevel(logging.INFO)

        # 配置日志：同时输出到文件和控制台
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 文件处理器
        file_handler = logging.FileHandler(APP_CONFIG['LOG_FILENAME'], encoding='utf-8', mode='a')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logging.info("=" * 60)
        logging.info("应用启动")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = QuestionAssistant()
    app.run()
