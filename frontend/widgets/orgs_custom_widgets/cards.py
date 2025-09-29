from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QPixmap

class JoinedOrgCard(QtWidgets.QFrame):
    def __init__(self, logo_path, more_details, org_data, main_window):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 275)

        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(200, 200)
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        logo_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        if logo_path != "No Photo":
            pixmap = QPixmap(logo_path).scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap)
            else:
                logo_label.setText("No Logo")
        else:
            logo_label.setText("No Logo")

        btn_details = QtWidgets.QPushButton(more_details)
        btn_details.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        btn_details.clicked.connect(lambda: main_window.show_org_details(org_data))

        layout.addWidget(logo_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(btn_details)

class CollegeOrgCard(QtWidgets.QFrame):
    def __init__(self, logo_path, description, more_details, org_data, main_window):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 275)

        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(200, 200)
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        logo_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        if logo_path != "No Photo":
            pixmap = QPixmap(logo_path).scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap)
            else:
                logo_label.setText("No Logo")
        else:
            logo_label.setText("No Logo")

        desc_label = QtWidgets.QLabel()
        desc_label.setText(description)
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        desc_label.setWordWrap(True)

        btn_details = QtWidgets.QPushButton(more_details)
        btn_apply = QtWidgets.QPushButton("Apply")
        btn_details.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        btn_apply.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        btn_details.clicked.connect(lambda: main_window.show_org_details(org_data))

        layout.addWidget(logo_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(desc_label)
        layout.addWidget(btn_details)
        layout.addWidget(btn_apply)

class OfficerCard(QtWidgets.QFrame):
    def __init__(self, officer_data, main_window):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMinimumSize(250, 350)

        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        # Top spacer to center content vertically
        top_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        layout.addItem(top_spacer)

        image_label = QtWidgets.QLabel()
        image_label.setFixedSize(200, 250)
        image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

        if "card_image_path" in officer_data and officer_data["card_image_path"] != "No Photo":
            pixmap = QPixmap(officer_data["card_image_path"]).scaled(200, 250, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            if not pixmap.isNull():
                image_label.setPixmap(pixmap)
            else:
                image_label.setText("No Image")
        else:
            image_label.setText("No Image")

        name_label = QtWidgets.QLabel(officer_data.get("name", "Unknown"))
        name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        position_label = QtWidgets.QLabel(officer_data.get("position", "Unknown Position"))
        position_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        btn_details = QtWidgets.QPushButton("Officer Details")
        btn_details.setStyleSheet("background-color: #FFD700; color: black; border-radius: 5px;")
        btn_details.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        btn_details.clicked.connect(lambda: main_window.show_officer_dialog(officer_data))

        layout.addWidget(image_label)
        layout.addWidget(name_label)
        layout.addWidget(position_label)
        layout.addWidget(btn_details)

        # Bottom spacer to maintain vertical centering
        bottom_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        layout.addItem(bottom_spacer)

class EventCard(QtWidgets.QFrame):
    def __init__(self, event_data, main_window):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(125)  # Adjusted height to fit the design
        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 5px;
            }
            QFrame#eventHeader {
                background-color: #084924;
                color: #fff;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 5px;
            }
        """)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header section
        header = QtWidgets.QFrame(self)
        header.setObjectName("eventHeader")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 10, 0)

        name_label = QtWidgets.QLabel(event_data.get("name", "Unknown Event"))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        date_label = QtWidgets.QLabel(event_data.get("date", "No Date"))
        date_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        header_layout.addWidget(name_label)
        header_layout.addWidget(date_label)
        main_layout.addWidget(header)

        # Content section
        content_label = QtWidgets.QLabel(event_data.get("description", "No Description"))
        content_label.setStyleSheet("padding: 10px; font-size: 12px;")
        content_label.setWordWrap(True)
        content_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(content_label)