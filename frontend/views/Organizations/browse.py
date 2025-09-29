from PyQt6.QtWidgets import QWidget, QVBoxLayout
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # C:\Users\Yuri\Desktop\v-hub-tester
sys.path.insert(0, project_root)  # Insert at start to override other paths

from views.Organizations.student_organization import Student
from views.Organizations.faculty_organization import Faculty
from views.Organizations.officer_organization import Officer
from frontend.views.Organizations.user import User

print(f"Browse: Imported Student={Student is not None}, Faculty={Faculty is not None}, Officer={Officer is not None}")

class Browse(QWidget):
    def __init__(self, username="", roles=None, primary_role="", token=""):
        super().__init__()
        print(f"Browse: Initializing for username={username}, primary_role={primary_role}, roles={roles}")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if primary_role == "faculty":
            print("Browse: Loading Faculty view")
            self.view = Faculty(faculty_name=username)
        elif primary_role == "student":
            if "org_officer" in (roles or []):
                print("Browse: Loading Officer view")
                self.view = Officer(officer_name=username)
            else:
                print("Browse: Loading Student view")
                self.view = Student(student_name=username)
        else:
            print("Browse: Loading default Faculty view")
            self.view = Faculty(faculty_name=username)

        print(f"Browse: View created, type={type(self.view)}, ui={hasattr(self.view, 'ui')}")
        self.layout.addWidget(self.view)
        print("Browse: Widget added to layout")