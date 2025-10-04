import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui import (
    Card,
    InfoTextBox,
    LabeledInput,
    NavigationRail,
    PrimaryButton,
    ScrollSection,
    SectionHeader,
    SecondaryButton,
    TertiaryButton,
    DEFAULT_THEME,
)

class SettingsWindow(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        ai_manager,
        ocr_manager,
        save_callback,
        fonts,
        theme=DEFAULT_THEME,
    ):
        super().__init__(parent)
        self.parent = parent
        self.ai_manager = ai_manager
        self.ocr_manager = ocr_manager
        self.save_callback = save_callback
        self.fonts = fonts
        self.theme = theme

        self.title("设置")
        self.geometry("1080x720")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=self.theme.colors["background"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 16))
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.navigation = NavigationRail(container, fonts=self.fonts, theme=self.theme)
        self.navigation.grid(row=0, column=0, sticky="nsw", padx=(0, 16))

        content_card = Card(container, theme=self.theme, padding=(18, 18))
        content_card.grid(row=0, column=1, sticky="nsew")
        self.content_area = content_card.content
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.ocr_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.ai_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.prompt_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")

        for frame in (self.ocr_frame, self.ai_frame, self.prompt_frame):
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)

        self.navigation.add_item("ocr", "OCR 设置", lambda: self.select_frame_by_name("ocr"))
        self.navigation.add_item("ai", "AI 设置", lambda: self.select_frame_by_name("ai"))
        self.navigation.add_item("prompt", "提示词设置", lambda: self.select_frame_by_name("prompt"))

        self.create_ocr_tab(self.ocr_frame)
        self.create_ai_tab(self.ai_frame)
        self.create_prompt_tab(self.prompt_frame)

        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        action_bar.grid_columnconfigure(0, weight=1)
        action_bar.grid_columnconfigure(1, weight=0)

        cancel_btn = SecondaryButton(
            action_bar,
            text="取消",
            command=self.destroy,
            fonts=self.fonts,
            theme=self.theme,
            width=120,
        )
        cancel_btn.grid(row=0, column=0, sticky="e", padx=(0, 8))

        save_btn = PrimaryButton(
            action_bar,
            text="保存",
            command=self.save_settings,
            fonts=self.fonts,
            theme=self.theme,
            width=120,
        )
        save_btn.grid(row=0, column=1, sticky="e")

        self.select_frame_by_name("ocr")

        self.center_window()
        self.load_current_settings()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1080 // 2)
        y = (self.winfo_screenheight() // 2) - (720 // 2)
        self.geometry(f"1080x720+{x}+{y}")

    def select_frame_by_name(self, name):
        frames = {
            "ocr": self.ocr_frame,
            "ai": self.ai_frame,
            "prompt": self.prompt_frame,
        }
        for key, frame in frames.items():
            if key == name:
                frame.grid()
            else:
                frame.grid_remove()
        self.navigation.select(name)

    def create_ocr_tab(self, ocr_frame):
        ocr_frame.grid_columnconfigure(0, weight=1)

        SectionHeader(
            ocr_frame,
            title="OCR 设置",
            description="选择识别引擎并配置相关参数",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        self.ocr_type_var = ctk.StringVar()
        ocr_type_row = LabeledInput(ocr_frame, label="OCR 类型", fonts=self.fonts, theme=self.theme)
        ocr_type_row.grid(row=1, column=0, sticky="ew", pady=(16, 12))
        self.ocr_type_menu = ctk.CTkComboBox(
            ocr_type_row.body,
            variable=self.ocr_type_var,
            values=("tesseract", "baidu"),
            command=self.on_ocr_type_change,
            state="readonly",
        )
        ocr_type_row.mount(self.ocr_type_menu)
        if not self.ocr_type_var.get():
            self.ocr_type_var.set("tesseract")

        self.tesseract_section = Card(ocr_frame, theme=self.theme, padding=(16, 16), variant="surface-soft")
        self.tesseract_section.grid(row=2, column=0, sticky="ew", pady=(8, 12))
        t_body = self.tesseract_section.content
        t_body.grid_columnconfigure(0, weight=1)

        SectionHeader(
            t_body,
            title="Tesseract 配置",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        self.tesseract_path_var = ctk.StringVar()
        path_row = LabeledInput(t_body, label="Tesseract-OCR 路径", fonts=self.fonts, theme=self.theme)
        path_row.grid(row=1, column=0, sticky="ew", pady=(12, 10))
        path_entry = ctk.CTkEntry(path_row.body, textvariable=self.tesseract_path_var)
        path_row.mount(path_entry)
        browse_btn = SecondaryButton(
            path_row.body,
            text="浏览",
            command=self.browse_tesseract_path,
            fonts=self.fonts,
            theme=self.theme,
            width=90,
            height=36,
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))

        self.language_var = ctk.StringVar()
        language_row = LabeledInput(t_body, label="识别语言", fonts=self.fonts, theme=self.theme)
        language_row.grid(row=2, column=0, sticky="ew")
        language_combo = ctk.CTkComboBox(
            language_row.body,
            variable=self.language_var,
            values=("chi_sim+eng", "chi_sim", "eng", "chi_tra", "jpn", "kor"),
            state="readonly",
        )
        language_row.mount(language_combo)

        self.baidu_section = Card(ocr_frame, theme=self.theme, padding=(16, 16), variant="surface-soft")
        self.baidu_section.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        b_body = self.baidu_section.content
        b_body.grid_columnconfigure(0, weight=1)

        SectionHeader(
            b_body,
            title="百度云 OCR",
            description="在线识别服务，需配置 API 凭据",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        self.baidu_api_key_var = ctk.StringVar()
        api_row = LabeledInput(b_body, label="API Key", fonts=self.fonts, theme=self.theme)
        api_row.grid(row=1, column=0, sticky="ew", pady=(12, 8))
        api_entry = ctk.CTkEntry(api_row.body, textvariable=self.baidu_api_key_var)
        api_row.mount(api_entry)

        self.baidu_secret_key_var = ctk.StringVar()
        secret_row = LabeledInput(b_body, label="Secret Key", fonts=self.fonts, theme=self.theme)
        secret_row.grid(row=2, column=0, sticky="ew")
        secret_entry = ctk.CTkEntry(secret_row.body, textvariable=self.baidu_secret_key_var, show="*")
        secret_row.mount(secret_entry)

        help_text = """OCR设置说明：
Tesseract-OCR（本地）：
- 下载地址：https://github.com/UB-Mannheim/tesseract/wiki
- 安装后选择 tesseract.exe 路径
- 支持多种语言，默认安装路径: C:\\Program Files\\Tesseract-OCR\\tesseract.exe

百度云OCR（在线）：
- 注册百度智能云账号：https://cloud.baidu.com/
- 获取 API Key 与 Secret Key
- 识别准确率高，每月有免费额度，需要网络连接

注意：首次使用时请先配置 OCR 选项！"""

        help_label = ctk.CTkLabel(
            ocr_frame,
            text=help_text,
            justify="left",
            font=self.fonts["label"],
            text_color=self.theme.colors["text_muted"],
        )
        help_label.grid(row=4, column=0, sticky="w", pady=(4, 0))

    def on_ocr_type_change(self, choice):
        if choice == "tesseract":
            self.tesseract_section.grid()
            self.baidu_section.grid_remove()
        elif choice == "baidu":
            self.tesseract_section.grid_remove()
            self.baidu_section.grid()
        else:
            self.tesseract_section.grid()
            self.baidu_section.grid()

    def create_ai_tab(self, ai_frame):
        ai_frame.grid_columnconfigure(0, weight=1)
        ai_frame.grid_rowconfigure(1, weight=1)

        SectionHeader(
            ai_frame,
            title="AI 服务",
            description="管理启用的 AI 服务与模型配置",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        list_card = Card(ai_frame, theme=self.theme, padding=(16, 16))
        list_card.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        list_card.content.grid_columnconfigure(0, weight=1)
        list_card.content.grid_rowconfigure(0, weight=1)

        self.ai_list_frame = ScrollSection(list_card.content, theme=self.theme)
        self.ai_list_frame.grid(row=0, column=0, sticky="nsew")

        button_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(4, weight=1)

        add_btn = PrimaryButton(
            button_frame,
            text="添加AI",
            command=self.add_ai_config,
            fonts=self.fonts,
            theme=self.theme,
            width=120,
        )
        add_btn.grid(row=0, column=0, padx=(0, 8), pady=(0, 4))

        self.edit_btn = SecondaryButton(
            button_frame,
            text="编辑AI",
            command=self.edit_ai_config,
            fonts=self.fonts,
            theme=self.theme,
            state="disabled",
            width=120,
        )
        self.edit_btn.grid(row=0, column=1, padx=(0, 8), pady=(0, 4))

        self.delete_btn = SecondaryButton(
            button_frame,
            text="删除AI",
            command=self.delete_ai_config,
            fonts=self.fonts,
            theme=self.theme,
            state="disabled",
            width=120,
        )
        self.delete_btn.grid(row=0, column=2, padx=(0, 8), pady=(0, 4))

        self.test_btn = TertiaryButton(
            button_frame,
            text="测试连接",
            command=self.test_ai_config,
            fonts=self.fonts,
            theme=self.theme,
            state="disabled",
            width=120,
        )
        self.test_btn.grid(row=0, column=3, padx=(0, 8), pady=(0, 4))

        self.selected_ai_name = None
        self.ai_item_widgets = {}

    def create_prompt_tab(self, prompt_frame):
        prompt_frame.grid_columnconfigure(0, weight=1)
        prompt_frame.grid_rowconfigure(1, weight=1)

        SectionHeader(
            prompt_frame,
            title="系统提示词",
            description="自定义 AI 回答的语气与格式",
            fonts=self.fonts,
            theme=self.theme,
        ).grid(row=0, column=0, sticky="w")

        self.prompt_text = InfoTextBox(
            prompt_frame,
            fonts=self.fonts,
            theme=self.theme,
            height=360,
        )
        self.prompt_text.grid(row=1, column=0, sticky="nsew", pady=(12, 12))

        reset_btn = SecondaryButton(
            prompt_frame,
            text="重置为默认",
            command=self.reset_prompt,
            fonts=self.fonts,
            theme=self.theme,
            width=140,
        )
        reset_btn.grid(row=2, column=0, sticky="w")

    def browse_tesseract_path(self):
        filename = filedialog.askopenfilename(
            title="选择tesseract.exe",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.tesseract_path_var.set(filename)

    def add_ai_config(self):
        AIConfigDialog(self, self.ai_manager, callback=self.refresh_ai_list)

    def edit_ai_config(self):
        if not self.selected_ai_name:
            messagebox.showwarning("警告", "请先选择要编辑的AI配置")
            return
        AIConfigDialog(self, self.ai_manager, ai_name=self.selected_ai_name, callback=self.refresh_ai_list)

    def delete_ai_config(self):
        if not self.selected_ai_name:
            messagebox.showwarning("警告", "请先选择要删除的AI配置")
            return
        if messagebox.askyesno("确认", f"确定要删除AI配置 '{self.selected_ai_name}' 吗？"):
            self.ai_manager.remove_ai_config(self.selected_ai_name)
            self.refresh_ai_list()

    def test_ai_config(self):
        if not self.selected_ai_name:
            messagebox.showwarning("警告", "请先选择要测试的AI配置")
            return
        messagebox.showinfo("测试", f"测试功能待实现：{self.selected_ai_name}")

    def refresh_ai_list(self):
        for widget in self.ai_list_frame.winfo_children():
            widget.destroy()

        self.ai_item_widgets = {}

        ai_configs = self.ai_manager.get_settings().get('configs', {})
        if not isinstance(ai_configs, dict):
            messagebox.showerror("错误", "AI配置格式错误")
            return

        sorted_names = sorted(ai_configs.keys())
        for name in sorted_names:
            config = ai_configs[name]
            if not isinstance(config, dict):
                continue
            
            enabled = "是" if config.get("enabled", False) else "否"
            ai_type = config.get("type", "未知")
            
            card = Card(self.ai_list_frame, theme=self.theme, padding=(12, 12), variant="surface-soft")
            card.pack(fill="x", pady=6)
            body = card.content
            body.grid_columnconfigure(0, weight=1)

            title_label = ctk.CTkLabel(
                body,
                text=name,
                font=self.fonts["subtitle"],
                text_color=self.theme.colors["text_primary"],
            )
            title_label.grid(row=0, column=0, sticky="w")

            status_text = f"类型：{ai_type}    已启用：{enabled}"
            status_color = self.theme.colors["accent"] if enabled == "是" else self.theme.colors["text_muted"]
            status_label = ctk.CTkLabel(
                body,
                text=status_text,
                font=self.fonts["label"],
                text_color=status_color,
            )
            status_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

            for widget in (card, body, title_label, status_label):
                widget.bind("<Button-1>", lambda _event, n=name: self.on_ai_select(n))

            self.ai_item_widgets[name] = (card, title_label, status_label)

        self.on_ai_select(None)

    def on_ai_select(self, ai_name):
        self.selected_ai_name = ai_name
        for name, widgets in getattr(self, "ai_item_widgets", {}).items():
            card, title_label, status_label = widgets
            if name == ai_name:
                card.configure(fg_color=self.theme.colors["accent_muted"])
                title_label.configure(text_color="white")
                status_label.configure(text_color="white")
            else:
                card.configure(fg_color=self.theme.colors["surface_soft"])
                title_label.configure(text_color=self.theme.colors["text_primary"])
                config = self.ai_manager.get_ai_config(name) or {}
                enabled = config.get("enabled", False)
                status_color = self.theme.colors["accent"] if enabled else self.theme.colors["text_muted"]
                status_label.configure(text_color=status_color)

        state = "normal" if ai_name else "disabled"
        self.edit_btn.configure(state=state)
        self.delete_btn.configure(state=state)
        self.test_btn.configure(state=state)

    def reset_prompt(self):
        default_prompt = """你是一个专业的问题回答助手。请根据用户提供的题目，给出准确、详细的答案。
        
要求：
1. 回答要简重点突出
2. 如果是选择题，请明确指出正确答案
3. 如果是计算题，请提供详细的解题步骤
4. 如果是概念题，请给出准确的定义和解释
5. 回答要有逻辑性，条理清晰

请直接回答问题，不需要额外的寒暄。"""
        self.prompt_text.delete(1.0, "end")
        self.prompt_text.insert(1.0, default_prompt)

    def load_current_settings(self):
        ocr_settings = self.ocr_manager.get_settings()
        self.ocr_type_var.set(ocr_settings.get("type", "tesseract"))
        self.tesseract_path_var.set(ocr_settings.get("tesseract_path", ""))
        self.language_var.set(ocr_settings.get("language", "chi_sim+eng"))
        self.baidu_api_key_var.set(ocr_settings.get("baidu_api_key", ""))
        self.baidu_secret_key_var.set(ocr_settings.get("baidu_secret_key", ""))
        self.on_ocr_type_change(self.ocr_type_var.get())

        self.refresh_ai_list()

        ai_settings = self.ai_manager.get_settings()
        self.prompt_text.delete(1.0, "end")
        self.prompt_text.insert(1.0, ai_settings.get("system_prompt", self.ai_manager.DEFAULT_PROMPT))

    def save_settings(self):
        try:
            ocr_type = self.ocr_type_var.get()
            ocr_settings = {"type": ocr_type}
            if ocr_type == 'tesseract':
                ocr_settings["tesseract_path"] = self.tesseract_path_var.get()
                ocr_settings["language"] = self.language_var.get()
            elif ocr_type == 'baidu':
                ocr_settings["baidu_api_key"] = self.baidu_api_key_var.get()
                ocr_settings["baidu_secret_key"] = self.baidu_secret_key_var.get()
            self.ocr_manager.load_settings(ocr_settings)

            ai_settings = self.ai_manager.get_settings()
            ai_settings["system_prompt"] = self.prompt_text.get(1.0, "end-1c").strip()
            self.ai_manager.load_settings(ai_settings)

            if self.save_callback:
                self.save_callback()

            messagebox.showinfo("成功", "设置已保存")
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

class AIConfigDialog(ctk.CTkToplevel):
    def __init__(self, parent, ai_manager, ai_name=None, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.ai_manager = ai_manager
        self.ai_name = ai_name
        self.callback = callback
        self.is_edit = ai_name is not None
        self.original_name = ai_name

        self.title("编辑AI配置" if self.is_edit else "添加AI配置")
        self.geometry("550x600")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.init_variables()
        self.create_widgets()

        if self.is_edit:
            self.load_config()
        
        self.center_dialog()

    def init_variables(self):
        self.name_var = ctk.StringVar()
        self.type_var = ctk.StringVar(value="openai")
        self.api_key_var = ctk.StringVar()
        self.base_url_var = ctk.StringVar()
        self.max_tokens_var = ctk.StringVar(value="2000")
        self.enabled_var = ctk.BooleanVar(value=True)
        self.type_var.trace_add("write", self.on_type_change)

    def center_dialog(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"550x600+{x}+{y}")

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)

        row = 0
        ctk.CTkLabel(main_frame, text="AI名称: *").grid(row=row, column=0, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.name_var).grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        ctk.CTkLabel(main_frame, text="AI类型: *").grid(row=row, column=0, sticky="w")
        ctk.CTkComboBox(main_frame, variable=self.type_var, values=('openai', 'doubao', 'siliconflow', 'custom'), state='readonly').grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        ctk.CTkLabel(main_frame, text="API密钥: *").grid(row=row, column=0, sticky="w")
        key_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        key_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        self.api_key_entry = ctk.CTkEntry(key_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.pack(side="left", fill="x", expand=True)
        self.show_key_btn = ctk.CTkButton(key_frame, text="显示", width=60, command=self.toggle_key_visibility)
        self.show_key_btn.pack(side="left", padx=(5, 0))

        row += 1
        ctk.CTkLabel(main_frame, text="模型:").grid(row=row, column=0, sticky="w")
        self.model_combo = ctk.CTkComboBox(main_frame)
        self.model_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        ctk.CTkLabel(main_frame, text="API地址:").grid(row=row, column=0, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.base_url_var).grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        ctk.CTkLabel(main_frame, text="最大令牌数:").grid(row=row, column=0, sticky="w")
        ctk.CTkEntry(main_frame, textvariable=self.max_tokens_var).grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        row += 1
        ctk.CTkSwitch(main_frame, text="启用此AI", variable=self.enabled_var).grid(row=row, column=1, sticky="w", padx=5, pady=10)

        row += 1
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, sticky="e", pady=10)
        ctk.CTkButton(button_frame, text="保存", command=self.save_config).pack(side="right")
        ctk.CTkButton(button_frame, text="取消", command=self.on_close, fg_color="gray").pack(side="right", padx=5)
        
        self.update_model_list()

    def toggle_key_visibility(self):
        if self.api_key_entry.cget('show') == '*':
            self.api_key_entry.configure(show='')
            self.show_key_btn.configure(text='隐藏')
        else:
            self.api_key_entry.configure(show='*')
            self.show_key_btn.configure(text='显示')

    def update_model_list(self, *args):
        ai_type = self.type_var.get()
        if ai_type == "openai":
            models = [
                'gpt-4-turbo-preview', 'gpt-4-vision-preview', 'gpt-4',
                'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
            ]
            base_url = 'https://api.openai.com/v1'
            model = 'gpt-3.5-turbo'
        elif ai_type == "doubao":
            models = ['doubao-pro-32k', 'doubao-pro-4k']
            base_url = 'https://ark.cn-beijing.volces.com/api/v3'
            model = 'doubao-pro-4k'
        elif ai_type == "siliconflow":
            models = ['alibaba/Qwen2-72B-Instruct']
            base_url = 'https://api.siliconflow.cn/v1'
            model = 'alibaba/Qwen2-72B-Instruct'
        else:
            models = []
            base_url = ''
            model = ''
        
        self.model_combo.configure(values=models)
        if not self.model_combo.get():
            self.model_combo.set(model)
        if not self.base_url_var.get():
            self.base_url_var.set(base_url)

    def on_type_change(self, *args):
        self.base_url_var.set("")
        self.model_combo.set("")
        self.update_model_list()

    def load_config(self):
        config = self.ai_manager.get_ai_config(self.ai_name)
        if not config:
            messagebox.showerror("错误", f"找不到AI配置: {self.ai_name}")
            self.destroy()
            return
        self.name_var.set(self.ai_name)
        self.type_var.set(config.get("type", "openai"))
        self.api_key_var.set(config.get("api_key", ""))
        self.model_combo.set(config.get("model", ""))
        self.base_url_var.set(config.get("base_url", ""))
        self.max_tokens_var.set(str(config.get("max_tokens", "2000")))
        self.enabled_var.set(config.get("enabled", False))
        self.update_model_list()

    def on_close(self):
        if messagebox.askyesno("确认", "确定要关闭吗？未保存的更改将会丢失。"):
            self.destroy()

    def validate_config(self):
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("请输入AI名称")
        if not self.is_edit and name in self.ai_manager.ai_configs:
            raise ValueError(f"AI名称 '{name}' 已存在")
        if not self.api_key_var.get().strip():
            raise ValueError("请输入API密钥")
        if not self.model_combo.get().strip():
            raise ValueError("请选择或输入模型名称")
        return name

    def save_config(self):
        try:
            name = self.validate_config()
            config = {
                "type": self.type_var.get().lower(),
                "api_key": self.api_key_var.get().strip(),
                "model": self.model_combo.get().strip(),
                "enabled": self.enabled_var.get(),
                "base_url": self.base_url_var.get().strip(),
                "max_tokens": int(self.max_tokens_var.get().strip())
            }
            if self.is_edit and name != self.original_name:
                self.ai_manager.remove_ai_config(self.original_name)
            self.ai_manager.add_ai_config(name, config)
            if self.callback:
                self.callback()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
