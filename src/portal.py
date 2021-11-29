import requests
from bs4 import BeautifulSoup
import json

class Portal:
    session = requests.Session()
    classDatas = {}


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
        bs = BeautifulSoup(self.session.post('https://portal.kookmin.ac.kr/por/sso/CreateRequestAuth.jsp',
                                             data={'loginId': id, 'pswd': pw}, timeout=3).text, 'html.parser')
        needParams = ['RelayState', 'SAMLRequest', 'authParameter']
        requestData = self.makeData(bs, needParams)

        bs = BeautifulSoup(self.session.post('https://sso.kookmin.ac.kr/sso/Request.jsp', data=requestData, timeout=3).text,
                           'html.parser')
        needParams = ['RelayState', 'SAMLResponse']
        responseData = self.makeData(bs, needParams)

        self.session.post('https://portal.kookmin.ac.kr/por/sso/Response.jsp', data=responseData, timeout=3).text
        self.session.post('https://portal.kookmin.ac.kr/por/lgin', timeout=3).text
        self.session.get('https://portal.kookmin.ac.kr/por/mn', timeout=3).text
        self.session.get('https://portal.kookmin.ac.kr/por/main/MainPtCtr/getPrtletView.do?vId=mainpt0127', timeout=3)

        header = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                  'Content-Type': 'application/json; charset=UTF-8'}

        for i in range(1, 8):
            self.classDatas[i - 1] = []
            try:
                result = self.session.post('https://portal.kookmin.ac.kr/por/api?serviceId=MAINPT0127-01',
                                           headers=header, data='{"daywCd":' + str(i) + '}', timeout=3).text
                if result:
                    classData = json.loads(result)
                    for myClass in classData:
                        classTime = myClass['lessnLestmNm'].split('~')
                        tmpClass = {'className': myClass['subjtNm'], 'startTime': classTime[0], 'endTime': classTime[1],
                                    'professor': myClass['instrEmpnm'], 'room': myClass['rmnmNm']}
                        self.classDatas[(i + 5) % 7].append(tmpClass)
            except requests.exceptions.ConnectionError:
                continue