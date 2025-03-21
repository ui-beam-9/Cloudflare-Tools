#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import json
import requests
from datetime import datetime
import threading

class CloudflareManager:
    def __init__(self, email=None, api_key=None, token=None):
        """初始化 Cloudflare 管理器"""
        # 尝试从环境变量获取凭证
        self.email = email or os.environ.get('CLOUDFLARE_EMAIL')
        self.api_key = api_key or os.environ.get('CLOUDFLARE_API_KEY')
        self.token = token or os.environ.get('CLOUDFLARE_TOKEN')
        
        if not ((self.email and self.api_key) or self.token):
            raise ValueError("必须提供 Cloudflare 凭证，可以是 email+api_key 或者 token")
            
        self.headers = {}
        if self.token:
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        else:
            self.headers = {
                'X-Auth-Email': self.email,
                'X-Auth-Key': self.api_key,
                'Content-Type': 'application/json'
            }
        
        self.api_url = "https://api.cloudflare.com/client/v4"
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """发送请求到 Cloudflare API"""
        url = f"{self.api_url}/{endpoint}"
        
        response = None
        if method.upper() == 'GET':
            response = requests.get(url, headers=self.headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=self.headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=self.headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=self.headers)
        else:
            raise ValueError(f"不支持的请求方法: {method}")
        
        # 解析结果
        result = response.json()
        
        # 检查响应状态
        if not result.get('success'):
            error_messages = [error.get('message', 'Unknown error') for error in result.get('errors', [])]
            raise Exception(f"API 错误: {'; '.join(error_messages)}")
            
        return result
    
    def list_zones(self):
        """列出所有域名（zones）"""
        result = self._make_request('GET', 'zones')
        return result.get('result', [])
    
    def get_zone_info(self, zone_id):
        """获取域名信息"""
        result = self._make_request('GET', f'zones/{zone_id}')
        return result.get('result', {})
    
    def list_dns_records(self, zone_id):
        """列出域名下所有记录"""
        result = self._make_request('GET', f'zones/{zone_id}/dns_records')
        return result.get('result', [])
    
    def add_dns_record(self, zone_id, name, record_type, content, ttl=1, proxied=False):
        """添加记录"""
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied
        }
        result = self._make_request('POST', f'zones/{zone_id}/dns_records', data=data)
        return result.get('result', {})
    
    def update_dns_record(self, zone_id, record_id, name, record_type, content, ttl=1, proxied=False):
        """更新记录"""
        data = {
            'type': record_type,
            'name': name,
            'content': content,
            'ttl': ttl,
            'proxied': proxied
        }
        result = self._make_request('PUT', f'zones/{zone_id}/dns_records/{record_id}', data=data)
        return result.get('result', {})
    
    def delete_dns_record(self, zone_id, record_id):
        """删除记录"""
        result = self._make_request('DELETE', f'zones/{zone_id}/dns_records/{record_id}')
        return result.get('result', {})
    
    def get_dns_record_info(self, zone_id, record_id):
        """获取记录信息"""
        result = self._make_request('GET', f'zones/{zone_id}/dns_records/{record_id}')
        return result.get('result', {})


class CloudflareDNSManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloudflare DNS 管理器")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico")
        if os.path.exists(icon_path):
            # 对于tkinter应用, 需要使用PhotoImage来设置图标
            try:
                from PIL import Image, ImageTk
                icon = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon)
            except ImportError:
                # 如果没有PIL库，尝试使用tk原生方法
                try:
                    from tkinter import PhotoImage
                    icon = PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon)
                except:
                    pass  # 如果无法加载图标，则忽略
        
        # 初始化变量
        self.current_zone = None
        self.current_zone_id = None
        self.records = []
        self.cloudflare = None
        self.zones = []
        
        # 创建界面
        self.create_widgets()
        
        # 尝试加载配置
        self.load_config()
        
        # 尝试连接
        if self.config.get('cloudflare_token'):
            self.connect_to_cloudflare(token=self.config['cloudflare_token'])
        elif self.config.get('cloudflare_email') and self.config.get('cloudflare_api_key'):
            self.connect_to_cloudflare(
                email=self.config['cloudflare_email'],
                api_key=self.config['cloudflare_api_key']
            )
        else:
            self.show_login_dialog()
    
    def create_widgets(self):
        # 创建工具栏框架
        self.toolbar_frame = ttk.Frame(self.root, padding=5)
        self.toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 域名选择下拉框
        ttk.Label(self.toolbar_frame, text="域名:").pack(side=tk.LEFT, padx=(0, 5))
        self.zone_var = tk.StringVar()
        self.zone_combobox = ttk.Combobox(self.toolbar_frame, textvariable=self.zone_var, state="readonly", width=30)
        self.zone_combobox.pack(side=tk.LEFT, padx=(0, 10))
        self.zone_combobox.bind("<<ComboboxSelected>>", self.on_zone_selected)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(self.toolbar_frame, text="刷新", command=self.refresh_records)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 添加记录按钮
        self.add_record_button = ttk.Button(self.toolbar_frame, text="添加记录", command=self.show_add_record_dialog)
        self.add_record_button.pack(side=tk.LEFT, padx=5)
        
        # 设置凭证按钮
        self.settings_button = ttk.Button(self.toolbar_frame, text="设置凭证", command=self.show_login_dialog)
        self.settings_button.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建表格
        self.create_records_table()
        
        # 设置状态
        self.status_var.set("准备就绪")
    
    def create_records_table(self):
        # 表格框架
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ("名称", "类型", "内容", "TTL", "代理", "ID")
        self.records_table = ttk.Treeview(self.table_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.records_table.heading(col, text=col)
            if col == "内容":
                self.records_table.column(col, width=200, anchor=tk.W)
            elif col == "ID":
                self.records_table.column(col, width=60, anchor=tk.CENTER)
            elif col == "代理":
                self.records_table.column(col, width=60, anchor=tk.CENTER)
            else:
                self.records_table.column(col, width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        table_scroll_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.records_table.yview)
        self.records_table.configure(yscrollcommand=table_scroll_y.set)
        
        # 放置表格和滚动条
        self.records_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.records_table.bind("<Double-1>", self.on_record_double_click)
        
        # 绑定右键菜单
        self.create_context_menu()
        self.records_table.bind("<Button-3>", self.show_context_menu)
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑记录", command=self.edit_selected_record)
        self.context_menu.add_command(label="删除记录", command=self.delete_selected_record)
    
    def show_context_menu(self, event):
        try:
            selected_item = self.records_table.selection()[0]
            self.context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass  # 没有选中项
    
    def show_login_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Cloudflare 凭证设置")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建选项卡
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API Token 选项卡
        token_frame = ttk.Frame(notebook, padding=10)
        notebook.add(token_frame, text="API Token")
        
        ttk.Label(token_frame, text="API Token:").grid(row=0, column=0, sticky=tk.W, pady=10)
        token_entry = ttk.Entry(token_frame, width=40, show="*")
        token_entry.grid(row=0, column=1, pady=10)
        
        if self.config.get('cloudflare_token'):
            token_entry.insert(0, self.config['cloudflare_token'])
        
        # Global API Key 选项卡
        key_frame = ttk.Frame(notebook, padding=10)
        notebook.add(key_frame, text="Global API Key")
        
        ttk.Label(key_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(key_frame, width=40)
        email_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(key_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        api_key_entry = ttk.Entry(key_frame, width=40, show="*")
        api_key_entry.grid(row=1, column=1, pady=5)
        
        if self.config.get('cloudflare_email'):
            email_entry.insert(0, self.config['cloudflare_email'])
        if self.config.get('cloudflare_api_key'):
            api_key_entry.insert(0, self.config['cloudflare_api_key'])
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def on_login():
            current_tab = notebook.index(notebook.select())
            
            try:
                if current_tab == 0:  # API Token
                    token = token_entry.get().strip()
                    if not token:
                        messagebox.showerror("错误", "API Token 不能为空", parent=dialog)
                        return
                    
                    self.connect_to_cloudflare(token=token)
                    self.config['cloudflare_token'] = token
                    self.config.pop('cloudflare_email', None)
                    self.config.pop('cloudflare_api_key', None)
                    
                else:  # Global API Key
                    email = email_entry.get().strip()
                    api_key = api_key_entry.get().strip()
                    
                    if not email or not api_key:
                        messagebox.showerror("错误", "Email 和 API Key 不能为空", parent=dialog)
                        return
                    
                    self.connect_to_cloudflare(email=email, api_key=api_key)
                    self.config['cloudflare_email'] = email
                    self.config['cloudflare_api_key'] = api_key
                    self.config.pop('cloudflare_token', None)
                
                self.save_config()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("连接错误", f"无法连接到 Cloudflare: {str(e)}", parent=dialog)
        
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="连接", command=on_login).pack(side=tk.RIGHT, padx=5)
    
    def connect_to_cloudflare(self, email=None, api_key=None, token=None):
        try:
            self.status_var.set("正在连接到 Cloudflare...")
            self.cloudflare = CloudflareManager(email, api_key, token)
            self.load_zones()
            self.status_var.set("已连接到 Cloudflare")
        except Exception as e:
            self.status_var.set(f"连接失败: {str(e)}")
            raise
    
    def load_zones(self):
        if not self.cloudflare:
            return
        
        def background_task():
            try:
                zones = self.cloudflare.list_zones()
                
                # 在主线程中更新 UI
                self.root.after(0, lambda: self._update_zones_ui(zones))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"加载域名失败: {str(e)}"))
        
        self.status_var.set("正在加载域名列表...")
        threading.Thread(target=background_task).start()
    
    def _update_zones_ui(self, zones):
        self.zones = zones
        zone_names = [zone['name'] for zone in zones]
        self.zone_combobox['values'] = zone_names
        
        if zone_names:
            self.zone_combobox.current(0)
            self.current_zone = zone_names[0]
            self.current_zone_id = zones[0]['id']
            self.refresh_records()
        
        self.status_var.set(f"已加载 {len(zone_names)} 个域名")
    
    def on_zone_selected(self, event):
        index = self.zone_combobox.current()
        if index >= 0 and index < len(self.zones):
            self.current_zone = self.zones[index]['name']
            self.current_zone_id = self.zones[index]['id']
            self.refresh_records()
    
    def refresh_records(self):
        if not self.cloudflare or not self.current_zone_id:
            return
        
        def background_task():
            try:
                self.root.after(0, lambda: self.status_var.set(f"正在加载 {self.current_zone} 的记录..."))
                records = self.cloudflare.list_dns_records(self.current_zone_id)
                
                # 在主线程中更新 UI
                self.root.after(0, lambda: self._update_records_ui(records))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"加载记录失败: {str(e)}"))
        
        threading.Thread(target=background_task).start()
    
    def _update_records_ui(self, records):
        # 清空表格
        for item in self.records_table.get_children():
            self.records_table.delete(item)
        
        # 添加记录到表格
        for record in records:
            ttl_value = "自动" if record.get('ttl') == 1 else record.get('ttl')
            proxied_value = "是" if record.get('proxied') else "否"
            
            self.records_table.insert("", tk.END, values=(
                record.get('name'),
                record.get('type'),
                record.get('content'),
                ttl_value,
                proxied_value,
                record.get('id')
            ))
        
        self.records = records
        self.status_var.set(f"已加载 {len(records)} 条记录")
    
    def on_record_double_click(self, event):
        self.edit_selected_record()
    
    def edit_selected_record(self):
        try:
            selected_item = self.records_table.selection()[0]
            values = self.records_table.item(selected_item, "values")
            
            record_id = values[5]
            record_data = None
            
            # 查找匹配的记录数据
            for record in self.records:
                if record['id'] == record_id:
                    record_data = record
                    break
            
            if record_data:
                self.show_edit_record_dialog(record_data)
            
        except IndexError:
            messagebox.showinfo("提示", "请先选择一条记录")
    
    def delete_selected_record(self):
        try:
            selected_item = self.records_table.selection()[0]
            values = self.records_table.item(selected_item, "values")
            
            name = values[0]
            record_id = values[5]
            
            if messagebox.askyesno("确认删除", f"确定要删除记录 {name} 吗?"):
                try:
                    self.cloudflare.delete_dns_record(self.current_zone_id, record_id)
                    self.refresh_records()
                    messagebox.showinfo("成功", "记录已删除")
                except Exception as e:
                    messagebox.showerror("错误", f"删除记录失败: {str(e)}")
            
        except IndexError:
            messagebox.showinfo("提示", "请先选择一条记录")
    
    def show_add_record_dialog(self):
        self.show_record_dialog()
    
    def show_edit_record_dialog(self, record_data):
        self.show_record_dialog(record_data)
    
    def show_record_dialog(self, record_data=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑记录" if record_data else "添加记录")
        dialog.geometry("420x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 域名部分填充
        current_zone = self.current_zone
        
        ttk.Label(dialog, text=f"域名: {current_zone}").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
        
        # 创建表单
        ttk.Label(dialog, text="名称:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="记录类型:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        type_var = tk.StringVar()
        type_combobox = ttk.Combobox(dialog, textvariable=type_var, width=15, state="readonly")
        type_combobox['values'] = ("A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV", "CAA")
        type_combobox.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
        type_combobox.current(0)
        
        ttk.Label(dialog, text="内容:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        content_entry = ttk.Entry(dialog, width=30)
        content_entry.grid(row=3, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="TTL:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
        ttl_var = tk.StringVar(value="自动")
        ttl_combobox = ttk.Combobox(dialog, textvariable=ttl_var, width=15)
        ttl_combobox['values'] = ("自动", "60", "120", "300", "600", "1800", "3600", "7200", "86400")
        ttl_combobox.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(dialog, text="代理:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=10)
        proxied_var = tk.BooleanVar(value=False)
        proxied_check = ttk.Checkbutton(dialog, variable=proxied_var)
        proxied_check.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)
        
        # 如果是编辑操作，填充现有数据
        if record_data:
            name = record_data['name']
            # 移除域名后缀以获取子域名部分
            if name.endswith(f".{current_zone}"):
                name = name[:-len(f".{current_zone}") - 1]
            elif name == current_zone:
                name = "@"
            
            name_entry.insert(0, name)
            type_var.set(record_data['type'])
            content_entry.insert(0, record_data['content'])
            
            if record_data['ttl'] == 1:
                ttl_var.set("自动")
            else:
                ttl_var.set(str(record_data['ttl']))
                
            proxied_var.set(record_data['proxied'])
        
        def on_submit():
            name = name_entry.get().strip()
            record_type = type_var.get()
            content = content_entry.get().strip()
            ttl_text = ttl_var.get()
            proxied = proxied_var.get()
            
            if not name or not content:
                messagebox.showerror("错误", "名称和内容不能为空", parent=dialog)
                return
            
            # 转换名称格式
            full_name = name
            if name == "@":
                full_name = current_zone
            elif not name.endswith(f".{current_zone}") and name != current_zone:
                full_name = f"{name}.{current_zone}"
            
            # 转换 TTL 值
            if ttl_text == "自动":
                ttl = 1
            else:
                try:
                    ttl = int(ttl_text)
                except ValueError:
                    messagebox.showerror("错误", "TTL 必须是一个整数", parent=dialog)
                    return
            
            # 部分记录类型不能使用代理
            if proxied and record_type in ("MX", "TXT", "NS", "SRV", "CAA"):
                messagebox.showerror("错误", f"{record_type} 类型的记录不能启用代理", parent=dialog)
                return
            
            try:
                if record_data:  # 编辑记录
                    self.cloudflare.update_dns_record(
                        self.current_zone_id,
                        record_data['id'],
                        full_name,
                        record_type,
                        content,
                        ttl,
                        proxied
                    )
                    messagebox.showinfo("成功", "记录已更新", parent=dialog)
                else:  # 添加记录
                    self.cloudflare.add_dns_record(
                        self.current_zone_id,
                        full_name,
                        record_type,
                        content,
                        ttl,
                        proxied
                    )
                    messagebox.showinfo("成功", "记录已添加", parent=dialog)
                
                dialog.destroy()
                self.refresh_records()
                
            except Exception as e:
                messagebox.showerror("错误", f"操作失败: {str(e)}", parent=dialog)
        
        # 添加按钮
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="保存", command=on_submit).pack(side=tk.LEFT, padx=10)
    
    def load_config(self):
        self.config = {}
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, "cloudflare_manager.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                pass
    
    def save_config(self):
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, "cloudflare_manager.json")
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")


def main():
    root = tk.Tk()
    app = CloudflareDNSManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 