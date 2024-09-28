import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTextEdit, QListWidget, QLabel,
                             QInputDialog, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'chat_flow_config.json')

class PromptEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle('Visual Prompt Editor')
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for flow steps
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.flow_list = QListWidget()
        left_layout.addWidget(QLabel("Chat Flow Steps:"))
        left_layout.addWidget(self.flow_list)

        btn_layout = QHBoxLayout()
        self.add_step_btn = QPushButton("Add Step")
        self.remove_step_btn = QPushButton("Remove Step")
        self.move_up_btn = QPushButton("Move Up")
        self.move_down_btn = QPushButton("Move Down")
        btn_layout.addWidget(self.add_step_btn)
        btn_layout.addWidget(self.remove_step_btn)
        btn_layout.addWidget(self.move_up_btn)
        btn_layout.addWidget(self.move_down_btn)
        left_layout.addLayout(btn_layout)

        # Right panel for editing prompts
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_content = QWidget()
        right_layout = QVBoxLayout(right_content)

        self.step_name = QLineEdit()
        right_layout.addWidget(QLabel("Step Name:"))
        right_layout.addWidget(self.step_name)

        self.prompt = QTextEdit()
        right_layout.addWidget(QLabel("Prompt:"))
        right_layout.addWidget(self.prompt)

        self.evaluation = QTextEdit()
        right_layout.addWidget(QLabel("Evaluation:"))
        right_layout.addWidget(self.evaluation)

        self.save_btn = QPushButton("Save Changes")
        right_layout.addWidget(self.save_btn)

        right_panel.setWidget(right_content)

        # System Prompt Editor
        self.system_prompt = QTextEdit()
        left_layout.addWidget(QLabel("System Prompt:"))
        left_layout.addWidget(self.system_prompt)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

        # Connect signals
        self.flow_list.currentItemChanged.connect(self.update_prompt_view)
        self.add_step_btn.clicked.connect(self.add_step)
        self.remove_step_btn.clicked.connect(self.remove_step)
        self.move_up_btn.clicked.connect(self.move_step_up)
        self.move_down_btn.clicked.connect(self.move_step_down)
        self.save_btn.clicked.connect(self.save_changes)

    def load_config(self):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.update_flow_list()
        self.system_prompt.setPlainText(self.config.get('system_prompt', ''))

    def update_flow_list(self):
        self.flow_list.clear()
        for step in self.config['flow']:
            self.flow_list.addItem(step['step'])

    def update_prompt_view(self, current, previous):
        if not current:
            return
        step = next(s for s in self.config['flow'] if s['step'] == current.text())
        self.step_name.setText(step['step'])
        self.prompt.setPlainText(step['prompt'])
        self.evaluation.setPlainText(step['evaluation'])

    def add_step(self):
        step_name, ok = QInputDialog.getText(self, "Add Step", "Enter step name:")
        if ok and step_name:
            new_step = {
                "step": step_name,
                "prompt": "",
                "evaluation": ""
            }
            self.config['flow'].append(new_step)
            self.update_flow_list()
            self.flow_list.setCurrentRow(self.flow_list.count() - 1)

    def remove_step(self):
        current_item = self.flow_list.currentItem()
        if current_item:
            self.config['flow'] = [s for s in self.config['flow'] if s['step'] != current_item.text()]
            self.update_flow_list()

    def move_step_up(self):
        current_row = self.flow_list.currentRow()
        if current_row > 0:
            self.config['flow'][current_row], self.config['flow'][current_row-1] = self.config['flow'][current_row-1], self.config['flow'][current_row]
            self.update_flow_list()
            self.flow_list.setCurrentRow(current_row - 1)

    def move_step_down(self):
        current_row = self.flow_list.currentRow()
        if current_row < self.flow_list.count() - 1:
            self.config['flow'][current_row], self.config['flow'][current_row+1] = self.config['flow'][current_row+1], self.config['flow'][current_row]
            self.update_flow_list()
            self.flow_list.setCurrentRow(current_row + 1)

    def save_changes(self):
        current_item = self.flow_list.currentItem()
        if current_item:
            step = next(s for s in self.config['flow'] if s['step'] == current_item.text())
            step['step'] = self.step_name.text()
            step['prompt'] = self.prompt.toPlainText()
            step['evaluation'] = self.evaluation.toPlainText()

        self.config['system_prompt'] = self.system_prompt.toPlainText()

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        self.update_flow_list()
        QMessageBox.information(self, "Save Successful", "Changes have been saved successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PromptEditor()
    ex.show()
    sys.exit(app.exec_())