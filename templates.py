
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
\\usepackage{amsmath}
\\usepackage{algorithmic} 
\\usepackage{algorithm2e}


\\hypersetup{
  colorlinks = TRUE,
  citecolor=blue,
  linkcolor=red,
  urlcolor=black
}

\\begin{document} 

\\title{Here is a really great title}
\\date{\today}

\\author{John J. Horton \\\\ oDesk Research \\& Harvard Kennedy
  School\\footnote{Author contact information, datasets and code are
    currently or will be available at
    \\href{http://www.john-joseph-horton.com/}{http://www.john-joseph-horton.com/}.}}
\\maketitle
\\begin{abstract}
\\noindent  Here is a really great abstract.  \\newline

\\noindent JEL J01, J24, J3
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

\\section{Inputted Model}

\\input{model.tex} 

\\section{Using matplotlib for making figures}

\\begin{figure}[h]
  \\centering
  \\includegraphics[scale=0.25]{./diagrams/matplotlib.png}
  \\caption{Here is a matplot lib constructed figure}
  \\label{fig:matplotlib}
\\end{figure}

\\bibliographystyle{aer}
\\bibliography{%s.bib}

\\end{document} 
"""

LATEX_INPUT_FILE="""
\\input{insitustart.tex}
Here is a model
\\input{insituend.tex} 
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
    cp.main(input_dir, options.output_path, options.flush, options.get_data, options.run_r, options.run_py)
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
<script> 

function copyToClipboard (text) {
  window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);
}

</script> 
</head>
 <body>
  %s
 <h1>Resources</h1> 
 <ul>
 <li><a href="./submit/%s.pdf" target="_blank">PDF of the paper</a></li> 
 <li><a href="./writeup/%s.tex.html">HTML of tex source</a></li> 
 <li><a href=".">Directory listing</a></li>     
 <li>All LaTeX Stitched Together <a href="./combined_file.tex">(tex)</a><a href="./combined_file.tex.html">(html)</a></li>  
 <li><a href="./%s">LaTeX Log File</a></li>  
 </ul>
 </body> 
 <button type="button" onClick="copyToClipboard('%s')">Copy directory path</button>
 </html> 
"""

MATPLOTLIB_EXAMPLE = """
import numpy as np
import matplotlib.pyplot as plt

a = np.arange(0,3,.02)
b = np.arange(0,3,.02)
c = np.exp(a)
d = c[::-1]

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(a,c,'k--',a,d,'k:',a,c+d,'k')
leg = ax.legend(('Model length', 'Data length', 'Total message length'),
           'upper center', shadow=True)
ax.set_ylim([-1,20])
ax.grid(False)
ax.set_xlabel('Model complexity --->')
ax.set_ylabel('Message length --->')
ax.set_title('Minimum Message Length')

ax.set_yticklabels([])
ax.set_xticklabels([])

# set some legend properties.  All the code below is optional.  The
# defaults are usually sensible but if you need more control, this
# shows you how

# the matplotlib.patches.Rectangle instance surrounding the legend
frame  = leg.get_frame()
frame.set_facecolor('0.80')    # set the frame face color to light gray

# matplotlib.text.Text instances
for t in leg.get_texts():
    t.set_fontsize('small')    # the legend text fontsize

# matplotlib.lines.Line2D instances
for l in leg.get_lines():
    l.set_linewidth(1.5)  # the legend line width

#plt.show()

plt.savefig("../../writeup/diagrams/matplotlib.png", 
             format="png")
"""




LATEX_INSITU_START = """ 
\\documentclass[11pt]{article}

\\usepackage{booktabs}
\\usepackage{colortbl}
\\usepackage{dcolumn} 
\\usepackage{epstopdf}
\\usepackage{fourier}
\\usepackage{fullpage}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{longtable} 
\\usepackage{natbib}
\\usepackage{rotating}
\\usepackage{setspace} 
\\usepackage{Sweave} 
\\usepackage{tabularx}

\\hypersetup{
  colorlinks,
  citecolor=blue,
  linkcolor=blue,
  urlcolor=blue,
  filecolor=white
}

\\newtheorem{proposition}{Proposition}

\\title{Here is a title}

\\begin{document}
   \\maketitle
"""

LATEX_INSITU_END = """ 
\\end{document}
"""

