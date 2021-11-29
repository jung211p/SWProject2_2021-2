import requests
import threading
from bs4 import BeautifulSoup
from time import sleep
from portal import Portal

class Ecampus:
    session = requests.Session()
    studentName = ''
    p = Portal()

    def __init__(self):
        pingThread = threading.Thread(target=self.ping)
        pingThread.setDaemon(True)
        pingThread.start()


    # 10초마다 세션 유지
    def ping(self):
        while True:
            self.session.get('https://ecampus.kookmin.ac.kr', timeout=5)
            sleep(10)

    # result-web page, needParams-필요한 데이터
    def makeData(self, result, needParams):
        resultData = {}
        for needParam in needParams:
            paramElement = result.find('input', attrs={'name': needParam})
            if paramElement:
                resultData[needParam] = paramElement['value']

        if len(resultData) == len(needParams):
            return resultData
        else:
            print('error!')

    def login(self, id, pw):
        # LoginToken Get, Get Session
        bs = BeautifulSoup(self.session.get('https://ecampus.kookmin.ac.kr/login/index.php', timeout=3).text, 'html.parser')
        loginTokenElement = bs.find('input', attrs={'name': 'logintoken'})
        if loginTokenElement:
            loginToken = (loginTokenElement['value'])

        if loginToken:
            loginData = {'anchor': '', 'logintoken': loginToken, 'loginId': id, 'loginPwd': pw}

            bs = BeautifulSoup(
                self.session.post('https://ecampus.kookmin.ac.kr/magicsso/requestAuth.php', data=loginData, timeout=3).text,
                'html.parser')
            needParams = ['procType', 'nick', 'site', 'group', 'sessionId', 'clg', 'loginId', 'loginPwd', 'gubun',
                          'relayState', 'logout', 'erreturn']
            s2srequestParam = self.makeData(bs, needParams)

            bs = BeautifulSoup(
                self.session.post('https://sso.kookmin.ac.kr/magicsso/S2SRequest.jsp', data=s2srequestParam, timeout=3).text,
                'html.parser')
            needParams = ['procType', 'ED']
            ssoParam = self.makeData(bs, needParams)

            bs = BeautifulSoup(
                self.session.post('https://ecampus.kookmin.ac.kr/magicsso/response.php', data=ssoParam, timeout=3).text,
                'html.parser')

            img = bs.find('img', attrs={'class': 'userpicture'})
            if img:
                self.studentName = img['alt'][:-3]
                self.p.login(id, pw)
                self.getClassInfo()
                return True
        self.session.cookies.clear()
        return False

    def getClassInfo(self):
        result = self.session.get('https://ecampus.kookmin.ac.kr', timeout=3).text
        bs = BeautifulSoup(result, 'html.parser')

        myClasses = bs.find_all('a', attrs={'class': 'course-link'})
        for myClass in myClasses:
            eLink = myClass['href']
            eString = myClass.text

            for dayClasses in self.p.classDatas:
                for idx, lesson in enumerate(self.p.classDatas[dayClasses]):
                    lessonName = lesson['className']
                    if lessonName in eString:
                        self.p.classDatas[dayClasses][idx]['url'] = eLink

    def getWeekdayClasses(self, weekday):
        return self.p.classDatas[weekday]

    def getThisweekInfo(self, url):
        result = []
        bs = BeautifulSoup(self.session.get(url).text, 'html.parser')
        bs = bs.find('div', attrs={'class': 'course-box course-box-current'})
        links = bs.find_all('li', attrs={'class': 'activity'})
        for link in links:
            tmpUrl = link.find('a')['href']
            if 'zoom' in link['class'] or 'url' in link['class']:
                realURL = self.getRealURL(tmpUrl)
                if 'youtu' in realURL or 'zoom' in realURL:
                    lesson = [link.text, realURL]
                    result.append(lesson)

        return result

    def getRealURL(self, url):
        if 'mod/url/' in url:
            bs = BeautifulSoup(self.session.get(url, timeout=3).text, 'html.parser')
            bs = bs.find('div', attrs={'class': 'urlworkaround'})
            if bs:
                return bs.find('a')['href']
            else:
                return 'error'
        # 이부분 강의가 열렸을 때 직접 파싱해볼 것
        elif 'mod/zoom' in url:
            bs = BeautifulSoup(self.session.get(url, timeout=3).text, 'html.parser')
            bs = bs.find('input', attrs={'name': 'id', 'type': 'hidden'})
            if bs:
                res = self.session.get('https://ecampus.kookmin.ac.kr/mod/zoom/loadmeeting.php?id=' + bs['value'], timeout=3)
                return res.url


            return 'zoom_error'