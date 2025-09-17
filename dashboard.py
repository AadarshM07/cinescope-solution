import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QGridLayout,
    QMessageBox, QTextEdit, QSizePolicy, QDateEdit, QLineEdit
)

from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utils.db_query import fetch_query_data


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CineScope – Dashboard")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: #121212; color: white; padding: 20px;")
        self.selected_top_button = None
        self.selected_bottom_buttons = set()
        self.query_mode = None
        self.filter_condition = ""
        self.selected_columns = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        header = QLabel("🎬 CineScope Dashboard")
        header.setFont(QFont("Arial", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(80)
        main_layout.addWidget(header)

        split_layout = QHBoxLayout()

        left_container = QVBoxLayout()
        left_container.setSpacing(10)
        left_container.setAlignment(Qt.AlignTop)

        self.existing_buttons = [
            ("Search by Genre", "genre"),
            ("Search by Year", "year"),
            ("Search by IMDB Rating", "rating"),
            ("Search by Director", "director"),
            ("Search by Actor", "actor"),
            ("Export Results to CSV", "export"),
        ]

        existing_grid = QGridLayout()

        for index, (label, mode) in enumerate(self.existing_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.default_button_style())
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, button=btn, m=mode: self.select_top_button(button, m))
            row, col = divmod(index, 2)
            existing_grid.addWidget(btn, row, col)

        left_container.addLayout(existing_grid)

        category_heading = QLabel("Select Columns (Multiple Selection)")
        category_heading.setFont(QFont("Arial", 18, QFont.Bold))
        category_heading.setAlignment(Qt.AlignLeft)
        left_container.addWidget(category_heading)

        self.category_buttons = [
            ("Title", "Series_Title"),
            ("Year", "Released_Year"),
            ("Genre", "Genre"),
            ("Rating", "IMDB_Rating"),
            ("Director", "Director"),
            ("Stars", "Star1, Star2, Star3"),
        ]

        category_grid = QGridLayout()

        for index, (label, columns) in enumerate(self.category_buttons):
            btn = QPushButton(label)
            btn.setStyleSheet(self.default_button_style())
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, button=btn, cols=columns: self.toggle_bottom_button(button, cols))
            row, col = divmod(index, 3)
            category_grid.addWidget(btn, row, col)

        left_container.addLayout(category_grid)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter filter value (e.g. 1999 for Year)")
        self.query_input.setStyleSheet("background-color: #1e1e1e; color: white; padding: 5px; border: 1px solid #444;")
        self.query_input.setFixedHeight(30)
        left_container.addWidget(self.query_input)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("background-color: #e50914; color: white; padding: 6px; border-radius: 5px;")
        send_btn.setFixedWidth(100)
        send_btn.clicked.connect(self.execute_query)
        left_container.addWidget(send_btn, alignment=Qt.AlignLeft)

        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(10)

        right_content = QWidget()
        right_content.setStyleSheet("background-color: black; border-radius: 8px;")
        right_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                color: white;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 4px;
            }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        right_content_layout = QVBoxLayout()
        right_content_layout.addWidget(self.table)
        right_content.setLayout(right_content_layout)

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("System output will appear here...")
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #444;
                border-radius: 10px;
                font-family: Consolas, monospace;
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.text_area.setFixedHeight(80)

        right_side_layout.addWidget(right_content)
        right_side_layout.addWidget(self.text_area)

        split_layout.addLayout(left_container, 2)
        split_layout.addLayout(right_side_layout, 8)

        main_layout.addLayout(split_layout)
        self.setLayout(main_layout)
        
        # Load initial data
        self.load_initial_data()

    def load_initial_data(self):
        """Load all data when the application starts"""
        base_query = """
        SELECT Series_Title, Released_Year, Genre, IMDB_Rating, Director, Star1, Star2, Star3
        FROM Movies
        """
        self.execute_query_with_sql(base_query)

    def default_button_style(self):
        return """
            QPushButton {
                background-color: #1f1f1f;
                border: 1px solid #333;
                border-radius: 3px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """

    def highlighted_button_style(self):
        return """
            QPushButton {
                background-color: #ffcc00;
                border: 1px solid #ff9900;
                border-radius: 3px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #ff9900;
            }
        """

    def select_top_button(self, button, mode):
        if mode == "export":
            self.export_csv()
            return
            
        if self.selected_top_button:
            self.selected_top_button.setStyleSheet(self.default_button_style())
        self.selected_top_button = button
        button.setStyleSheet(self.highlighted_button_style())
        self.query_mode = mode
        self.update_input_placeholder()

    def toggle_bottom_button(self, button, columns):
        if button in self.selected_bottom_buttons:
            self.selected_bottom_buttons.remove(button)
            button.setStyleSheet(self.default_button_style())
            cols_to_remove = columns.split(", ")
            self.selected_columns = [col for col in self.selected_columns if col not in cols_to_remove]
        else:
            self.selected_bottom_buttons.add(button)
            button.setStyleSheet(self.highlighted_button_style())
            self.selected_columns.extend(columns.split(", "))
            
    def update_input_placeholder(self):
        if self.query_mode == "year":
            self.query_input.setPlaceholderText("Enter year (e.g. 1999)")
        elif self.query_mode == "genre":
            self.query_input.setPlaceholderText("Enter genre (e.g. Drama)")
        elif self.query_mode == "rating":
            self.query_input.setPlaceholderText("Enter minimum rating (e.g. 8.5)")
        elif self.query_mode == "director":
            self.query_input.setPlaceholderText("Enter director name (e.g. Nolan)")
        elif self.query_mode == "actor":
            self.query_input.setPlaceholderText("Enter actor name (e.g. DiCaprio)")
        else:
            self.query_input.setPlaceholderText("Enter filter value")

    def execute_query(self):
        if not self.selected_columns:
            self.text_area.setText("Please select at least one column to display.")
            return
            
        select_columns = ", ".join(set(self.selected_columns))  # Remove duplicates
        base_query = f"SELECT {select_columns} FROM Movies"
        
        filter_value = self.query_input.text().strip()
        if self.query_mode and filter_value:
            if self.query_mode == "year":
                where_clause = f"WHERE Released_Year = {filter_value}"
            elif self.query_mode == "genre":
                where_clause = f"WHERE Genre LIKE '%{filter_value}%'"
            elif self.query_mode == "rating":
                where_clause = f"WHERE IMDB_Rating >= {float(filter_value)}"
            elif self.query_mode == "director":
                where_clause = f"WHERE Director LIKE '%{filter_value}%'"
            elif self.query_mode == "actor":
                where_clause = f"WHERE (Star1 LIKE '%{filter_value}%' OR Star2 LIKE '%{filter_value}%' OR Star3 LIKE '%{filter_value}%')"
            else:
                where_clause = ""
            
            base_query += f" {where_clause}"
            
        self.execute_query_with_sql(base_query)

    def execute_query_with_sql(self, sql_query):
        try:
            headers, rows = fetch_query_data(sql_query)
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(rows))
            self.table.setHorizontalHeaderLabels(headers)

            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.text_area.setText(f"Query executed successfully.\n\nSQL: {sql_query}")
        except Exception as e:
            self.text_area.setText(f"Error: {str(e)}")

    def export_csv(self):
        QMessageBox.information(self, "Export", "Export Results to CSV clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())