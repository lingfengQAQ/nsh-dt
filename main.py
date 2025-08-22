import customtkinter as ctk
from tkinter import messagebox
import threading
import json
import os
import logging
from screenshot_tool import ScreenshotTool
from ai_manager import AIManager
from ocr_manager import OCRManager
from settings_window import SettingsWindow
from knowledge_base_manager import KnowledgeBaseManager

class QuestionAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("问题回答助手")
        self.geometry("800x600")
        self.resizable(True, True)

        self.setup_logging()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.screenshot_tool = ScreenshotTool(self)
        self.ai_manager = AIManager()
        self.ocr_manager = OCRManager()
        self.kb_manager = KnowledgeBaseManager()

        self.load_settings()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(top_frame, text="问题回答助手")
        title_label.grid(row=0, column=0, sticky="w")

        button_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        self.screenshot_btn = ctk.CTkButton(button_frame, text="打开截图区域", command=self.toggle_screenshot_area)
        self.screenshot_btn.pack(side="left", padx=(0, 10))

        self.capture_btn = ctk.CTkButton(button_frame, text="截图并识别", command=self.capture_and_recognize, state="disabled")
        self.capture_btn.pack(side="left", padx=(0, 10))

        settings_btn = ctk.CTkButton(button_frame, text="设置", command=self.open_settings)
        settings_btn.pack(side="left")

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        question_frame = ctk.CTkFrame(main_frame)
        question_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        question_frame.grid_columnconfigure(0, weight=1)
        question_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(question_frame, text="识别的题目:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.question_text = ctk.CTkTextbox(question_frame, wrap="word")
        self.question_text.grid(row=1, column=0, sticky="nsew")

        answers_frame_container = ctk.CTkFrame(main_frame)
        answers_frame_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        answers_frame_container.grid_columnconfigure(0, weight=1)
        answers_frame_container.grid_rowconfigure(0, weight=1)

        self.answers_text = ctk.CTkTextbox(answers_frame_container, wrap="word")
        self.answers_text.grid(row=0, column=0, sticky="nsew")
        self.answers_text.tag_config("bold")

        self.status_var = ctk.StringVar(value="就绪")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 5))

    def toggle_screenshot_area(self):
        if self.screenshot_tool.is_active:
            self.screenshot_tool.hide_overlay()
            self.screenshot_btn.configure(text="打开截图区域")
            self.capture_btn.configure(state="disabled")
        else:
            self.screenshot_tool.show_overlay()
            self.screenshot_btn.configure(text="隐藏截图区域")
            self.capture_btn.configure(state="normal")

    def capture_and_recognize(self):
        self.status_var.set("正在截图...")
        self.update()
        threading.Thread(target=self._capture_and_recognize_thread, daemon=True).start()

    def _capture_and_recognize_thread(self):
        try:
            image = self.screenshot_tool.capture_area()
            if image is None:
                self.after(0, lambda: self.status_var.set("截图失败"))
                return

            enabled_ais = self.ai_manager.get_enabled_ais()
            has_vision_model = any(config.get("model") in self.ai_manager.vision_models for config in enabled_ais.values())

            question_text = ""
            if not has_vision_model:
                self.after(0, lambda: self.status_var.set("正在识别文字..."))
                ocr_thread = threading.Thread(target=self._ocr_thread, args=(image,), daemon=True)
                ocr_thread.start()
                return

            self.after(0, self.clear_ai_answers)
            trigger_phrase = "请从以下字中选出一句诗词"
            is_poem_task = trigger_phrase in question_text
            self.after(0, lambda: self.status_var.set("正在获取AI及本地回答..."))
            self.get_all_answers_parallel(question_text, image, is_poem_task)
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in capture and recognize thread: {e}", exc_info=True)
            self.after(0, lambda: self.status_var.set(f"错误: {error_msg}"))
            self.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误:\n{error_msg}"))

    def _ocr_thread(self, image):
        try:
            question_text = self.ocr_manager.extract_text(image)
            if not question_text.strip():
                self.after(0, lambda: self.status_var.set("未识别到文字"))
                return
            self.after(0, lambda: self.update_question_text(question_text))
            self.after(0, self.clear_ai_answers)
            trigger_phrase = "请从以下字中选出一句诗词"
            is_poem_task = trigger_phrase in question_text
            self.after(0, lambda: self.status_var.set("正在获取AI及本地回答..."))
            self.get_all_answers_parallel(question_text, image, is_poem_task)
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in OCR thread: {e}", exc_info=True)
            self.after(0, lambda: self.status_var.set(f"错误: {error_msg}"))
            self.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误:\n{error_msg}"))

    def get_all_answers_parallel(self, question_text, image, is_poem_task):
        self.answers_text.delete(1.0, "end")
        
        threads = []
        if is_poem_task:
            trigger_phrase = "请从以下字中选出一句诗词"
            chars_to_find = question_text.replace(trigger_phrase, "").strip()
            thread = threading.Thread(target=self._find_poem_locally, args=(chars_to_find,), daemon=True)
            threads.append(thread)
            thread.start()

        enabled_ais = self.ai_manager.get_enabled_ais()
        ai_to_process = dict(list(enabled_ais.items())[:3])

        if not ai_to_process and not is_poem_task:
            self.after(0, lambda: self.status_var.set("未配置或启用任何服务"))
            self.after(0, lambda: messagebox.showwarning("警告", "请先在设置中启用至少一个AI服务"))
            return

        for ai_name, config in ai_to_process.items():
            thread = threading.Thread(target=self._get_single_ai_answer, args=(ai_name, config, question_text, image), daemon=True)
            threads.append(thread)
            thread.start()

    def _find_poem_locally(self, chars):
        try:
            results = self.kb_manager.find_poem_from_chars(chars)
            self.after(0, lambda: self.update_answers_text("本地知识库", results, is_poem=True))
        except Exception as e:
            error_msg = f"本地搜索出错: {str(e)}"
            logging.error(f"Error finding poem locally: {e}", exc_info=True)
            self.after(0, lambda: self.update_answers_text("本地知识库", error_msg))

    def clear_ai_answers(self):
        self.answers_text.delete(1.0, "end")

    def update_question_text(self, text):
        self.question_text.delete(1.0, "end")
        self.question_text.insert(1.0, text)


    def update_answers_text(self, name, answer, is_poem=False):
        self.answers_text.insert("end", f"{name}: ", "bold")
        if is_poem:
            if not answer:
                self.answers_text.insert("end", "本地知识库中未找到匹配的诗词。\n\n")
            else:
                for i, (poem, matched_clauses) in enumerate(answer):
                    title = poem.get('title', '无题')
                    author = poem.get('author', '佚名')
                    self.answers_text.insert("end", f"《{title}》 - {author}\n")
                    content = poem.get('content', [])
                    for line in content:
                        is_matched_line = any(clause in line for clause in matched_clauses)
                        if is_matched_line:
                            self.answers_text.insert("end", line + "\n", "bold")
                        else:
                            self.answers_text.insert("end", line + "\n")
                    if i < len(answer) - 1:
                        self.answers_text.insert("end", "\n" + "="*20 + "\n\n")
        else:
            self.answers_text.insert("end", f"{answer}\n\n")

    def check_if_all_threads_done(self, threads):
        if not any(t.is_alive() for t in threads):
            self.status_var.set("所有任务已完成")

    def _get_single_ai_answer(self, ai_name, config, question_text, image):
        try:
            stream = self.ai_manager.get_answer(ai_name, config, question_text, image)
            self.after(0, lambda: self.answers_text.insert("end", f"{ai_name}: ", "bold"))
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                self.after(0, lambda c=content: self.answers_text.insert("end", c))
            self.after(0, lambda: self.answers_text.insert("end", "\n\n"))
        except Exception as e:
            error_msg = f"获取{ai_name}回答时出错: {str(e)}"
            logging.error(f"Error getting answer from {ai_name}: {e}", exc_info=True)
            self.after(0, lambda: self.update_answers_text(ai_name, error_msg))

    def open_settings(self):
        if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
            self.settings_win.focus()
        else:
            self.settings_win = SettingsWindow(self, self.ai_manager, self.ocr_manager, self.save_settings)

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
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
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}", exc_info=True)
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def on_closing(self):
        self.screenshot_tool.cleanup()
        self.destroy()

    def setup_logging(self):
        logging.basicConfig(filename='app.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = QuestionAssistant()
    app.run()
