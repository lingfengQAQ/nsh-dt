import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
from screenshot_tool import ScreenshotTool
from ai_manager import AIManager
from ocr_manager import OCRManager
from settings_window import SettingsWindow
from knowledge_base_manager import KnowledgeBaseManager

class QuestionAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("问题回答助手")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.screenshot_tool = ScreenshotTool(self)
        self.ai_manager = AIManager()
        self.ocr_manager = OCRManager()
        self.kb_manager = KnowledgeBaseManager()
        
        # 加载设置
        self.load_settings()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="问题回答助手", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 截图按钮
        self.screenshot_btn = ttk.Button(
            button_frame, 
            text="打开截图区域", 
            command=self.toggle_screenshot_area
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 截图并识别按钮
        self.capture_btn = ttk.Button(
            button_frame, 
            text="截图并识别", 
            command=self.capture_and_recognize,
            state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 设置按钮
        settings_btn = ttk.Button(
            button_frame, 
            text="设置", 
            command=self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="识别结果和AI回答", padding="10")
        result_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # 识别的题目文本
        ttk.Label(result_frame, text="识别的题目:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.question_text = tk.Text(result_frame, height=4, wrap=tk.WORD)
        self.question_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 滚动条
        question_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.question_text.yview)
        question_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 10))
        self.question_text.configure(yscrollcommand=question_scrollbar.set)
        
        # AI回答区域
        ttk.Label(result_frame, text="AI回答:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 创建一个框架来垂直显示多个AI的回答
        self.answers_frame = ttk.Frame(result_frame)
        self.answers_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.rowconfigure(3, weight=2)
        self.answers_frame.columnconfigure(0, weight=1)
        
        # 用来存储AI回答控件的字典
        self.answer_widgets = {}
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def toggle_screenshot_area(self):
        """切换截图区域显示/隐藏"""
        if self.screenshot_tool.is_active:
            self.screenshot_tool.hide_overlay()
            self.screenshot_btn.config(text="打开截图区域")
            self.capture_btn.config(state=tk.DISABLED)
        else:
            self.screenshot_tool.show_overlay()
            self.screenshot_btn.config(text="隐藏截图区域")
            self.capture_btn.config(state=tk.NORMAL)
            
    def capture_and_recognize(self):
        """截图并识别题目"""
        self.status_var.set("正在截图...")
        self.root.update()
        
        # 在新线程中执行截图和识别
        threading.Thread(target=self._capture_and_recognize_thread, daemon=True).start()
        
    def _capture_and_recognize_thread(self):
        """截图和识别的线程函数"""
        try:
            # 获取截图
            image = self.screenshot_tool.capture_area()
            if image is None:
                self.root.after(0, lambda: self.status_var.set("截图失败"))
                return
                
            self.root.after(0, lambda: self.status_var.set("正在识别文字..."))
            
            # OCR识别
            question_text = self.ocr_manager.extract_text(image)
            if not question_text.strip():
                self.root.after(0, lambda: self.status_var.set("未识别到文字"))
                return
                
            # 更新界面显示识别结果
            self.root.after(0, lambda: self.update_question_text(question_text))
            
            # 清空之前的回答
            self.root.after(0, self.clear_ai_answers)
            
            # 检查是否为“找诗词”的特定问题
            trigger_phrase = "请从以下字中选出一句诗词"
            is_poem_task = trigger_phrase in question_text
            
            # 启动AI回答
            self.root.after(0, lambda: self.status_var.set("正在获取AI及本地回答..."))
            self.get_all_answers_parallel(question_text, image, is_poem_task)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.status_var.set(f"错误: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误:\n{error_msg}"))

    def get_all_answers_parallel(self, question_text, image, is_poem_task):
        """并行获取所有AI和本地知识库的回答"""
        
        # 1. 启动本地知识库搜索（如果适用）
        if is_poem_task:
            self.create_answer_frame("本地知识库", 0) # 预先创建框架
            trigger_phrase = "请从以下字中选出一句诗词"
            chars_to_find = question_text.replace(trigger_phrase, "").strip()
            threading.Thread(
                target=self._find_poem_locally, 
                args=(chars_to_find,), 
                daemon=True
            ).start()

        # 2. 启动所有启用的AI服务
        enabled_ais = self.ai_manager.get_enabled_ais()
        ai_to_process = dict(list(enabled_ais.items())[:3])

        if not ai_to_process and not is_poem_task:
            self.root.after(0, lambda: self.status_var.set("未配置或启用任何服务"))
            self.root.after(0, lambda: messagebox.showwarning("警告", "请先在设置中启用至少一个AI服务"))
            return

        # 为每个AI创建显示区域并获取回答
        # 如果是诗词任务，AI框架的索引要向后移
        start_index = 1 if is_poem_task else 0
        for i, (ai_name, config) in enumerate(ai_to_process.items(), start=start_index):
            self.create_answer_frame(ai_name, i)
            threading.Thread(
                target=self._get_single_ai_answer,
                args=(ai_name, config, question_text, image),
                daemon=True
            ).start()

    def _find_poem_locally(self, chars):
        """在本地知识库中查找诗句的线程函数。"""
        try:
            results = self.kb_manager.find_poem_from_chars(chars)
            self.root.after(0, lambda: self.update_local_answer_frame(results))
        except Exception as e:
            error_msg = f"本地搜索出错: {str(e)}"
            self.root.after(0, lambda: self.update_answer_frame("本地知识库", error_msg))

    def clear_ai_answers(self):
        """清空所有AI回答框架"""
        for widget in self.answers_frame.winfo_children():
            widget.destroy()
        self.answer_widgets = {}
            
    def update_question_text(self, text):
        """更新识别的题目文本"""
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, text)

    def create_answer_frame(self, name, index):
        """为回答创建垂直排列的框架"""
        answer_frame = ttk.LabelFrame(self.answers_frame, text=name, padding="5")
        answer_frame.grid(row=index, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.answers_frame.rowconfigure(index, weight=1)
        answer_frame.columnconfigure(0, weight=1)
        answer_frame.rowconfigure(0, weight=1)

        text_widget = tk.Text(answer_frame, wrap=tk.WORD, state=tk.DISABLED, height=5)
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 为粗体高亮配置tag
        text_widget.tag_configure("bold", font=("Arial", 10, "bold"))

        scrollbar = ttk.Scrollbar(answer_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.config(state=tk.NORMAL)
        text_widget.insert(1.0, "正在获取回答...")
        text_widget.config(state=tk.DISABLED)

        self.answer_widgets[name] = text_widget
        
    def update_answer_frame(self, name, answer):
        """更新回答框架的内容（通用）"""
        if name in self.answer_widgets:
            text_widget = self.answer_widgets[name]
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, answer)
            text_widget.config(state=tk.DISABLED)
        self.check_all_tasks_done()

    def update_local_answer_frame(self, results):
        """专门更新本地知识库的回答框架，支持高亮"""
        name = "本地知识库"
        if name not in self.answer_widgets:
            return

        text_widget = self.answer_widgets[name]
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)

        if not results:
            text_widget.insert(1.0, "本地知识库中未找到匹配的诗词。")
        else:
            for i, (poem, matched_clauses) in enumerate(results):
                # 插入标题和作者
                title = poem.get('title', '无题')
                author = poem.get('author', '佚名')
                text_widget.insert(tk.END, f"《{title}》 - {author}\n")
                
                # 插入诗歌内容并高亮
                content = poem.get('content', [])
                for line in content:
                    # 检查当前行是否包含任何一个匹配的诗句
                    is_matched_line = any(clause in line for clause in matched_clauses)
                    if is_matched_line:
                        text_widget.insert(tk.END, line + "\n", "bold")
                    else:
                        text_widget.insert(tk.END, line + "\n")
                
                # 在多首诗之间添加分隔符
                if i < len(results) - 1:
                    text_widget.insert(tk.END, "\n" + "="*20 + "\n\n")

        text_widget.config(state=tk.DISABLED)
        self.check_all_tasks_done()

    def check_all_tasks_done(self):
        """检查是否所有任务都已完成"""
        all_done = all(
            widget.get(1.0, tk.END).strip() != "正在获取回答..."
            for widget in self.answer_widgets.values()
        )
        if all_done:
            self.status_var.set("所有任务已完成")

    def _get_single_ai_answer(self, ai_name, config, question_text, image):
        """获取单个AI的回答"""
        try:
            answer = self.ai_manager.get_answer(ai_name, config, question_text, image)
            self.root.after(0, lambda: self.update_answer_frame(ai_name, answer))
        except Exception as e:
            error_msg = f"获取{ai_name}回答时出错: {str(e)}"
            self.root.after(0, lambda: self.update_answer_frame(ai_name, error_msg))
        
    def open_settings(self):
        """打开设置窗口"""
        SettingsWindow(self.root, self.ai_manager, self.ocr_manager, self.save_settings)
        
    def load_settings(self):
        """加载设置"""
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.ai_manager.load_settings(settings.get("ai", {}))
                    self.ocr_manager.load_settings(settings.get("ocr", {}))
            except Exception as e:
                messagebox.showerror("错误", f"加载设置失败: {str(e)}")
                
    def save_settings(self):
        """保存设置"""
        try:
            settings = {
                "ai": self.ai_manager.get_settings(),
                "ocr": self.ocr_manager.get_settings()
            }
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
            
    def on_closing(self):
        """程序关闭时的处理"""
        self.screenshot_tool.cleanup()
        self.root.destroy()
        
    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = QuestionAssistant()
    app.run()
