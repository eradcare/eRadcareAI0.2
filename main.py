import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFrame,QToolBar,QStatusBar,QMessageBox,QDialog,QPlainTextEdit,QHBoxLayout, QComboBox, QGridLayout,QListWidget
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QColor, QFont, QScreen,QGuiApplication,QIcon,QAction,QIntValidator
import qdarktheme
import psycopg2
import psycopg2.extras
import uuid
psycopg2.extras.register_uuid()
import re  
from training import trainingWindow
from siteOAR import siteOARWindow

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

global conn
gusername =""
 # Modify these with your PostgreSQL database details
conn  = psycopg2.connect(
        database="aieradcare",
        user="postgres",
        password="Pass@143",
        host="localhost",
        port="5432",
    )
# Function to check if the provided username and password match the database
def check_credentials(username, password):    
    cursor = conn.cursor()
    #cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    cursor.execute("SELECT password FROM users WHERE username = %s ", (username, ))  
    stored_password = cursor.fetchone()
    cursor.close()
    if stored_password:
        return stored_password[0] == password
    return False

class userWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - User")
        if gusername.lower() =="admin" :
            self.resize(900, 270)
        else :
            self.resize(400,250)
        self.setWindowIcon(QIcon("images/erai.png"))

        layout =  QGridLayout()
        # Create vertical frame
        vertical_frame = QFrame()
        vertical_frame.setFrameShape(QFrame.StyledPanel)
        vertical_layout = QVBoxLayout()
        self.onlyInt = QIntValidator()

        # Add details to vertical frame
        self.username_label = QLabel('User Name')
        self.username_input = QLineEdit()
        self.email_label = QLabel('eMail')
        self.eamil_input = QLineEdit()
        self.mob_label = QLabel("Mobile #")
        self.mob_input = QLineEdit()
        self.mob_input.setValidator(self.onlyInt)
        self.mob_input.setMaxLength(10)
        self.role_lable = QLabel("Role")        
        self.role_com =  QComboBox()
        self.role_com.addItem("Radiation Oncologist")
        self.role_com.addItem("Medical Physicist")
        vertical_layout.addWidget(self.username_label)
        vertical_layout.addWidget(self.username_input)
        vertical_layout.addWidget(self.email_label)
        vertical_layout.addWidget(self.eamil_input)
        vertical_layout.addWidget(self.mob_label)
        vertical_layout.addWidget(self.mob_input)
        vertical_layout.addWidget(self.role_lable)
        vertical_layout.addWidget(self.role_com)
        if gusername.lower() !="admin":                        
            cursor = conn.cursor()
            cursor.execute("SELECT email,phone,orole FROM users WHERE username = %s ", (gusername, ))  
            stored_data = cursor.fetchone()           
            self.username_input.setText(gusername)
            self.eamil_input.setText(stored_data[0])
            self.mob_input.setText(stored_data[1])
            self.role_com.setCurrentText(stored_data[2])

        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame,0,0)
         # Create horizontal frame
        horizontal_frame = QFrame()
        horizontal_frame.setFrameShape(QFrame.StyledPanel)
        horizontal_layout = QHBoxLayout()

        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton("Delete")  
        self.close_button = QPushButton("Close")
        self.add_button.clicked.connect(self.adddata)
        self.delete_button.clicked.connect(self.deletedata)        
        self.close_button.clicked.connect(self.closedata)

        if gusername.lower() !="admin":
            self.add_button.setText("Save")
            self.delete_button.setHidden(True)                  

        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.addWidget(self.delete_button)
        horizontal_layout.addWidget(self.close_button)
        
        horizontal_frame.setLayout(horizontal_layout)
        layout.addWidget(horizontal_frame,1,0)

        if gusername.lower() == "admin":
            #list frame
            # Create horizontal frame
            list_frame = QFrame()
            list_frame.setFrameShape(QFrame.StyledPanel)
            list_layout = QHBoxLayout()

            self.user_list = QListWidget()
            cursor = conn.cursor()
            cursor.execute("SELECT username from users ")  
            stored_data = cursor.fetchall()            
            cursor.close()
            for useritem in stored_data : self.user_list.addItems((useritem))
            self.user_list.itemClicked.connect(self.listclick)
            list_layout.addWidget(self.user_list)
            list_frame.setLayout(list_layout)
            layout.addWidget(list_frame,0,1)
            self.disableText()

            #update and reset button
             # Create horizontal frame
            updatereset_frame = QFrame()
            updatereset_frame.setFrameShape(QFrame.StyledPanel)
            updatereset_layout = QHBoxLayout()

            self.update_button = QPushButton('Update')
            self.reset_button = QPushButton("Reset")            
            self.update_button.clicked.connect(self.updatedata)
            self.reset_button.clicked.connect(self.resetpassword)

            updatereset_layout.addWidget(self.update_button)
            updatereset_layout.addWidget(self.reset_button)
            
        
            updatereset_frame.setLayout(updatereset_layout)
            layout.addWidget(updatereset_frame,1,1)

        self.setLayout(layout)
        self.center_window()
        
    def checkLic(self,num):
            cursor = conn.cursor()
            cursor.execute("SELECT lic FROM hospitalreg") 
            stored_data = cursor.fetchone()
            lic_no = stored_data[0]            
            cursor.execute("SELECT orole FROM users WHERE orole = %s ", ("Radiation Oncologist", ))  
            stored_data = cursor.fetchall()  
            return ((len(stored_data)+num) > lic_no )
           
    def updatedata(self):         
        allow1 =0
        if len(self.username_input.text()) == 0 and self.update_button.text() == "Update":
            dlg = QMessageBox.critical(self,"eRadcareAI","User name should not empty")
            allow1=1
            
        if  self.username_input.text() == "admin" :
            dlg = QMessageBox.critical(self,"eRadcareAI","User name should not   admin  ?")
            allow1 =1

        if len(self.username_input.text()) != 0 and self.update_button.text() == "Update" and allow1 == 0:          
            self.update_button.setText("Save")
            self.delete_button.setText("Cancel")
            self.close_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            self.add_button.setEnabled(False)
            self.enableText()
            self.username_input.setEnabled(False)
            self.eamil_input.setFocus()
            allow1 =1 
        
        if self.update_button.text() =="Save" and allow1 ==0 :       
               
            if len(self.eamil_input.text()) == 0 or len(self.mob_input.text()) ==0 :
                dlg = QMessageBox.critical(self,"eRadcareAI","User details should not be empty")
                #self.eamil_input.setFocus(True)
                allow1 =1
            if (re.fullmatch(regex, self.eamil_input.text())) :
                 print("Valid mail")
            else:
                dlg = QMessageBox.critical(self,"eRadcareAI","The eMail address is not correct !!!")  
                #self.eamil_input.setFocus(True)
                allow1 =1
            if self.checkLic(num=0) == True :
                dlg = QMessageBox.critical(self,"eRadcareAI","Number of Lic exceeded... ")  
                allow1 =1
             
            if allow1 == 0 :          
                
                cursor = conn.cursor()
                cursor.execute("UPDATE users  SET username =%s ,email=%s, phone=%s ,orole=%s where username = %s " ,(self.username_input.text(),self.eamil_input.text(),self.mob_input.text(),str(self.role_com.currentText()),gusername)) 
                conn.commit()
                dlg = QMessageBox.information(self,"eRadcareAI","The user data updated")                 
                cursor.close()
                self.clearData()
                self.add_button.setEnabled(True)
                self.update_button.setText("Update")

    def resetpassword(self):
                print(self.username_input.text())
                 
                if len(self.username_input.text()) == 0  or self.username_input.text() == "admin" :
                    dlg = QMessageBox.critical(self,"eRadcareAI","User name should not empty or admin as a username?")
                 
                else :
                    dlg = QMessageBox(self)
                    dlg.setWindowTitle("eRadcareAI!")
                    dlg.setText("Shall I reset the password?")
                    dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    dlg.setIcon(QMessageBox.Question)
                    button = dlg.exec()

                    if button == QMessageBox.Yes:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users  SET password=%s WHERE username = %s ", ("pass",self.username_input.text(), )) 
                        conn.commit()
                        cursor.close()
                        dlg = QMessageBox.critical(self,"eRadcareAI","The password reseted")
    
    def listclick(self, idx: int):        
        listname=([item.text() for item in self.user_list.selectedItems()])
        ls = ""
        ln = ls.join(listname)         
        self.username_input.setText(ls.join(listname))
        cursor = conn.cursor()
        cursor.execute("SELECT email,phone,orole FROM users WHERE username = %s ", (ln, ))  
        stored_data = cursor.fetchone()           
        self.eamil_input.setText(stored_data[0])
        self.mob_input.setText(stored_data[1])
        self.role_com.setCurrentText(stored_data[2])

    def adddata(self) :

        allow =0 

        if self.add_button.text() == "Save":
        
            if len(self.username_input.text()) == 0 or len(self.eamil_input.text()) == 0 or len(self.mob_input.text()) ==0 :
                dlg = QMessageBox.critical(self,"eRadcareAI","User details should not be empty")
                self.username_input.setFocus()
                allow =1
            if (re.fullmatch(regex, self.eamil_input.text())) :
                 print("Valid mail")
            else:
                dlg = QMessageBox.critical(self,"eRadcareAI","eMail address is not correct")  
                self.eamil_input.setFocus(True)
                allow = 1

             
            if self.checkLic( num = 1) == True :
                dlg = QMessageBox.critical(self,"eRadcareAI","Number of Lic exceeded... ")  
                allow =1
             
        if allow == 0 and self.add_button.text() == "Save"  :
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username = %s ", (gusername, )) 
            stored_data = cursor.fetchone()
            print(len(stored_data))
            if gusername.lower() != "admin" :
                if len(stored_data) > 1  :
                    print ( "duplicate data")
                    dlg = QMessageBox.critical(self,"eRadcareAI", "Username Shoud be Unique" )
                if len(stored_data) == 1 :                 
                    cursor.execute("UPDATE users  SET username =%s ,email=%s, phone=%s ,orole=%s where username = %s " ,(self.username_input.text(),self.eamil_input.text(),self.mob_input.text(),str(self.role_com.currentText()),gusername)) 
                    dlg = QMessageBox.information(self,"eRadcareAI","User Data Update")                 
                    cursor.close()
            
            if len(stored_data) == 1 and gusername.lower() == "admin" :
                passworddf = "pass"
                cursor.execute("INSERT INTO users( uuid,username,email,phone,orole,password) VALUES ( %s,%s,%s,%s,%s,%s)",( uuid.uuid4(),self.username_input.text(),self.eamil_input.text(),self.mob_input.text(),str(self.role_com.currentText()),passworddf))
                conn.commit()
                cursor.close()
                self.user_list.addItem(self.username_input.text())                              
                dlg = QMessageBox.information(self,"eRadcareAI","The new user data Added")                
                allow =2
                self.clearData()

                

        if  allow !=2 and self.add_button.text() == "Add":
            self.add_button.setText("Save")
            self.delete_button.setText("Cancel")
            self.close_button.setEnabled(False)
            self.update_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            self.enableText()
            self.username_input.setFocus()
            self.clearText()

    def clearData(self) :
                self.clearText()
                self.add_button.setText("Add")
                self.delete_button.setText("Delete")
                self.update_button.setEnabled(True)
                self.reset_button.setEnabled(True)
                self.close_button.setEnabled(True)
                self.disableText()

    def clearText(self):
        self.username_input.setText("")
        self.eamil_input.setText("")
        self.mob_input.setText("")
        self.role_com.setCurrentText("")


     

    def deletedata(self):
        allow =0
        if self.delete_button.text() =="Cancel" :
            self.clearData() 
            allow=1
        if allow == 0 and self.delete_button.text() == "Delete" :
            if len(self.username_input.text()) == 0:
                dlg = QMessageBox.critical(self,"eRadcareAI","User name should not empty")
            else :
                dlg = QMessageBox(self)
                dlg.setWindowTitle("eRadcareAI!")
                dlg.setText("Shall I delete?")
                dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                dlg.setIcon(QMessageBox.Question)
                button = dlg.exec()

                if button == QMessageBox.Yes:
                    cursor = conn.cursor()
                    cursor.execute("Delete FROM users WHERE username = %s ", (self.username_input.text(), )) 
                    conn.commit()
                    cursor.close()
                    dlg = QMessageBox.critical(self,"eRadcareAI","User deleted")
                    cursor = conn.cursor()
                    cursor.execute("SELECT username from users ")  
                    stored_data = cursor.fetchall()            
                    cursor.close()  
                    self.user_list.clear()  
                    self.clearText()            
                    for useritem in stored_data : self.user_list.addItems((useritem))
                else:
                    print("No!")

    def closedata(self):
        self.hide()
    
    def center_window(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        x = screen_geometry.width() // 2 - window_geometry.width() // 2
        y = screen_geometry.height() // 2 - window_geometry.height() // 2
        self.move(x, y)
    
    def enableText(self):
        self.username_input.setEnabled(True)
        self.eamil_input.setEnabled(True)
        self.mob_input.setEnabled(True)
        self.role_com.setEnabled(True)
        if gusername.lower() == "admin" :             
            self.user_list.setEnabled(False)

    def disableText(self):
        self.username_input.setEnabled(False)
        self.eamil_input.setEnabled(False)
        self.mob_input.setEnabled(False)
        self.role_com.setEnabled(False)
        if gusername.lower() == "admin" :            
            self.user_list.setEnabled(True)

class bSiteWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - BodySite")
        self.resize(600,300)
        self.setWindowIcon(QIcon("images/erai.png"))
        global sitemode 
        sitemode="None"

        layout =  QGridLayout()
        # Create vertical frame
        vertical_frame = QFrame()
        vertical_frame.setFrameShape(QFrame.StyledPanel)
        vertical_layout = QVBoxLayout()
        self.onlyInt = QIntValidator()

        # Add details to vertical frame
        self.bsite_label = QLabel('Site')
        self.bsite_input = QLineEdit()
        self.remarks_label = QLabel('Remarks')
        self.remarks_input = QPlainTextEdit()
        vertical_layout.addWidget(self.bsite_label)
        vertical_layout.addWidget(self.bsite_input)
        vertical_layout.addWidget(self.remarks_label)
        vertical_layout.addWidget(self.remarks_input)        
        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame,0,0)
         # Create horizontal frame
        horizontal_frame = QFrame()
        horizontal_frame.setFrameShape(QFrame.StyledPanel)
        horizontal_layout = QHBoxLayout()
        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton("Delete")  
        self.update_button = QPushButton("Update")
        self.add_button.clicked.connect(self.adddata)
        self.delete_button.clicked.connect(self.deletedata)        
        self.update_button.clicked.connect(self.updatedata)        
        horizontal_layout.addWidget(self.add_button)
        horizontal_layout.addWidget(self.delete_button)
        horizontal_layout.addWidget(self.update_button)        
        horizontal_frame.setLayout(horizontal_layout)
        layout.addWidget(horizontal_frame,1,0)
            #list frame
            # Create horizontal frame
        list_frame = QFrame()
        list_frame.setFrameShape(QFrame.StyledPanel)
        list_layout = QHBoxLayout()

        self.user_list = QListWidget()
        cursor = conn.cursor()
        cursor.execute("SELECT bsite_name from bsite ")  
        stored_data = cursor.fetchall()            
        cursor.close()
        for useritem in stored_data : self.user_list.addItems((useritem))
        self.user_list.itemClicked.connect(self.listclick)
        list_layout.addWidget(self.user_list)
        list_frame.setLayout(list_layout)
        layout.addWidget(list_frame,0,1)
        self.disableText()

        #update and reset button
        # Create horizontal frame
        close_frame = QFrame()
        close_frame.setFrameShape(QFrame.StyledPanel)
        close_layout = QHBoxLayout()
        self.close_button = QPushButton('Close')        
        self.close_button.clicked.connect(self.closedata)
        close_layout.addWidget(self.close_button)
        close_frame.setLayout(close_layout)
        layout.addWidget(close_frame,1,1)

        self.setLayout(layout)
        self.center_window()

    def updatedata(self):   
        global sitemode      
        
        siteallow1 =0


        if len(self.bsite_input.text()) == 0 and self.update_button.text() == "Update":
            dlg = QMessageBox.critical(self,"eRadcareAI","Site name should not empty")
            siteallow1=1

        if len(self.bsite_input.text()) != 0 and self.update_button.text() == "Update" and siteallow1 == 0:          
            self.update_button.setText("Save")
            self.delete_button.setText("Cancel")
            self.close_button.setEnabled(False)            
            self.add_button.setEnabled(False)
            sitemode = self.bsite_input.text()
            self.enableText()             
            siteallow1 =1 
        
        if self.update_button.text() =="Save" and siteallow1 ==0 :       

            if len(self.bsite_input.text()) == 0 :
                dlg = QMessageBox.critical(self,"eRadcareAI","Site details should not be empty")                
                siteallow1 =1
            cursor = conn.cursor()
            cursor.execute("SELECT bsite_name FROM bsite WHERE bsite_name = %s ", (self.bsite_input.text(), )) 
            stored_data = cursor.fetchall()          
            cursor.close()

            if sitemode != self.bsite_input.text() and len(stored_data) >= 1 :
                dlg = QMessageBox.critical(self,"eRadcareAI","Site details should not be empty")
                self.bsite_input.setFocus()
                siteallow =1

            if siteallow1 == 0  :
                cursor = conn.cursor()
                cursor.execute("UPDATE bsite  SET bsite_name =%s , remarks=%s" ,(self.bsite_input.text(),self.remarks_input.toPlainText())) 
                conn.commit()
                cursor.execute("SELECT bsite_name from bsite ")  
                stored_data = cursor.fetchall()            
                cursor.close()  
                self.user_list.clear()  
                self.clearText()            
                for useritem in stored_data : self.user_list.addItems((useritem))
                dlg = QMessageBox.information(self,"eRadcareAI","The data updated")                 
                
                self.clearData()
                self.add_button.setEnabled(True)
                self.update_button.setText("Update")

    def listclick(self, idx: int):        
        listname=([item.text() for item in self.user_list.selectedItems()])
        ls = ""
        ln = ls.join(listname)         
        self.bsite_input.setText(ls.join(listname))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bsite WHERE bsite_name = %s ", (ln, ))  
        stored_data = cursor.fetchone()           
        self.remarks_input.setPlainText(stored_data[2])
        
    def adddata(self) :

        siteallow5 =0 
        global sitemode

        if self.add_button.text() == "Save":        
            if len(self.bsite_input.text()) == 0 :
                dlg = QMessageBox.critical(self,"eRadcareAI","Site details should not be empty")
                self.bsite_input.setFocus()
                siteallow5 =1

        if siteallow5 == 0 and self.add_button.text() == "Save"  :            
            cursor = conn.cursor()
            cursor.execute("SELECT bsite_name FROM bsite WHERE bsite_name = %s ", (self.bsite_input.text(), )) 
            stored_data = cursor.fetchall()           
            #print(stored_data)

            if sitemode=="add" and len(stored_data) >= 1 :
                print ( "duplicate data")
                dlg = QMessageBox.critical(self,"eRadcareAI", "Site name shoud be Unique" )
            if sitemode=="add" and len(stored_data) == 0 :
                cursor.execute("INSERT INTO bsite( uuid,bsite_name,remarks) VALUES ( %s,%s,%s)",( uuid.uuid4(),self.bsite_input.text(),self.remarks_input.toPlainText()))
                conn.commit()
                cursor.close()
                self.user_list.addItem(self.bsite_input.text())  
                self.clearData() 
                siteallow5 = 3                           
                dlg = QMessageBox.information(self,"eRadcareAI","The new site data Added")                
                sitemode="None"
                print("before",siteallow5)

        if  siteallow5 !=3 and self.add_button.text() == "Add":
            self.add_button.setText("Save")
            self.delete_button.setText("Cancel")
            self.close_button.setEnabled(False)
            self.update_button.setEnabled(False)            
            self.enableText()            
            self.clearText()
            sitemode="add"
            

    def clearData(self) :
                self.clearText()
                self.add_button.setText("Add")
                self.delete_button.setText("Delete")
                self.update_button.setEnabled(True)                
                self.close_button.setEnabled(True)
                self.disableText()

    def clearText(self):
        self.bsite_input.setText("")
        self.remarks_input.setPlainText("")
        
    def deletedata(self):
        siteallow3 =0
        if self.delete_button.text() =="Cancel" :
            self.clearData() 
            siteallow3=1
        if siteallow3 == 0 and self.delete_button.text() == "Delete" :
            if len(self.bsite_input.text()) == 0:
                dlg = QMessageBox.critical(self,"eRadcareAI","Site name should not empty")
            else :
                dlg = QMessageBox(self)
                dlg.setWindowTitle("eRadcareAI!")
                dlg.setText("Shall I delete?")
                dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                dlg.setIcon(QMessageBox.Question)
                button = dlg.exec()

                if button == QMessageBox.Yes:
                    cursor = conn.cursor()
                    cursor.execute("Delete FROM bsite WHERE bsite_name = %s ", (self.bsite_input.text(), )) 
                    conn.commit()
                    cursor.close()
                    dlg = QMessageBox.critical(self,"eRadcareAI","Site deleted")
                    cursor = conn.cursor()
                    cursor.execute("SELECT bsite_name from bsite ")  
                    stored_data = cursor.fetchall()            
                    cursor.close()  
                    self.user_list.clear()  
                    self.clearText()            
                    for useritem in stored_data : self.user_list.addItems((useritem))
                else:
                    print("No!")

    def closedata(self):
        self.hide()
    
    def center_window(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        x = screen_geometry.width() // 2 - window_geometry.width() // 2
        y = screen_geometry.height() // 2 - window_geometry.height() // 2
        self.move(x, y)
    
    def enableText(self):
        self.bsite_input.setEnabled(True)
        self.remarks_input.setEnabled(True)        
        self.user_list.setEnabled(False)

    def disableText(self):
        self.bsite_input.setEnabled(False)
        self.remarks_input.setEnabled(False)
        self.user_list.setEnabled(True)
 
class CpassWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - Change Password")
        self.resize(400, 200)
        self.setWindowIcon(QIcon("images/erai.png"))
        
        layout = QVBoxLayout()
        # Create vertical frame
        vertical_frame = QFrame()
        vertical_frame.setFrameShape(QFrame.StyledPanel)
        vertical_layout = QVBoxLayout()

        # Add details to vertical frame
        self.oldpassword_label = QLabel('Old PAssword')
        self.oldpassword_input = QLineEdit()
        self.newpassword_label = QLabel('New PAssword')
        self.newpassword_input = QLineEdit()

        vertical_layout.addWidget(self.oldpassword_label)
        vertical_layout.addWidget(self.oldpassword_input)
        vertical_layout.addWidget(self.newpassword_label)
        vertical_layout.addWidget(self.newpassword_input)
        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame)
         # Create horizontal frame
        horizontal_frame = QFrame()
        horizontal_frame.setFrameShape(QFrame.StyledPanel)
        horizontal_layout = QHBoxLayout()

        self.save_button = QPushButton('Save')  
        self.close_button = QPushButton("Close")
        self.save_button.clicked.connect(self.savedata)
        self.close_button.clicked.connect(self.closedata)

        horizontal_layout.addWidget(self.save_button)
        horizontal_layout.addWidget(self.close_button)
        horizontal_frame.setLayout(horizontal_layout)
        layout.addWidget(horizontal_frame)

        self.setLayout(layout)
        self.center_window()

    def savedata(self):
        global gusername
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s and password=%s ", (gusername,self.oldpassword_input.text()))  
        store_data = cursor.fetchall()
        print(len(store_data))
    
        if len(store_data) == 0 :
            dlg = QMessageBox(self)
            dlg.setWindowTitle("eRadcareAI")
            dlg.setText("Old password incorrect.")
            button = dlg.exec()
        else :
            cursor.execute("UPDATE users  SET password=%s where username = %s " ,(gusername,self.newpassword_input.text())) 
            dlg = QMessageBox(self)
            dlg.setWindowTitle("eRadcareAI")
            dlg.setText("          New Password changed     ")
            button = dlg.exec() 
            cursor.close()
            self.hide()
    
    def closedata(self):
        self.hide()

    def center_window(self):
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            window_geometry = self.frameGeometry()
            x = screen_geometry.width() // 2 - window_geometry.width() // 2
            y = screen_geometry.height() // 2 - window_geometry.height() // 2
            self.move(x, y)



class HospitalRegWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("eRadcareAI - Hospital Registration")
        self.resize(400, 300)
        
        #Pull Hospital Data
        cursor = conn.cursor()    
        cursor.execute("SELECT * FROM hospitalreg")  
        stored_data = cursor.fetchone()
        cursor.close()

        layout = QVBoxLayout()

        # Create vertical frame
        vertical_frame = QFrame()
        vertical_frame.setFrameShape(QFrame.StyledPanel)
        vertical_layout = QVBoxLayout()

        # Add details to vertical frame
        self.hospital_label = QLabel('Hospital Name')
        self.add_label = QLabel('Address')
        self.hospital_input = QLineEdit(stored_data[1])
        self.add_input = QPlainTextEdit(stored_data[2])        
        self.add_input.setPlaceholderText("Enter your address")   
        self.lic_label = QLabel('Number of Lic.')
        self.lic_input = QLineEdit(str(stored_data[5]))            
       
        vertical_layout.addWidget(self.hospital_label)
        vertical_layout.addWidget(self.hospital_input)
        vertical_layout.addWidget(self.add_label)
        vertical_layout.addWidget(self.add_input)
        vertical_layout.addWidget(self.lic_label )
        vertical_layout.addWidget(self.lic_input)
        self.setWindowIcon(QIcon("images/erai.png"))
        
        vertical_frame.setLayout(vertical_layout)
        layout.addWidget(vertical_frame)

        # Create horizontal frame
        horizontal_frame = QFrame()
        horizontal_frame.setFrameShape(QFrame.StyledPanel)
        horizontal_layout = QHBoxLayout()

        self.login_button = QPushButton('Save')  
        self.close_button = QPushButton("Close")
        self.login_button.clicked.connect(self.savedata)
        self.close_button.clicked.connect(self.closedata)

        horizontal_layout.addWidget(self.login_button)
        horizontal_layout.addWidget(self.close_button)
        horizontal_frame.setLayout(horizontal_layout)
        layout.addWidget(horizontal_frame)

        self.setLayout(layout)
        self.center_window()

    def savedata(self):
        cursor = conn.cursor()  
        cursor.execute("UPDATE hospitalreg  SET hospital_name=%s, address=%s,  lic=%s" ,(self.hospital_input.text(),self.add_input.toPlainText(),self.lic_input.text()))  
        cursor.close()
        self.hide()
    
    def closedata(self):
        self.hide()

    def center_window(self):
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            window_geometry = self.frameGeometry()
            x = screen_geometry.width() // 2 - window_geometry.width() // 2
            y = screen_geometry.height() // 2 - window_geometry.height() // 2
            self.move(x, y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('eRadcareAI')
        self.resize(1200, 700)

        label = QLabel('eRadcareAI!', alignment=Qt.AlignCenter)
        label.setFont(QFont('Arial', 20))
        #slabel = QLabel('Personalized Radiotherapy Contouring' )
        #slabel.setFont(QFont('Arial', 14))        
        self.setWindowFlags(Qt.WindowCloseButtonHint )

        layout = QVBoxLayout()
        layout.addWidget(label)
        #layout.addWidget(slabel)
        self.setWindowIcon(QIcon("images/erai.png"))
        
        

        toolbar = QToolBar("maintoolbar")
        toolbar.setIconSize(QSize(25,25))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("images/hospital.png"), "", self)
        cpass_action = QAction(QIcon("images/cpass.png"), "", self)
        euser_action = QAction(QIcon("images/user.png"), "", self)
        bsite_action = QAction(QIcon("images/bsite.png"),"",self)
        siteOAR_action =QAction(QIcon("images/siteOAR.png"),"",self)
        training_action = QAction(QIcon("images/training.png"),"",self)
        button_action.setStatusTip("Hospital Registration")
        cpass_action.setStatusTip("Change your password")
        euser_action.setStatusTip("User Details")
        bsite_action.setStatusTip("Body Site")
        siteOAR_action.setStatusTip("Site and OARs adding")
        training_action.setStatusTip("Training the Organ at Risks (OARS)")
        button_action.triggered.connect(self.open_child_window)
        cpass_action.triggered.connect(self.open_childwindow_cpass)
        euser_action.triggered.connect(self.open_childwindow_user)
        bsite_action.triggered.connect(self.open_childwindow_bsite)
        siteOAR_action.triggered.connect(self.open_childwindow_siteOAR)
        training_action.triggered.connect(self.open_childwindow_training)

        button_action.setCheckable(True)
        toolbar.addAction(button_action)
        toolbar.addAction(cpass_action)
        toolbar.addAction(euser_action)
        toolbar.addSeparator()
        toolbar.addAction(bsite_action)
        toolbar.addAction(siteOAR_action)        
        toolbar.addSeparator()
        toolbar.addAction(training_action)

        self.setStatusBar(QStatusBar(self))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.center_window()
         

    def open_child_window(self):
        self.child_window = HospitalRegWindow(self)
        self.child_window.exec()

    def open_childwindow_cpass(self):
        self.child_window = CpassWindow(self)
        self.child_window.exec()

    def open_childwindow_user(self):
        self.child_window = userWindow(self)
        self.child_window.exec()
    
    def open_childwindow_bsite(self):
        self.child_window = bSiteWindow(self)
        self.child_window.exec()

    def open_childwindow_training(self):
        self.child_window = trainingWindow(self)
        self.child_window.exec()
    
    def open_childwindow_siteOAR(self):
        self.child_window = siteOARWindow(self)
        self.child_window.exec()


    def center_window(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        x = screen_geometry.width() // 2 - window_geometry.width() // 2
        y = screen_geometry.height() // 2 - window_geometry.height() // 2
        self.move(x, y)

    def closeEvent(self, event):
            print ("User has clicked the red x on the main window")
            conn.close()
            event.accept()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Login')       

        # Create a colored frame with the label "eRadcareAI"
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background-color: blue; color: white;")

        layout_frame = QVBoxLayout()
        layout_frame.addWidget(QLabel('eRadcareAI', alignment=Qt.AlignCenter))
        frame.setLayout(layout_frame)

        self.username_label = QLabel('Username:')
        self.password_label = QLabel('Password:')
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        self.login_button = QPushButton('Login')
        self.cr_lable = QLabel("© KRSIP 2023",alignment=Qt.AlignCenter)        
        self.login_button.clicked.connect(self.login)
        self.setWindowIcon(QIcon("images/erai.png"))



        layout_main = QVBoxLayout()
        layout_main.addWidget(frame)
        layout_main.addWidget(self.username_label)
        layout_main.addWidget(self.username_input)
        layout_main.addWidget(self.password_label)
        layout_main.addWidget(self.password_input)
        layout_main.addWidget(self.login_button)
        layout_main.addWidget(self.cr_lable)

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
        self.center_window()  # Center the window on the screen

        # ... (rest of the implementation remains the same) ...

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QScreen().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def login(self):
        global gusername
        username = self.username_input.text()
        password = self.password_input.text()

        if check_credentials(username, password):
            print('Login successful!')
            gusername = username
            self.hide()  # Hide the login window
            self.main_window = MainWindow()
            self.main_window.show()  # Show the main application window
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("eRadcareAI")
            dlg.setText("Login failed. Please check your username and password.")
            button = dlg.exec()



def main():
    

    app = QApplication([])
    login_window = LoginWindow()
    login_window.setWindowFlags(Qt.WindowCloseButtonHint )

    qdarktheme.setup_theme("dark")
    qdarktheme.setup_theme(corner_shape="sharp")
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

#nuitka   as.py --enable-plugin=tk-inter --noinclude-numba-mode=nofollow --windows-icon-from-ico=erai.ico --windows-disable-console
#nuitka3 --standalone --plugin-enable=pyside6 examples/installer_test/hello.py