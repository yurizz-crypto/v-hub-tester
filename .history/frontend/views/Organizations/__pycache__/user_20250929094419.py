import os
import json
from typing import List, Dict, Optional
from PyQt6 import QtWidgets, QtCore, QtGui

class User(QtWidgets.QMainWindow):
    def __init__(self, name: str = "User"):
        super().__init__()
        self.name = name
        self.current_org: Optional[Dict] = None
        self.ui = None
        self.no_member_label = None
        self.table = None
        self.officer_count = 0
        self.college_org_count = 0

    @staticmethod
    def _load_data() -> List[Dict]:
        """Load organization and branch data from JSON file."""
        json_path = os.path.join(os.path.dirname(__file__), 'organizations_data.json')
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
                return data.get('organizations', [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {json_path}: {str(e)}")
            return []

    def save_data(self) -> None:
        """Save updated organization data back to JSON file."""
        organizations = self._load_data()
        if self.current_org:
            for org in organizations:
                if org["id"] == self.current_org["id"]:
                    org.update(self.current_org)
                    break
            json_path = os.path.join(os.path.dirname(__file__), 'organizations_data.json')
            try:
                with open(json_path, 'w') as file:
                    json.dump({"organizations": organizations}, file, indent=4)
            except Exception as e:
                print(f"Error saving {json_path}: {str(e)}")

    @staticmethod
    def _get_logo_path(rel_path: str) -> str:
        """Resolve absolute logo path, return relative path if file doesn't exist."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        abs_path = os.path.join(base_dir, rel_path)
        return abs_path if os.path.exists(abs_path) else rel_path

    def set_circular_logo(self, logo_label: QtWidgets.QLabel, logo_path: str, size: int = 200, border_width: int = 4) -> None:
        """Set a circular logo with a border on the given label."""
        logo_label.setFixedSize(size, size)
        if logo_path == "No Photo" or QtGui.QPixmap(logo_path).isNull():
            logo_label.setText("No Logo")
            return

        pixmap = QtGui.QPixmap(logo_path).scaled(size, size, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        centered_pixmap = QtGui.QPixmap(size, size)
        centered_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        
        with QtGui.QPainter(centered_pixmap) as painter:
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            x = (size - pixmap.width()) // 2
            y = (size - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)

        mask = QtGui.QPixmap(size, size)
        mask.fill(QtCore.Qt.GlobalColor.transparent)
        with QtGui.QPainter(mask) as painter:
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.fillPath(path, QtCore.Qt.GlobalColor.white)

        centered_pixmap.setMask(mask.createMaskFromColor(QtCore.Qt.GlobalColor.white, QtCore.Qt.MaskMode.MaskOutColor))

        final_pixmap = QtGui.QPixmap(size, size)
        final_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        with QtGui.QPainter(final_pixmap) as painter:
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setBrush(QtGui.QBrush(centered_pixmap))
            painter.setPen(QtGui.QPen(QtGui.QColor(8, 73, 36), border_width))
            painter.drawEllipse(border_width // 2, border_width // 2, size - border_width, size - border_width)

        logo_label.setPixmap(final_pixmap)

    def show_org_details(self, org_data: Dict) -> None:
        """Display organization details on the details page."""
        self.current_org = org_data
        self.ui.header_label_2.setText("Organization" if not org_data["is_branch"] else "Branch")
        self.ui.status_btn.setText("Active")
        self.ui.org_name.setText(org_data["name"])
        self.ui.org_type.setText("Branch" if org_data["is_branch"] else "Organization")
        self.ui.brief_label.setText(org_data.get("brief", "No brief available"))
        self.ui.obj_label.setText(org_data.get("description", "No description available"))
        self.ui.obj_label_2.setText("\n".join([branch["name"] for branch in org_data.get("branches", [])]) or "No branches available")
        self.set_circular_logo(self.ui.logo, self._get_logo_path(org_data["logo_path"]))
        
        self.ui.officer_history_dp.clear()
        semesters = org_data.get("officer_history", {}).keys()
        self.ui.officer_history_dp.addItem("Current Officers")
        self.ui.officer_history_dp.addItems(sorted(semesters))
        
        self.load_officers(org_data.get("officers", []))
        self.load_events(org_data.get("events", []))
        self.ui.label.setText("A.Y. 2025-2026 - 1st Semester")
        self.ui.stacked_widget.setCurrentIndex(1)

    def load_officers(self, officers: List[Dict]) -> None:
        """Load officer cards into the officer grid."""
        from frontend.widgets.orgs_custom_widgets.cards import OfficerCard
        self._clear_grid(self.ui.officer_cards_grid)
        self.officer_count = 0
        self.ui.officers_scroll_area.verticalScrollBar().setValue(0)

        if not officers:
            self._add_no_record_label(self.ui.officer_cards_grid)
            return

        for officer in officers:
            card = OfficerCard(officer, self)
            col = self.officer_count % 3
            row = self.officer_count // 3
            self.ui.officer_cards_grid.addWidget(card, row, col, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.officer_count += 1
            self.ui.officer_cards_grid.setRowMinimumHeight(row, 400)

    def load_events(self, events: List[Dict]) -> None:
        """Load event cards into the events layout."""
        from frontend.utils.orgs_custom_widgets.cards import EventCard
        while self.ui.verticalLayout_14.count():
            if item := self.ui.verticalLayout_14.takeAt(0).widget():
                item.deleteLater()

        for event in events:
            self.ui.verticalLayout_14.addWidget(EventCard(event, self))

        self.ui.verticalLayout_14.addStretch()
        self.ui.scroll_area_events.verticalScrollBar().setValue(0)

    def _clear_grid(self, grid_layout: QtWidgets.QGridLayout) -> None:
        """Remove all widgets from the given grid layout."""
        for i in reversed(range(grid_layout.count())):
            if widget := grid_layout.itemAt(i).widget():
                widget.setParent(None)

    def _add_no_record_label(self, grid_layout: QtWidgets.QGridLayout) -> None:
        """Add 'No Record(s) Found' label to the grid layout."""
        no_record_label = QtWidgets.QLabel("No Record(s) Found")
        no_record_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        no_record_label.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(no_record_label, 0, 0, 1, 5)

    def _update_scroll_areas(self) -> None:
        """Update scroll areas and geometry."""
        if hasattr(self.ui, 'college_org_scrollable'):
            self.ui.college_org_scrollable.adjustSize()
            self.ui.college_org_scrollable.updateGeometry()
        if hasattr(self.ui, 'joined_org_scrollable'):
            self.ui.joined_org_scrollable.adjustSize()
            self.ui.joined_org_scrollable.updateGeometry()
        self.update()