import unittest
from ecampus import Ecampus
testID = input('id : ')
testPW = input('pw : ')

# 소프2 수강생만 test 가능
class testEcampus(unittest.TestCase):

    def testEcam(self):
        self.ecam = Ecampus()
        self.assertTrue(self.ecam.login(testID, testPW))
        self.assertIn(str({'className': '소프트웨어프로젝트Ⅱ', 'startTime': '10:30', 'endTime': '12:00', 'professor': '윤성혜', 'room': '미래관4층47호실', 'url': 'https://ecampus.kookmin.ac.kr/course/view.php?id=43081'}), str(self.ecam.getWeekdayClasses(2)))



if __name__ == '__main__':

    # e = testEcampus()
    unittest.main()
    # e.testEcam(testID, testPW)