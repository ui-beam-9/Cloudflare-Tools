import sys
import json
import requests
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                           QLabel, QLineEdit, QComboBox, QMessageBox, QDialog,
                           QFormLayout, QCheckBox, QHeaderView, QStyledItemDelegate,
                           QMenu)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QEvent, QPoint
from dotenv import load_dotenv
import os

class CloudflareDNS:
    def __init__(self, api_token: str, zone_id: str):
        """
        初始化Cloudflare DNS管理器
        
        Args:
            api_token (str): Cloudflare API令牌
            zone_id (str): 域名区域ID
        """
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def list_records(self) -> Dict[str, Any]:
        """获取所有DNS记录"""
        response = requests.get(self.base_url, headers=self.headers)
        return response.json()

    def create_record(self, name: str, content: str, type: str, proxied: bool = True) -> Dict[str, Any]:
        """
        创建新的DNS记录
        
        Args:
            name (str): 记录名称
            content (str): 记录内容
            type (str): 记录类型 (A, AAAA, CNAME, MX, TXT, SRV, LOC, NS, SPF)
            proxied (bool): 是否启用Cloudflare代理
        """
        data = {
            "name": name,
            "content": content,
            "type": type,
            "proxied": proxied
        }
        response = requests.post(self.base_url, headers=self.headers, json=data)
        return response.json()

    def update_record(self, record_id: str, name: str, content: str, type: str, proxied: bool = True) -> Dict[str, Any]:
        """
        更新现有DNS记录
        
        Args:
            record_id (str): 记录ID
            name (str): 新的记录名称
            content (str): 新的记录内容
            type (str): 记录类型
            proxied (bool): 是否启用Cloudflare代理
        """
        url = f"{self.base_url}/{record_id}"
        data = {
            "name": name,
            "content": content,
            "type": type,
            "proxied": proxied
        }
        response = requests.put(url, headers=self.headers, json=data)
        return response.json()

    def delete_record(self, record_id: str) -> Dict[str, Any]:
        """
        删除DNS记录
        
        Args:
            record_id (str): 记录ID
        """
        url = f"{self.base_url}/{record_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()


class DNSRecordDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.setWindowTitle("DNS 记录")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.name = QLineEdit()
        self.content = QLineEdit()
        self.type = QComboBox()
        self.type.addItems(['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'LOC', 'NS', 'SPF'])
        self.proxied = QCheckBox()
        self.proxied.setChecked(True)
        
        if record:
            self.name.setText(record['name'])
            self.content.setText(record['content'])
            self.type.setCurrentText(record['type'])
            self.proxied.setChecked(record['proxied'])
        
        layout.addRow("名称:", self.name)
        layout.addRow("内容:", self.content)
        layout.addRow("类型:", self.type)
        layout.addRow("启用代理:", self.proxied)
        
        buttons = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        self.setLayout(layout)


class TypeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dns_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'LOC', 'NS', 'SPF']
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.dns_types)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setCurrentText(value)
    
    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)


class ProxiedDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(['True', 'False'])
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setCurrentText(value)
    
    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cloudflare DNS Manager")
        self.setMinimumSize(800, 600)
        
        # 加载配置
        load_dotenv()
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        
        layout.addLayout(button_layout)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "内容", "类型", "代理"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # 设置表格列宽自适应
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # ID列可手动调整
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # 名称列可手动调整
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # 内容列自动拉伸
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)        # 类型列固定宽度
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)        # 代理列固定宽度
        
        # 设置初始列宽
        self.table.setColumnWidth(0, 200)  # ID列
        self.table.setColumnWidth(1, 150)  # 名称列
        # 内容列宽度由Stretch模式自动计算
        self.table.setColumnWidth(3, 60)   # 类型列
        self.table.setColumnWidth(4, 50)   # 代理列
        
        # 让内容列也适当拉伸
        self.table.horizontalHeader().setStretchLastSection(False)
        
        # 设置类型列和代理列的委托
        self.table.setItemDelegateForColumn(3, TypeDelegate(self.table))
        self.table.setItemDelegateForColumn(4, ProxiedDelegate(self.table))
        
        # 禁用编辑，改为只读模式
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 设置上下文菜单策略
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # 初始化DNS管理器
        self.dns_manager = None
        self.init_dns_manager()
        
        # 刷新记录
        self.refresh_records()
    
    def init_dns_manager(self):
        if self.api_token and self.zone_id:
            self.dns_manager = CloudflareDNS(self.api_token, self.zone_id)
        else:
            QMessageBox.warning(self, "错误", "请在.env文件中配置CLOUDFLARE_API_TOKEN和CLOUDFLARE_ZONE_ID")
    
    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        
        add_action = QAction("添加记录", self)
        refresh_action = QAction("刷新", self)
        
        menu.addAction(add_action)
        menu.addAction(refresh_action)
        
        # 如果有选中的行，添加编辑和删除选项
        current_row = self.table.currentRow()
        if current_row >= 0:
            edit_action = QAction("编辑记录", self)
            delete_action = QAction("删除记录", self)
            menu.addSeparator()
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            
            edit_action.triggered.connect(self.edit_record)
            delete_action.triggered.connect(self.delete_record)
        
        add_action.triggered.connect(self.add_record)
        refresh_action.triggered.connect(self.refresh_records)
        
        # 在鼠标位置显示菜单
        menu.exec(self.table.viewport().mapToGlobal(pos))
    
    def refresh_records(self):
        if not self.dns_manager:
            QMessageBox.warning(self, "错误", "请在.env文件中配置CLOUDFLARE_API_TOKEN和CLOUDFLARE_ZONE_ID")
            return
        
        try:
            response = self.dns_manager.list_records()
            if response.get('success', False):
                records = response['result']
                self.table.setRowCount(len(records))
                
                for i, record in enumerate(records):
                    id_item = QTableWidgetItem(record['id'])
                    self.table.setItem(i, 0, id_item)
                    self.table.setItem(i, 1, QTableWidgetItem(record['name']))
                    self.table.setItem(i, 2, QTableWidgetItem(record['content']))
                    self.table.setItem(i, 3, QTableWidgetItem(record['type']))
                    self.table.setItem(i, 4, QTableWidgetItem(str(record['proxied'])))
            else:
                error_msg = "未知错误"
                if 'errors' in response and len(response['errors']) > 0:
                    error_msg = response['errors'][0].get('message', '未知错误')
                QMessageBox.warning(self, "错误", f"获取记录失败: {error_msg}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"发生错误: {str(e)}")
    
    def add_record(self):
        if not self.dns_manager:
            QMessageBox.warning(self, "错误", "请在.env文件中配置CLOUDFLARE_API_TOKEN和CLOUDFLARE_ZONE_ID")
            return
        
        dialog = DNSRecordDialog(self)
        if dialog.exec():
            try:
                response = self.dns_manager.create_record(
                    name=dialog.name.text(),
                    content=dialog.content.text(),
                    type=dialog.type.currentText(),
                    proxied=dialog.proxied.isChecked()
                )
                
                if response['success']:
                    QMessageBox.information(self, "成功", "记录创建成功")
                    self.refresh_records()
                else:
                    QMessageBox.warning(self, "错误", f"创建记录失败: {response['errors'][0]['message']}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"发生错误: {str(e)}")
    
    def edit_record(self):
        if not self.dns_manager:
            QMessageBox.warning(self, "错误", "请在.env文件中配置CLOUDFLARE_API_TOKEN和CLOUDFLARE_ZONE_ID")
            return
        
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "错误", "请先选择要编辑的记录")
            return
        
        record = {
            'id': self.table.item(current_row, 0).text(),
            'name': self.table.item(current_row, 1).text(),
            'content': self.table.item(current_row, 2).text(),
            'type': self.table.item(current_row, 3).text(),
            'proxied': self.table.item(current_row, 4).text().lower() == 'true'
        }
        
        dialog = DNSRecordDialog(self, record)
        if dialog.exec():
            try:
                response = self.dns_manager.update_record(
                    record_id=record['id'],
                    name=dialog.name.text(),
                    content=dialog.content.text(),
                    type=dialog.type.currentText(),
                    proxied=dialog.proxied.isChecked()
                )
                
                if response['success']:
                    QMessageBox.information(self, "成功", "记录更新成功")
                    self.refresh_records()
                else:
                    QMessageBox.warning(self, "错误", f"更新记录失败: {response['errors'][0]['message']}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"发生错误: {str(e)}")
    
    def delete_record(self):
        if not self.dns_manager:
            QMessageBox.warning(self, "错误", "请在.env文件中配置CLOUDFLARE_API_TOKEN和CLOUDFLARE_ZONE_ID")
            return
        
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "错误", "请先选择要删除的记录")
            return
        
        record_id = self.table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = self.dns_manager.delete_record(record_id)
                
                if response.get('success', False):
                    QMessageBox.information(self, "成功", "记录删除成功")
                    self.refresh_records()
                else:
                    error_msg = "未知错误"
                    if 'errors' in response and len(response['errors']) > 0:
                        error_msg = response['errors'][0].get('message', '未知错误')
                    QMessageBox.warning(self, "错误", f"删除记录失败: {error_msg}")
                    # 刷新以恢复原始数据
                    self.refresh_records()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"发生错误: {str(e)}")
                # 刷新以恢复原始数据
                self.refresh_records()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 