import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from ai_manager import AIManager  # 导入AIManager类

class SettingsWindow:
    def __init__(self, parent, ai_manager, ocr_manager, save_callback):
        self.parent = parent
        self.ai_manager = ai_manager
        self.ocr_manager = ocr_manager
        self.save_callback = save_callback
        
        # 创建设置窗口
        self.window = tk.Toplevel(parent)
        self.window.title("设置")
        self.window.geometry("700x600")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()
        
        # 初始化变量
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        self.api_key_var = tk.StringVar()
        self.base_url_var = tk.StringVar(value="https://api.openai.com/v1")
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
        # 加载当前设置
        self.load_current_settings()
        
    def center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
        
    def toggle_key_visibility(self, entry):
        """切换密钥显示/隐藏"""
        if entry['show'] == '*':
            entry['show'] = ''
            entry.button.configure(text='隐藏') if hasattr(entry, 'button') else None
        else:
            entry['show'] = '*'
            entry.button.configure(text='显示') if hasattr(entry, 'button') else None
            
    def create_widgets(self):
        """创建界面组件"""
        # 创建Notebook
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # OCR设置标签页
        self.create_ocr_tab(notebook)
        
        # AI设置标签页
        self.create_ai_tab(notebook)
        
        # 提示词设置标签页
        self.create_prompt_tab(notebook)
        
        # 按钮区域
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存设置", command=self.save_settings)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
    def create_ocr_tab(self, notebook):
        """创建OCR设置标签页"""
        ocr_frame = ttk.Frame(notebook)
        notebook.add(ocr_frame, text="OCR设置")
        
        # 主框架
        main_frame = ttk.Frame(ocr_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # OCR类型选择
        ttk.Label(main_frame, text="OCR类型:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.ocr_type_var = tk.StringVar()
        ocr_type_combo = ttk.Combobox(main_frame, textvariable=self.ocr_type_var, width=30)
        ocr_type_combo['values'] = ('tesseract', 'baidu')
        ocr_type_combo.bind('<<ComboboxSelected>>', self.on_ocr_type_change)
        ocr_type_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        # Tesseract设置框架
        self.tesseract_frame = ttk.LabelFrame(main_frame, text="Tesseract-OCR设置", padding="10")
        self.tesseract_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.tesseract_frame.columnconfigure(0, weight=1)
        
        # Tesseract路径设置
        ttk.Label(self.tesseract_frame, text="Tesseract-OCR路径:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(self.tesseract_frame)
        path_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)
        
        self.tesseract_path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.tesseract_path_var)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="浏览", command=self.browse_tesseract_path)
        browse_btn.grid(row=0, column=1)
        
        # 语言设置
        ttk.Label(self.tesseract_frame, text="识别语言:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(self.tesseract_frame, textvariable=self.language_var, width=30)
        language_combo['values'] = ('chi_sim+eng', 'chi_sim', 'eng', 'chi_tra', 'jpn', 'kor')
        language_combo.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # 百度云OCR设置框架
        self.baidu_frame = ttk.LabelFrame(main_frame, text="百度云OCR设置", padding="10")
        self.baidu_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.baidu_frame.columnconfigure(0, weight=1)
        
        # API Key
        ttk.Label(self.baidu_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.baidu_api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(self.baidu_frame, textvariable=self.baidu_api_key_var, width=50)
        api_key_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Secret Key
        ttk.Label(self.baidu_frame, text="Secret Key:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.baidu_secret_key_var = tk.StringVar()
        secret_key_entry = ttk.Entry(self.baidu_frame, textvariable=self.baidu_secret_key_var, width=50, show="*")
        secret_key_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 帮助信息
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
        
        help_label = tk.Label(main_frame, text=help_text, justify=tk.LEFT, wraplength=600, 
                             fg="gray", font=("Arial", 9))
        help_label.grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        
        main_frame.columnconfigure(0, weight=1)
        
    def on_ocr_type_change(self, event=None):
        """OCR类型改变时的处理"""
        ocr_type = self.ocr_type_var.get()
        if ocr_type == "tesseract":
            # 显示Tesseract设置，隐藏百度云设置
            self.tesseract_frame.grid()
            self.baidu_frame.grid_remove()
        elif ocr_type == "baidu":
            # 显示百度云设置，隐藏Tesseract设置
            self.tesseract_frame.grid_remove()
            self.baidu_frame.grid()
        
    def create_ai_tab(self, notebook):
        """创建AI设置标签页"""
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="AI设置")

        # 主框架
        main_frame = ttk.Frame(ai_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # AI列表框架
        list_frame = ttk.LabelFrame(main_frame, text="已配置的AI服务", padding="10")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # 创建TreeView来显示AI列表
        columns = ("name", "type", "enabled")
        self.ai_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.ai_tree.heading("name", text="名称")
        self.ai_tree.heading("type", text="类型")
        self.ai_tree.heading("enabled", text="已启用")
        self.ai_tree.column("name", width=150)
        self.ai_tree.column("type", width=100)
        self.ai_tree.column("enabled", width=80, anchor=tk.CENTER)
        
        self.ai_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.ai_tree.yview)
        self.ai_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 绑定选择事件
        self.ai_tree.bind("<<TreeviewSelect>>", self.on_ai_select)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # 添加按钮
        add_btn = ttk.Button(button_frame, text="添加AI", command=self.add_ai_config)
        add_btn.pack(side=tk.LEFT)

        # 编辑按钮
        self.edit_btn = ttk.Button(button_frame, text="编辑AI", state=tk.DISABLED, command=self.edit_ai_config)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        # 删除按钮
        self.delete_btn = ttk.Button(button_frame, text="删除AI", state=tk.DISABLED, command=self.delete_ai_config)
        self.delete_btn.pack(side=tk.LEFT)
        
        # 测试按钮 (占位)
        self.test_btn = ttk.Button(button_frame, text="测试连接", state=tk.DISABLED, command=self.test_ai_config)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
    def on_ai_select(self, event):
        """当AI列表中有项目被选中时"""
        selection = self.ai_tree.selection()
        
        # 存储按钮引用
        if not hasattr(self, 'edit_btn'):
            return
            
        if selection:
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
            self.test_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)
            self.test_btn.config(state=tk.DISABLED)
        
    def create_prompt_tab(self, notebook):
        """创建提示词设置标签页"""
        prompt_frame = ttk.Frame(notebook)
        notebook.add(prompt_frame, text="提示词设置")
        
        # 主框架
        main_frame = ttk.Frame(prompt_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="系统提示词:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 创建文本框
        self.prompt_text = tk.Text(main_frame, wrap=tk.WORD, height=15)
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 滚动条
        prompt_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 10))
        self.prompt_text.configure(yscrollcommand=prompt_scrollbar.set)
        
        # 重置按钮
        reset_btn = ttk.Button(main_frame, text="重置为默认", command=self.reset_prompt)
        reset_btn.grid(row=2, column=0, sticky=tk.W)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def browse_tesseract_path(self):
        """浏览Tesseract路径"""
        filename = filedialog.askopenfilename(
            title="选择tesseract.exe",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.tesseract_path_var.set(filename)
            
    def add_ai_config(self):
        """添加AI配置"""
        AIConfigDialog(self.window, self.ai_manager, callback=self.refresh_ai_list)
        
    def edit_ai_config(self):
        """编辑AI配置"""
        selection = self.ai_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的AI配置")
            return
            
        item = self.ai_tree.item(selection[0])
        ai_name = item['values'][0]
        
        AIConfigDialog(self.window, self.ai_manager, ai_name=ai_name, callback=self.refresh_ai_list)
        
    def delete_ai_config(self):
        """删除AI配置"""
        selection = self.ai_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的AI配置")
            return
            
        item = self.ai_tree.item(selection[0])
        ai_name = item['values'][0]
        
        if messagebox.askyesno("确认", f"确定要删除AI配置 '{ai_name}' 吗？"):
            self.ai_manager.remove_ai_config(ai_name)
            self.refresh_ai_list()
            
    def test_ai_config(self):
        """测试AI配置"""
        selection = self.ai_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要测试的AI配置")
            return
            
        item = self.ai_tree.item(selection[0])
        ai_name = item['values'][0]
        
        # 这里可以实现测试功能
        messagebox.showinfo("测试", f"测试功能待实现：{ai_name}")
        
    def refresh_ai_list(self):
        """刷新AI列表"""
        try:
            # 清空现有项目
            for item in self.ai_tree.get_children():
                self.ai_tree.delete(item)
                
            # 添加AI配置
            ai_configs = self.ai_manager.get_settings().get('configs', {})
            
            if not isinstance(ai_configs, dict):
                messagebox.showerror("错误", "AI配置格式错误")
                return
                
            # 排序显示
            sorted_names = sorted(ai_configs.keys())
            for name in sorted_names:
                config = ai_configs[name]
                if not isinstance(config, dict):
                    continue
                enabled = "是" if config.get("enabled", False) else "否"
                ai_type = config.get("type", "未知")
                self.ai_tree.insert('', 'end', values=(name, ai_type, enabled))
                
            # 禁用编辑和删除按钮
            self.on_ai_select(None)
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新AI列表失败: {str(e)}")
            
    def reset_prompt(self):
        """重置提示词为默认值"""
        default_prompt = """你是一个专业的问题回答助手。请根据用户提供的题目，给出准确、详细的答案。
        
要求：
1. 回答要简重点突出
2. 如果是选择题，请明确指出正确答案
3. 如果是计算题，请提供详细的解题步骤
4. 如果是概念题，请给出准确的定义和解释
5. 回有逻辑性，条理清晰

请直接回答问题，不需要额外的寒暄。"""
        
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, default_prompt)
        
    def load_current_settings(self):
        """加载当前设置"""
        # 加载OCR设置
        ocr_settings = self.ocr_manager.get_settings()
        self.ocr_type_var.set(ocr_settings.get("type", "tesseract"))
        self.tesseract_path_var.set(ocr_settings.get("tesseract_path", ""))
        self.language_var.set(ocr_settings.get("language", "chi_sim+eng"))
        self.baidu_api_key_var.set(ocr_settings.get("baidu_api_key", ""))
        self.baidu_secret_key_var.set(ocr_settings.get("baidu_secret_key", ""))
        self.on_ocr_type_change()
        
        # 加载AI列表
        self.refresh_ai_list()
        
        # 加载系统提示词
        ai_settings = self.ai_manager.get_settings()
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, ai_settings.get("system_prompt", self.ai_manager.DEFAULT_PROMPT))

    def save_settings(self):
        """保存设置"""
        try:
            # 保存OCR设置
            ocr_settings = {
                "type": self.ocr_type_var.get(),
                "tesseract_path": self.tesseract_path_var.get(),
                "language": self.language_var.get(),
                "baidu_api_key": self.baidu_api_key_var.get(),
                "baidu_secret_key": self.baidu_secret_key_var.get()
            }
            self.ocr_manager.load_settings(ocr_settings)
            
            # AI设置已在AIConfigDialog中单独处理，这里只需保存提示词
            ai_settings = self.ai_manager.get_settings()
            ai_settings["system_prompt"] = self.prompt_text.get(1.0, tk.END).strip()
            self.ai_manager.load_settings(ai_settings)
            
            # 调用主保存回调
            if self.save_callback:
                self.save_callback()
            
            messagebox.showinfo("成功", "设置已保存")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

class AIConfigDialog:
    def __init__(self, parent, ai_manager, ai_name=None, callback=None):
        self.parent = parent
        self.ai_manager = ai_manager
        self.ai_name = ai_name
        self.callback = callback
        self.is_edit = ai_name is not None
        self.original_name = ai_name  # 保存原始名称，用于检测是否更改
        
        try:
            # 验证AI管理器
            if not isinstance(ai_manager, AIManager):
                raise ValueError("无效的AI管理器")
                
            # 如果是编辑模式，验证配置是否存在
            if self.is_edit and not ai_manager.get_ai_config(ai_name):
                raise ValueError(f"找不到AI配置: {ai_name}")
                
            # 创建对话框
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("编辑AI配置" if self.is_edit else "添加AI配置")
            self.dialog.geometry("500x500")
            self.dialog.resizable(False, False)
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # 防止关闭按钮
            self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
            
            # 初始化变量
            self.init_variables()
            
            # 创建界面
            self.create_widgets()
            
            # 如果是编辑模式，加载现有配置
            if self.is_edit:
                self.load_config()
                
            # 居中显示
            self.center_dialog()
            
        except Exception as e:
            messagebox.showerror("错误", f"初始化AI配置对话框失败: {str(e)}")
            if hasattr(self, 'dialog'):
                self.dialog.destroy()
                
    def init_variables(self):
        """初始化所有变量"""
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar(value="openai")  # 默认选择OpenAI
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.base_url_var = tk.StringVar()
        self.max_tokens_var = tk.StringVar(value="2000") # 新增
        self.enabled_var = tk.BooleanVar(value=True)  # 默认启用
        
        # 设置模型变量的追踪
        self.type_var.trace_add("write", self.on_type_change)
            
    def center_dialog(self):
        """对话框居中显示"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x450+{x}+{y}") # 增加高度以适应更多字段
        
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 使用网格布局
        main_frame.columnconfigure(1, weight=1)
        
        # AI名称
        row = 0
        ttk.Label(main_frame, text="AI名称: *").grid(row=row, column=0, sticky=tk.W)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var)
        name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # AI类型
        row += 1
        ttk.Label(main_frame, text="AI类型: *").grid(row=row, column=0, sticky=tk.W)
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, state='readonly')
        type_combo['values'] = ('openai', 'doubao', 'siliconflow', 'custom')
        type_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # API密钥
        row += 1
        ttk.Label(main_frame, text="API密钥: *").grid(row=row, column=0, sticky=tk.W)
        key_frame = ttk.Frame(main_frame)
        key_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.show_key_btn = ttk.Button(key_frame, text="显示", width=6, command=self.toggle_key_visibility)
        self.show_key_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 模型
        row += 1
        ttk.Label(main_frame, text="模型:").grid(row=row, column=0, sticky=tk.W)
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, width=30)
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # API基础URL
        row += 1
        self.base_url_label = ttk.Label(main_frame, text="API地址:")
        self.base_url_label.grid(row=row, column=0, sticky=tk.W)
        self.base_url_entry = ttk.Entry(main_frame, textvariable=self.base_url_var)
        self.base_url_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 最大令牌数
        row += 1
        ttk.Label(main_frame, text="最大令牌数:").grid(row=row, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.max_tokens_var).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 启用状态
        row += 1
        enabled_check = ttk.Checkbutton(
            main_frame, 
            text="启用此AI",
            variable=self.enabled_var,
            style='Switch.TCheckbutton'
        )
        enabled_check.grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)
        
        # 分隔线
        row += 1
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        
        # 按钮区域
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.E, pady=10)
        
        ttk.Button(button_frame, text="取消", command=self.on_close).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save_config).pack(side=tk.RIGHT)
        
        # 初始更新界面状态
        self.update_model_list()
        
    def toggle_key_visibility(self):
        """切换API密钥显示/隐藏"""
        if self.api_key_entry['show'] == '*':
            self.api_key_entry['show'] = ''
            self.show_key_btn['text'] = '隐藏'
        else:
            self.api_key_entry['show'] = '*'
            self.show_key_btn['text'] = '显示'
        
    def update_model_list(self, *args):
        """更新模型列表"""
        # 设置OpenAI模型列表
        models = [
            'gpt-4-turbo-preview',
            'gpt-4-vision-preview',
            'gpt-4',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k'
        ]
        
        self.model_combo['values'] = models
        if not self.model_var.get():
            self.model_var.set('gpt-3.5-turbo')  # 默认模型
            
        # 设置默认基础URL
        if not self.base_url_var.get():
            self.base_url_var.set('https://api.openai.com/v1')
            
    def on_type_change(self, *args):
        """当AI类型改变时的处理"""
        self.update_model_list()
                
    def load_config(self):
        """加载现有配置"""
        try:
            # 从AI管理器获取配置
            config = self.ai_manager.get_ai_config(self.ai_name)
            if not config:
                raise ValueError(f"找不到AI配置: {self.ai_name}")
                
            # 设置界面值
            self.name_var.set(self.ai_name)
            
            # 设置AI类型
            self.type_var.set(config.get("type", "openai"))
            
            # 设置其他字段
            self.api_key_var.set(config.get("api_key", ""))
            self.model_var.set(config.get("model", ""))
            self.base_url_var.set(config.get("base_url", ""))
            self.max_tokens_var.set(config.get("max_tokens", "2000")) # 新增
            self.enabled_var.set(config.get("enabled", False))
            
            # 更新模型列表
            self.update_model_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载AI配置失败: {str(e)}")
            self.dialog.destroy()
            
    def on_close(self):
        """关闭对话框"""
        if messagebox.askyesno("确认", "确定要关闭吗？未保存的更改将会丢失。"):
            self.dialog.destroy()
            
    def validate_config(self):
        """验证配置"""
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("请输入AI名称")
            
        if not self.is_edit and name in self.ai_manager.ai_configs:
            raise ValueError(f"AI名称 '{name}' 已存在")
            
        ai_type = self.type_var.get().lower()
        if not ai_type:
            raise ValueError("请选择AI类型")
            
        api_key = self.api_key_var.get().strip()
        if not api_key:
            raise ValueError("请输入API密钥")
            
        model = self.model_var.get().strip()
        if not model:
            raise ValueError("请选择或输入模型名称")
            
        return name, ai_type, api_key, model
        
    def save_config(self):
        """保存配置"""
        try:
            # 验证输入
            name, ai_type, api_key, model = self.validate_config()
            
            # 准备配置
            config = {
                "type": ai_type,
                "api_key": api_key,
                "model": model,
                "enabled": self.enabled_var.get(),
                "base_url": self.base_url_var.get().strip(),
                "max_tokens": self.max_tokens_var.get().strip() # 新增
            }
            
            # 如果是编辑模式且名称改变，先删除旧配置
            if self.is_edit and name != self.original_name:
                self.ai_manager.remove_ai_config(self.original_name)
                
            # 添加新配置
            self.ai_manager.add_ai_config(name, config)
            
            # 调用回调函数并关闭窗口
            if self.callback:
                self.callback()
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def get_default_model(self, ai_type):
        """获取默认模型名称"""
        return "gpt-3.5-turbo"
        
    def on_close(self):
        """对话框关闭处理"""
        try:
            if hasattr(self, 'callback'):
                self.callback()
            self.dialog.destroy()
        except Exception as e:
            self.dialog.destroy()
