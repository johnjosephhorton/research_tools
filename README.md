Overview 
======== 

'research_tools' is my (John Horton's) software tools for managing
papers. It is distributed under the GNU public license. It's basic
purpose is to automate many of the tedious parts of writing papers and
making it easier to start new projects with everything needed.

What it does
============
There are two main components: 

create_project.py - This python script creates a new project by: 
a) creates complete file structure 
b) creates stub files for R code, LaTeX, BibTex etc. using templates.py 
c) creates a local "make.py" file for building the paper 

create_paper.py - This orchestrates the building on the paper---it manages the 
running of SQL scripts, R scripts, latex/bibtex etc.

How it works
============
TK. 

To Do
=====
1. Add the option of running sed on all tex files before combination 
2. [DONE] Add ability to do a make-like sequencing of R files 
3. Do something smarter with config information 
4. Make the HTML data view optional 
5. [DONE] Make a "where is what?" view of the source document as HTML  
6. Add WSD integration 
7. Add HTML export 
8. Turn Bibtex file into HTML file w/ links 
10. Make the HTML CSV tables sortable 
11. Generate HTML / ODF / PS output versions 
12. Add arxiv/ssrn bundler 
13. add google docs export options  
14. Add a reasonable 'gitignore' to the templates 
15. Show several table examples
16. Investigate virtualenv-like solutions 
