To Do
=====
1. Add the option of running sed on all tex files before combination 
2. Add ability to do a make-like sequencing of R files 
3. Do something smarter with config information 
4. Make the HTML data view optional 
5. Make a "where is what?" view of the source document as HTML  
6. Add WSD integration 
7. Add HTML export 
8. Turn Bibtex file into HTML file w/ links 


Overview 
========
This repository is a template for all future research 
projects.  


Getting Started
===============

1. Fork this repository
2. Rename .tex, .bib and repository to a single new name 
3. Edit the yaml.config if the databse needs to change 


How it works
============

The main creat_paper.py script does several things based on the options 
based to it. It will go get data from database when based the '-g' option; 
it will re-run the R analysis if passed the '-r' option. It will always
generate the pdf and put it into the /submit folder.  

When the PDF is done running, it opens two tabs in chrome: 
1. The output directory (where all log files etc. are available)
2. A PDF of the actual document. 
3. In the /data folder, a HTML version of CSV files is created for quick inspection 

To Do
=====
1. Make the HTML CSV tables sortable 
2. Generate HTML / ODF / PS output versions 
3. Integrate the WSD.py
4. Add arxiv/ssrn bundler 
5. add google docs export options 
6. 
