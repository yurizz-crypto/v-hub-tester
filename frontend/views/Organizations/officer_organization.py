from PyQt6 import QtWidgets
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(project_root)

from typing import Dict
from frontend.views.Organizations.student_organization import Student
from frontend.views.Organizations.manager_base import ManagerBase
from frontend.widgets.orgs_custom_widgets.dialogs import OfficerDialog

class Officer(ManagerBase, Student):
    """Officer view with member and applicant management capabilities."""
    
    def __init__(self, officer_name: str = "Ruben, Stephen Joseph"):
        Student.__init__(self, student_name=officer_name)
        ManagerBase.__init__(self)
        self._setup_officer_connections()
    
    def _setup_officer_connections(self) -> None:
        """Set up additional signal-slot connections for officer-specific functionality."""
        self.ui.view_members_btn.clicked.disconnect()
        self.ui.view_members_btn.clicked.connect(self._to_members_page)
        self.ui.back_btn_member.clicked.disconnect()
        self.ui.back_btn_member.clicked.connect(self._return_to_prev_page)
        self.ui.search_line_3.textChanged.connect(self._perform_member_search)
    
    def show_officer_dialog(self, officer_data: Dict) -> None:
        """Display officer details in a dialog."""
        OfficerDialog(officer_data, self).exec()
    
    def show_org_details(self, org_data: Dict) -> None:
        """Display organization details with officer-specific features."""
        super().show_org_details(org_data)
        self.current_org = org_data
        
        # Clean up existing edit button
        if self.edit_btn:
            self.ui.verticalLayout_10.removeWidget(self.edit_btn)
            self.edit_btn.deleteLater()
            self.edit_btn = None
        
        # Check if current user is an officer
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
            self.ui.header_label_3.setText(
                "Organization" if not self.current_org["is_branch"] else "Branch"
            )
        self.is_viewing_applicants = False
        self.load_members(self._get_search_text())
        self.ui.stacked_widget.setCurrentIndex(2)
    
    def _return_to_prev_page(self) -> None:
        """Navigate back to the previous page, handling applicants view."""
        if self.ui.stacked_widget.currentIndex() == 2:
            if self.is_viewing_applicants:
                self.is_viewing_applicants = False
                self.load_members(self._get_search_text())
            else:
                self.ui.stacked_widget.setCurrentIndex(1)
        else:
            if self.ui.comboBox.currentIndex() == 0:
                self.load_orgs()
            else:
                self.load_branches()
            self.ui.stacked_widget.setCurrentIndex(0)
