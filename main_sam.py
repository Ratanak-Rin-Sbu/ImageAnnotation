import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QLabel, QPushButton, QToolButton, \
    QFileDialog, QMessageBox, QMenu, QDesktopWidget, QGroupBox, QFormLayout, QLineEdit, QComboBox, \
    QDialogButtonBox, QVBoxLayout, QDialog, QListWidget
from PyQt5.QtGui import QImage, QBrush, QIcon, QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt,QRect,QPoint

import cv2

class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.title = 'Image Annotation Tool for AI'
        self.width = 1200
        self.height = 820

        self.draw_rect = False

        self.draw_frame = QLabel(self)
        self.label = QLabel(self)
        self.label_tmp=QLabel(self)
        
        self.roi_annotation_list = QListWidget(self)

        self.load_img=False

        self.begin, self.destination = QPoint(), QPoint()	

        self.ui_components()

    def ui_components(self):
        self.resize(self.width, self.height)
        self.center()
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(r'pic\icon\icon_win.png'))
        self.menu_bar()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def menu_bar(self):
        self.rectangle = QPushButton('Rectangle', self)
        self.rectangle.move(10, 23)
        self.rectangle.resize(105, 55)
        self.rectangle.clicked.connect(self.draw_rectangle)
        
        self.load = QPushButton('Load Image', self)
        self.load.move(125, 23)
        self.load.resize(130, 55)
        self.load.clicked.connect(self.browse_image)

        self.save = QPushButton('Save Annotation', self)
        self.save.move(265, 23)
        self.save.resize(170, 55)
        self.save.clicked.connect(self.save_annotation)
        
        self.delete = QPushButton('delete Annotation', self)
        self.delete.move(445, 23)
        self.delete.resize(170, 55)
        self.delete.setEnabled(False)
        self.delete.clicked.connect(self.delete_annotation)
        
        self.roi_annotation_list.move(821,110)
        self.roi_annotation_list.resize(369,700)
        self.roi_annotation_list.itemSelectionChanged.connect(self.roi_itemSelectionChange)
        
    def roi_itemSelectionChange(self):        
        item = self.roi_annotation_list.currentItem()
        if(item == None):
            self.delete.setEnabled(False)
        else:
            self.delete.setEnabled(True)

    def delete_annotation(self):
        rn = self.roi_annotation_list.currentRow()
        
        draw_pixmap = QPixmap(self.label.size())
        draw_pixmap.fill(Qt.transparent)
        self.draw_frame.setPixmap(draw_pixmap)
        self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())
        
        painter = QPainter(self.draw_frame.pixmap())
        painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        
        del(self.annotation_content[self.roi_annotation_list.item(rn).text()])
        for annotation_c in self.annotation_content:
            
            rect = QRect(round(self.annotation_content[annotation_c]['x0']*self.img_scale),round(self.annotation_content[annotation_c]['y0']*self.img_scale),
                          round((self.annotation_content[annotation_c]['x1']-self.annotation_content[annotation_c]['x0'])*self.img_scale),
                          round((self.annotation_content[annotation_c]['y1']-self.annotation_content[annotation_c]['y0'])*self.img_scale))
            painter.drawRect(rect.normalized())
            
        self.roi_annotation_list.takeItem(rn)
        
        
    def browse_image(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, 'Open File', r'C:\Users\USER\OneDrive - Stony Brook University\Documents\Summer_2022_Caimi_Internship\Projects\Image_Editor\test', 'Image Files (*.png *.jpg *.jpeg)')
        if self.filename:
            self.load_original_image()

    def save_annotation(self):
        f=open(self.filename.replace(".jpg",".txt").replace(".jpeg",".txt").replace(".png",".txt"),"w")
        for ann in self.annotation_content:
            f.write(str(self.annotation_content[ann]['x0'])+","+str(self.annotation_content[ann]['y0'])+","+
                    str(self.annotation_content[ann]['x1'])+","+str(self.annotation_content[ann]['y1'])+"\n")
        f.close()

    def draw_rectangle(self):
        draw_pixmap = QPixmap(self.label.size())
        draw_pixmap.fill(Qt.transparent)
        self.draw_frame.setPixmap(draw_pixmap)
        self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())
        self.draw_rect = True

    def load_original_image(self):
        self.image = cv2.imread(self.filename, 1)
        self.print_image(self.filename)
        self.annotation_content={}
        self.roi_number = 1

    def print_image(self, filename):
        pix = QPixmap()
        pix.load(filename)
        raw_img_w=pix.size().width()
        pix = pix.scaledToWidth(800)
        re_img_w=pix.size().width()
        self.img_scale=re_img_w/raw_img_w
        
        self.label.setPixmap(pix)        
        self.label.setGeometry(11, 110, pix.size().width(), pix.size().height())
        self.label.lower()
        self.load_img = True

    def paintEvent(self, event):
        if self.load_img and self.draw_rect:
            pix_tmp = QPixmap(self.label.size())
            pix_tmp.fill(Qt.transparent)
            self.label_tmp.setPixmap(pix_tmp)
            self.label_tmp.setGeometry(11, 110, pix_tmp.size().width(), pix_tmp.size().height())
            painter = QPainter(self.label_tmp.pixmap())
            painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
            if not self.begin.isNull() and not self.destination.isNull():
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())

    def mousePressEvent(self, event):
        if self.load_img and self.draw_rect:
            if event.buttons() & Qt.LeftButton:
                self.begin = event.pos()
                self.begin -= QPoint(11, 110)
                self.destination = self.begin
                self.update()

    def mouseMoveEvent(self, event):
        if self.load_img and self.draw_rect:
            if event.buttons() & Qt.LeftButton:		
                self.destination = event.pos()
                self.destination -= QPoint(11, 110)
                self.update()

    def mouseReleaseEvent(self, event):
        if self.load_img and self.draw_rect:
            if event.button() & Qt.LeftButton:
                rect = QRect(self.begin, self.destination)
                
                x0=min([self.begin.x(),self.destination.x()])
                x1=max([self.begin.x(),self.destination.x()])
                y0=min([self.begin.y(),self.destination.y()])
                y1=max([self.begin.y(),self.destination.y()])

                self.annotation_content["Label_%d"%self.roi_number]={'x0':round(x0/self.img_scale),'y0':round(y0/self.img_scale),
                                                                     'x1':round(x1/self.img_scale),'y1':round(y1/self.img_scale)}
                
                painter = QPainter(self.draw_frame.pixmap())
                painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
                painter.drawRect(rect.normalized())
                
                self.roi_annotation_list.addItem("Label_%d"%self.roi_number)
                self.roi_number += 1
                
                self.begin, self.destination = QPoint(), QPoint()
                self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())