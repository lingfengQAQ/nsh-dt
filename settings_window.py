import customtkinter as ctk
from tkinter import messagebox, filedialog
from ai_manager import AIManager

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, ai_manager, ocr_manager, save_callback):
        super().__init__(parent)
        self.parent = parent
        self.ai_manager = ai_manager
        self.ocr_manager = ocr_manager
        self.save_callback = save_callback

        self.title("设置")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="设置")
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.ocr_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                        text="OCR 设置", fg_color="transparent", text_color=("gray10", "gray90"),
                                        hover_color=("gray70", "gray30"),
                                        anchor="w", command=self.ocr_button_event)
        self.ocr_button.grid(row=1, column=0, sticky="ew")

        self.ai_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                       text="AI 设置", fg_color="transparent", text_color=("gray10", "gray90"),
                                       hover_color=("gray70", "gray30"),
                                       anchor="w", command=self.ai_button_event)
        self.ai_button.grid(row=2, column=0, sticky="ew")

        self.prompt_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                           text="提示词设置", fg_color="transparent", text_color=("gray10", "gray90"),
                                           hover_color=("gray70", "gray30"),
                                           anchor="w", command=self.prompt_button_event)
        self.prompt_button.grid(row=3, column=0, sticky="ew")

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        save_btn = ctk.CTkButton(button_frame, text="保存", command=self.save_settings)
        save_btn.pack(side="right", padx=(0, 10))

        cancel_btn = ctk.CTkButton(button_frame, text="取消", command=self.destroy, fg_color="gray")
        cancel_btn.pack(side="right")

        self.ocr_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.ai_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.prompt_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.create_ocr_tab(self.ocr_frame)
        self.create_ai_tab(self.ai_frame)
        self.create_prompt_tab(self.prompt_frame)

        self.select_frame_by_name("ocr")
        
        self.center_window()
        self.load_current_settings()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")

    def select_frame_by_name(self, name):
        self.ocr_button.configure(fg_color=("gray75", "gray25") if name == "ocr" else "transparent")
        self.ai_button.configure(fg_color=("gray75", "gray25") if name == "ai" else "transparent")
        self.prompt_button.configure(fg_color=("gray75", "gray25") if name == "prompt" else "transparent")

        if name == "ocr":
            self.ocr_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        else:
            self.ocr_frame.grid_forget()
        if name == "ai":
            self.ai_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        else:
            self.ai_frame.grid_forget()
        if name == "prompt":
            self.prompt_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        else:
            self.prompt_frame.grid_forget()

    def ocr_button_event(self):
        self.select_frame_by_name("ocr")

    def ai_button_event(self):
        self.select_frame_by_name("ai")

    def prompt_button_event(self):
        self.select_frame_by_name("prompt")

    def create_ocr_tab(self, ocr_frame):
        ocr_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(ocr_frame, text="OCR 类型:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.ocr_type_var = ctk.StringVar()
        ocr_type_combo = ctk.CTkComboBox(ocr_frame, variable=self.ocr_type_var, values=('tesseract', 'baidu'), command=self.on_ocr_type_change)
        ocr_type_combo.grid(row=1, column=0, sticky="w", pady=(0, 15))

        self.tesseract_frame = ctk.CTkFrame(ocr_frame)
        self.tesseract_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.tesseract_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.tesseract_frame, text="Tesseract-OCR 路径:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        path_frame = ctk.CTkFrame(self.tesseract_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        path_frame.grid_columnconfigure(0, weight=1)
        self.tesseract_path_var = ctk.StringVar()
        path_entry = ctk.CTkEntry(path_frame, textvariable=self.tesseract_path_var)
        path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        browse_btn = ctk.CTkButton(path_frame, text="浏览", command=self.browse_tesseract_path, width=80)
        browse_btn.grid(row=0, column=1)

        ctk.CTkLabel(self.tesseract_frame, text="识别语言:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.language_var = ctk.StringVar()
        language_combo = ctk.CTkComboBox(self.tesseract_frame, variable=self.language_var, values=('chi_sim+eng', 'chi_sim', 'eng', 'chi_tra', 'jpn', 'kor'))
        language_combo.grid(row=3, column=0, sticky="w", pady=(0, 10))

        self.baidu_frame = ctk.CTkFrame(ocr_frame)
        self.baidu_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.baidu_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.baidu_frame, text="API Key:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.baidu_api_key_var = ctk.StringVar()
        ctk.CTkEntry(self.baidu_frame, textvariable=self.baidu_api_key_var).grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(self.baidu_frame, text="Secret Key:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.baidu_secret_key_var = ctk.StringVar()
        ctk.CTkEntry(self.baidu_frame, textvariable=self.baidu_secret_key_var, show="*").grid(row=3, column=0, sticky="ew", pady=(0, 10))

        help_text = """OCR设置说明：
Tesseract-OCR（本地）：
- 下载地址：https://github.com/UB-Mannheim/tesseract/wiki
- 需要安装到本地，选择tesseract.exe路径
- 支持多种语言，免费使用
- 默认安装路径: C:\\Program Files\\Tesseract-OCR\\tesseract.exe

百度云OCR（在线）：
- 注册百度智能云账号：https://cloud.baidu.com/
- 创建文字识别应用，获取API Key和Secret Key
- 识别准确率高，每月有免费额度
- 需要网络连接

注意：首次使用时请先配置OCR选项！"""
        
        help_label = ctk.CTkLabel(ocr_frame, text=help_text, justify="left", text_color="gray")
        help_label.grid(row=4, column=0, sticky="w", pady=(10, 0))

    def on_ocr_type_change(self, choice):
        if choice == "tesseract":
            self.tesseract_frame.grid()
            self.baidu_frame.grid_remove()
        elif choice == "baidu":
            self.tesseract_frame.grid_remove()
            self.baidu_frame.grid()

    def create_ai_tab(self, ai_frame):
        ai_frame.grid_columnconfigure(0, weight=1)
        ai_frame.grid_rowconfigure(0, weight=1)

        list_frame = ctk.CTkFrame(ai_frame)
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self.ai_list_frame = ctk.CTkScrollableFrame(list_frame, label_text="已配置的AI服务")
        self.ai_list_frame.grid(row=0, column=0, sticky="nsew")

        button_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        add_btn = ctk.CTkButton(button_frame, text="添加AI", command=self.add_ai_config)
        add_btn.pack(side="left")

        self.edit_btn = ctk.CTkButton(button_frame, text="编辑AI", state="disabled", command=self.edit_ai_config)
        self.edit_btn.pack(side="left", padx=5)

        self.delete_btn = ctk.CTkButton(button_frame, text="删除AI", state="disabled", command=self.delete_ai_config)
        self.delete_btn.pack(side="left")

        self.test_btn = ctk.CTkButton(button_frame, text="测试连接", state="disabled", command=self.test_ai_config)
        self.test_btn.pack(side="left", padx=5)
        
        self.selected_ai_name = None

    def create_prompt_tab(self, prompt_frame):
        prompt_frame.grid_columnconfigure(0, weight=1)
        prompt_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(prompt_frame, text="系统提示词:").grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.prompt_text = ctk.CTkTextbox(prompt_frame, wrap="word")
        self.prompt_text.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        reset_btn = ctk.CTkButton(prompt_frame, text="重置为默认", command=self.reset_prompt)
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
            
            item_frame = ctk.CTkFrame(self.ai_list_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            label = ctk.CTkLabel(item_frame, text=f"{name} ({ai_type}) - 已启用: {enabled}")
            label.pack(side="left", padx=5)
            
            label.bind("<Button-1>", lambda e, n=name: self.on_ai_select(n))
            item_frame.bind("<Button-1>", lambda e, n=name: self.on_ai_select(n))

        self.on_ai_select(None)

    def on_ai_select(self, ai_name):
        self.selected_ai_name = ai_name
        
        for child in self.ai_list_frame.winfo_children():
            child.configure(fg_color="transparent")
            if ai_name and child.winfo_children()[0].cget("text").startswith(ai_name):
                 child.configure(fg_color=("gray75", "gray25"))

        if ai_name:
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            self.test_btn.configure(state="normal")
        else:
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.test_btn.configure(state="disabled")

    def reset_prompt(self):
        default_prompt = """你是一个专业的问题回答助手。请根据用户提供的题目，给出准确、详细的答案。
        
要求：
1. 回答要简重点突出
2. 如果是选择题，请明确指出正确答案
3. 如果是计算题，请提供详细的解题步骤
4. 如果是概念题，请给出准确的定义和解释
5. 回有逻辑性，条理清晰

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
        self.geometry("500x550")
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
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"500x550+{x}+{y}")

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
