import sys
import os
import importlib
import configparser
import subprocess
import hou

#Adding the Script directory, this will be more flexible when we lay out essential environment variables


#Houdini script directory
script_dir = os.path.join(os.getenv("SCRIPTSPATH"), "ibl_importer_v2")
modulesPath = os.path.join(script_dir, "modules")

# Add to Python path if not already there
if modulesPath not in sys.path:
    sys.path.insert(0, modulesPath)  # Insert at start to prioritize our modules

# Clear any existing module references
if 'dbQuery' in sys.modules:
    del sys.modules['dbQuery']
if 'iblImporter_houLogic' in sys.modules:
    del sys.modules['iblImporter_houLogic']

try:
    import dbQuery
    import iblImporter_houLogic
    1
except ImportError as e:
    # Provide detailed error message
    hou.ui.displayMessage(
        f"Failed to load required modules:\n{str(e)}\n\n"
        f"Please verify the modules exist in:\n{modulesPath}",
        severity=hou.severityType.Error
    )
    raise



try:
    from PySide2.QtCore import QTimer 
    from PySide2 import QtCore
    from PySide2.QtCore import Qt
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from PySide2.QtGui import QPixmap
    from PySide2 import QtUiTools
    from shiboken2 import wrapInstance #import shiboken 2 to make sure wrapInstance works
except:
    from PySide6.QtCore import QTimer
    from PySide6 import QtCore
    from PySide6.QtCore import Qt
    from PySide6 import QtWidgets
    from PySide6 import QtGui
    from PySide6.QtGui import QPixmap
    from PySide6 import QtUiTools
    from shiboken6 import wrapInstance #import shiboken 6 to make sure wrapInstance works

###
#
# Reading the config.ini and setting the default batch size to 10. 
# More settings can be added to this as the script grows. 
###


def read_config():
    """
    Read the configuration file and return the settings as a dictionary.
    If the file is missing, return default values.
    """
    config = configparser.ConfigParser()
    
    # Default values
    config_path = os.path.join(script_dir, "config.ini")
    settings = {
        "batch_size": 10  # Default batch size
    }
    
    # Check if the config file exists
    if os.path.exists(config_path):
        config.read(config_path)
        # Update with values from the config file
        if "Settings" in config:
            settings["batch_size"] = int(config["Settings"].get("batch_size", 20))
    
    return settings


###
#
# Constructing the class and its method for the UI.
#
###

class iblImporter(QtWidgets.QDialog):
    def __init__(self):
        super(iblImporter, self).__init__()
        
        # Construct the path to the UI file relative to the script's directory
        self.main_Ui_Path = os.path.join(script_dir,"ui", "importerUI.ui")
        self.iblItem_Ui_Path = os.path.join(script_dir,"ui", "itemUI.ui")
        self.selItem_Ui_Path = os.path.join(script_dir,"ui", "selItemUI.ui")
        
        
        print(f"UI Path: {self.main_Ui_Path}")
        self.setWindowTitle("IBL Importer v0.1")

        # Read the config file and store the batch size
        config = read_config()  # Get the settings dictionary
        self.batch_size = config["batch_size"]  # Extract the batch_size value
        print(f"Batch size: {self.batch_size}")  # Debugging: Print the batch size

        self.firstRun = True
        self.loaded_items_count = 0 #to keep track of the number of items loaded
        self.current_items = [] #store current loaded items
        self.user_selected_items = [] 

        self.init_ui()
        self.create_layout()
        self.create_groups()
        self.create_connections()
        self.populate_typeList()

    # --- UI Functions ---

    def init_ui(self):
        f = QtCore.QFile(self.main_Ui_Path)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        f.close()

    #Load the ui for the all IBL in database type. 
    def iblItem_Ui(self):
        f = QtCore.QFile(self.iblItem_Ui_Path)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.itemUI = loader.load(f, parentWidget = self.ui)
        
        f.close()

    #Load the ui for the selected items
    def selItem_Ui(self):
        f = QtCore.QFile(self.selItem_Ui_Path)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.selectionItemUI = loader.load(f, parentWidget = self.ui)
        
        f.close()


    #Create a group with the radio buttons from main UI to make sure no two can be selected at the same time
    def create_groups(self):
        self.typeGroup = QtWidgets.QButtonGroup()
        self.typeGroup.addButton(self.ui.hdriRadioButton, 1)
        self.typeGroup.addButton(self.ui.lgtMapsRadioButton, 2)
        self.typeGroup.addButton(self.ui.allRadioButton, 3)

        self.renderGroup = QtWidgets.QButtonGroup()
        self.renderGroup.addButton(self.ui.solarisRadioButton, 1)
        self.renderGroup.addButton(self.ui.arnoldRadioButton, 2)
        
        self.ui.hdriRadioButton.setChecked(True)
        

    #Creates the main layout for the UI.
    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)
        self.ui.batchSizeSpinBox.setValue(self.batch_size)

    def create_connections(self):
        self.ui.hdriRadioButton.toggled.connect(self.populate_typeList)
        self.ui.lgtMapsRadioButton.toggled.connect(self.populate_typeList)
        self.ui.allRadioButton.toggled.connect(self.populate_typeList)
        self.ui.typeListWidget.itemClicked.connect(self.populate_items)
        self.ui.batchSizeSpinBox.valueChanged.connect(self.update_batch_size)

        #Connect to scrollbar value changed signal
        self.scrollbar = self.ui.scrollArea.verticalScrollBar()
        self.scrollbar.valueChanged.connect(self.scrollbar_changed)
        self.ui.importButton.clicked.connect(self.import_selected_items)


    def create_itemUi_connections(self):
        self.itemUI.addSelButton.clicked.connect(self.add_item_to_sel_ui)
        
        # Connect selection change signals
        self.itemUI.unprocListWidget.itemSelectionChanged.connect(self.on_unproc_list_selection_changed)
        self.itemUI.procListWidget.itemSelectionChanged.connect(self.on_proc_list_selection_changed)

    def create_selectedItem_UI_connections(self, ui_widget):
        print("Creating connections for selected item UI")
        
        # Disconnect any existing connections first
        try:
            ui_widget.intensityQSlider.valueChanged.disconnect()
            ui_widget.exposureQSlider.valueChanged.disconnect()
            ui_widget.instensityQSpinBox.valueChanged.disconnect()
            ui_widget.exposureQSpinBox.valueChanged.disconnect()
        except:
            pass
        
        # Connect intensity controls
        ui_widget.intensityQSlider.valueChanged.connect(
            lambda value: self.on_intensitySlider_change(value, ui_widget)
        )
        ui_widget.instensityQSpinBox.valueChanged.connect(
            lambda value: self.on_intensityQSpinBox_change(value, ui_widget)
        )
        
        # Connect exposure controls
        ui_widget.exposureQSlider.valueChanged.connect(
            lambda value: self.on_exposureSlider_change(value, ui_widget)
        )
        ui_widget.exposureQSpinBox.valueChanged.connect(
            lambda value: self.on_exposureQSpinBox_change(value, ui_widget)
        )
    
        ui_widget.removeButton.clicked.connect(lambda: self.remove_selected_item_ui(ui_widget))


    
    # --- Slots ---
    
    def remove_selected_item_ui(self, ui_widget):
        print("Removing selected item UI")
        
        # Remove the specific widget instance from the list
        if ui_widget in self.user_selected_items:
            self.user_selected_items.remove(ui_widget)
        
        # Remove the widget from the layout
        self.ui.selItemVerticalLayout.removeWidget(ui_widget)
        
        # Delete the widget
        ui_widget.deleteLater()
        
        print(f"Remaining items: {len(self.user_selected_items)}")
        print(self.user_selected_items)
    
    def on_intensitySlider_change(self, value, ui_widget):
        ui_widget.instensityQSpinBox.setValue(value)
        

    def on_exposureSlider_change(self, value, ui_widget):
        ui_widget.exposureQSpinBox.setValue(value)
        

    def on_intensityQSpinBox_change(self, value, ui_widget):
        ui_widget.intensityQSlider.setValue(value)

    def on_exposureQSpinBox_change(self, value, ui_widget):
        ui_widget.exposureQSlider.setValue(value)

    def on_unproc_list_selection_changed(self):
    # When something is selected in unproc list, clear selection in proc list
        if self.itemUI.unprocListWidget.selectedItems():
            self.itemUI.procListWidget.clearSelection()

    def on_proc_list_selection_changed(self):
        # When something is selected in proc list, clear selection in unproc list
        if self.itemUI.procListWidget.selectedItems():
            self.itemUI.unprocListWidget.clearSelection()

    # --- Functionality ---

    def import_selected_items(self):
        if not self.user_selected_items:
            print("No items selected for import")
            return
        
        for widget in self.user_selected_items:
            try:
                # Get the item data from the widget's stored data
                item_data = widget.item_data['data']  # Access the nested 'data' dictionary
                file_name = widget.item_data['file_name']
                resolution = widget.item_data['resolution']
                
                print(f"Importing: {item_data['name']} at resolution {resolution}, file: {file_name}")
                
                # Get the full path to the file
                file_path = os.path.join(item_data['path'], file_name)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue
                
                if self.ui.arnoldRadioButton.isChecked():
                    renderer = "arnold"
                elif self.ui.solarisRadioBytton.isChecked():
                    renderer = "solaris"

                # Create the light based on item type
                if item_data['itemType'] == "HDRI":
                    iblImporter_houLogic.create_light(item_data, file_path, renderer, intensity=widget.instensityQSpinBox.value(), 
                                        exposure=widget.exposureQSpinBox.value())
                elif item_data['itemType'] == "Lightmap":
                    
                    iblImporter_houLogic.create_light(item_data,file_path, renderer, intensity=widget.instensityQSpinBox.value(), 
                                        exposure=widget.exposureQSpinBox.value())
                
                
                self.clear_selection_items()        
            
            except Exception as e:
                print(f"Error importing {item_data.get('name', 'unknown')}: {str(e)}")
                continue




    def populate_typeList(self):
        if self.firstRun:
            hdriTypes = dbQuery.hdriTypes()
            print(hdriTypes)
            for i in hdriTypes:
                self.ui.typeListWidget.addItem(i)
            self.firstRun = False
        
        else:
            if self.ui.hdriRadioButton.isChecked():
                self.ui.typeListWidget.clear()
                hdriTypes = dbQuery.hdriTypes()
                for i in hdriTypes:
                    self.ui.typeListWidget.addItem(i)
            elif self.ui.lgtMapsRadioButton.isChecked():
                self.ui.typeListWidget.clear()
                lgtMapTypes = dbQuery.lgtMapTypes()
                for i in lgtMapTypes:
                    self.ui.typeListWidget.addItem(i)
            elif self.ui.allRadioButton.isChecked():
                self.ui.typeListWidget.clear()
                allTypes = dbQuery.lgtMaps_and_hdris_types()
                for i in allTypes:
                    self.ui.typeListWidget.addItem(i)

    def populate_items(self):
            self.clear_items()
            selItem = self.ui.typeListWidget.currentItem()
            self.scrollbar.setValue(self.scrollbar.minimum())
            if not selItem:
                return
            
            if self.ui.hdriRadioButton.isChecked():
                self.current_items = dbQuery.get_items_from_type(selItem.text(), "HDRIs")
            elif self.ui.lgtMapsRadioButton.isChecked():
                self.current_items = dbQuery.get_items_from_type(selItem.text(), "Lightmaps")
            elif self.ui.allRadioButton.isChecked():
                self.current_items = dbQuery.get_items_from_type(selItem.text(), "All")
            
            self.loaded_items_count = 0  # Reset the count of loaded items
            self.loadNextBatchOfItems(self.current_items, len(self.current_items), self.get_selected_collection())

    def populate_unprocessed_list(self, unprocessed):
        """
        Populate the unprocessedList QListWidget with resolutions from the unprocessed array.
        Handles both single items (dict) and arrays of items.
        """
        self.itemUI.unprocListWidget.clear()  # Clear the list before populating
        
        if not unprocessed:
            return
        
        # Handle case where unprocessed is a single dictionary
        if isinstance(unprocessed, dict):
            for resolution, file_name in unprocessed.items():
                item_text = f"{resolution}: {file_name}"
                self.itemUI.unprocListWidget.addItem(item_text)
            return
        
        # Handle case where unprocessed is a list/array
        for item in unprocessed:
            if isinstance(item, dict):
                for resolution, file_name in item.items():
                    item_text = f"{resolution}: {file_name}"
                    self.itemUI.unprocListWidget.addItem(item_text)
            else:
                # Fallback for unexpected formats
                self.itemUI.unprocListWidget.addItem(str(item))

    def populate_processed_list(self, processed):
        """
        Populate the processedList QListWidget with resolutions from the processed array.
        Handles both single items (dict) and arrays of items.
        """
        self.itemUI.procListWidget.clear()  # Clear the list before populating
        
        if not processed:
            return
        
        # Handle case where processed is a single dictionary
        if isinstance(processed, dict):
            for resolution, file_name in processed.items():
                item_text = f"{resolution}: {file_name}"
                self.itemUI.procListWidget.addItem(item_text)
            return
        
        # Handle case where processed is a list/array
        for item in processed:
            if isinstance(item, dict):
                for resolution, file_name in item.items():
                    item_text = f"{resolution}: {file_name}"
                    self.itemUI.procListWidget.addItem(item_text)
            else:
                # Fallback for unexpected formats
                self.itemUI.procListWidget.addItem(str(item))

    def clear_items(self):
        for i in reversed(range(self.ui.itemVerticalLayout.count())):
            item = self.ui.itemVerticalLayout.itemAt(i)
            item.widget().deleteLater()

    def clear_selection_items(self):
        for i in reversed(range(self.ui.selItemVerticalLayout.count())):
            item = self.ui.selItemVerticalLayout.itemAt(i)
            item.widget().deleteLater()
        self.user_selected_items = []

    def get_selected_collection(self):
        """
        Get the name of the selected collection based on the radio buttons.
        """
        if self.ui.hdriRadioButton.isChecked():
            return "HDRIs"
        elif self.ui.lgtMapsRadioButton.isChecked():
            return "Lightmaps"
        elif self.ui.allRadioButton.isChecked():
            return "All"
        return None

    def loadNextBatchOfItems(self, items, amount, sel):
        """
        Load the next batch of items based on the batch size.
        """
        start_index = self.loaded_items_count
        end_index = min(start_index + self.batch_size, amount)
        
        for i in range(start_index, end_index):
            if sel == "HDRIs":
                item = dbQuery.get_item_info(items[i], "HDRIs")
                self.add_item_to_ui(item)
            elif sel == "Lightmaps":
                item = dbQuery.get_item_info(items[i], "Lightmaps")
                self.add_item_to_ui(item)
            elif sel == "All":
                item = dbQuery.get_item_info(items[i], "All")
                self.add_item_to_ui(item)
        
        self.loaded_items_count = end_index  # Update the count of loaded items
        self.ui.loadedItemsLabel.setText(f"Loaded items: {self.loaded_items_count}/{amount}")
        

    def add_item_to_ui(self, item):
        self.current_item = item
        self.iblItem_Ui()
        self.ui.itemVerticalLayout.addWidget(self.itemUI)
        self.itemUI.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,  # Horizontal policy
            QtWidgets.QSizePolicy.Expanding   # Vertical policy
        )
        self.itemUI.setMinimumSize(500, 250)
        self.itemUI.setMaximumSize(9999, 250)
        self.itemUI.nameLabel.setText(item['name'])
        self.itemUI.idLabel.setText(str(item['_id']))

        self.populate_unprocessed_list(item.get('unprocessed', []))
        self.populate_processed_list(item.get('processed', []))

        # Set the type label based on the radio button selection
        self.itemUI.typeLabel.setText(item['itemType'])
        
        # Load the thumbnail
        try:
            # Construct the full path to the thumbnail
            pixmapPath = os.path.join(item['path'], item['thumbnail'])
            
            # Load the pixmap
            pixmap = QtGui.QPixmap(pixmapPath)
            
            # Scale the pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.itemUI.thumbnail.size(),  # Target size (size of the QLabel)
                QtCore.Qt.KeepAspectRatio,    # Maintain aspect ratio
                QtCore.Qt.SmoothTransformation  # Use smooth scaling
            )
            
            # Set the scaled pixmap to the QLabel
            self.itemUI.thumbnail.setPixmap(scaled_pixmap)
        
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            self.itemUI.thumbnail.setText("N/A")

        # Store the item data with the button
        self.itemUI.addSelButton.item_data = item
        self.create_itemUi_connections()


    def add_item_to_sel_ui(self):
        button = self.sender()
        item_data = button.item_data
        
        # Get selected items from both lists
        unproc_selected = button.parent().unprocListWidget.selectedItems()
        proc_selected = button.parent().procListWidget.selectedItems()
        
        # Ensure exactly one item is selected
        if len(unproc_selected) + len(proc_selected) != 1:
            print("Please select exactly one resolution (either from Unprocessed or Processed list)")
            return
        
        # Determine which list has the selection and get the resolution and file name
        if unproc_selected:
            selected_item = unproc_selected[0]
            parts = selected_item.text().split(": ")
            if len(parts) == 2:
                selected_resolution = parts[0].strip()
                file_name = parts[1].strip()
            else:
                selected_resolution = selected_item.text()
                file_name = "N/A"
        else:
            selected_item = proc_selected[0]
            parts = selected_item.text().split(": ")
            if len(parts) == 2:
                selected_resolution = parts[0].strip()
                file_name = parts[1].strip()
            else:
                selected_resolution = selected_item.text()
                file_name = "N/A"
        
        # Now create the selection UI
        self.selItem_Ui()
        self.ui.selItemVerticalLayout.addWidget(self.selectionItemUI)
        self.selectionItemUI.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.selectionItemUI.setMinimumSize(365, 270)
        self.selectionItemUI.setMaximumSize(9999, 270)
        
        # Populate UI with item data
        self.selectionItemUI.nameLabel.setText(item_data['name'])
        self.selectionItemUI.idLabel.setText(str(item_data['_id']))
        self.selectionItemUI.itemTypeLabel.setText(item_data['itemType'])
        self.selectionItemUI.resolutionLabel.setText(f"{selected_resolution}")
        self.selectionItemUI.fileNameLabel.setText(file_name)
        
        # Load thumbnail
        try:
            pixmapPath = os.path.join(item_data['path'], item_data['thumbnail'])
            pixmap = QtGui.QPixmap(pixmapPath)
            scaled_pixmap = pixmap.scaled(
                self.selectionItemUI.thumbnail.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.selectionItemUI.thumbnail.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            self.selectionItemUI.thumbnail.setText("N/A")

        #Store the item data with the UI widget
        self.selectionItemUI.item_data = {
            'data': item_data,
            'resolution': selected_resolution,
            'file_name': file_name,
            'unique_id': f"{item_data['_id']}_{selected_resolution}_{len(self.user_selected_items)}"  # Add unique identifier
        }
    
        # Create connections for this specific UI instance
        self.create_selectedItem_UI_connections(self.selectionItemUI)
        
        self.user_selected_items.append(self.selectionItemUI)  # Store the UI widget in the list
        print(f"Adding item: {item_data['name']} to the selection.")
        print(f"Current selection count: {len(self.user_selected_items)}")
        
    
    def update_batch_size(self, value):
        self.batch_size = value
        self.populate_items()

    def scrollbar_changed(self, value):
        scrollbar = self.ui.scrollArea.verticalScrollBar()
        if value == scrollbar.maximum():
            self.loadNextBatchOfItems(self.current_items, len(self.current_items), self.get_selected_collection())


# ... (all your previous code remains the same until the run() function)

def run():
    """Function to create and show the window, returns the window instance"""
    window = iblImporter()
    window.setParent(hou.qt.mainWindow(),Qt.WindowStaysOnTopHint | Qt.Dialog)
    window.show()
    return window




run()



if __name__ == "__main__":
    # Use a different variable name for the window instance
    global ibl_window
    
    try:
        # Try to close previous instance if it exists
        ibl_window.close()
        ibl_window.deleteLater()
    except:
        pass
    
    # Create and show new window
    ibl_window = iblImporter()
    ibl_window.setParent(hou.qt.mainWindow(),Qt.WindowStaysOnTopHint | Qt.Dialog)
    ibl_window.show()