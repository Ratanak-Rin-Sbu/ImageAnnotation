import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QLabel, QPushButton, QToolButton, \
    QFileDialog, QDesktopWidget, QListWidget
from PyQt5.QtGui import QBrush, QIcon, QPixmap, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QRect, QPoint
import os, os.path
import cv2

class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.title = 'Image Annotation Tool for AI'
        self.width = 1220
        self.height = 820

        self.draw_rect = False

        self.draw_frame = QLabel(self)
        self.label = QLabel(self)
        self.label_tmp=QLabel(self)
        
        self.roi_annotation_list = QListWidget(self)

        self.load_img=False

        self.begin, self.destination = QPoint(), QPoint()	

        self.ui_components()

        self.fileList = []
        self.text_list = []

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
        self.rectangle.setDisabled(True)
        self.rectangle.clicked.connect(self.draw_rectangle)
        
        self.load = QPushButton('Load Image', self)
        self.load.move(125, 23)
        self.load.resize(130, 55)
        self.load.clicked.connect(self.browse_image)

        self.save = QPushButton('Save Annotation', self)
        self.save.move(265, 23)
        self.save.resize(170, 55)
        self.save.setDisabled(True)
        self.save.clicked.connect(self.save_annotation)
        
        self.delete = QPushButton('delete Annotation', self)
        self.delete.move(445, 23)
        self.delete.resize(170, 55)
        self.delete.setEnabled(False)
        self.delete.clicked.connect(self.delete_annotation)

        self.next = QPushButton('Next', self)
        self.next.move(685, 450)
        self.next.setVisible(False)
        self.next.clicked.connect(self.next_image)

        self.prev = QPushButton('Previous', self)
        self.prev.move(20, 450)
        self.prev.setVisible(False)
        self.prev.clicked.connect(self.prev_image)

        self.roi_annotation_list.move(850, 110)
        self.roi_annotation_list.resize(350, 650)
        self.roi_annotation_list.itemSelectionChanged.connect(self.roi_itemSelectionChange)
        
    def roi_itemSelectionChange(self):        
        item = self.roi_annotation_list.currentItem()
        if(item == None):
            self.delete.setEnabled(False)
        else:
            self.delete.setEnabled(True)

    def delete_annotation(self):
        rn = self.roi_annotation_list.currentRow()

        counter = 0
        
        draw_pixmap = QPixmap(self.label.size())
        draw_pixmap.fill(Qt.transparent)
        self.draw_frame.setPixmap(draw_pixmap)
        self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())

        painter = QPainter(self.draw_frame.pixmap())

        del(self.annotation_content[self.roi_annotation_list.item(rn).text()])

        self.roi_annotation_list.takeItem(rn)

        for annotation_c in self.annotation_content:
            painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
            rect = QRect(round(int(self.annotation_content[annotation_c]['x0'])*self.img_scale),
                         round(int(self.annotation_content[annotation_c]['y0'])*self.img_scale),
                         round((int(self.annotation_content[annotation_c]['x1'])-int(self.annotation_content[annotation_c]['x0']))*self.img_scale),
                         round((int(self.annotation_content[annotation_c]['y1'])-int(self.annotation_content[annotation_c]['y0']))*self.img_scale))
            painter.drawRect(rect.normalized())

            rect2 = QRect(round(int(self.annotation_content[annotation_c]['x0'])*self.img_scale),
                          round(int(self.annotation_content[annotation_c]['y0'])*self.img_scale)-15,
                          round(int(self.annotation_content[annotation_c]['x1'])*self.img_scale)-round(
                              int(self.annotation_content[annotation_c]['x0'])*self.img_scale)+1, 15)
            painter.fillRect(round(int(self.annotation_content[annotation_c]['x0'])*self.img_scale)-1,
                             round(int(self.annotation_content[annotation_c]['y0'])*self.img_scale)-16,
                             round(int(self.annotation_content[annotation_c]['x1'])*self.img_scale)-round(
                                 int(self.annotation_content[annotation_c]['x0'])*self.img_scale)+3, 15, Qt.green)

            painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
            painter.drawText(rect2.normalized(), Qt.AlignLeft, self.roi_annotation_list.item(counter).text())
            counter += 1
        
        
    def browse_image(self):
        self.text_list.clear()
        self.fileList.clear()
        self.filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Image Files (*.png *.jpg *.jpeg)')
        if self.filename:
            for file in os.listdir(os.path.split(self.filename)[0]):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    self.fileList.append(file)
                else:
                    self.text_list.append(file) if file not in self.text_list else self.text_list
            self.load_original_image(self.filename)

    def save_annotation(self):
        f=open(self.filename.replace(".jpg",".txt").replace(".jpeg",".txt").replace(".png",".txt"),"w")
        for ann in self.annotation_content:
            f.write(str(self.annotation_content[ann]['x0'])+","+str(self.annotation_content[ann]['y0'])+","+
                    str(self.annotation_content[ann]['x1'])+","+str(self.annotation_content[ann]['y1'])+"\n")

        self.text_list.append(f.name.split("/")[-1]) if f.name.split("/")[-1] not in self.text_list else self.text_list
        f.close()

    def draw_rectangle(self):
        QLabel.setCursor(self, Qt.CrossCursor)
        draw_pixmap = QPixmap(self.label.size())
        draw_pixmap.fill(Qt.transparent)
        self.draw_frame.setPixmap(draw_pixmap)
        self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())
        self.draw_rect = True

        painter = QPainter(self.draw_frame.pixmap())
        counter = 0
        for annotation_c in self.annotation_content:
            painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
            rect = QRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale),
                         round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale),
                         round((int(self.annotation_content[annotation_c]['x1']) - int(
                             self.annotation_content[annotation_c][
                                 'x0'])) * self.img_scale),
                         round((int(self.annotation_content[annotation_c]['y1']) - int(
                             self.annotation_content[annotation_c][
                                 'y0'])) * self.img_scale))
            painter.drawRect(rect.normalized())

            rect2 = QRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale),
                          round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale) - 15,
                          round(int(self.annotation_content[annotation_c]['x1']) * self.img_scale) - round(
                              int(self.annotation_content[annotation_c]['x0']) * self.img_scale) + 1, 15)
            painter.fillRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale) - 1,
                             round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale) - 16,
                             round(int(self.annotation_content[annotation_c]['x1']) * self.img_scale) - round(
                                 int(self.annotation_content[annotation_c]['x0']) * self.img_scale) + 3, 15, Qt.green)

            painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
            painter.drawText(rect2.normalized(), Qt.AlignLeft, self.roi_annotation_list.item(counter).text())
            counter += 1

    def load_original_image(self, x):
        self.next.setVisible(True)
        self.prev.setVisible(True)
        self.rectangle.setDisabled(False)
        self.save.setDisabled(False)

        self.roi_annotation_list.clear()
        self.annotation_content = {}
        name = os.path.split(x)[-1].split(".")[0]
        text = name + ".txt"
        path = x.replace(x.split("/")[-1], "")

        if (text in self.text_list):
            self.image = cv2.imread(x, 1)
            self.print_image(x)
            full_path = path + text
            file1 = open(full_path, 'r')
            lines = file1.readlines()
            self.roi_number = 0

            counter = 0

            draw_pixmap = QPixmap(self.label.size())
            draw_pixmap.fill(Qt.transparent)
            self.draw_frame.setPixmap(draw_pixmap)
            self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())

            painter = QPainter(self.draw_frame.pixmap())

            for line in lines:
                self.annotation_content["Label_%d" % self.roi_number] = {'x0': line.split(",")[0],
                                                                     'y0': line.split(",")[1],
                                                                     'x1': line.split(",")[2],
                                                                     'y1': line.strip().split(",")[3]}
                self.roi_annotation_list.addItem("Label_%d" % self.roi_number)
                self.roi_number += 1

            for annotation_c in self.annotation_content:
                painter.setPen(QPen(Qt.green, 3, Qt.SolidLine))
                rect = QRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale),
                             round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale),
                             round((int(self.annotation_content[annotation_c]['x1']) - int(self.annotation_content[annotation_c][
                                 'x0'])) * self.img_scale),
                             round((int(self.annotation_content[annotation_c]['y1']) - int(self.annotation_content[annotation_c][
                                 'y0'])) * self.img_scale))
                painter.drawRect(rect.normalized())

                rect2 = QRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale),
                              round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale) - 15,
                              round(int(self.annotation_content[annotation_c]['x1']) * self.img_scale) - round(
                                  int(self.annotation_content[annotation_c]['x0']) * self.img_scale) + 1, 15)
                painter.fillRect(round(int(self.annotation_content[annotation_c]['x0']) * self.img_scale) - 1,
                                 round(int(self.annotation_content[annotation_c]['y0']) * self.img_scale) - 16,
                                 round(int(self.annotation_content[annotation_c]['x1']) * self.img_scale) - round(
                                     int(self.annotation_content[annotation_c]['x0']) * self.img_scale) + 3, 15, Qt.green)

                painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
                painter.drawText(rect2.normalized(), Qt.AlignLeft, self.roi_annotation_list.item(counter).text())
                counter += 1
        else:
            self.roi_annotation_list.clear()
            self.image = cv2.imread(x, 1)
            self.print_image(x)

            draw_pixmap = QPixmap(self.label.size())
            draw_pixmap.fill(Qt.transparent)
            self.draw_frame.setPixmap(draw_pixmap)
            self.draw_frame.setGeometry(11, 110, draw_pixmap.size().width(), draw_pixmap.size().height())

            painter = QPainter(self.draw_frame.pixmap())

            self.roi_number = 0

        if (len(self.fileList) == 1):
            self.next.setDisabled(True)
            self.prev.setDisabled(True)
        else:
            self.next.setDisabled(False)
            self.prev.setDisabled(False)

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

    def next_image(self):
        self.roi_annotation_list.clear()
        currentDir = os.path.split(self.filename)
        currentImage = currentDir[-1]
        currentIndex = self.fileList.index(currentImage)
        if (currentIndex == len(self.fileList)-1):
            self.filename = os.path.join(currentDir[0], self.fileList[0]).replace("\\", "/")
            self.load_original_image(self.filename)
        else:
            self.filename = os.path.join(currentDir[0], self.fileList[currentIndex + 1]).replace("\\", "/")
            self.load_original_image(self.filename)

    def prev_image(self):
        self.roi_annotation_list.clear()
        currentDir = os.path.split(self.filename)
        currentImage = currentDir[-1]
        currentIndex = self.fileList.index(currentImage)
        if (currentIndex == 0):
            self.filename = os.path.join(currentDir[0], self.fileList[len(self.fileList)-1]).replace("\\", "/")
            self.load_original_image(self.filename)
        else:
            self.filename = os.path.join(currentDir[0], self.fileList[currentIndex - 1]).replace("\\", "/")
            self.load_original_image(self.filename)

    def paintEvent(self, event):
        tool_bar_rect = QPainter(self)
        tool_bar_rect.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        tool_bar_rect.drawRect(-1, 0, 1220, 97)

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
                QLabel.setCursor(self, Qt.CustomCursor)

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

                rect = QRect(x0, y0-15, x1-x0+1, 15)
                painter.fillRect(x0-1, y0-16, x1-x0+4, 15, Qt.green)
                painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
                painter.drawText(rect, Qt.AlignLeft, "Label %d"%self.roi_number)
                
                self.roi_annotation_list.addItem("Label_%d"%self.roi_number)
                self.roi_number += 1
                
                self.begin, self.destination = QPoint(), QPoint()
                self.update()

            QLabel.setCursor(self, Qt.CustomCursor)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())