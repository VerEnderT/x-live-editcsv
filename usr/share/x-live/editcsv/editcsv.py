#!/usr/bin/python3

import sys
import csv
import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox, QLabel,
    QHeaderView, QDialog, QTextEdit, QAction, QMenu, QCheckBox
)

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QResizeEvent, QIntValidator, QClipboard, QIcon

class CSVEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Live EditCSV")
        self.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-editcsv.png"))
        self.resize(1000, 600)
        self.tab_size = [8, 30, 30, 16, 16]
        self.header_data = ["-", "-", "-", "-", "-"]

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Menübar erstellen
        menubar = self.menuBar()

        # Menü "Datei" hinzufügen
        file_menu = menubar.addMenu("Datei")
        tabble_menu = menubar.addMenu("Tabelle")
        row_menu = menubar.addMenu("Zeile")
        info_menu = menubar.addMenu("Info")

        # Aktionen für das Menü - Datei 
        open_action = QAction("Öffnen", self)
        open_action.triggered.connect(self.load_csv)
        save_action = QAction("speichern", self)
        save_action.triggered.connect(self.save_csv)
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        

        # Aktionen für das Menü - Tabelle
        header_action = QAction("Kopfzeile bearbeiten", self)
        header_action.triggered.connect(self.edit_header)
        clear_action = QAction("Tabelle leeren", self)
        clear_action.triggered.connect(self.clear_data)
        
        # Aktionen für das Menü - Zeile
        add_action = QAction("hinzufügen", self)
        add_action.triggered.connect(self.add_entry)
        edit_action = QAction("bearbeiten", self)
        edit_action.triggered.connect(self.edit_entry)
        remove_action = QAction("entfernen", self)
        remove_action.triggered.connect(self.delete_entry)

        # Aktionen für das Menü - Info 
        about_action = QAction("über", self)
        about_action.triggered.connect(self.show_about_dialog)
        
        # Aktionen zu den Menüs hinzufügen
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()  # Trennlinie
        file_menu.addAction(exit_action)
        tabble_menu.addAction(header_action)
        tabble_menu.addAction(clear_action)
        row_menu.addAction(add_action)
        row_menu.addAction(edit_action)
        row_menu.addAction(remove_action)
        info_menu.addAction(about_action)

        # layouts erstellen
        self.layout = QVBoxLayout(self.central_widget)
        line_top_layout = QHBoxLayout()
        
        # Suchfeld
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("darf enthalten...")
        self.search_field.textChanged.connect(self.search_table)
        self.search_field_ex = QLineEdit()
        self.search_field_ex.setPlaceholderText("darf nicht enthalten...")
        self.search_field_ex.textChanged.connect(self.search_table)
        self.search_field_ex.hide()
        self.search_revbox = QCheckBox("mehr filter")               
        self.search_revbox.stateChanged.connect(self.search_table_ex)


        # Tabelle
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.header_data))
        self.table.setHorizontalHeaderLabels(self.header_data)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Einfaches Eintrag bearbeiten unterbinden
        self.table.cellDoubleClicked.connect(self.edit_entry)
        # komplette zeile auswähle
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Rechtsklick-Kontextmenü aktivieren
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        # **Spaltenbreite automatisch anpassen**
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Buttons
        self.add_button = QPushButton("neue Zeile")
        self.add_button.clicked.connect(self.add_entry)
        self.print_button = QPushButton("Markierte Ausgeben")
        self.print_button.clicked.connect(self.print_data)

        # layouts zusammenstellung
        line_top_layout.addWidget(self.add_button)
        line_top_layout.addWidget(QLabel("Filter:")) 
        line_top_layout.addWidget(self.search_field)
        line_top_layout.addWidget(self.search_field_ex)
        line_top_layout.addWidget(self.search_revbox)
        
        self.layout.addLayout(line_top_layout)
        self.layout.addWidget(self.table)

        self.data = []       
        QTimer.singleShot(50,self.table_resize)
        
    def table_resize(self):
        self.set_column_widths(self.tab_size)

    def set_column_widths(self, percentages):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        """Setzt die Spaltenbreite in Prozent der Gesamtbreite."""
        total_width = self.table.viewport().width()
        for index, percentage in enumerate(percentages):
            self.table.setColumnWidth(index, total_width * int(percentage) // 100)

    def resizeEvent(self, event: QResizeEvent):
        """Passen die Spaltenbreite bei Größenänderung des Fensters an."""
        self.set_column_widths(self.tab_size)
        super().resizeEvent(event)


    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "CSV-Datei auswählen", "", "CSV-Dateien (*.csv)")
        x = file_path.split("/")[-1]
        self.setWindowTitle(f"X-Live EditCSV - {x}")
        if file_path:
            try:
                with open(file_path, newline='', encoding='utf-8') as csv_file:
                    reader = csv.reader(csv_file)
                    self.data = [row for row in reader if row]
                    self.header_data = self.data[0]
                    header_colums = len(self.header_data)+1
                    self.tab_size_str = self.data[1]
                    self.tab_size = []
                    for data in self.tab_size_str:
                        self.tab_size.append(int(data))
                    self.data = self.data[2:]
                    # IDs hinzufügen, falls keine vorhanden sind
                    if not self.data[0][0].isdigit():
                        self.data = [[str(i)] + row for i, row in enumerate(self.data, start=1)]
                    for x, row in enumerate(self.data):
                        while(len(self.data[x])) < header_colums:
                            self.data[x].append("")
                        self.data[x]=self.data[x][:header_colums]
                    x = file_path.split("/")[-1]
                    self.setWindowTitle(f"X-Live EditCSV - {x}")
                    self.update_table()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Datei: {e}")
        QTimer.singleShot(50,self.table_resize)

    def save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "CSV-Datei speichern", "", "CSV-Dateien (*.csv)")
        if not file_path.endswith(".csv"):
            file_path=file_path +".csv"
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(self.header_data) 
                    writer.writerow(self.tab_size) 
                    for row in self.data:
                        writer.writerow(row[1:])  # ID entfernen
                    QMessageBox.information(self, "Erfolg", "Datei wurde erfolgreich gespeichert!")
                    x = file_path.split("/")[-1]
                    self.setWindowTitle(f"X-Live EditCSV - {x}")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Datei: {e}")

    def update_table(self):
        self.table.setColumnCount(len(self.header_data))
        self.table.setHorizontalHeaderLabels(self.header_data)
        self.table.setRowCount(0)
        header_colums = len(self.header_data)+1
                    
        for x, row in enumerate(self.data):
            while(len(self.data[x])) < header_colums:
                self.data[x].append("")
            self.data[x]=self.data[x][:header_colums]
                    
        for row_data in self.data:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column, cell_data in enumerate(row_data[1:]):  # ID ignorieren
                self.table.setItem(row_number, column, QTableWidgetItem(cell_data))

        self.set_column_widths(self.tab_size)
        self.search_table()

    def add_entry(self):

        # Current date in dd.mm.yy format
        current_date = datetime.now().strftime("%d.%m.%y")
        header_colums = len(self.header_data)
        x = 0
        header = [str(len(self.data) + 1)]
        while x < header_colums:
            header.append("")
            x = x + 1
        new_row = header
        self.data.append(new_row)
        row = len(self.data)-1
        
        edit_dialog = EditDialog(self, self.data[row][1:],self.header_data,"Eintrag erstellen")  # ID ignorieren
        if edit_dialog.exec_():
            self.data[row][1:] = edit_dialog.get_data()  # ID bleibt unverändert
            self.update_table()
        else:
            self.data = self.data[:-1]
            self.update_table()

    def edit_entry(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hinweis", "Bitte wähle eine Zeile zum Bearbeiten aus.")
            return

        row = selected_items[0].row()
        edit_dialog = EditDialog(self, self.data[row][1:],self.header_data,"Eintrag bearbeiten")  # ID ignorieren
        if edit_dialog.exec_():
            self.data[row][1:] = edit_dialog.get_data()  # ID bleibt unverändert
            self.update_table()
            
    def edit_header(self):
        edit_dialog = EditHeaderDialog(self,self.header_data,self.tab_size)  # ID ignorieren
        if edit_dialog.exec_():
            self.header_data,self.tab_size = edit_dialog.get_data()  # ID bleibt unverändert
            self.update_table()

    def delete_entry(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hinweis", "Bitte wähle eine Zeile zum Löschen aus.")
            return
            
        #rows = list(set(item.row() for item in selected_items))
        rows = sorted(set(item.row() for item in selected_items), reverse=True)  # Von groß nach klein sortiert

        x = 0
        for row in rows:
            del self.data[row]
        
        self.update_table()
        
    def search_table(self):
        search_text = self.search_field.text().lower()
        exclude_text = self.search_field_ex.text().lower()  # Der zusätzliche Filter
        
        for row in range(self.table.rowCount()):
            # Überprüfe, ob der Text im Suchfeld vorhanden ist
            match = any(
                search_text in self.table.item(row, col).text().lower() for col in range(self.table.columnCount())
            )
            
            # Wenn die CheckBox aktiviert ist, überprüfe den Ausschlussfilter
            if self.search_revbox.isChecked() and exclude_text != "":
                exclude_match = any(
                    exclude_text in self.table.item(row, col).text().lower() for col in range(self.table.columnCount())
                )
            else:
                exclude_match = False  # Wenn nicht aktiviert, keine Ausschlussprüfung

            # Zeile ausblenden, wenn sie im Ausschlussfilter ist oder das Suchkriterium nicht erfüllt
            self.table.setRowHidden(row, not match or exclude_match)
          
    def search_table_ex(self):
        print("test")
        if self.search_revbox.isChecked():
            self.search_field_ex.show()
        else:
            self.search_field_ex.hide()
        self.search_table()
            
    def clear_data(self):
        self.data = []
        self.update_table()
        QTimer.singleShot(50,self.table_resize)
        self.setWindowTitle("X-Live EditCSV")

    def print_data(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Hinweis", "Bitte wähle eine Zeile zum Bearbeiten aus.")
            return
        rows = list(set(item.row() for item in selected_items))
        #rows = [item.row() for item in selected_items]
        data = [self.data[row][1:] for row in rows]
        text = []
        for row in data:
            text.append(", ".join(row))
        fulltext = "\n".join(text)
        total_width = self.table.viewport().width()
        
        PrintDialog(self,fulltext,total_width).exec_()  
        
    
    def open_context_menu(self, position: QPoint):
        """
        Kontextmenü bei Rechtsklick öffnen.
        """
        # Holen der ausgewählten Zeile
        index = self.table.indexAt(position)
        if not index.isValid():
            return  # Kein gültiger Eintrag unter dem Rechtsklick

        row = index.row()
        name = self.table.item(row, 0).text()  # Daten aus der ersten Spalte holen

        # Kontextmenü erstellen
        menu = QMenu(self)

        # Menüoptionen hinzufügen
         
        action_add = menu.addAction("Neu Zeile hinzufügen")
        action_edit = menu.addAction("Zeile bearbeit")
        action_delete = menu.addAction("Zeile(n) löschen")
        action_print = menu.addAction("Zeile(n) Ausgeben")
        

        # Kontextmenü anzeigen
        action = menu.exec_(self.table.viewport().mapToGlobal(position))

        # Aktionen auswerten
        if action == action_add:
            self.add_entry()
        elif action == action_edit:
            self.edit_entry()
        elif action == action_delete:
            self.delete_entry()  # Zeile löschen
        elif action == action_print:
            self.print_data()  # Zeilen ausgebenen


    # Ermittlung der Benutzersprache
    def get_user_language(self):
        return os.environ.get('LANG', 'en_US')


    def show_about_dialog(self):
        # Extrahiere die Version aus der Versionsermittlungsfunktion
        version = self.get_version_info()
        language = self.get_user_language()

        # Setze den Text je nach Sprache
        if language.startswith("de"):
            title = "Über X-Live EditCSV"
            text = (f"X-Live EditCSV<br><br>"
                    f"Autor: VerEnderT aka F. Maczollek<br>"
                    f"Webseite: <a href='https://github.com/verendert/'>https://github.com/verendert/</a><br>"
                    f"Version: {version}<br><br>"
                    f"Copyright © 2024 VerEnderT<br>"
                    f"Dies ist freie Software; Sie können es unter den Bedingungen der GNU General Public License Version 3 oder einer späteren Version weitergeben und/oder modifizieren.<br>"
                    f"Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich ist, aber OHNE JEDE GARANTIE; sogar ohne die implizite Garantie der MARKTGÄNGIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.<br><br>"
                    f"Sie sollten eine Kopie der GNU General Public License zusammen mit diesem Programm erhalten haben. Wenn nicht, siehe <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.")
        else:
            title = "About X-Live EditCSV"
            text = (f"X-Live EditCSV<br><br>"
                    f"Author: VerEnderT aka F. Maczollek<br>"
                    f"Website: <a href='https://github.com/verendert'>https://github.com/verendert</a><br>"
                    f"Version: {version}<br><br>"
                    f"Copyright © 2024 VerEnderT<br>"
                    f"This is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License Version 3 or any later version.<br>"
                    f"This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br><br>"
                    f"You should have received a copy of the GNU General Public License along with this program. If not, see <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.")
        
        # Über Fenster anzeigen
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setTextFormat(Qt.RichText)  # Setze den Textformatierungsmodus auf RichText (HTML)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()

    def get_version_info(self):
        try:
            result = subprocess.run(['apt', 'show', 'x-live-editcsv'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"Fehler beim Abrufen der Version: {e}")
        return "Unbekannt"





class EditDialog(QDialog):
    def __init__(self, parent, row_data, header_data,text):
        super().__init__(parent)
        self.setWindowTitle(text)
        self.row_data = row_data.copy()
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        

        self.inputs = []
        self.inputs_date = []
        for label, value in zip(
            header_data, self.row_data
        ):
            input_layout = QHBoxLayout()
            layout.addLayout(input_layout)

            input_label = QLabel(label + ":")
            input_layout.addWidget(input_label)

            input_field = QLineEdit(value)
            self.inputs.append(input_field)
            input_layout.addWidget(input_field)
            
            input_date = QPushButton("D")
            input_date.setFixedWidth(24)
            self.inputs_date.append(input_date)
            input_layout.addWidget(input_date)
            
        for x, button in enumerate(self.inputs_date):
            button.clicked.connect(lambda _, index=x: self.set_date(index))


        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
    def accept(self):
        self.row_data = [input_field.text() for input_field in self.inputs]
        super().accept()

    def reject(self):
        super().reject()

    def get_data(self):
        return self.row_data
        
    def set_date(self, x):
        # Current date in dd.mm.yy format
        current_date = datetime.now().strftime("%d.%m.%y")
        if self.inputs[x].text() == "":
            self.inputs[x].setText(current_date)


class EditHeaderDialog(QDialog):
    def __init__(self, parent, header_data, size):
        super().__init__(parent)
        self.setWindowTitle("Kopfzeile bearbeiten")
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        self.inputs_layout = QVBoxLayout(self)
        
        self.inputs = []
        self.inputs_size = []
        self.labels = []
        for x, value in enumerate(header_data):
            #print(size[x])
            input_layout = QHBoxLayout()
            self.inputs_layout.addLayout(input_layout)

            input_label = QLabel(f"Spalte {x+1}:")
            self.labels.append(input_label)
            input_layout.addWidget(input_label)

            input_field = QLineEdit(value)
            self.inputs.append(input_field)
            input_layout.addWidget(input_field)
            
        
            input_size = QLineEdit(str(size[x]))
            input_size.setFixedWidth(40)
            validator = QIntValidator(0, 100, self)
            input_size.setValidator(validator)
            self.inputs_size.append(input_size)
            input_layout.addWidget(input_size)
            
        button_layout = QHBoxLayout()
        
        layout.addLayout(self.inputs_layout)
        layout.addLayout(button_layout)

        
        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_button_action)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("-")
        self.remove_button.clicked.connect(self.remove_button_action)
        button_layout.addWidget(self.remove_button)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.adjustSize()
        
        
    def accept(self):
        self.row_data = [input_field.text() for input_field in self.inputs]
        self.size_data = [input_size.text() for input_size in self.inputs_size]
        self.size_check = sum(int(size) for size in self.size_data if size.isdigit())
        if self.size_check == 100:
            super().accept()
        else:
            QMessageBox.critical(self, "Fehler", f"Alle Spaltengrößen zusammen müssen 100 ergeben!\nAktuell ergeben diese: {self.size_check}")

    def remove_button_action(self):
        x = len(self.labels)
        if x >2: 
            self.labels[-1].hide()
            self.inputs[-1].hide()
            self.inputs_size[-1].hide()
            self.labels = self.labels[:-1]
            self.inputs = self.inputs[:-1]
            self.inputs_size = self.inputs_size[:-1]
        else:
            QMessageBox.critical(self, "Fehler", "Mindestens 2 Spalten müssen bleiben !")
        self.adjustSize()
        
    def add_button_action(self):
        x = len(self.labels)
        value = ""
        input_layout = QHBoxLayout()
        self.inputs_layout.addLayout(input_layout)
        input_label = QLabel(f"Spalte {x+1}:")
        self.labels.append(input_label)
        input_layout.addWidget(input_label)
        input_field = QLineEdit(value)
        self.inputs.append(input_field)
        input_layout.addWidget(input_field)
        input_size = QLineEdit("5")
        input_size.setFixedWidth(40)
        validator = QIntValidator(0, 100, self)
        input_size.setValidator(validator)
        self.inputs_size.append(input_size)
        input_layout.addWidget(input_size)
        self.adjustSize()
        
    def reject(self):
        super().reject()

    def get_data(self):
        return self.row_data,self.size_data
        

class PrintDialog(QDialog):
    def __init__(self, parent, fulltext, width):
        super().__init__(parent)
        self.setWindowTitle("Markierter Text")
        self.resize(width, 200)
        self.fulltext = fulltext
        layout = QVBoxLayout(self)

            
        self.output_field = QTextEdit()
        self.output_field.setText(fulltext)
        layout.addWidget(self.output_field)
        
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        
        self.copy_button = QPushButton("in zwischenablage kopieren")
        self.copy_button.clicked.connect(self.copy_text)
        button_layout.addWidget(self.copy_button)
        
        self.ok_button = QPushButton("Schließen")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
    def accept(self):
        super().accept()
        
    def copy_text(self):
            clipboard = QApplication.clipboard()
            # Text in die Zwischenablage kopieren
            clipboard.setText(self.fulltext)
            QMessageBox.information(self, "Erfolg", "Daten in Zischenablage kopiert!")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVEditor()
    window.show()
    sys.exit(app.exec_())
