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
import sys

def hashfree(dir):
    """Makes sure---before we start doing lots of intense computations---that
       there are not any files w/ hash in front of them (which the shutil utility
       cannot copy for some reason) """
    for root, subFolders, files in os.walk(dir):
        for file in files:
            if re.search('\.#.*', file):
                return (False, file) 
    return (True, None) 
  
def nickname(n): 
    """Appends the octal [a-h] representation of directory number 
       to the date time stamp folder to make command line navigation easier."""
    return 'a' if n==0 else ''.join([chr(97 + int(i)) for i in oct(n)[1:]]) 

def get_pg_connection():
    """Creates a connection to ODW""" 
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


def run_group(group, query_location, last_execution_time): 
    """ 
    Determines if any query in the last has a modification time greater than 
    the last execution time.
    """
    if group['setup']:
        queries = [group['setup']] + group['output'] 
    else:
        queries = group['output']
    for q in queries:
        f = os.path.join(query_location, q)
        if os.path.getmtime(f) > last_execution_time:
            return True
    return False

def get_last_execution_time():
    try:
        f = open(os.path.join(os.getcwd(), "code", "sql", "execution_history.log"), "r")
        times = f.readlines()
        if not times: # no lines in the log file 
            return -1.0 
        f.close()
        return float(times[len(times)-1])
    except IOError: # log filed oesn't exist - treating as if never been run 
        return -1.0

def record_execution_time(): 
    with open(os.path.join(
            os.getcwd(), "code", "sql", "execution_history.log"), "a") as myfile:
        myfile.write("%s" % time.time())
        myfile.write("\n")

def make_datasets():   
    last_execution_time = get_last_execution_time()

    yaml_file = os.path.join(os.getcwd(), "code", "sql", "make.yaml")
    query_plan = yaml.load(open(yaml_file, 'r'))
  
    data_location = os.path.join(os.getcwd(), "data")
    query_location = os.path.join(os.getcwd(), "code", "sql")

    groups_to_run = [] 
    for group_name in query_plan['groups']:
        group = query_plan['groups'][group_name]
        if run_group(group, query_location, last_execution_time):
            groups_to_run.append(group_name)

    if not groups_to_run:
        print("No groups to run")
        return True 

    conn = get_pg_connection()
    cur = conn.cursor()       

    for group_name in groups_to_run:
        group = query_plan['groups'][group_name]
        if group['setup']:
            setup_query_file = os.path.join(query_location, group['setup'])
            setup_query = open(setup_query_file, "r").read()
            record_execution_time()
            cur.execute(setup_query)
            cur.connection.commit()
        for output_query in group['output']:
            query_file = open(os.path.join(query_location, output_query), "r")
            csv_file = os.path.join(
                data_location, group_name + "-" + output_query + ".csv")
            record_execution_time()
            pg_query_to_csv(cur, query_file.read(), csv_file)
    
    csv_to_html(data_location)
             
    return None

def main():
    input_dir = os.getcwd() 
    try:
        result, file = hashfree(input_dir)
        assert(result)
    except: 
        print("you've got a temp file - go save %s" % file)
        return False 
    topic = os.path.basename(os.getcwd())
    print("The topic is %s" % topic)
    parser = optparse.OptionParser()

    parser.add_option("-d", "--output_dir", dest="output_dir", 
                      help="target directory for reports", default = "/tmp")
       
    parser.add_option("-r", "--run_r", dest="run_r", action="store_true", 
                      help="boolean for whether to run r", 
                      default = False)

    parser.add_option("-g", "--get_data", dest="get_data", action="store_true", 
                      help="boolean to get the data from odw", 
                      default = False)
    
    parser.add_option("-f", "--flush", dest="flush", action="store_true", 
                      help="boolean to flush out execution history and force a fresh data fetch", 
                      default = False)

    (options, args) = parser.parse_args() 

    if options.flush:
        os.remove(os.path.join(os.getcwd(), "code/sql/execution_history.log"))

    if options.get_data: 
        make_datasets()
        
       
    if options.run_r:
        os.chdir(os.path.join(os.getcwd(), "code/R/"))
        yaml_file = os.path.join(os.getcwd(), "r_make.yaml")
        execution_plan = yaml.load(open(yaml_file, 'r'))
        r_scripts = execution_plan['scripts']
        for script in r_scripts: 
            r_process = subprocess.Popen(['Rscript', script], 
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

    writeup_folder = os.path.join(dir_name, "writeup")
    for f in os.listdir(writeup_folder): 
        if re.search(r'.+\.(pdf|tex|bbl)$', f):
            source = os.path.join(writeup_folder, f)
            destination_input = os.path.join(input_dir, "submit", f)
            destination_output = os.path.join(dir_name, "submit", f)
            try:
                shutil.copy(source, destination_input)
                shutil.copy(source, destination_output)
            except IOError: 
                print("""Oops - looks like the pdf didn't get built, or it got built
                 but the filenames are wrong. In any case, check the latex log
                 in /writeup of the output directory.   
                 """)

    submit_pdf = os.path.join(dir_name, "submit", "%s.pdf" % topic)
    os.system("google-chrome %s" % dir_name)
    os.system("google-chrome %s" % submit_pdf)
    
    return None    

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

