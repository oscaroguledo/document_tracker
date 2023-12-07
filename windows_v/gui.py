import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,QTextEdit, QLineEdit, QDialog, QStatusBar, QMessageBox,QGraphicsScene, QGraphicsView, QCheckBox, QStyleFactory, QMenu, QRadioButton
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QAction, QIcon,QImage, QPixmap, QMovie
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from functools import partial
from backend import DataGetter, pd, time, shutil, os, json, plt, Source

class Settings():
    def __init__(self) -> None:
        with open('settings/setting.json', 'r') as file:
            data = json.load(file)
        self.theme = data["theme"]
    def settheme(self, theme):
        with open('settings/setting.json', 'r') as file:
            data = json.load(file)
        data['theme'] = theme

        # Write the updated data back to the JSON file
        with open('settings/setting.json', 'w') as file:
            json.dump(data, file, indent=4)

class DocumentTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Document Tracker")
        self.setWindowIcon(QIcon('icons/title.png'))
        self.datagetter=None
        self.file_name=None
        self.options={'view_table':"T",'view_continent':"K",'view_country':"C",'view_browser':"B",'view_readers':"R",'view_also_like':"L",'view_also_like_graph':"G"}
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.__init_ui()
        self.__load_theme()
        
    def closeEvent(self, event):
        # Perform actions when the window is about to close
        result = self.close_dialog()
        if result == QMessageBox.StandardButton.Yes:
            if os.path.exists('tmp'):
                shutil.rmtree('tmp')
            event.accept()  # Accept the close event
            sys.exit()  # Accept the close event
        else:
            try:
                event.ignore()
            except AttributeError as error:
                pass
                
    def close_dialog(self):
        # Create a confirmation dialog
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle("Confirmation")
        dialog.setText("Are you sure you want to close the window?")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return dialog.exec()  # Show the dialog and return the user's choice
    
    def __load_theme(self):
        settings = Settings()
        if settings.theme =='light':
            self.__change_to_light_theme()
        elif settings.theme =='dark':
            self.__change_to_dark_theme()
    def __change_to_dark_theme(self):
        QApplication.instance().setStyle(QStyleFactory.create("Fusion"))
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet("QApplication{}")
        # Open the text file in read mode
        with open('settings/themes/dark.txt', 'r') as file:
            # Read the content of the file
            dark = file.read()
            self.setStyleSheet(dark)
        settings = Settings()
        settings.settheme("dark")

    def __change_to_light_theme(self):
        QApplication.instance().setStyle(QStyleFactory.create("Fusion"))
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        self.setStyleSheet("QApplication{}")
        # Open the text file in read mode
        with open('settings/themes/light.txt', 'r') as file:
            # Read the content of the file
            light = file.read()
            self.setStyleSheet(light)
        settings = Settings()
        settings.settheme("light")
    
    def toggle_theme(self):
        dialog = QDialog(self)
        dialog.setMinimumWidth(200)
        dialog.setWindowTitle("Theme Changer")

        # Layout
        layout = QVBoxLayout()

        # Checkboxes for different themes
        checkbox_dark = QRadioButton("Dark Theme")
        checkbox_light = QRadioButton("Light Theme")

        layout.addWidget(checkbox_dark)
        layout.addWidget(checkbox_light)

        # Connect checkbox signals to slots
        checkbox_dark.setShortcut('Shift + D')
        checkbox_dark.clicked.connect(self.__change_to_dark_theme)
        checkbox_light.setShortcut('Shift + L')
        checkbox_light.clicked.connect(self.__change_to_light_theme)
        settings = Settings()
        if settings.theme == 'dark':
            checkbox_dark.setChecked(True)
        elif settings.theme == 'light':
            checkbox_light.setChecked(True)
        dialog.setLayout(layout)
        result = dialog.exec()
            
    def __init_ui(self):
        self.setWindowTitle("Document Tracker")
        self.setGeometry(100, 100, 800, 500)

        self.__create_menu_bar()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()

        self.bottom_bar = QHBoxLayout()
        # table Button
        self.analyze_button = QLabel("Loading...")
        self.analyze_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie = QMovie("icons/loader.gif")
        self.analyze_button.setMovie(movie)
        # Start the animation
        movie.start()
        self.bottom_bar.addWidget(self.analyze_button)
        # browser Button
        
        self.main_layout.addLayout(self.bottom_bar)
        self.central_widget.setLayout(self.main_layout)
        # Create a status bar
        self.statusBar = QStatusBar()
        self.label = QLabel('   Waiting for json file...')
        self.statusBar.addWidget(self.label)
        self.setStatusBar(self.statusBar)
        
    def __create_menu_bar(self):
        self.menubar = self.menuBar()
        ##file menu-------
        # open file dialog----------------
        self.open_file_action = QAction(QIcon("icons/open_file.png"),'Open', self)
        self.open_file_action.setShortcut('Ctrl+N')
        self.open_file_action.triggered.connect(self.choose_file)
        #exit action----------------------
        self.exit_action = QAction(QIcon("icons/exit.png"),'Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(self.closeEvent)

        self.file_menu = self.menubar.addMenu('File')
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        
        ##settings menu------
        self.theme_action = QAction(QIcon("icons/theme.png"),'Change Theme', self)
        self.theme_action.triggered.connect(self.toggle_theme)

        self.settings_menu = self.menubar.addMenu('Settings')
        self.settings_menu.addAction(self.theme_action)
   
    def choose_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select a json file")
        file_dialog.Option.DontUseNativeDialog
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Json Files (*.json)")

        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                file_name = os.path.basename(file_path)
                self.bottom_bar.removeWidget(self.analyze_button)
                self.set_main_layout(file_name=file_name, file_path=file_path)

    def set_main_layout(self, file_name, file_path):        
        # Load sample data into the table (replace with your actual data)
        start = time.time()
        datagetter = DataGetter(file_path)
        self.datagetter= datagetter
        self.file_name =file_name
        ## setting up menu options---------------------------

        ##clearing the options menu--------------------------------
        try:
            self.menubar.removeAction(self.options_menu.menuAction())
        except Exception:
            pass
        self.options_menu = QMenu("Options", self)
        self.menubar.addMenu(self.options_menu)

        # To insert the "Options" menu at a specific position (e.g., index 0)
        self.menubar.insertAction(None, self.options_menu.menuAction())

        # Move the "Options" menu to a specific position (e.g., index 0)
        self.menubar.insertAction(self.menubar.actions()[1], self.options_menu.menuAction())
        #----------------------------------------------------------------------------------------

        
        #ensure the bottom bar is not over populated-------------------
        while self.bottom_bar.count():
            item = self.bottom_bar.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout is not None:
                    while layout.count():
                        layout_item = layout.takeAt(0)
                        layout_widget = layout_item.widget()
                        if layout_widget is not None:
                            layout_widget.deleteLater()
            del item

        #-------------------------------------------------------------  
        for key, value in self.options.items():
            words = key.split()
            capitalized_words = [word.capitalize() for word in words]
            result = ' '.join(capitalized_words)
            key_title = result.replace('_', ' ')
            
            # Using functools.partial to create a callable object with pre-defined arguments
            option_trigger = partial(self.run_functionality, key, self.datagetter, self.file_name, key)

            option = QAction(QIcon(f"icons/{key}.png"),key_title, self)
            option.setShortcut(f'Ctrl+Alt+{value}')
            option.triggered.connect(option_trigger)
            self.options_menu.addAction(option)
            self.options_menu.addSeparator()
            ## setting up bottom buttons-------------------------
            analyze_button = QPushButton(key_title)
            analyze_button.clicked.connect(option_trigger)
            self.bottom_bar.addWidget(analyze_button)
        ##---------------------------------------------------
        
        self.run_functionality("view_table",self.datagetter,self.file_name)

    def run_functionality(self, func_type=None, datagetter=None, file_name=None, data_type=None):
        if func_type == "view_table":
            self.show_table(func_type,datagetter,file_name)
        elif func_type == "view_continent":
            self.show_histogram(func_type)
        elif func_type == "view_country":
            self.show_histogram(func_type)
        elif func_type == "view_browser":
            self.show_histogram(func_type)
        elif func_type == "view_readers":
            self.show_table(func_type,datagetter, file_name)
        elif func_type == "view_also_like":
            self.show_table(func_type,datagetter, file_name)
        elif func_type == "view_also_like_graph":
            self.show_graph(func_type,datagetter, file_name)
        else:
            pass


    def show_info(self,doc_type,datagetter, document):
        pass
    
    def show_graph(self,doc_type,datagetter, document):
        if not datagetter == None:
            try:
                self.menubar.removeAction(self.download_menu.menuAction())
            except Exception:
                pass
            
            self.download_menu = self.menubar.addMenu('Download Graph (Also Like)')
            """input dialog box"""
            dialog = QDialog(self)
            dialog.setWindowTitle("Enter Your Values")
            layout = QVBoxLayout()
            v_layout = QVBoxLayout()
                
            h_layout1 = QHBoxLayout()
            h_layout1.addWidget(QLabel("Limit:"))
            line_edit = QLineEdit()
            line_edit.setText('10')
            h_layout1.addWidget(line_edit)
        
            h_layout2 = QHBoxLayout()
            h_layout2.addWidget(QLabel("Doc Id:"))
            document_id = QLineEdit()
            h_layout2.addWidget(document_id)
        
            h_layout3 = QHBoxLayout()
            h_layout3.addWidget(QLabel("Visitor Id:"))
            visitor_id = QLineEdit()
            h_layout3.addWidget(visitor_id)

            v_layout.addLayout(h_layout1)
            v_layout.addLayout(h_layout2)
            v_layout.addLayout(h_layout3)

            layout.addLayout(v_layout)

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(dialog.accept)
            cancel_button = QPushButton("Cancel")
            cancel_button.clicked.connect(dialog.reject)
            buttons_layout = QHBoxLayout()
            buttons_layout.addWidget(ok_button)
            buttons_layout.addWidget(cancel_button)
            layout.addLayout(buttons_layout)

            dialog.setLayout(layout)
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                l = int(line_edit.text())
                doc_id = document_id.text()
                vis_id = visitor_id.text()
                data = datagetter.generate_also_like_graph(document=doc_id,reader=vis_id,limit=l)
                file_name= 'graph/also_like_graph.dot'
                dot_source = Source.from_file(file_name)

                # Create a QGraphicsScene and add the Graphviz .dot content
                scene = QGraphicsScene(self)
                view = QGraphicsView(scene)

                # Convert the Graphviz .dot content to a QImage
                image = dot_source.pipe(format='png')
                image_data = QImage.fromData(image)

                # Add the image to the scene
                scene.addPixmap(QPixmap.fromImage(image_data))
                
                children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
                if len(children)>=2:
                    self.main_layout.removeItem(self.main_layout.itemAt(0))
                    self.main_layout.insertWidget(0,view)
                else:
                    self.main_layout.insertWidget(0,view)

                formats = {"Dot":".dot","Pdf":".pdf","Ps":".ps","Png":".png"}
                self.download_menu.clear()
                for key, value in formats.items():
                    option_trigger = partial(self.download_file, datagetter,file_name, key, value)

                    format_ = QAction(QIcon(f"icons/{key}.png"),key, self)
                    if value == ".dot":
                        format_.setShortcut(f'Alt+D')
                    elif value == ".pdf":
                        format_.setShortcut(f'Alt+P')
                    elif value == ".ps":
                        format_.setShortcut(f'Alt+S')
                    format_.triggered.connect(option_trigger)
                    self.download_menu.addAction(format_)
                    self.download_menu.addSeparator()
        else:
            print('There is no data to populate')
        
    def show_table(self, func_type,datagetter,file_name=None):
        if not datagetter== None:
            if func_type == "view_readers":
                """input dialog box"""
                dialog = QDialog(self)
                dialog.setWindowTitle("Enter Your Values")
                layout = QVBoxLayout()

                h_layout = QHBoxLayout()
                h_layout.addWidget(QLabel("Limit:"))
                line_edit = QLineEdit()
                line_edit.setText('10')
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)

                ok_button = QPushButton("OK")
                ok_button.clicked.connect(dialog.accept)
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(dialog.reject)
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(ok_button)
                buttons_layout.addWidget(cancel_button)
                layout.addLayout(buttons_layout)

                dialog.setLayout(layout)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    l = int(line_edit.text())
                    data = datagetter.get_reading_time(limit=l)
                    # Create QTableWidget
                    self.tableWidget = QTableWidget()
                    self.tableWidget.setWindowTitle(f"Top {l} Readers")
                    self.tableWidget.setGeometry(50, 50, 400, 300)

                    children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
                    if len(children)>=2:
                        self.main_layout.removeItem(self.main_layout.itemAt(0))
                        self.main_layout.insertWidget(0,self.tableWidget)
                    else:
                        self.main_layout.insertWidget(0,self.tableWidget)
                    # Set row and column count
                    self.tableWidget.setRowCount(len(data))
                    self.tableWidget.setColumnCount(len(data[0]))

                    # Set table headers
                    headers = list(data[0].keys())
                    self.tableWidget.setHorizontalHeaderLabels(headers)
                    
                    # Populate table with data
                    for row, rowData in enumerate(data):
                        for col, value in enumerate(rowData.values()):
                            item = QTableWidgetItem(str(value))
                            self.tableWidget.setItem(row, col, item)

            elif func_type == "view_also_like":
                """input dialog box"""
                dialog = QDialog(self)
                dialog.setWindowTitle("Enter Your Values")
                layout = QVBoxLayout()
                v_layout = QVBoxLayout()
                    
                h_layout1 = QHBoxLayout()
                h_layout1.addWidget(QLabel("Limit:"))
                line_edit = QLineEdit()
                line_edit.setText('10')
                h_layout1.addWidget(line_edit)
            
                h_layout2 = QHBoxLayout()
                h_layout2.addWidget(QLabel("Doc Id:"))
                document_id = QLineEdit()
                h_layout2.addWidget(document_id)
            
                h_layout3 = QHBoxLayout()
                h_layout3.addWidget(QLabel("Visitor Id:"))
                visitor_id = QLineEdit()

                h_layout3.addWidget(visitor_id)
                v_layout.addLayout(h_layout1)
                v_layout.addLayout(h_layout2)
                v_layout.addLayout(h_layout3)

                layout.addLayout(v_layout)

                ok_button = QPushButton("OK")
                ok_button.clicked.connect(dialog.accept)
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(dialog.reject)
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(ok_button)
                buttons_layout.addWidget(cancel_button)
                layout.addLayout(buttons_layout)

                dialog.setLayout(layout)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    l = int(line_edit.text())
                    doc_id = document_id.text()
                    vis_id = visitor_id.text()
                    data = datagetter.get_also_like_documents(doc_id, vis_id, sorting_function = lambda x: datagetter.order(x, "desc", l))
                    # Create QTableWidget
                    tableWidget = QTableWidget()
                    tableWidget.setWindowTitle(f"Top {l} Readers")
                    tableWidget.setGeometry(50, 50, 400, 300)

                    children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
                    if len(children)>=2:
                        self.main_layout.removeItem(self.main_layout.itemAt(0))
                        self.main_layout.insertWidget(0,tableWidget)
                    else:
                        self.main_layout.insertWidget(0,tableWidget)
                    # Set row and column count
                    tableWidget.setRowCount(len(data))
                    tableWidget.setColumnCount(len(data[0]))

                    # Set table headers
                    headers = list(data[0].keys())
                    tableWidget.setHorizontalHeaderLabels(headers)
                    
                    # Populate table with data
                    for row, rowData in enumerate(data):
                        for col, value in enumerate(rowData.values()):
                            item = QTableWidgetItem(str(value))
                            tableWidget.setItem(row, col, item)
                
            else:
                # Converting the dictionary to a DataFrame
                df = pd.DataFrame(datagetter.data)
                columns = df.columns.tolist()
                # Table to Display Document Info
                document_table = QTableWidget()
                document_table.setWindowTitle(f"{file_name} Info")
                
                children = [self.main_layout.itemAt(i) for i in range(self.main_layout.count())]
                if len(children)>=2:
                    self.main_layout.removeItem(self.main_layout.itemAt(0))
                    self.main_layout.insertWidget(0,document_table)
                else:
                    self.main_layout.insertWidget(0,document_table)

                document_table.setColumnCount(len(columns))
                document_table.setHorizontalHeaderLabels(columns)
                document_table.setRowCount(len(df.index))
                for row_idx, (_, row) in enumerate(df.iterrows()):
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        document_table.setItem(row_idx, col_idx, item)

                self.label.setText(file_name+f"\t({document_table.columnCount()}columns"+f"\t{document_table.rowCount()}rows)")

        else:
            print("there is no data to populate")
            pass
    
    def show_histogram(self,data_type):
        if self.datagetter is None:
            print('There is no data to populate')
        else:
            if data_type=="view_country":
                """input dialog box"""
                dialog = QDialog(self)
                dialog.setWindowTitle("Enter Your Document Id")
                layout = QVBoxLayout()
                v_layout = QVBoxLayout()
                    
                h_layout = QHBoxLayout()
                h_layout.addWidget(QLabel("Doc Id:"))
                document_id = QLineEdit()
                h_layout.addWidget(document_id)
            
                v_layout.addLayout(h_layout)

                layout.addLayout(v_layout)

                ok_button = QPushButton("OK")
                ok_button.clicked.connect(dialog.accept)
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(dialog.reject)
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(ok_button)
                buttons_layout.addWidget(cancel_button)
                layout.addLayout(buttons_layout)

                dialog.setLayout(layout)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    document_id = document_id.text()
                    countries= self.datagetter.get_countries_data(document_uuid=document_id)
                    categories = list(countries.keys())
                    values = list(countries.values())
                    self.__plot_data(categories=categories,values=values,data_type=data_type)
            elif data_type=="view_continent":
                """input dialog box"""
                dialog = QDialog(self)
                dialog.setWindowTitle("Enter Your Document Id")
                layout = QVBoxLayout()
                v_layout = QVBoxLayout()
                    
                h_layout = QHBoxLayout()
                h_layout.addWidget(QLabel("Doc Id:"))
                document_id = QLineEdit()
                h_layout.addWidget(document_id)
            
                v_layout.addLayout(h_layout)

                layout.addLayout(v_layout)

                ok_button = QPushButton("OK")
                ok_button.clicked.connect(dialog.accept)
                cancel_button = QPushButton("Cancel")
                cancel_button.clicked.connect(dialog.reject)
                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(ok_button)
                buttons_layout.addWidget(cancel_button)
                layout.addLayout(buttons_layout)

                dialog.setLayout(layout)
                result = dialog.exec()
                if result == QDialog.DialogCode.Accepted:
                    document_id = document_id.text()
                    countries= self.datagetter.get_countries_data(document_uuid=document_id)
                    countries= self.datagetter.get_continent_data(document_uuid=document_id)
                    categories = list(countries.keys())
                    values = list(countries.values())
                    self.__plot_data(categories=categories,values=values,data_type=data_type)
                
            elif data_type=="view_browser":
                countries= self.datagetter.get_browsers
                categories = list(countries.keys())
                values = list(countries.values())
                self.__plot_data(categories=categories,values=values,data_type=data_type)  
            else:
                pass
    
    def __plot_data(self,categories, values, data_type):
        self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
        self.main_layout.removeItem(self.main_layout.itemAt(0))
        self.main_layout.insertWidget(0, self.canvas)

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
        # Adjust the height of the subplot (axes)
        pos = ax.get_position()  # Get the current position and size of the subplot
        pos.y0 = 0.5  # Adjust the bottom of the subplot
        pos.y1 = 0.9  # Adjust the top of the subplot
        """        pos.x0=0.5
        pos.x1=1"""
        pos.x1=0.975
        pos.x0=0.075
        """print(pos.x1,pos.x0)"""
        ax.set_position(pos)  # Set the new position and size
        self.canvas.draw()

    def download_file(self, datagetter,file_name,name,ext):
        file_dialog = QFileDialog()
        file_dialog.Option.DontUseNativeDialog
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_path, _ = file_dialog.getSaveFileName(self, "Save File", "", f"{name} Files (*{ext})")

        if file_path:
            if ext == ".pdf":
                datagetter.convert_dot_to_pdf(file_name, file_path)
            elif ext == ".ps":
                datagetter.convert_dot_to_ps(file_name, file_path)
            elif ext == ".dot":
                datagetter.convert_dot_to_dot(file_name, file_path)
            elif ext == ".png":
                datagetter.convert_dot_to_png(file_name, file_path)
            else:
                pass

def run_gui_app():
    app = QApplication(sys.argv)
    # Apply dark theme.
    main_app = DocumentTrackerApp()
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui_app()
