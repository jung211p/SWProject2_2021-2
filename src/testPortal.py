import unittest
from portal import Portal
testID = input('id : ')
testPW = input('pw : ')

class testPortal(unittest.TestCase):
    def setUp(self) :
        self.ptal = Portal()
        self.ptal.login(testID, testPW)

    def testPtal(self):
        self.assertIn('소프트웨어프로젝트', str(self.ptal.classDatas))


if __name__ == '__main__':
    unittest.main()
