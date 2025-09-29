from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog

class OfficerDialog(QtWidgets.QDialog):
    def __init__(self, officer_data, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.setFixedSize(400, 300)  # Adjust size as needed

        main_layout = QtWidgets.QVBoxLayout(self)

        # Top layout for close button
        top_layout = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        top_layout.addItem(spacer)
        close_btn = QtWidgets.QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("background-color: transparent; border: none; color: gray;")
        close_btn.clicked.connect(self.close)
        top_layout.addWidget(close_btn)
        main_layout.addLayout(top_layout)

        # Horizontal layout for photo and info
        hlayout = QtWidgets.QHBoxLayout()
        self.photo_label = QtWidgets.QLabel()
        parent.set_circular_logo(self.photo_label, officer_data.get("photo_path", "No Photo"), size=150, border_width=4)
        hlayout.addWidget(self.photo_label)

        vinfo = QtWidgets.QVBoxLayout()
        self.name_label = QtWidgets.QLabel(officer_data.get("name", "Unknown"))
        self.name_label.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Weight.Bold))
        vinfo.addWidget(self.name_label)
        self.position_label = QtWidgets.QLabel(officer_data.get("position", "Unknown Position"))
        vinfo.addWidget(self.position_label)
        self.date_label = QtWidgets.QLabel(f"{officer_data.get('start_date', '07/08/2025')} - Present")
        vinfo.addWidget(self.date_label)
        hlayout.addLayout(vinfo)

        main_layout.addLayout(hlayout)

        cv_btn = QtWidgets.QPushButton("Curriculum Vitae")
        cv_btn.setStyleSheet("background-color: #084924; color: white; border-radius: 5px;")
        contact_btn = QtWidgets.QPushButton("Contact Me")
        contact_btn.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px;")
        main_layout.addWidget(cv_btn)
        main_layout.addWidget(contact_btn)

        if parent.officer_name == officer_data.get("name"):
            edit_btn = QtWidgets.QPushButton("Edit")
            edit_btn.setStyleSheet("background-color: #FFD700; color: black; border: 1px solid #ccc; border-radius: 5px;")
            edit_btn.clicked.connect(lambda: self.open_edit_officer(officer_data))
            main_layout.addWidget(edit_btn)

    def open_edit_officer(self, officer_data):
        dialog = EditOfficerDialog(officer_data, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            updated_data = dialog.updated_data
            self.parent().update_officer_in_org(updated_data)
            self.update_dialog(updated_data)

    def update_dialog(self, officer_data):
        self.parent().set_circular_logo(self.photo_label, officer_data.get("photo_path", "No Photo"), size=150, border_width=4)
        self.position_label.setText(officer_data.get("position", "Unknown Position"))
        self.date_label.setText(f"{officer_data.get('start_date', '07/08/2025')} - Present")

class EditOrgDialog(QtWidgets.QDialog):
    def __init__(self, org_data: dict, parent: QtWidgets.QMainWindow):
        super().__init__(parent)
        self.org_data = org_data
        self.parent_window = parent
        self.setWindowTitle("Edit Organization/Branch Details")
        self.setFixedSize(600, 500)

        main_layout = QtWidgets.QVBoxLayout(self)

        content_layout = QtWidgets.QHBoxLayout()

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setFixedSize(200, 200)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.parent_window.set_circular_logo(self.preview_label, self.parent_window._get_logo_path(org_data["logo_path"]))
        left_layout.addWidget(self.preview_label)

        browse_btn = QtWidgets.QPushButton("Browse Image")
        browse_btn.clicked.connect(self.browse_image)
        left_layout.addWidget(browse_btn)

        content_layout.addWidget(left_widget)

        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)

        right_layout.addWidget(QtWidgets.QLabel("Brief Overview"))
        self.brief_edit = QtWidgets.QTextEdit(org_data.get("brief", ""))
        right_layout.addWidget(self.brief_edit)

        right_layout.addWidget(QtWidgets.QLabel("Objectives"))
        self.desc_edit = QtWidgets.QTextEdit(org_data.get("description", ""))
        right_layout.addWidget(self.desc_edit)

        content_layout.addWidget(right_widget)
        main_layout.addLayout(content_layout)

        btn_layout = QtWidgets.QHBoxLayout()
        confirm_btn = QtWidgets.QPushButton("Confirm")
        confirm_btn.clicked.connect(self.confirm)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.org_data["logo_path"] = file_path
            self.parent_window.set_circular_logo(self.preview_label, file_path)

    def confirm(self):
        self.org_data["brief"] = self.brief_edit.toPlainText()
        self.org_data["description"] = self.desc_edit.toPlainText()

        self.parent_window.ui.brief_label.setText(self.org_data["brief"])
        self.parent_window.ui.obj_label.setText(self.org_data["description"])
        self.parent_window.set_circular_logo(self.parent_window.ui.logo, self.org_data["logo_path"])

        self.parent_window.save_data()

        self.accept()

class EditOfficerDialog(QtWidgets.QDialog):
    def __init__(self, officer_data, parent=None):
        super().__init__(parent)
        self.officer_data = officer_data.copy()
        self.setWindowTitle("Edit Officer Details")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)

        # Photo section
        photo_layout = QtWidgets.QHBoxLayout()
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setFixedSize(150, 150)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        parent.parent().set_circular_logo(self.preview_label, self.officer_data.get("photo_path", "No Photo"), size=150, border_width=4)
        photo_layout.addWidget(self.preview_label)
        browse_btn = QtWidgets.QPushButton("Browse Photo")
        browse_btn.clicked.connect(self.browse_photo)
        photo_layout.addWidget(browse_btn)
        main_layout.addLayout(photo_layout)

        # Position
        main_layout.addWidget(QtWidgets.QLabel("Position:"))
        self.position_edit = QtWidgets.QLineEdit(self.officer_data.get("position", ""))
        main_layout.addWidget(self.position_edit)

        # Start Date
        main_layout.addWidget(QtWidgets.QLabel("Start Date (MM/DD/YYYY):"))
        self.date_edit = QtWidgets.QLineEdit(self.officer_data.get("start_date", ""))
        main_layout.addWidget(self.date_edit)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        confirm_btn = QtWidgets.QPushButton("Confirm")
        confirm_btn.clicked.connect(self.confirm)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

    def browse_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Officer Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.officer_data["photo_path"] = file_path
            self.officer_data["card_image_path"] = file_path
            self.parent().parent().set_circular_logo(self.preview_label, file_path, size=150, border_width=4)

    def confirm(self):
        self.officer_data["position"] = self.position_edit.text()
        self.officer_data["start_date"] = self.date_edit.text()
        self.updated_data = self.officer_data
        self.accept()

class EditMemberDialog(QtWidgets.QDialog):
    def __init__(self, member_data: list, parent=None):
        super().__init__(parent)
        self.member_data = member_data
        self.setWindowTitle("Edit Member Position")
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(QtWidgets.QLabel("Position:"))
        self.position_edit = QtWidgets.QComboBox()
        possible_positions = ["President", "Vice - Internal Chairperson", "Vice - External Chairperson", "Secretary", "Treasurer", "Member"]  # Add your possible positions here
        self.position_edit.addItems(possible_positions)
        self.position_edit.setCurrentText(member_data[1])
        main_layout.addWidget(self.position_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        confirm_btn = QtWidgets.QPushButton("Confirm")
        confirm_btn.clicked.connect(self.confirm)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

    def confirm(self):
        self.updated_position = self.position_edit.currentText()
        self.accept()