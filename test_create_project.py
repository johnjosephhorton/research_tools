import tempfile 
import unittest2
import create_project
import os 

class CreateProjectsTest(unittest2.TestCase):

    def setUp(self):
        pass
    
    def test_integration(self):
        os.system("rm -rf /tmp/foobar ; python create_project.py foobar /tmp")

if __name__ == '__main__':
    unittest2.main()
