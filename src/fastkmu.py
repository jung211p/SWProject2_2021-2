import sys
import requests
from PyQt5.QtCore import Qt
from ecampus import Ecampus

import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QWidget, QPushButton, QDialog, QApplication, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QLabel,
                             QMessageBox, QGridLayout,
                             QTableWidget, QTableWidgetItem,  QAbstractItemView, QListView)
import webbrowser



class LoginWindow(QDialog):
    e = Ecampus()
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setWindowTitle('Fast KMU Login')
        self.setGeometry(300, 300, 310, 210)
        self.textId = QLineEdit(self)
        self.textPw = QLineEdit(self)
        self.textPw.setEchoMode(QLineEdit.Password)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)

        labelLogin = QLabel('로그인')
        labelLogin.setAlignment(Qt.AlignCenter)
        font = labelLogin.font()
        font.setPointSize(font.pointSize() + 10)
        labelLogin.setFont(font)

        layout = QGridLayout(self)
        layout.addWidget(labelLogin, 0, 0, 1, 2)
        layout.addWidget(QLabel('아이디'), 1, 0)
        layout.addWidget(self.textId, 1, 1)
        layout.addWidget(QLabel('비밀번호'), 2, 0)
        layout.addWidget(self.textPw, 2, 1)
        layout.addWidget(self.buttonLogin, 3, 0, 1, 2)

    def handleLogin(self):
        try:
            if self.e.login(self.textId.text(), self.textPw.text()):
                self.accept()
            else:
                QMessageBox.warning(
                    self, 'Error', '로그인에 실패하였습니다. 비밀번호를 맞게 입력했다면 한영키도 확인해 주십시오.')
        except requests.exceptions.ReadTimeout:
            QMessageBox.warning(
                self, 'Error', '서버로부터 응답이 없습니다.')


class MainWindow(QWidget):
    days = ['월', '화', '수', '목', '금', '토']
    selectedWeekday = 0
    showData = []
    lessons = []
    lastShowMessage = ''

    def __init__(self, e):
        super().__init__()
        self.e = e
        self.initUI()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.setMessage)
        self.timer.start()


    def initUI(self):
        self.setGeometry(300, 300, 700, 350)
        self.setWindowTitle('Fast KMU - ' + self.e.studentName)

        self.labelMessage = QLabel('샘플 메세지')
        mainLayout = QGridLayout()

        leftLayout = QVBoxLayout()
        weekdayButtonLayout = QHBoxLayout()
        for i in range(6):
            weekdayButton = QPushButton()
            weekdayButton.setText(self.days[i])
            weekdayButton.clicked.connect(self.buttonWeekdayClicked)
            weekdayButtonLayout.addWidget(weekdayButton)

        self.tableview = QTableWidget()
        self.tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableview.cellClicked.connect(self.tableClicked)
        leftLayout.addLayout(weekdayButtonLayout)
        leftLayout.addWidget(self.tableview)

        rightLayout = QVBoxLayout()

        selectAttendButton = QPushButton()
        selectAttendButton.setText('실시간 강의 입장')
        selectAttendButton.clicked.connect(self.buttonAttendClicked)

        self.labelClassName = QLabel('왼쪽에서 강의를 선택해 주세요.')
        self.listview = QListView(self)
        self.listview.setFixedWidth(200)
        rightLayout.addWidget(selectAttendButton)
        rightLayout.addWidget(self.labelClassName)
        rightLayout.addWidget(self.listview)
        rightLayout.addStretch()
        mainLayout.addWidget(self.labelMessage, 0, 0)
        mainLayout.addLayout(leftLayout, 1, 0)
        mainLayout.addLayout(rightLayout, 1, 1)

        # 오늘자 수업 출력하기
        self.selectedWeekday = datetime.datetime.now().weekday()
        todayClasses = self.e.getWeekdayClasses(self.selectedWeekday)
        self.showData = todayClasses
        self.setTableView(todayClasses)

        self.setLayout(mainLayout)
        self.show()
        self.setMessage()



    def buttonWeekdayClicked(self):
        clickedButton = self.sender().text()

        for idx, value in enumerate(self.days):
            if clickedButton == value:
                self.selectedWeekday = idx
                classes = self.e.getWeekdayClasses(idx)
                self.showData = classes
                self.setTableView(classes)
                return

    def tableClicked(self, row, col):
        myClass = self.showData[row]
        self.lessons = self.e.getThisweekInfo(myClass['url'])
        self.labelClassName.setText('금주 ' + myClass['className'] + ' 강의')
        self.setListView(self.lessons)

    def setListView(self, lessons):
        model = QStandardItemModel()
        for lesson in lessons:
            model.appendRow(QStandardItem(lesson[0]))
        self.listview.setModel(model)

    def buttonAttendClicked(self):
        if self.listview.selectedIndexes():
            row = self.listview.selectedIndexes()[0].row()
            openUrl = self.lessons[row][1]
            if openUrl == 'zoom_error':
                self.showMessage('열리지 않은 강의입니다.')
                return

            webbrowser.open(openUrl)

    def showMessage(self, msg):
        QMessageBox.warning(self, 'Error', msg)


    def setTableView(self, classes):
        self.tableview.clear()

        columnHeaders = ['과목명', '교수', '시작시간', '종료시간', '강의실']
        self.tableview.setColumnCount(len(columnHeaders))
        self.tableview.setHorizontalHeaderLabels(columnHeaders)

        self.tableview.setRowCount(len(classes))
        for idx, todayClass in enumerate(classes):
            name = QTableWidgetItem(todayClass['className'])
            professor = QTableWidgetItem(todayClass['professor'])
            start = QTableWidgetItem(todayClass['startTime'])
            end = QTableWidgetItem(todayClass['endTime'])
            room = QTableWidgetItem(todayClass['room'])
            self.tableview.setItem(idx, 0, name)
            self.tableview.setItem(idx, 1, professor)
            self.tableview.setItem(idx, 2, start)
            self.tableview.setItem(idx, 3, end)
            self.tableview.setItem(idx, 4, room)

        self.tableview.resizeColumnsToContents()

    def setMessage(self):
        todayClasses = self.e.getWeekdayClasses(datetime.datetime.now().weekday())
        if not todayClasses:
            self.labelMessage.setText('오늘은 수업이 없습니다.')
            return

        now = datetime.datetime.now()

        for i, lesson in enumerate(todayClasses):
            startTime = datetime.datetime.now()
            startTime = startTime.replace(hour=int(lesson['startTime'].split(':')[0]), minute=int(lesson['startTime'].split(':')[1]))
            if now < startTime:
                span = (startTime - now)
                afterH = span.seconds // 3600
                afterM = (span.seconds // 60) % 60
                self.labelMessage.setText(f'{lesson["className"]} 강의까지 {afterH}시간 {afterM}분 남았습니다.')
                if afterH == 0 and afterM == 5 and lesson['className'] != self.lastShowMessage:
                    self.showMessage(f'{lesson["className"]} 강의까지 {afterH}시간 {afterM}분 남았습니다.')
                    self.lastShowMessage = lesson['className']
                break
        else:
            # 강의가 끝난건지, 아직 진행중인지 판단
            endTime = datetime.datetime.now()
            endTime = endTime.replace(hour=int(todayClasses[-1]['endTime'].split(':')[0]), minute=int(todayClasses[-1]['endTime'].split(':')[1]))

            if now < endTime:
                span = (endTime - now)
                afterH = span.seconds // 3600
                afterM = (span.seconds // 60) % 60
                self.labelMessage.setText(f'{afterH}시간 {afterM}분만 힘내요!')
            else:
                self.labelMessage.setText(f'오늘 수업은 다 끝났어요! 😊')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        fkmu = MainWindow(login.e)
        sys.exit(app.exec_())
