import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QListWidget, QWidget, QTabWidget, QMessageBox, QCalendarWidget, QFormLayout, QDialog
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication
#from loading_screen import LoadingScreen  # Import the loading screen class

#app = QApplication([])

# Initialize and show the loading screen
'''loading_screen = LoadingScreen() #check if working in school
loading_screen.show()'''

try:
    conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234"
            )
    
    cur=conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS studyscheduler")
    print("Database STUDYSCHEDULER has been created successfully")
    cur.execute("USE studyscheduler")
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
                """)
    print("Table USERS created successfully")
    cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INT PRIMARY KEY AUTO_INCREMENT,
                    subject VARCHAR(255) NOT NULL,
                    task_description TEXT NOT NULL,
                    note TEXT,
                    due_date DATE,
                    user_id INT,
                    iscomplete TINYINT(1) DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
                """)
    print("Table tasks created successfully")
except mysql.connector.Error as e:
    print("Error:",e)



# Database Authentication
def authenticate_user(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="studyscheduler"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            return user[0]  # Return user id
        else:
            return None
    except mysql.connector.Error as err:
        QMessageBox.critical(None, "Database Error", f"Error: {err}")
        return None

# Function to create a new user in the database
def create_new_user(username, password):
    if username and password:
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            QMessageBox.information(None, "Success", "New user created successfully!")
        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")
    else:
        QMessageBox.warning(None, "Missing Information", "Please fill all fields.")

# MainWindow for the Application
class MainWindow(QMainWindow):#BLANK SCREEN PUT LOADING SCREEN HERE
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Planner")
        self.setGeometry(100, 100, 800, 600)

        self.login_ui()

    def login_ui(self):
        self.login_window = LoginWindow()
        self.login_window.show()

# Login Window to authenticate the user
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 300, 400, 200)

        layout = QFormLayout()
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.authenticate)

        # New User Button
        self.new_user_button = QPushButton("New User", self)
        self.new_user_button.clicked.connect(self.open_new_user_dialog)

        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.new_user_button)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user_id = authenticate_user(username, password)

        if user_id:
            self.accept()  # Close the login window and open the main window
            self.main_window = MainApp(user_id)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Authentication Failed", "Invalid username or password.")

    def open_new_user_dialog(self):
        dialog = NewUserDialog()
        dialog.exec_()

# Dialog for new user registration
class NewUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New User")
        self.setGeometry(500, 300, 400, 200)

        layout = QFormLayout()
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.create_button = QPushButton("Create", self)
        self.create_button.clicked.connect(self.create_user)

        layout.addRow("New Username:", self.username_input)
        layout.addRow("New Password:", self.password_input)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        create_new_user(username, password)
        self.accept()  # Close the dialog

# Main App for managing tasks and calendars
class MainApp(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Study Planner")
        self.setGeometry(100, 100, 1000, 600)
        self.user_id = user_id

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(MainCalendar(self.user_id), "Main Calendar")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Physics"), "Physics")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Chemistry"), "Chemistry")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Math"), "Math")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Computer Science"), "Computer Science")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "English"), "English")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Tutions"), "Tutions")
        self.tabs.addTab(SubjectTaskManagement(self.user_id, "Other"), "Other")

        self.show()

# Calendar for the main page
# Calendar for the main page
# Update the MainCalendar class to include the tab widget with "Pending Tasks", "Completed Tasks", and "Backlog" tabs.
class MainCalendar(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        layout = QVBoxLayout()

        # Main Tab Widget for Pending, Completed, and Backlog Tasks
        self.tab_widget = QTabWidget(self)
        
        # Pending Tasks Tab
        self.pending_tasks_tab = QWidget()
        self.pending_tasks_list = QListWidget(self.pending_tasks_tab)
        self.load_pending_tasks()
        pending_layout = QVBoxLayout()
        pending_layout.addWidget(self.pending_tasks_list)
        self.pending_tasks_tab.setLayout(pending_layout)
        self.tab_widget.addTab(self.pending_tasks_tab, "Pending Tasks")

        # Completed Tasks Tab
        self.completed_tasks_tab = QWidget()
        self.completed_tasks_list = QListWidget(self.completed_tasks_tab)
        self.load_completed_tasks()
        completed_layout = QVBoxLayout()
        completed_layout.addWidget(self.completed_tasks_list)
        self.completed_tasks_tab.setLayout(completed_layout)
        self.tab_widget.addTab(self.completed_tasks_tab, "Completed Tasks")

        # Backlog Tab
        self.backlog_tab = QWidget()
        self.backlog_list = QListWidget(self.backlog_tab)
        self.load_backlog_tasks()
        backlog_layout = QVBoxLayout()
        backlog_layout.addWidget(self.backlog_list)
        self.backlog_tab.setLayout(backlog_layout)
        self.tab_widget.addTab(self.backlog_tab, "Backlog")

        # Add the tab widget to the main layout
        layout.addWidget(self.tab_widget)

        # Calendar widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.load_tasks_for_selected_date)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)#removes week number
        layout.addWidget(self.calendar)

        # Task list below the calendar
        self.task_list = QListWidget(self)
        layout.addWidget(self.task_list)

        self.setLayout(layout)

        # Load tasks for today's date by default
        self.load_tasks_for_selected_date()

    def load_tasks_for_selected_date(self):
        """Load tasks for the date selected in the calendar, including notes."""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
        # Clear the task list
        self.task_list.clear()

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT subject, task_description, note FROM tasks
                WHERE user_id=%s AND due_date=%s
            """, (self.user_id, selected_date))
            tasks = cur.fetchall()
            conn.close()

            # Display each task in the task list with notes
            if tasks:
                for subject, task_description, note in tasks:
                    self.task_list.addItem(f"{subject}: {task_description}\nNote: {note}")
            else:
                self.task_list.addItem("No data for selected date")

        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")

    def load_pending_tasks(self):
        """Load tasks that are pending (not completed) and display them with the days remaining."""
        self.pending_tasks_list.clear()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT subject, task_description, due_date FROM tasks
                WHERE user_id=%s AND iscomplete=0
            """, (self.user_id,))
            print('works')
            tasks = cur.fetchall()
            print(tasks)
            conn.close()

            today = QDate.currentDate()
            for subject, task_description, due_date in tasks:
                due_date_obj = QDate.fromString(due_date.strftime("%Y-%m-%d"), "yyyy-MM-dd")

                days_left = today.daysTo(due_date_obj)
                self.pending_tasks_list.addItem(f"{subject}: {task_description} - Due in {days_left} days ({due_date})")

        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")
            
    

    def load_completed_tasks(self):
        """Load tasks that have been marked as completed."""
        self.completed_tasks_list.clear()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT subject, task_description, due_date FROM tasks
                WHERE user_id=%s AND iscomplete=1
            """, (self.user_id,))
            tasks = cur.fetchall()
            conn.close()

            for subject, task_description, due_date in tasks:
                self.completed_tasks_list.addItem(f"{subject}: {task_description} - Completed on {due_date}")

        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")

    def load_backlog_tasks(self):
        """Load tasks that are overdue and not completed, displaying them with 'NOT DONE!'."""
        self.backlog_list.clear()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT subject, task_description, due_date FROM tasks
                WHERE user_id=%s AND iscomplete=0 AND due_date < CURDATE()
            """, (self.user_id,))
            tasks = cur.fetchall()
            conn.close()

            for subject, task_description, due_date in tasks:
                self.backlog_list.addItem(f"{subject}: {task_description} - Due on {due_date} - NOT DONE!")

        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")


# Task Management for each Subject
class SubjectTaskManagement(QWidget):
    def __init__(self, user_id, subject):
        super().__init__()
        self.user_id = user_id
        self.subject = subject
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Input fields for adding tasks
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText(f"Enter task for {self.subject}")
        
        self.note_input = QTextEdit(self)
        self.note_input.setPlaceholderText("Enter notes for the task")

        self.due_date_input = QLineEdit(self)
        self.due_date_input.setPlaceholderText("Enter due date (YYYY-MM-DD)")

        self.add_button = QPushButton(f"Add {self.subject} Task", self)
        self.add_button.clicked.connect(self.add_task)
        
        self.complete_button = QPushButton("Complete Task", self)
        self.complete_button.clicked.connect(self.complete_task)

        self.remove_button = QPushButton(f"Remove {self.subject} Task", self)
        self.remove_button.clicked.connect(self.remove_task)
        
        

        self.task_list = QListWidget(self)
        
        layout.addWidget(self.task_input)
        layout.addWidget(self.note_input)
        layout.addWidget(self.due_date_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.task_list)
        layout.addWidget(self.complete_button)

        self.setLayout(layout)

        self.load_tasks()

    def add_task(self):
        task_description = self.task_input.text()
        note = self.note_input.toPlainText()
        due_date = self.due_date_input.text()

        if task_description and due_date:
            self.insert_task_into_db(task_description, note, due_date)
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Missing Information", "Please fill all fields.")

    def remove_task(self):
        selected_task = self.task_list.currentItem()
        if selected_task:
            task_description = selected_task.text()
            self.delete_task_from_db(task_description)
            self.load_tasks()
        else:
            QMessageBox.warning(self, "No Task Selected", "Please select a task to remove.")

    def insert_task_into_db(self, task_description, note, due_date):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tasks (subject, task_description, note, due_date, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.subject, task_description, note, due_date, self.user_id))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")

    def delete_task_from_db(self, task_description):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM tasks WHERE subject=%s AND task_description=%s AND user_id=%s
            """, (self.subject, task_description, self.user_id))
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")

    def load_tasks(self):
        self.task_list.clear()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",
                database="studyscheduler"
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT task_description FROM tasks
                WHERE subject=%s AND user_id=%s
            """, (self.subject, self.user_id))
            tasks = cur.fetchall()
            conn.close()
            
            for task in tasks:
                self.task_list.addItem(task[0])

        except mysql.connector.Error as err:
            QMessageBox.critical(None, "Database Error", f"Error: {err}")
    
    def complete_task(self):
    # Get the selected task from the list
        selected_task = self.task_list.currentItem()

        if selected_task:
            description = selected_task.text()  # Get the task description from the selected item

            try:
                # Establish connection to the database
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="1234",
                    database="studyscheduler"
                )
                cur = conn.cursor()

                # Update the task to mark it as complete
                cur.execute("""
                    UPDATE tasks
                    SET iscomplete = TRUE
                    WHERE subject = %s AND task_description = %s AND user_id = %s AND iscomplete = FALSE   
                """, (self.subject, description, self.user_id))

                # Check if any row was updated
                if cur.rowcount > 0:
                    conn.commit()
                    QMessageBox.information(None, "Task Completed", "The task has been marked as complete.")
                else:
                    QMessageBox.warning(None, "Task Not Found", "No incomplete task matching the criteria was found.")

                conn.close()

            except mysql.connector.Error as err:
                # Handle database connection or query errors
                QMessageBox.critical(None, "Database Error", f"Error: {err}")
        else:
            QMessageBox.warning(None, "No Task Selected", "Please select a task to mark as complete.")

# Main application execution
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
