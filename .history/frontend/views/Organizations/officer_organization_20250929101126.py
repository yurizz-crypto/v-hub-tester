from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox
import sys

import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  # Adjust to reach project root
sys.path.append(project_root)
from typing import Dict, Optional
from student_organization import Student
from frontend.widgets.orgs_custom_widgets.dialogs import OfficerDialog, EditMemberDialog, EditOrgDialog
from frontend.widgets.orgs_custom_widgets.tables import ViewMembers, ViewApplicants

class Officer(Student):
    def __init__(self, officer_name: str = "Ruben, Stephen Joseph"):
        super().__init__(student_name=officer_name)
        self.is_managing: bool = False
        self.is_viewing_applicants: bool = False
        self.edit_btn: Optional[QtWidgets.QPushButton] = None
        self.manage_applicants_btn: Optional[QtWidgets.QPushButton] = None
        self._setup_officer_connections()

    def _setup_officer_connections(self) -> None:
        """Set up additional signal-slot connections for officer-specific functionality."""
        self.ui.view_members_btn.clicked.disconnect()
        self.ui.view_members_btn.clicked.connect(self._to_members_page)
        self.ui.back_btn_member.clicked.disconnect()
        self.ui.back_btn_member.clicked.connect(self._return_to_prev_page)
        self.ui.search_line_3.textChanged.connect(self._perform_member_search)

    def _perform_member_search(self) -> None:
        """Handle member or applicant search based on current view."""
        search_text = self.ui.search_line_3.text().strip().lower()
        if self.is_viewing_applicants:
            self.load_applicants(search_text)
        else:
            self.load_members(search_text)

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
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Accept",
            f"Are you sure you want to accept {applicant[0]} as a member?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
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
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm Decline",
            f"Are you sure you want to decline {applicant[0]}'s application?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            self.current_org["applicants"].pop(original_index)
            self.save_data()
            self.load_applicants(search_text)

    def open_edit_dialog(self):
        """Open the edit dialog for current org."""
        if self.current_org:
            dialog = EditOrgDialog(self.current_org, self)
            dialog.exec()

    def show_org_details(self, org_data: Dict) -> None:
        """Display organization details with officer-specific features."""
        super().show_org_details(org_data)
        self.current_org = org_data
        if self.edit_btn:
            self.ui.verticalLayout_10.removeWidget(self.edit_btn)
            self.edit_btn.deleteLater()
            self.edit_btn = None

        officers = org_data.get("officers", [])
        officer_names = [off.get("name", "") for off in officers]
        self.is_managing = self.name in officer_names
        if self.is_managing:
            self.ui.view_members_btn.setText("Manage Members")
            self.edit_btn = QtWidgets.QPushButton("Edit")
            self.edit_btn.setObjectName("edit_btn")
            self.edit_btn.clicked.connect(self.open_edit_dialog)
            desc_index = self.ui.verticalLayout_10.indexOf(self.ui.derscription_container)
            self.ui.verticalLayout_10.insertWidget(desc_index + 1, self.edit_btn)
        else:
            self.ui.view_members_btn.setText("View Members")

    def _to_members_page(self) -> None:
        """Navigate to the members page with officer-specific view."""
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

    def update_officer_in_org(self, updated_officer: Dict) -> None:
        """Update the officer data in the current organization and save."""
        if not self.current_org:
            return
        if "officers" in self.current_org:
            for i, off in enumerate(self.current_org["officers"]):
                if off["name"] == updated_officer["name"]:
                    self.current_org["officers"][i] = updated_officer
                    break
        if "officer_history" in self.current_org:
            for semester, offs in self.current_org["officer_history"].items():
                for i, off in enumerate(offs):
                    if off["name"] == updated_officer["name"]:
                        self.current_org["officer_history"][semester][i] = updated_officer
                        break
        self.save_data()
        current_index = self.ui.officer_history_dp.currentIndex()
        selected_semester = self.ui.officer_history_dp.itemText(current_index)
        officers = self.current_org.get("officer_history", {}).get(selected_semester, []) if selected_semester != "Current Officers" else self.current_org.get("officers", [])
        self.load_officers(officers)

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
        
        confirm = QMessageBox.question(
            self, "Confirm Kick",
            f"Are you sure you want to kick {members[original_index][0]}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            del self.current_org["members"][original_index]
            self.save_data()
            self.load_members(search_text)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Officer()
    window.show()
    sys.exit(app.exec())