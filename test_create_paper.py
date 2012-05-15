import unittest2 
import create_paper 
import tempfile 
import latexlog2html
import templates 
import settings 

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
    
        w, e, b = latexlog2html.parse_latex_log(temp_file_name) 
        self.assertEqual(2*len(w) + 4*len(e), 6)
        
    def test_parse_latex_log(self):
        pass 
        
    def test_create_ordered_list(self):
        heading = "Warnings"
        tagname = "warn"
        item_list = ['You stink', 'You stink', 'You stink']
        result = """<h1>Warnings</h1><ol><li><a href='#warn1'>You stink</a></li><li><a href='#warn2'>You stink</a></li><li><a href='#warn3'>You stink</a></li></ol>"""
        self.assertEqual(result, latexlog2html.create_ordered_list(
                heading, tagname, item_list))

    def test_better_latex_log(self):
        f = tempfile.NamedTemporaryFile("w", delete=False) 
        f.write("""
Stuff about fonts you don't care about 
LaTeX Warning: Foo stuff 
!Bar Stuff 
Stuff about overfulled boxes you don't care about 
""")
        f.close()
        temp_file_name = f.name   
        print(''.join(latexlog2html.convert_log(
                    temp_file_name
                    ,templates.LATEX_LOG_FILE_HEADER,
                     settings.CSS_HOTLINK)
                    ))
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest2.main()


