import sys, json, os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from backend import DataGetter, pd

class DocumentTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datagetter=None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Document Tracker")
        self.setGeometry(100, 100, 800, 500)

        self.create_menu_bar()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        # Status Display
        self.main_layout_label = QLabel(text="Document Status")
        self.main_layout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.main_layout_label)

        
        
        self.status_bar = QHBoxLayout()
        # Analyze Data Button
        self.analyze_button = QPushButton("View browser data")
        self.analyze_button.clicked.connect(lambda: self.show_histogram("Browsers"))
        self.status_bar.addWidget(self.analyze_button)
        # contries Button
        self.analyze_button = QPushButton("View country histogram")
        self.analyze_button.clicked.connect(lambda: self.show_histogram("Countries"))
        self.status_bar.addWidget(self.analyze_button)
        # continent Button
        self.analyze_button = QPushButton("View continent histogram")
        self.analyze_button.clicked.connect(lambda: self.show_histogram("Continents"))
        self.status_bar.addWidget(self.analyze_button)

        self.main_layout.addLayout(self.status_bar)
        self.central_widget.setLayout(self.main_layout)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        ##file menu-------
        # open file dialog------
        
        open_file_action = QAction(QIcon("icons/icons8-open-file-16.png"),'Open', self)
        open_file_action.setShortcut('Ctrl+N')
        open_file_action.triggered.connect(self.choose_file)
        #exit action----------------------
        exit_action = QAction(QIcon("icons/icons8-exit-16.png"),'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)

        file_menu = menubar.addMenu('File')
        file_menu.addAction(open_file_action)
        file_menu.addAction(exit_action)
        ##format menu------
        format_menu = menubar.addMenu('Format')
        format_menu.addAction(open_file_action)
        format_menu.addAction(exit_action)

    def choose_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                print(f"Selected file: {file_path}")
                
                file_name = os.path.basename(file_path)
                self.set_main_layout(file_name=file_name, file_path=file_path)

    def set_main_layout(self, file_name, file_path):        
        # Load sample data into the table (replace with your actual data)
        datagetter = DataGetter(file_path)
        self.datagetter= datagetter
        # Converting the dictionary to a DataFrame
        df = pd.DataFrame(datagetter.data)
        columns = df.columns.tolist()
        # Table to Display Document Info
        self.document_table = QTableWidget()
        
        children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
        
        if len(children)>=3:
            self.main_layout.removeItem(self.main_layout.itemAt(1))
            self.main_layout.insertWidget(1,self.document_table)
        else:
            self.main_layout.insertWidget(1,self.document_table)

        self.document_table.setColumnCount(len(columns))
        self.document_table.setHorizontalHeaderLabels(columns)
        self.document_table.setRowCount(len(df.index))
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.document_table.setItem(row_idx, col_idx, item)
        self.main_layout_label.setText(file_name+f"\t({self.document_table.columnCount()}columns"+f"\t{self.document_table.rowCount()}rows)")

    def __plot_data(self,categories, values, data_type):
        # Creating the histogram
        colors = ['blue', 'orange', 'green', 'red', 'purple', 'gray', 'cyan', 'magenta', 'yellow', 'lime', 'pink', 'teal', "brown"]
        self.canvas.figure.clear()  # Clear previous plot (if any)
        self.canvas.figure.set_size_inches(12, 6)
        self.canvas.figure.tight_layout()
        ax =self.canvas.figure.add_subplot(111)
        ax.bar(categories, values, color=colors, width=1)
        ax.tick_params(axis='x', rotation=70, labelsize=9)
        ax.set_xlabel(data_type)
        ax.set_ylabel('Frequency')
        ax.set_title(f'{data_type} of viewers')
        
        
        self.canvas.draw()
    def show_histogram(self,data_type):
        # Placeholder for data analysis functionality
        if self.datagetter is None:
            print("its is none")
        else:
            if data_type=="Countries":
                self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
                self.main_layout.removeItem(self.main_layout.itemAt(1))
                children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
                print(children,"===")
                self.main_layout.insertWidget(1, self.canvas)

                countries= self.datagetter.get_countries_data()
                #self.datagetter.show_histogram(countries,x_label='Countries', y_label='Frequency',title='Countries of viewers')
                categories = list(countries.keys())
                values = list(countries.values())
                self.__plot_data(categories=categories,values=values,data_type=data_type)
            elif data_type=="Continents":
                self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
                self.main_layout.removeItem(self.main_layout.itemAt(1))
                self.main_layout.insertWidget(1, self.canvas)

                countries= self.datagetter.get_continent_data()
                #self.datagetter.show_histogram(countries,x_label='Countries', y_label='Frequency',title='Countries of viewers')
                categories = list(countries.keys())
                values = list(countries.values())
                self.__plot_data(categories=categories,values=values,data_type=data_type)
            elif data_type=="Browsers":
                self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
                self.main_layout.removeItem(self.main_layout.itemAt(1))
                self.main_layout.insertWidget(1, self.canvas)

                countries= self.datagetter.get_browser_data()
                #self.datagetter.show_histogram(countries,x_label='Countries', y_label='Frequency',title='Countries of viewers')
                categories = list(countries.keys())
                values = list(countries.values())
                self.__plot_data(categories=categories,values=values,data_type=data_type)  
            else:
                pass
        print("Performing data analysis...")

def run_app():
    app = QApplication(sys.argv)
    main_app = DocumentTrackerApp()
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
