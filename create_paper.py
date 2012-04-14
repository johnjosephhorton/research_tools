#!/user/bin/env python 

import csv 
import datetime 
import distutils.dir_util as d 
import optparse 
import os
import psycopg2 
import re
import shutil
import subprocess 
import time  
import yaml 

# to do
# Add arxiv bundler 
# Support postscript 
# Add wsd support 
# Add html export option 

def nickname(n): 
    """Appends the octal [a-h] representation of directory number 
       to the date time stamp folder to make command line navigation easier."""
    return 'a' if n==0 else ''.join([chr(97 + int(i)) for i in oct(n)[1:]]) 

def get_pg_connection():
    config_yaml = os.path.join(os.getcwd(), "config.yaml")
    db_params = yaml.load(open(config_yaml, 'r'))
    connect_tuple = tuple([db_params[x] for x in ['dbname', 'user', 'password', 
                                                    'host', 'port']])
    return psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % 
                            connect_tuple)

def csv_to_html(data_dir): 
    """Generates a HTML file of tables of the dataset - useful for quick viewing. Ideally, 
       the tables would be sortable, searcheable, summarizeable etc., but right now, that
       functionality doesn't work. Not sure why.
       Probably want to switch to: http://tablesorter.com/docs/ 
    """
    html = open(os.path.join(data_dir, "consolidated_data.html"), "w")
    html.write("""
    <html>
    <head>
    <script type="text/javascript" src='../libraries/sorttable.js'></script>

   <style>
   table.sortable thead {
    background-color:#eee;
    color:#666666;
    font-weight: bold;
    cursor: default;
   }
</style>
   </head><body>""")
    csv_files = [c for c in os.listdir(data_dir) if re.search(r'.+\.csv', c)]
    for csv_file in csv_files:
        html.write("<h1>%s</h1>" % csv_file)
        html.write("<table class='sortable'>")
        for line in csv.reader(open(os.path.join(data_dir, csv_file), "r")):
            html.write("<tr>\n")
            html.write("</tr>\n")
            for item in line: 
                html.write('<td>' + item + '</td>')
        html.write("</table>")
    html.close() 

def pg_query_to_csv(cur, query, csv_fn):
    """
    Given cursor cur and query, output the result to csv_fn.

    This function is only designed to handle one statement, do not include
    multiple statements with semicolons!
    """
    query_wo_returns = re.sub(r'[\n\r]', ' ', query)
    query_wo_semicolon = re.sub(r'\s*;\s*$', '', query_wo_returns)
    cur.copy_expert("""COPY (%s) TO STDOUT WITH CSV HEADER""" % query_wo_semicolon,
                    file(csv_fn,'w'))

def make_datasets():   
    yaml_file = os.path.join(os.getcwd(), "code", "sql", "make.yaml")
    query_plan = yaml.load(open(yaml_file, 'r'))
    print query_plan
    conn = get_pg_connection()
    cur = conn.cursor()
    # execute the set-up scripts 
        
        # execute the actual data scripts 
    data_location = os.path.join(os.getcwd(), "data")
    query_location = os.path.join(os.getcwd(), "code", "sql")
    setup_query =  open(os.path.join(query_location, query_plan['setup']), "r").read()
    cur.execute(setup_query)
    cur.connection.commit()
    for query in query_plan['output']:
        query_file = open(os.path.join(query_location, query), "r")
        csv_file = os.path.join(data_location, query + ".csv")
        pg_query_to_csv(cur, query_file.read(), csv_file)
    csv_to_html(data_location)
    return None 

def main():
    input_dir = os.getcwd() 
    topic = os.path.basename(os.getcwd())
    parser = optparse.OptionParser()

    parser.add_option("-d", "--output_dir", dest="output_dir", 
                      help="target directory for reports", default = "/tmp")
       
    parser.add_option("-r", "--run_r", dest="run_r", action="store_true", 
                      help="boolean for whether to run r", 
                      default = False)

    parser.add_option("-g", "--get_data", dest="get_data", action="store_true", 
                      help="boolean to get the data from odw", 
                      default = False)

    (options, args) = parser.parse_args() 

    if options.get_data: 
        make_datasets()
        
        

    if options.run_r:
        os.chdir(os.path.join(os.getcwd(), "code/R/"))
        r_process = subprocess.Popen(['Rscript', 'analysis.R'], 
                                     shell=False, 
                                     stdout=subprocess.PIPE)
        flush = r_process.communicate()[0]
    
    num_dirs = 0
    try:
        num_dirs = len(os.listdir(options.output_dir))
    except OSError:
        print "OSError - trying to find the number of folders in the dictory failed"

    folder_name = nickname(num_dirs) + '-' + datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    dir_name = os.path.join(options.output_dir, folder_name)
    os.mkdir(dir_name)

    # moves to the output directory 
    d.copy_tree(input_dir,dir_name)
   
    os.chdir(os.path.join(dir_name, "writeup"))
    seq = ['p','b','p','b','p','p','p']
    for op in seq: 
        print "Doing a %s iteration" % op 
        
        if op is 'p':
            pdftex_process = subprocess.Popen(['pdflatex', 
                                               '-interaction=nonstopmode', '%s'%topic], 
                                              shell=False, 
                                              stdout=subprocess.PIPE)
            print "PDFTEX return code is %s" % pdftex_process.returncode
            if pdftex_process.returncode != 0:
                txt = pdftex_process.communicate()[0].split("\n")
                for l in txt:
                    if len(l) > 0 and l[0]=='!':
                        print l
      
        if op is 'b':
            os.system('bibtex %s'%topic)
        if op is 'l':
            os.system('latex %s'%topic)

    final_pdf = os.path.join(dir_name, "writeup", "%s.pdf" % topic)
    submit_pdf = os.path.join(input_dir, "submit", "%s.pdf" % topic)
    try:
        shutil.copy(final_pdf, submit_pdf)
    except IOError: 
        print("Oops - looks like the pdf didn't get built - check the latex log")
    os.system("google-chrome %s" % dir_name)
    os.system("google-chrome %s" % submit_pdf)
    
    return None    


# def create_paper(topic, path, postscript=False, writeup_folder = "writeup"): 
#     dir_name = "/tmp/%s%s"%(topic,int(round(time.time(),0)))
#     print path, dir_name
#     d.copy_tree(path,dir_name)
#     os.chdir(dir_name + "/%s" % writeup_folder)
#     sweave_process = subprocess.Popen(["echo", "Sweave('%s.Rnw')"%topic], stdout=subprocess.PIPE)
#     r_process = subprocess.Popen(["R", "--vanilla"], 
#                                  shell = False, 						                  
#                                  stdin=sweave_process.stdout,
#                                  stdout=subprocess.PIPE, 
#                                  stderr=subprocess.PIPE
#                                  )
#     sweave_process.stdout.close()
#     txt = r_process.communicate()[1].split("\n")
#     for l in txt:
#         if l[0:5]=="Error":
#             print l

#     print "The R process return code: %s" % r_process.returncode
#     #return False
#     #print r_process.returncode

#     seq = ['p','b','p','b','p','p','p']
#     for op in seq: 
#         print "Doing a %s iteration"%op
#         if op is 'p'
#             pdftex_process = subprocess.Popen(['pdflatex', '-interaction=nonstopmode', '%s'%topic], 
#                                               shell=False, stdout=subprocess.PIPE)
#             print "PDFTEX return code is %s" % pdftex_process.returncode
#             #if pdftex_process.returncode != 0:
#             txt = pdftex_process.communicate()[0].split("\n")
#             for l in txt:
#                 if len(l) > 0 and l[0]=='!':
#                     print l
    
#             #pdftex_process.close()
#         if op is 'b':
#             os.system('bibtex %s'%topic)
#         if op is 'l':
#             os.system('latex %s'%topic)

#     try:
#         if postscript:
#             os.system('dvips -t letter -o temp.ps temp.dvi')
#             os.system('ps2pdf temp.ps') 
#             shutil.copy('temp.ps', path + "/submit/" + topic + ".ps")

#         shutil.copy('%s.pdf'%topic, path + "/submit/" + topic + ".pdf")
#         shutil.copy('%s.tex'%topic, path + "/submit/" + topic + ".tex")
#         shutil.copy('%s.bbl'%topic, path + "/submit/" + topic + ".bbl")
#     except IOError:
# 	print "Can't copy because the PDF/TEX/Bib etc. didn't get made"


if __name__ == '__main__':
    main()

