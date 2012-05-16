
LATEX_BASE_PAPER = """
\\documentclass[11pt]{article}

\\usepackage{booktabs}
\\usepackage{dcolumn} 
\\usepackage{epstopdf}
\\usepackage{fourier}
\\usepackage{fullpage}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{longtable} 
\\usepackage{natbib}
\\usepackage{rotating}
\\usepackage{tabularx}

\\begin{document} 

\\title{Here is a really great title}
\\date{March 30, 2012}

\\author{John J. Horton \\\\ oDesk Research \\& Harvard Kennedy
  School\\footnote{Author contact information, datasets and code are
    currently or will be available at
    \\href{http://www.john-joseph-horton.com/}{http://www.john-joseph-horton.com/}.}}
\\maketitle
\\begin{abstract}
  Here is a really great abstract.  
\\end{abstract} 

\\section{Introduction}
\\cite{smith1999wealth} had some great ideas! 

\\section{Getting some stuff done in R}
According to R's calculations, $1 + 1$ is equal to:
\\input{./numbers/tough_problem.txt}

\\subsection{Plots!}

\\begin{figure}[h]
  \\centering
  \\includegraphics[scale=0.25]{./plots/hist.png}
  \\caption{Here is a figure}
  \\label{fig:hist}
\\end{figure}


\\subsection{We can make R get data from our database}

\\input{./numbers/sql_output.txt}

\\bibliographystyle{aer}
\\bibliography{%s.bib}

\\end{document} 
"""

SQLMAKE = """groups:
  P1: 
     setup: one_plus_one.sql 
     output: 
       - get_one_plus_one.sql 
"""

SQLCODE_SETUP = """ 
CREATE OR REPLACE VIEW analytics.test as
SELECT 1 + 1; 
"""

SQLCODE_OUTPUT = """
SELECT * FROM analytics.test;  
"""

RMAKE = """scripts: [%s.R]"""

RCODE = """
library(ggplot2)
library(RPostgreSQL)
sink("../../writeup/numbers/tough_problem.txt")
cat(1+1)
sink() 

png("../../writeup/plots/hist.png")
 qplot(runif(100))
dev.off()


drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, %s)
df.raw <- dbGetQuery(con, "select * from analytics.test")

sink("../../writeup/numbers/sql_output.txt")
 summary(df.raw)
sink()
"""

LOCAL_MAKE = """
import os 
import sys 
sys.path.append('%s')
import research_tools.create_paper as cp

if __name__ == '__main__':
    options, args = cp.parse_terminal_input() 
    input_dir = os.getcwd() 
    cp.main(input_dir, options.output_path, options.flush, options.get_data, options.run_r)
"""


BIBTEX ="""
@book{smith1999wealth,
  title={Wealth of nations},
  author={Smith, A.},
  year={1999},
  publisher={Wiley Online Library}
}
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
