TEMPLATE_PAPER = """
\documentclass{article}
\title{Cartesian closed categories and the price of eggs}
\author{Jane Doe}
\date{September 1994}
\begin{document}
   \maketitle
   Hello world!
\end{document}
"""

TEMPLATE_R_MAKE = """
"""

TEMPLATE_R = """
"""

LATEX_LOG_FILE_HEADER = """ 
    <html>
    <head> 
    <link rel="stylesheet" href="%s">
    </head>
    <body>
    <a name="top">
    """


TEMPLATE_CREATE_PAPER = """ 
"""


TEMPLATE_HTML_INDEX = """ 
 <html>
 <head> 
 <link rel="stylesheet" href="http://twitter.github.com/bootstrap/1.4.0/bootstrap.min.css">
 </head>
 <body>
  %s
 <h1>Resources</h1> 
 <ul>
 <li><a href="./submit/%s.pdf" target="_blank">PDF of the paper</a></li> 
 <li><a href="./latex_log.html" target="_blank">LaTeX Log File</a></li> 
 <li><a href="./writeup/%s.tex.html" target="_blank">HTML of tex source</a></li> 
 <li><a href="." target="_blank">Directory listing</a></li>     
 <li><a href="./data/consolidated_data.html" target="_blank">Data sets</a></li>     
 </ul>
 </body> 
 </html> 
"""
