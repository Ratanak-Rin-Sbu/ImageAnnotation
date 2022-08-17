import sys
import os.path
from os import path
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QLabel, QPushButton, QListWidget, QListWidgetItem, \
    QFileDialog, QMessageBox, QMenu, QDesktopWidget, QGroupBox, QFormLayout, QLineEdit, QComboBox, \
    QDialogButtonBox, QVBoxLayout, QDialog
from PyQt5.QtGui import QImage, QBrush, QIcon, QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QRect, QPoint

import cv2



class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.count = 1;
        self.title = 'Image Annotation Tool for AI'
        self.win_x = 350
        self.win_y = 80
        self.width = 1200
        self.height = 820
        self.zoom = 1
        self.x_pos = 0
        self.y_pos = 0
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.pixel = 3
        self.font_scale = 1
        self.select_color_x = 675
        self.select_color_y = 32
        self.color = (0, 0, 0)
        self.draw_rect = False
        self.content_list = []

        self.ui_components()

        self.draw_frame = QLabel(self)
        self.label = QLabel(self)
        self.label_tmp = QLabel(self)


    def ui_components(self):
        self.resize(self.width, self.height)
        self.center()
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(r'pic\icon\icon_win.png'))
        self.menu_bar()
        self.tools_bar()
        self.disable_action()
        self.backup_image()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def menu_bar(self):
        self.label_list = QListWidget(self)
        self.label_list.setGeometry(QtCore.QRect(670, 110, 500, 700))
        self.label_list.setStyleSheet("QListWidget::item { border: 0px solid red }")
        self.label_list.setObjectName("label_list")
        self.label_list.setStyleSheet("font-size: 40px")

        self.load = QPushButton('Load Image', self)
        self.load.move(125, 23)
        self.load.resize(130, 55)
        self.load.clicked.connect(self.browse_image)

        self.save = QPushButton('Save Annotation', self)
        self.save.move(265, 23)
        self.save.resize(150, 55)
        self.save.clicked.connect(self.save_image)

        self.save = QPushButton('Delete Rectangle', self)
        self.save.move(435, 23)
        self.save.resize(150, 55)
        self.save.clicked.connect(self.delete_rectangle)

    def tools_bar(self):
        self.rectangle = QPushButton('Rectangle', self)
        self.rectangle.move(10, 23)
        self.rectangle.resize(105, 55)
        self.rectangle.clicked.connect(self.draw_rectangle)

    # ********************   menu bar operations   ********************************************************************
    def browse_image(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '.', 'Image Files (*.png *.jpg *.jpeg)')
        if path.exists(self.filename.split("/")[-1].split(".")[0] + ".txt"):
            print(self.filename.split("/")[-1].split(".")[0] + ".txt")
            self.textfile = open(self.filename.split("/")[-1].split(".")[0] + ".txt", "r")
            self.file_content = self.textfile.read()
            self.content_list = self.file_content.split("\n")
            self.textfile.close()
            # print(self.content_list)
            for item in self.content_list:
                self.item = QListWidgetItem(item)
                self.label_list.addItem(self.item)
        else:
            self.label_list.clear()

        if self.filename:
            self.load_original_image()
        self.converted = False

    def save_image(self):
        
        #######################################################################################
        #######   Modify  #####################################################################
        #######################################################################################
        self.image = self.backup_img
        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "",
                                                        "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if self.filePath:
            cv2.imwrite(self.filePath, self.image)
            
        f=open(self.filePath.split("/")[-1].split(".")[0]+".txt","w")
        for ann in self.annotation_content:
            f.write(ann)
        f.close()
        
        #######################################################################################

    # ********************   tool bar operations   ********************************************************************
    def draw_rectangle(self):
        self.draw_rect = True
        QLabel.setCursor(self, Qt.CrossCursor)

        item = "Label" + str(self.count)
        self.count = self.count + 1
        self.label_list.addItem(item)

    def load_original_image(self):
        self.image = cv2.imread(self.filename, 1)
        self.print_image(self.image)
        
        #######################################################################################
        #######   Modify  #####################################################################
        #######################################################################################
        
        self.annotation_content=""
        
        #######################################################################################
        
        cv2.imwrite('backup_img.jpg', self.image)
        self.backup_image()

    # ********************   print image   ****************************************************************************
    def print_image(self, image):
        self.enable_action()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        self.qformat = QImage.Format_ARGB32
        self.img = QImage(image.data, int(image.shape[1]), int(image.shape[0]), int(self.qformat))
        self.label.setPixmap((QPixmap.scaled(QPixmap.fromImage(self.img), int(image.shape[1] * self.zoom),
                                             int(image.shape[0] * self.zoom), Qt.KeepAspectRatio,
                                             Qt.SmoothTransformation)))
        self.label.setGeometry(11, 110, int(image.shape[1] * self.zoom), int(image.shape[0] * self.zoom))

    def delete_rectangle(self):
        rn = self.roi_annotation_list.currentRow()

        draw_pixmap = QPixmap(self.label.size())
        draw_pixmap.fill(Qt.transparent)
        self.draw_frame.setPixmap(draw_pixmap)
        self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())

        painter = QPainter(self.draw_frame.pixmap())
        painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))

        del (self.annotation_content[self.roi_annotation_list.item(rn).text()])
        for annotation_c in self.annotation_content:
            rect = QRect(round(self.annotation_content[annotation_c]['x0'] * self.img_scale),
                         round(self.annotation_content[annotation_c]['y0'] * self.img_scale),
                         round((self.annotation_content[annotation_c]['x1'] - self.annotation_content[annotation_c][
                             'x0']) * self.img_scale),
                         round((self.annotation_content[annotation_c]['y1'] - self.annotation_content[annotation_c][
                             'y0']) * self.img_scale))
            painter.drawRect(rect.normalized())

        self.roi_annotation_list.takeItem(rn)

    # ********************   mouse control   *************************************************************************
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.draw_rect:
                self.flag = True
                self.x0 = event.x()
                self.y0 = event.y()
            elif 679 < event.x() < 699 and 36 < event.y() < 56:
                self.color = (0, 0, 0)
                self.select_color_x = 675
                self.select_color_y = 32
                self.update()
            elif 708 < event.x() < 728 and 36 < event.y() < 56:
                self.color = (128, 128, 128)
                self.select_color_x = 704
                self.select_color_y = 32
                self.update()
            elif 737 < event.x() < 757 and 36 < event.y() < 56:
                self.color = (0, 0, 128)
                self.select_color_x = 733
                self.select_color_y = 32
                self.update()
            elif 766 < event.x() < 786 and 36 < event.y() < 56:
                self.color = (0, 128, 128)
                self.select_color_x = 762
                self.select_color_y = 32
                self.update()
            elif 795 < event.x() < 815 and 36 < event.y() < 56:
                self.color = (0, 128, 0)
                self.select_color_x = 791
                self.select_color_y = 32
                self.update()
            elif 824 < event.x() < 844 and 36 < event.y() < 56:
                self.color = (128, 128, 0)
                self.select_color_x = 820
                self.select_color_y = 32
                self.update()
            elif 853 < event.x() < 873 and 36 < event.y() < 56:
                self.color = (128, 0, 0)
                self.select_color_x = 849
                self.select_color_y = 32
                self.update()
            elif 882 < event.x() < 902 and 36 < event.y() < 56:
                self.color = (128, 0, 128)
                self.select_color_x = 878
                self.select_color_y = 32
                self.update()

            elif 679 < event.x() < 699 and 64 < event.y() < 84:
                self.color = (255, 255, 255)
                self.select_color_x = 675
                self.select_color_y = 60
                self.update()
            elif 708 < event.x() < 728 and 64 < event.y() < 84:
                self.color = (192, 192, 192)
                self.select_color_x = 704
                self.select_color_y = 60
                self.update()
            elif 737 < event.x() < 757 and 64 < event.y() < 84:
                self.color = (0, 0, 255)
                self.select_color_x = 733
                self.select_color_y = 60
                self.update()
            elif 766 < event.x() < 786 and 64 < event.y() < 84:
                self.color = (0, 255, 255)
                self.select_color_x = 762
                self.select_color_y = 60
                self.update()
            elif 795 < event.x() < 815 and 64 < event.y() < 84:
                self.color = (0, 255, 0)
                self.select_color_x = 791
                self.select_color_y = 60
                self.update()
            elif 824 < event.x() < 844 and 64 < event.y() < 84:
                self.color = (255, 255, 0)
                self.select_color_x = 820
                self.select_color_y = 60
                self.update()
            elif 853 < event.x() < 873 and 64 < event.y() < 84:
                self.color = (255, 0, 0)
                self.select_color_x = 849
                self.select_color_y = 60
                self.update()
            elif 882 < event.x() < 902 and 64 < event.y() < 84:
                self.color = (255, 0, 255)
                self.select_color_x = 878
                self.select_color_y = 60
                self.update()

        elif event.buttons() == Qt.RightButton:
            if self.draw_rect:
                self.draw_rect = False
                QLabel.setCursor(self, Qt.CustomCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.flag:
                self.x1 = event.x()
                self.y1 = event.y()
                self.update()
                instant_img = cv2.imread('backup_img.jpg')
                if self.draw_rect:
                    cv2.rectangle(instant_img, (self.x0 - 11, self.y0 - 110),
                                  (self.x1 - 11, self.y1 - 110), self.color, self.pixel)
                self.print_image(instant_img)

    def mouseReleaseEvent(self, event):
        if self.draw_rect:
            self.flag = False
            cv2.rectangle(self.backup_img, (self.x0 - 11, self.y0 - 110), (self.x1 - 11, self.y1 - 110),
                          self.color, self.pixel)
            cv2.rectangle(self.image, (self.x0 - 11, self.y0 - 110), (self.x1 - 11, self.y1 - 110),
                          self.color, self.pixel)
            if self.converted:
                self.print_image(self.backup_img)
                cv2.imwrite('backup_img.jpg', self.backup_img)
            else:
                self.print_image(self.image)
                cv2.imwrite('backup_img.jpg', self.image)
            self.draw_rect = False
            QLabel.setCursor(self, Qt.CustomCursor)

            #######################################################################################
            #######   Modify  #####################################################################
            #######################################################################################
            
            self.annotation_content = self.annotation_content+str(self.x0 - 11)+","+str(self.y0 - 110)+","+str(self.x1 - 11)+","+str(self.y1 - 110)+"\n"
            
            #######################################################################################
            # print(self.x0 + "," + self.y0)

    # ********************   press enter actions   ********************************************************************
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.crop:
                if self.converted:
                    self.backup_img = self.backup_img[self.y0 - 110:self.y1 - 110,
                                      self.x0 - 11:self.x1 - 11]
                    self.image = self.image[self.y0 - 110:self.y1 - 110,
                                 self.x0 - 11:self.x1 - 11]
                    self.reset_crop_label()
                    self.print_image(self.backup_img)
                    cv2.imwrite('backup_img.jpg', self.backup_img)
                if not self.converted:
                    self.image = self.image[self.y0 - 110:self.y1 - 110,
                                 self.x0 - 11:self.x1 - 11]
                    self.reset_crop_label()
                    self.print_image(self.image)
                    cv2.imwrite('backup_img.jpg', self.image)
                self.crop = False
                self.cursor_shape()

    # ********************   set cursor   *****************************************************************************
    def cursor_shape(self):
        if self.crop:
            QLabel.setCursor(self, Qt.CrossCursor)
        else:
            QLabel.setCursor(self, Qt.CustomCursor)

    # *****************************************************************************************************************
    def backup_image(self):
        self.backup_img = cv2.imread('backup_img.jpg', 1)

    # *****************************************************************************************************************
    def paintEvent(self, event):
        tool_bar_rect = QPainter(self)
        tool_bar_rect.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        tool_bar_rect.drawRect(-1, 0, 1201, 97)

        # label_rect = QPainter(self)
        # pen = QPen(Qt.black, 3, Qt.SolidLine)
        # label_rect.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        # label_rect.setPen(pen)
        # label_rect.drawRect(600, 110, 550, 650)

        black_rect = QPainter(self)
        black_rect.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        black_rect.drawRect(679, 28, 20, 20)
        dark_gray_rect = QPainter(self)
        dark_gray_rect.setBrush(QBrush(Qt.darkGray, Qt.SolidPattern))
        dark_gray_rect.drawRect(708, 28, 20, 20)
        dark_red_rect = QPainter(self)
        dark_red_rect.setBrush(QBrush(Qt.darkRed, Qt.SolidPattern))
        dark_red_rect.drawRect(737, 28, 21, 21)
        dark_yellow_rect = QPainter(self)
        dark_yellow_rect.setBrush(QBrush(Qt.darkYellow, Qt.SolidPattern))
        dark_yellow_rect.drawRect(766, 28, 21, 21)
        dark_green_rect = QPainter(self)
        dark_green_rect.setBrush(QBrush(Qt.darkGreen, Qt.SolidPattern))
        dark_green_rect.drawRect(795, 28, 21, 21)
        dark_cyan_rect = QPainter(self)
        dark_cyan_rect.setBrush(QBrush(Qt.darkCyan, Qt.SolidPattern))
        dark_cyan_rect.drawRect(824, 28, 21, 21)
        dark_blue_rect = QPainter(self)
        dark_blue_rect.setBrush(QBrush(Qt.darkBlue, Qt.SolidPattern))
        dark_blue_rect.drawRect(853, 28, 21, 21)
        dark_magenta_rect = QPainter(self)
        dark_magenta_rect.setBrush(QBrush(Qt.darkMagenta, Qt.SolidPattern))
        dark_magenta_rect.drawRect(882, 28, 21, 21)

        white_rect = QPainter(self)
        white_rect.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        white_rect.drawRect(679, 56, 20, 20)
        light_gray_rect = QPainter(self)
        light_gray_rect.setBrush(QBrush(Qt.lightGray, Qt.SolidPattern))
        light_gray_rect.drawRect(708, 56, 20, 20)
        red_rect = QPainter(self)
        red_rect.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        red_rect.drawRect(737, 56, 21, 21)
        yellow_rect = QPainter(self)
        yellow_rect.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
        yellow_rect.drawRect(766, 56, 21, 21)
        green_rect = QPainter(self)
        green_rect.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        green_rect.drawRect(795, 56, 21, 21)
        cyan_rect = QPainter(self)
        cyan_rect.setBrush(QBrush(Qt.cyan, Qt.SolidPattern))
        cyan_rect.drawRect(824, 56, 21, 21)
        blue_rect = QPainter(self)
        blue_rect.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
        blue_rect.drawRect(853, 56, 21, 21)
        magenta_rect = QPainter(self)
        magenta_rect.setBrush(QBrush(Qt.magenta, Qt.SolidPattern))
        magenta_rect.drawRect(882, 56, 21, 21)

        select_rect = QPainter(self)
        select_rect.drawRect(self.select_color_x, self.select_color_y-8, 28, 28)

    def disable_action(self):
        self.disabled_list = []
        for i in range(len(self.disabled_list)):
            self.disabled_list[i].setDisabled(True)

    def enable_action(self):
        for i in range(len(self.disabled_list)):
            self.disabled_list[i].setDisabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())