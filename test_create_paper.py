import unittest2 
import create_paper 
import tempfile 

class CreatePaperTest(unittest2.TestCase):

    def setUp(self):
        pass 

    def test(self): 
        #a = f.read()
        f = tempfile.NamedTemporaryFile("w", delete=False) 
        f.write("""
Stuff about fonts you don't care about 
LaTeX Warning: Foo stuff 
!Bar Stuff 
Stuff about overfulled boxes you don't care about 
""")
        f.close()
        temp_file_name = f.name
    
        w, e, b = create_paper.parse_latex_log(temp_file_name) 
        self.assertEqual(2*len(w) + 4*len(e), 6)
        
    def test_parse_latex_log(self):
        pass 
        

if __name__ == '__main__':
    unittest2.main()
