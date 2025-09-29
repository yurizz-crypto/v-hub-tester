from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox
import sys

import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from typing import Dict, Optional
from user import User
from frontend.utils.orgs_custom_widgets.dialogs import OfficerDialog, EditMemberDialog, EditOrgDialog
from frontend.utils.orgs_custom_widgets.tables import ViewMembers, ViewApplicants
from frontend.ui.org_main_ui import Ui_MainWindow

class Faculty(User):
    def __init__(self, faculty_name: str = "Faculty Name"):
        super().__init__(name=faculty_name)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.joined_container.setVisible(False)
        self.edit_btn: Optional[QtWidgets.QPushButton] = None
        self.manage_applicants_btn: Optional[QtWidgets.QPushButton] = None
        self.is_managing: bool = True
        self.is_viewing_applicants: bool = False
        self.table = self.findChild(QtWidgets.QTableView, "list_view")
        self._setup_no_member_label()
        self.ui.verticalLayout_17.addWidget(self.no_member_label)
        self._setup_connections()
        self.load_orgs()

    def _setup_connections(self) -> None:
        """Set up signal-slot connections."""
        self.ui.comboBox.currentIndexChanged.connect(self._on_combobox_changed)
        self.ui.view_members_btn.clicked.connect(self._to_members_page)
        self.ui.back_btn_member.clicked.connect(self._return_to_prev_page)
        self.ui.back_btn.clicked.connect(self._return_to_prev_page)
        self.ui.search_line.textChanged.connect(self._perform_search)
        self.ui.search_line_3.textChanged.connect(self._perform_member_search)
        self.ui.officer_history_dp.currentIndexChanged.connect(self._on_officer_history_changed)

    def _setup_no_member_label(self) -> None:
        """Initialize the 'No Record(s) Found' label for members or applicants."""
        self.no_member_label = QtWidgets.QLabel("No Record(s) Found", self.ui.list_container)
        self.no_member_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.no_member_label.setStyleSheet("font-size: 20px;")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
        self.no_member_label.setSizePolicy(sizePolicy)
        self.no_member_label.hide()

    def _perform_search(self) -> None:
        """Handle organization/branch search."""
        search_text = self.ui.search_line.text().strip().lower()
        self.load_orgs(search_text) if self.ui.comboBox.currentIndex() == 0 else self.load_branches(search_text)

    def _perform_member_search(self) -> None:
        """Handle member or applicant search based on current view."""
        search_text = self.ui.search_line_3.text().strip().lower()
        if self.is_viewing_applicants:
            self.load_applicants(search_text)
        else:
            self.load_members(search_text)

    def load_orgs(self, search_text: str = "") -> None:
        """Load and display organizations, filtered by search text."""
        organizations = self._load_data()
        self._clear_grid(self.ui.college_org_grid)
        self.college_org_count = 0

        filtered_college = [org for org in organizations if not org["is_branch"] and (search_text in org["name"].lower() or not search_text)]
        for org in filtered_college:
            self._add_college_org(org)

        if self.college_org_count == 0:
            self._add_no_record_label(self.ui.college_org_grid)

        self._update_scroll_areas()

    def load_branches(self, search_text: str = "") -> None:
        """Load and display branches, filtered by search text."""
        organizations = self._load_data()
        self._clear_grid(self.ui.college_org_grid)
        self.college_org_count = 0

        filtered_college_branches = []
        for org in organizations:
            for branch in org.get("branches", []):
                if search_text in branch["name"].lower() or not search_text:
                    filtered_college_branches.append(branch)

        for branch in filtered_college_branches:
            self._add_college_org(branch)

        if self.college_org_count == 0:
            self._add_no_record_label(self.ui.college_org_grid)

        self._update_scroll_areas()

    def hide_apply_buttons(self) -> None:
        """Hide all apply buttons in the UI."""
        for child in self.ui.college_org_scrollable.findChildren(QtWidgets.QPushButton):
            if child.text() == "Apply":
                child.setVisible(False)

    def show_org_details(self, org_data: Dict) -> None:
        """Display organization details with faculty-specific features."""
        super().show_org_details(org_data)
        self.current_org = org_data
        self.ui.view_members_btn.setText("Manage Members")
        if self.edit_btn is None:
            self.edit_btn = QtWidgets.QPushButton("Edit")
            self.edit_btn.setObjectName("edit_btn")
            self.edit_btn.clicked.connect(self.open_edit_dialog)
            desc_index = self.ui.verticalLayout_10.indexOf(self.ui.derscription_container)
            self.ui.verticalLayout_10.insertWidget(desc_index + 1, self.edit_btn)

    def open_edit_dialog(self):
        """Open the edit dialog for current org."""
        if self.current_org:
            dialog = EditOrgDialog(self.current_org, self)
            dialog.exec()

    def _add_college_org(self, org_data: Dict) -> None:
        """Add a college organization card to the grid."""
        from frontend.utils.orgs_custom_widgets.cards import CollegeOrgCard
        card = CollegeOrgCard(
            self._get_logo_path(org_data["logo_path"]), org_data["description"],
            org_data["details"], org_data, self
        )
        col = self.college_org_count % 5
        row = self.college_org_count // 5
        self.ui.college_org_grid.addWidget(card, row, col, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.college_org_count += 1
        self.ui.college_org_grid.setRowMinimumHeight(row, 300)

    def load_members(self, search_text: str = "") -> None:
        """Load and filter members into the table view."""
        if not self.current_org:
            return

        members_data = self.current_org.get("members", [])
        filtered_members = [
            member for member in members_data
            if any(search_text in str(field).lower() for field in member)
        ] if search_text else members_data

        self.ui.list_view.setModel(None)
        self.ui.list_view.clearSpans()
        self.ui.list_view.verticalHeader().reset()

        model = ViewMembers(filtered_members, is_managing=self.is_managing)
        self.ui.list_view.setModel(model)
        self.ui.list_view.horizontalHeader().setStretchLastSection(True)
        self.ui.list_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        if filtered_members:
            self.ui.list_view.show()
            self.no_member_label.hide()
        else:
            self.ui.list_view.hide()
            self.no_member_label.show()

        if self.manage_applicants_btn:
            self.ui.verticalLayout_16.removeWidget(self.manage_applicants_btn)
            self.manage_applicants_btn.deleteLater()
            self.manage_applicants_btn = None
            self.ui.verticalLayout_16.removeItem(self.ui.verticalLayout_16.itemAt(0))
            self.ui.verticalLayout_16.insertWidget(0, self.ui.label_2)
            self.ui.verticalLayout_16.addWidget(self.ui.line_5)

        if self.is_managing:
            for row in range(len(filtered_members)):
                action_widget = QtWidgets.QWidget()
                hlayout = QtWidgets.QHBoxLayout(action_widget)
                hlayout.setContentsMargins(5, 5, 5, 5)
                hlayout.setSpacing(5)

                edit_btn = QtWidgets.QPushButton("Edit")
                edit_btn.setStyleSheet("background-color: green; color: white; border-radius: 5px;")
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_member(r))

                kick_btn = QtWidgets.QPushButton("Kick")
                kick_btn.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                kick_btn.clicked.connect(lambda checked, r=row: self.kick_member(r))

                hlayout.addWidget(edit_btn)
                hlayout.addWidget(kick_btn)

                self.ui.list_view.setIndexWidget(model.index(row, model.columnCount() - 1), action_widget)

            self.ui.verticalLayout_16.removeWidget(self.ui.label_2)
            self.ui.verticalLayout_16.removeWidget(self.ui.line_5)
            header_hlayout = QtWidgets.QHBoxLayout()
            self.ui.label_2.setText("Member List")
            header_hlayout.addWidget(self.ui.label_2)
            header_hlayout.addStretch()
            self.manage_applicants_btn = QtWidgets.QPushButton("Manage Applicants")
            self.manage_applicants_btn.setStyleSheet("background-color: #084924; color: white; border-radius: 5px;")
            self.manage_applicants_btn.clicked.connect(lambda: self.load_applicants(self.ui.search_line_3.text().strip().lower()))
            header_hlayout.addWidget(self.manage_applicants_btn)
            self.ui.verticalLayout_16.insertLayout(0, header_hlayout)
            self.ui.verticalLayout_16.addWidget(self.ui.line_5)

    def load_applicants(self, search_text: str = ""):
        """Load and filter applicants into the table view."""
        if not self.current_org:
            return

        applicants_data = self.current_org.get("applicants", [])
        filtered_applicants = [
            applicant for applicant in applicants_data
            if any(search_text in str(field).lower() for field in applicant)
        ] if search_text else applicants_data

        self.ui.list_view.setModel(None)
        self.ui.list_view.clearSpans()
        self.ui.list_view.verticalHeader().reset()

        model = ViewApplicants(filtered_applicants)
        self.ui.list_view.setModel(model)
        self.ui.list_view.horizontalHeader().setStretchLastSection(True)
        self.ui.list_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        if filtered_applicants:
            self.ui.list_view.show()
            self.no_member_label.hide()
        else:
            self.ui.list_view.hide()
            self.no_member_label.show()

        for row in range(len(filtered_applicants)):
            action_widget = QtWidgets.QWidget()
            hlayout = QtWidgets.QHBoxLayout(action_widget)
            hlayout.setContentsMargins(5, 5, 5, 5)
            hlayout.setSpacing(5)

            accept_btn = QtWidgets.QPushButton("Accept")
            accept_btn.setStyleSheet("background-color: green; color: white; border-radius: 5px;")
            accept_btn.clicked.connect(lambda checked, r=row: self.accept_applicant(r))

            decline_btn = QtWidgets.QPushButton("Decline")
            decline_btn.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
            decline_btn.clicked.connect(lambda checked, r=row: self.decline_applicant(r))

            hlayout.addWidget(accept_btn)
            hlayout.addWidget(decline_btn)

            self.ui.list_view.setIndexWidget(model.index(row, model.columnCount() - 1), action_widget)

        self.ui.verticalLayout_16.removeWidget(self.ui.label_2)
        self.ui.verticalLayout_16.removeWidget(self.ui.line_5)
        header_hlayout = QtWidgets.QHBoxLayout()
        self.ui.label_2.setText("Applicant List")
        header_hlayout.addWidget(self.ui.label_2)
        header_hlayout.addStretch()
        self.ui.verticalLayout_16.insertLayout(0, header_hlayout)
        self.ui.verticalLayout_16.addWidget(self.ui.line_5)

        self.is_viewing_applicants = True

    def accept_applicant(self, row: int):
        """Confirm and move applicant to members."""
        search_text = self.ui.search_line_3.text().strip().lower()
        applicants = self.current_org.get("applicants", [])
        filtered_applicants = [
            applicant for applicant in applicants
            if any(search_text in str(field).lower() for field in applicant)
        ] if search_text else applicants

        if row >= len(filtered_applicants):
            return

        filtered_applicant = filtered_applicants[row]
        original_index = next((i for i, app in enumerate(applicants) if app[0] == filtered_applicant[0]), None)

        if original_index is None:
            return

        applicant = applicants[original_index]
        confirm = QMessageBox.question(
            self,
            "Confirm Accept",
            f"Are you sure you want to accept {applicant[0]} as a member?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.current_org["applicants"].pop(original_index)
            self.current_org["members"].append([
                applicant[0], applicant[1], "Active",
                QtCore.QDate.currentDate().toString("yyyy-MM-dd")
            ])
            self.save_data()
            self.load_applicants(search_text)

    def decline_applicant(self, row: int):
        """Confirm and remove applicant from list."""
        search_text = self.ui.search_line_3.text().strip().lower()
        applicants = self.current_org.get("applicants", [])
        filtered_applicants = [
            applicant for applicant in applicants
            if any(search_text in str(field).lower() for field in applicant)
        ] if search_text else applicants

        if row >= len(filtered_applicants):
            return

        filtered_applicant = filtered_applicants[row]
        original_index = next((i for i, app in enumerate(applicants) if app[0] == filtered_applicant[0]), None)

        if original_index is None:
            return

        applicant = applicants[original_index]
        confirm = QMessageBox.question(
            self,
            "Confirm Decline",
            f"Are you sure you want to decline {applicant[0]}'s application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.current_org["applicants"].pop(original_index)
            self.save_data()
            self.load_applicants(search_text)

    def edit_member(self, row: int) -> None:
        """Open dialog to edit member's position."""
        if not self.current_org:
            return
        search_text = self.ui.search_line_3.text().strip().lower()
        members = self.current_org.get("members", [])
        filtered_members = [
            member for member in members
            if any(search_text in str(field).lower() for field in member)
        ] if search_text else members
        
        if row >= len(filtered_members):
            return
        
        filtered_member = filtered_members[row]
        original_index = next((i for i, mem in enumerate(members) if mem[0] == filtered_member[0]), None)
        
        if original_index is None:
            return
        
        member = self.current_org["members"][original_index]
        dialog = EditMemberDialog(member, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_position = dialog.updated_position
            self.current_org["members"][original_index][1] = new_position
            self.save_data()
            self.load_members(search_text)

    def kick_member(self, row: int) -> None:
        """Remove a member from the organization."""
        if not self.current_org:
            return
        search_text = self.ui.search_line_3.text().strip().lower()
        members = self.current_org.get("members", [])
        filtered_members = [
            member for member in members
            if any(search_text in str(field).lower() for field in member)
        ] if search_text else members
        
        if row >= len(filtered_members):
            return
        
        filtered_member = filtered_members[row]
        original_index = next((i for i, mem in enumerate(members) if mem[0] == filtered_member[0]), None)
        
        if original_index is None:
            return
        
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirm Kick",
            f"Are you sure you want to kick {members[original_index][0]}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.current_org["members"][original_index]
            self.save_data()
            self.load_members(search_text)

    def _on_combobox_changed(self, index: int) -> None:
        """Handle combo box change to switch between organizations and branches."""
        self.ui.college_label.setText("College Organization(s)" if index == 0 else "College Branch(es)")
        self.load_orgs() if self.ui.comboBox.currentIndex() == 0 else self.load_branches()
        self.ui.college_org_scrollable.verticalScrollBar().setValue(0)

    def _on_officer_history_changed(self, index: int) -> None:
        """Handle officer history combobox change."""
        if not self.current_org:
            return
        selected_semester = self.ui.officer_history_dp.itemText(index)
        officers = self.current_org.get("officer_history", {}).get(selected_semester, []) if selected_semester != "Current Officers" else self.current_org.get("officers", [])
        self.load_officers(officers)

    def _to_members_page(self) -> None:
        """Navigate to the members page."""
        if self.current_org:
            self.ui.header_label_3.setText("Organization" if not self.current_org["is_branch"] else "Branch")
        self.is_viewing_applicants = False
        self.load_members(self.ui.search_line_3.text().strip().lower())
        self.ui.stacked_widget.setCurrentIndex(2)

    def _return_to_prev_page(self) -> None:
        """Navigate back to the previous page, handling applicants view."""
        if self.ui.stacked_widget.currentIndex() == 2:
            if self.is_viewing_applicants:
                self.is_viewing_applicants = False
                self.load_members(self.ui.search_line_3.text().strip().lower())
            else:
                self.ui.stacked_widget.setCurrentIndex(1)
        else:
            self.load_orgs() if self.ui.comboBox.currentIndex() == 0 else self.load_branches()
            self.ui.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Faculty()
    window.show()
    sys.exit(app.exec())