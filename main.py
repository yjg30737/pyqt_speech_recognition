import os, sys
import subprocess

from PyQt5.QtGui import QFont

from loadingLbl import LoadingLabel

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from PyQt5.QtCore import pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QFileDialog, QHBoxLayout, QLabel, QWidget, QAction, \
    QMenu, QLineEdit, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt

from PyQt5.QtCore import QThread

from script import mp3_to_wav, wav_to_text

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))


class Thread(QThread):
    onTextConverted = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__()
        self.__filename = kwargs['filename']

    def run(self):
        try:
            src_filename = self.__filename
            dst_filename = f'{os.path.splitext(os.path.basename(self.__filename))[:-1][0]}.wav'
            mp3_to_wav(src_filename, dst_filename)
            self.onTextConverted.emit(wav_to_text(dst_filename))
            os.remove(dst_filename)
        except Exception as e:
            raise Exception(e)


class FindPathLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setMouseTracking(True)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepareMenu)

    def mouseMoveEvent(self, e):
        self.__showToolTip()
        return super().mouseMoveEvent(e)

    def __showToolTip(self):
        text = self.text()
        text_width = self.fontMetrics().boundingRect(text).width()

        if text_width > self.width():
            self.setToolTip(text)
        else:
            self.setToolTip('')

    def __prepareMenu(self, pos):
        menu = QMenu(self)
        openDirAction = QAction('Open Path')
        openDirAction.setEnabled(self.text().strip() != '')
        openDirAction.triggered.connect(self.__openPath)
        menu.addAction(openDirAction)
        menu.exec(self.mapToGlobal(pos))

    def __openPath(self):
        filename = self.text()
        path = filename.replace('/', '\\')
        subprocess.Popen(r'explorer /select,"' + path + '"')


class FindPathWidget(QWidget):
    findClicked = pyqtSignal()
    added = pyqtSignal(str)

    def __init__(self, default_filename: str = ''):
        super().__init__()
        self.__initVal()
        self.__initUi(default_filename)

    def __initVal(self):
        self.__ext_of_files = ''
        self.__directory = False

    def __initUi(self, default_filename: str = ''):
        self.__pathLineEdit = FindPathLineEdit()
        if default_filename:
            self.__pathLineEdit.setText(default_filename)

        self.__pathFindBtn = QPushButton('Find')

        self.__pathFindBtn.clicked.connect(self.__find)

        self.__pathLineEdit.setMaximumHeight(self.__pathFindBtn.sizeHint().height())

        lay = QHBoxLayout()
        lay.addWidget(self.__pathLineEdit)
        lay.addWidget(self.__pathFindBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def setLabel(self, text):
        self.layout().insertWidget(0, QLabel(text))

    def setExtOfFiles(self, ext_of_files):
        self.__ext_of_files = ext_of_files

    def getLineEdit(self):
        return self.__pathLineEdit

    def getButton(self):
        return self.__pathFindBtn

    def getFileName(self):
        return self.__pathLineEdit.text()

    def setCustomFind(self, f: bool):
        if f:
            self.__pathFindBtn.clicked.disconnect(self.__find)
            self.__pathFindBtn.clicked.connect(self.__customFind)

    def __customFind(self):
        self.findClicked.emit()

    def __find(self):
        if self.isForDirectory():
            filename = QFileDialog.getExistingDirectory(self, 'Open Directory', '', QFileDialog.ShowDirsOnly)
            if filename:
                pass
            else:
                return
        else:
            str_exp_files_to_open = self.__ext_of_files if self.__ext_of_files else 'All Files (*.*)'
            filename = QFileDialog.getOpenFileName(self, 'Find', '', str_exp_files_to_open)
            if filename[0]:
                filename = filename[0]
            else:
                return
        self.__pathLineEdit.setText(filename)
        self.added.emit(filename)

    def setAsDirectory(self, f: bool):
        self.__directory = f

    def isForDirectory(self) -> bool:
        return self.__directory


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt Speech Recognition')
        filePathWidget = FindPathWidget()
        filePathWidget.added.connect(self.__run)

        self.__loadingLabel = LoadingLabel()
        self.__loadingLabel.setVisible(False)

        self.__browser = QTextBrowser()
        self.__browser.setPlaceholderText('Result will be here')

        lay = QVBoxLayout()
        lay.addWidget(filePathWidget)
        lay.addWidget(self.__loadingLabel)
        lay.addWidget(self.__browser)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setCentralWidget(mainWidget)

    def __run(self, filename):
        self.__t = Thread(filename=filename)
        self.__t.started.connect(self.__started)
        self.__t.onTextConverted.connect(self.__browser.setText)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __started(self):
        self.__loadingLabel.start()

    def __finished(self):
        self.__loadingLabel.stop()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())