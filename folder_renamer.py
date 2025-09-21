import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具")
        self.root.geometry("800x600")
        
        # 设置变量
        self.current_directory = tk.StringVar()
        self.rename_rule = tk.StringVar(value="replace")
        self.search_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.prefix_text = tk.StringVar()
        self.suffix_text = tk.StringVar()
        self.start_number = tk.IntVar(value=1)
        self.date_format = tk.StringVar(value="%Y%m%d")
        self.regex_pattern = tk.StringVar()
        self.regex_replacement = tk.StringVar()
        self.file_data = []
        
        # 创建界面
        self.create_widgets()
        
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
        title_label = ttk.Label(main_frame, text="批量文件重命名工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 选择目录按钮
        ttk.Button(control_frame, text="选择目录", 
                  command=self.select_directory).grid(row=0, column=0, columnspan=2, 
                                                     pady=(0, 10), sticky=(tk.W, tk.E))
        
        # 当前目录显示
        ttk.Label(control_frame, text="当前目录:").grid(row=1, column=0, sticky=tk.W)
        dir_label = ttk.Label(control_frame, textvariable=self.current_directory, 
                             wraplength=200, foreground="blue")
        dir_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 查找文本
        ttk.Label(control_frame, text="查找文本:").grid(row=3, column=0, sticky=tk.W)
        search_entry = ttk.Entry(control_frame, textvariable=self.search_text)
        search_entry.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 重命名规则选择
        ttk.Label(control_frame, text="重命名规则:").grid(row=5, column=0, sticky=tk.W)
        rule_combo = ttk.Combobox(control_frame, textvariable=self.rename_rule, 
                                 values=["replace", "prefix", "suffix", "sequence", "datetime", "regex"],
                                 state="readonly", width=18)
        rule_combo.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        rule_combo.bind('<<ComboboxSelected>>', self.on_rule_change)
        
        # 创建不同规则的输入框架
        self.rule_frame = ttk.Frame(control_frame)
        self.rule_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 初始化规则输入控件
        self.create_rule_inputs()
        
        # 预览按钮
        self.preview_button = ttk.Button(control_frame, text="预览", 
                                        command=self.preview_rename, state='disabled')
        self.preview_button.grid(row=8, column=0, columnspan=2, pady=(0, 5), 
                                sticky=(tk.W, tk.E))
        
        # 执行重命名按钮
        self.rename_button = ttk.Button(control_frame, text="执行重命名", 
                                       command=self.execute_rename, state='disabled')
        self.rename_button.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 右侧显示区域
        display_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="10")
        display_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview用于显示文件列表
        columns = ('原名称', '新名称')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        self.tree.heading('原名称', text='原名称')
        self.tree.heading('新名称', text='新名称')
        
        # 设置列宽
        self.tree.column('原名称', width=200)
        self.tree.column('新名称', width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置Treeview和滚动条
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("请选择一个目录")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def create_rule_inputs(self):
        """创建不同规则的输入控件"""
        # 清空规则框架
        for widget in self.rule_frame.winfo_children():
            widget.destroy()
            
        rule = self.rename_rule.get()
        
        if rule == "replace":
            # 替换文本规则
            ttk.Label(self.rule_frame, text="查找文本:").grid(row=0, column=0, sticky=tk.W)
            search_entry = ttk.Entry(self.rule_frame, textvariable=self.search_text)
            search_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
            
            ttk.Label(self.rule_frame, text="替换为:").grid(row=2, column=0, sticky=tk.W)
            replace_entry = ttk.Entry(self.rule_frame, textvariable=self.replace_text)
            replace_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
        elif rule == "prefix":
            # 添加前缀规则
            ttk.Label(self.rule_frame, text="前缀文本:").grid(row=0, column=0, sticky=tk.W)
            prefix_entry = ttk.Entry(self.rule_frame, textvariable=self.prefix_text)
            prefix_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
        elif rule == "suffix":
            # 添加后缀规则
            ttk.Label(self.rule_frame, text="后缀文本:").grid(row=0, column=0, sticky=tk.W)
            suffix_entry = ttk.Entry(self.rule_frame, textvariable=self.suffix_text)
            suffix_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
        elif rule == "sequence":
            # 数字序列规则
            ttk.Label(self.rule_frame, text="起始数字:").grid(row=0, column=0, sticky=tk.W)
            start_spinbox = ttk.Spinbox(self.rule_frame, from_=1, to=9999, 
                                       textvariable=self.start_number, width=18)
            start_spinbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
        elif rule == "datetime":
            # 日期时间规则
            ttk.Label(self.rule_frame, text="日期格式:").grid(row=0, column=0, sticky=tk.W)
            format_combo = ttk.Combobox(self.rule_frame, textvariable=self.date_format,
                                      values=["%Y%m%d", "%Y-%m-%d", "%Y%m%d_%H%M%S", "%Y-%m-%d_%H-%M-%S"],
                                      state="readonly", width=16)
            format_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
            ttk.Label(self.rule_frame, text="示例:").grid(row=2, column=0, sticky=tk.W)
            example_label = ttk.Label(self.rule_frame, text="20250917", foreground="blue")
            example_label.grid(row=3, column=0, columnspan=2, sticky=tk.W)
            
        elif rule == "regex":
            # 正则表达式规则
            ttk.Label(self.rule_frame, text="正则模式:").grid(row=0, column=0, sticky=tk.W)
            pattern_entry = ttk.Entry(self.rule_frame, textvariable=self.regex_pattern)
            pattern_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
            
            ttk.Label(self.rule_frame, text="替换为:").grid(row=2, column=0, sticky=tk.W)
            replacement_entry = ttk.Entry(self.rule_frame, textvariable=self.regex_replacement)
            replacement_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
    def on_rule_change(self, event=None):
        """规则改变时的处理"""
        self.create_rule_inputs()
        
        # 清空预览
        if self.file_data:
            self.tree.delete(*self.tree.get_children())
            for file in self.file_data:
                self.tree.insert('', 'end', values=(file['original_name'], file['original_name']))
            self.status_var.set(f"找到 {len(self.file_data)} 个文件")
            self.rename_button.config(state='disabled')
        
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择要重命名文件的目录")
        if directory:
            self.current_directory.set(directory)
            self.load_files()
            self.preview_button.config(state='normal')
            self.status_var.set(f"已选择目录: {directory}")
            
    def load_files(self):
        """加载目录中的所有文件"""
        self.file_data.clear()
        self.tree.delete(*self.tree.get_children())
        
        directory = self.current_directory.get()
        if not directory:
            return
            
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):  # 只处理文件，不处理文件夹
                    self.file_data.append({
                        'original_name': item,
                        'new_name': item,
                        'path': item_path
                    })
                    self.tree.insert('', 'end', values=(item, item))
                    
            if self.file_data:
                self.status_var.set(f"找到 {len(self.file_data)} 个文件")
            else:
                self.status_var.set("所选目录中没有找到文件")
                
        except Exception as e:
            messagebox.showerror("错误", f"读取目录时出错: {str(e)}")
            
    def preview_rename(self):
        """预览重命名结果"""
        if not self.file_data:
            messagebox.showwarning("警告", "请先选择一个包含文件的目录")
            return
            
        rule = self.rename_rule.get()
        
        # 清空树形视图
        self.tree.delete(*self.tree.get_children())
        
        # 生成预览
        rename_count = 0
        for i, file in enumerate(self.file_data):
            original_name = file['original_name']
            new_name = self.apply_rename_rule(original_name, i)
                
            file['new_name'] = new_name
            
            # 如果名称有变化，标记为将要重命名
            if original_name != new_name:
                self.tree.insert('', 'end', values=(original_name, new_name), 
                               tags=('rename',))
                rename_count += 1
            else:
                self.tree.insert('', 'end', values=(original_name, new_name))
                
        # 设置标签样式
        self.tree.tag_configure('rename', foreground='red')
        
        if rename_count > 0:
            self.status_var.set(f"预览完成: {rename_count} 个文件将被重命名")
            self.rename_button.config(state='normal')
        else:
            self.status_var.set("没有文件需要重命名")
            self.rename_button.config(state='disabled')
            
    def apply_rename_rule(self, original_name, index):
        """应用重命名规则"""
        rule = self.rename_rule.get()
        
        if rule == "replace":
            # 替换文本规则
            search = self.search_text.get()
            replace = self.replace_text.get()
            if search:
                return original_name.replace(search, replace)
            return original_name
            
        elif rule == "prefix":
            # 添加前缀规则
            prefix = self.prefix_text.get()
            if prefix:
                # 获取文件扩展名
                name, ext = os.path.splitext(original_name)
                return prefix + name + ext
            return original_name
            
        elif rule == "suffix":
            # 添加后缀规则
            suffix = self.suffix_text.get()
            if suffix:
                # 获取文件扩展名
                name, ext = os.path.splitext(original_name)
                return name + suffix + ext
            return original_name
            
        elif rule == "sequence":
            # 数字序列规则
            start_num = self.start_number.get()
            # 获取文件扩展名
            name, ext = os.path.splitext(original_name)
            return f"{name}_{start_num + index}{ext}"
            
        elif rule == "datetime":
            # 日期时间规则
            from datetime import datetime
            date_format = self.date_format.get()
            current_time = datetime.now().strftime(date_format)
            # 获取文件扩展名
            name, ext = os.path.splitext(original_name)
            return f"{current_time}{ext}"
            
        elif rule == "regex":
            # 正则表达式规则
            pattern = self.regex_pattern.get()
            replacement = self.regex_replacement.get()
            if pattern:
                try:
                    return re.sub(pattern, replacement, original_name)
                except re.error:
                    return original_name
            return original_name
            
        return original_name
            
    def execute_rename(self):
        """执行重命名操作"""
        if not self.file_data:
            messagebox.showwarning("警告", "没有文件需要重命名")
            return
            
        # 统计需要重命名的文件
        rename_count = sum(1 for file in self.file_data 
                          if file['original_name'] != file['new_name'])
        
        if rename_count == 0:
            messagebox.showinfo("提示", "没有文件需要重命名")
            return
            
        # 确认对话框
        result = messagebox.askyesno("确认", 
                                     f"确定要重命名 {rename_count} 个文件吗？\n" +
                                     "此操作不可撤销，请确认！")
        if not result:
            return
            
        # 执行重命名
        success_count = 0
        error_count = 0
        errors = []
        
        directory = self.current_directory.get()
        
        for file in self.file_data:
            original_name = file['original_name']
            new_name = file['new_name']
            
            if original_name != new_name:
                original_path = os.path.join(directory, original_name)
                new_path = os.path.join(directory, new_name)
                
                try:
                    # 检查目标路径是否已存在
                    if os.path.exists(new_path):
                        errors.append(f"文件 '{new_name}' 已存在")
                        error_count += 1
                        continue
                        
                    os.rename(original_path, new_path)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"重命名 '{original_name}' 失败: {str(e)}")
                    error_count += 1
                    
        # 显示结果
        if error_count == 0:
            messagebox.showinfo("成功", 
                              f"成功重命名 {success_count} 个文件！")
            self.status_var.set(f"成功重命名 {success_count} 个文件")
        else:
            error_msg = f"重命名完成：\n成功: {success_count}\n失败: {error_count}\n\n"
            error_msg += "\n".join(errors[:5])  # 只显示前5个错误
            if len(errors) > 5:
                error_msg += f"\n... 还有 {len(errors) - 5} 个错误"
            messagebox.showwarning("部分成功", error_msg)
            self.status_var.set(f"重命名完成: 成功 {success_count} 个, 失败 {error_count} 个")
            
        # 重新加载文件列表
        self.load_files()
        self.rename_button.config(state='disabled')

def main():
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
