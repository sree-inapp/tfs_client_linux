import sys
import glob, os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase,QGuiApplication,QPalette,QColor
from PyQt5.QtWidgets import QWidget, QGridLayout,QPushButton, QApplication,QApplication,QFileDialog,QLineEdit
import json

with open("config.json") as f: 
    config = json.loads(f.read())


def checkTFSWorkspace(path):
    # Checks if a workspace is already configured in the selected folder
    isdir = os.path.isdir(path+"/.tf") 
    return isdir
    

def getStyleSheet(element,mode):
    # Stylesheets for UI elements : sililar to css
    styles = {
                "QPushButton": {     
                            "enabled":"background : #050505; min-height:30px; border:2px solid rgba(255,255,255,60)",
                            "disabled":"background:#111; min-height:30px; color:#3f3f3f; border:2px solid #0f0f0f",
                            "hilighted":"background:#141da3; min-height:30px;",
                            "success" : "background:#63a314"
                                },
                "QLineEdit":{
                            "enabled":"background : #050505; min-height:30px; border:2px solid rgba(255,255,255,60)",
                            "disabled":"background:#222; min-height:30px; border:2px solid #222",
                            "hilighted":"background:#034ba3; min-height:30px; "
                                }
            }
  
    return styles[element][mode]


class Window(QWidget):

    def __init__(self):

        super().__init__()

        # Add ui elements here
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        default_palette = QGuiApplication.palette()
        default_palette.setColor(QPalette.PlaceholderText,QColor(200,200,200,80))
        QGuiApplication.setPalette(default_palette)

        QFontDatabase.addApplicationFont('./fonts/Poppins/Poppins-Regular.ttf')

        self.setStyleSheet("""
                background-color:#1c1c1c;
                color:#FFF;
                font-family:Poppins;
                
                """)
        
       
        self.workspace_path = ""
        self.username= config['username']
        self.password= config['password']
        self.project_path=""
        
        self.btn_select_workspace = QPushButton('Select workspace')
        self.btn_select_workspace.setStyleSheet(getStyleSheet(self.btn_select_workspace.__class__.__name__,"hilighted"))
        grid_layout.addWidget(self.btn_select_workspace, 0, 0, 1, 2)
        self.btn_select_workspace.clicked.connect(self.getFolder)

        self.txb_collection_url = QLineEdit(self)
        self.txb_collection_url.setPlaceholderText("  Collection url")
        grid_layout.addWidget(self.txb_collection_url, 1, 0, 1, 1)

        self.txb_workspace_name = QLineEdit(self)
        self.txb_workspace_name.setPlaceholderText("  Workspace name")
        grid_layout.addWidget(self.txb_workspace_name, 1, 1, 1, 1)

        self.txb_project_path = QLineEdit(self)
        self.txb_project_path.setPlaceholderText("  $/Project path")
        grid_layout.addWidget(self.txb_project_path, 2, 0, 1, 1)

        self.btn_create_workspace = QPushButton('Create workspace')
        grid_layout.addWidget(self.btn_create_workspace, 2, 1, 1, 1)
        self.btn_create_workspace.clicked.connect(self.createWorkspace)
        
        

        self.btn_checkin = QPushButton('Checkin')
        grid_layout.addWidget(self.btn_checkin, 3, 0, 1, 2)
        self.btn_checkin.clicked.connect(self.checkinModified)

        self.txb_checkin_id = QLineEdit(self)
        self.txb_checkin_id.setPlaceholderText("  Id")
        grid_layout.addWidget(self.txb_checkin_id, 4, 0, 1,1)

        self.txb_checkin_message = QLineEdit(self)
        self.txb_checkin_message.setPlaceholderText("  Message")
        grid_layout.addWidget(self.txb_checkin_message, 4, 1, 1, 1)

    

        self.btn_checkout = QPushButton('Clone')
        grid_layout.addWidget(self.btn_checkout, 5, 0, 1, 2)
        self.btn_checkout.clicked.connect(self.clone)

        self.btn_get_modified = QPushButton('Checkout')
        grid_layout.addWidget(self.btn_get_modified, 6, 0, 1, 2)
        self.btn_get_modified.clicked.connect(self.checkout)

        self.workspace_widget = [self.txb_collection_url,self.txb_workspace_name,self.txb_project_path,self.btn_create_workspace]
        self.disableItems(self.workspace_widget)
        self.control_widget = [self.btn_checkin,self.txb_checkin_id,self.txb_checkin_message,self.btn_checkout,self.btn_get_modified]
        self.disableItems(self.control_widget)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("TFS Linux")
        self.show()

    def disableItems(self,items):
        # Takes a list of widgets as argument and disable them
        for x in items: 
            x.setEnabled(False)
            element = x.__class__.__name__
            x.setStyleSheet(getStyleSheet(element,"disabled"))
            
            
    def enableItems(self,items):
        # Takes a list of widgets as argument and enable them
        for x in items: 
            x.setEnabled(True)
            element = x.__class__.__name__
            x.setStyleSheet(getStyleSheet(element,"enabled"))


    
    
    def checkinModified(self):
        #Runs TFS CLI Command to checkin
        os.system(f'./tfs/tf checkin -recursive -login:{self.username},{self.password} "{self.workspace_path}/"')
        self.txb_checkin_id.clear()
        self.txb_checkin_message.clear()
       
    def clone(self):
        #Runs TFS CLI Command to clone
        os.system(f'./tfs/tf get -force -recursive -login:{self.username},{self.password} "{self.project_path}" "{self.workspace_path}/"')
    
    def checkout(self):
        #Runs TFS CLI Command to checkout
        os.system(f'./tfs/tf get -recursive -login:{self.username},{self.password} "{self.workspace_path}/"')

    def createWorkspace(self):
        #Runs TFS CLI Command to create workspace
        collection_url = self.txb_collection_url.text()
        locaion = "local"
        workspace_name = self.txb_workspace_name.text()
        self.project_path = self.txb_project_path.text()
        cmd_new_worspace = f"./tfs/tf workspace -new -collecton:{collection_url} -location:{locaion} {workspace_name}"
        cmd_map_worspace = f'./tfs/tf workfold -map -collecton:{collection_url} -workspace:{workspace_name} "{self.project_path}" "{self.workspace_path}/"'
        os.system(cmd_new_worspace)
        os.system(cmd_map_worspace)
        self.enableItems(self.control_widget)
        self.disableItems(self.workspace_widget)



    def getFolder(self):
        #Folder path picker
        self.workspace_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if self.workspace_path:
            workspace_exists = checkTFSWorkspace(self.workspace_path)
            if workspace_exists:
                self.disableItems(self.workspace_widget)
                self.enableItems(self.control_widget)
            else:
                self.enableItems(self.workspace_widget)
                self.disableItems(self.control_widget)

        

 
app = QApplication(sys.argv)

window = Window()
sys.exit(app.exec_())