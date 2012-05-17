#!/user/bin/env python 

import csv 
import datetime 
import distutils.dir_util as d 
import optparse 
import os
import re
import shutil
import subprocess 
import time  
import yaml 
import sys
import fileinput 

import settings
import templates 
import csv2html
import latexlog2html as l2h
import connect2db 

# external packages 
sys.path.append(settings.WSD_LOCATION)
import WritingSmellDetector.wsd as wsd
import flatex.flatex as flatex 

def writing_smell(combined_text, output_dir):
    """ 
    Uses the writing smell detector to create an HTML file showing 
    the problematic writing. 
    """
    # this is a kludge work around to accomodate the fact that the 
    # WSD main routine takes an object as an output (it's the result 
    # of the command line parsing). 
    class ArgSimulator(object): 
        def __init__(self, combined_text, output_dir):
            self.text = combined_text
            self.abspath=True
            self.include_empty=False    
            self.indent=4 
            self.no_embed_css=False 
            self.outfile=os.path.join(output_dir, 'smells.html')
            self.output_format='html' 
            self.reftext=False 
            self.rules=[]
     
    args = ArgSimulator(combined_text, output_dir)
    wsd.main(args)
    return None 
    
def make_html_index(output_dir, topic, alert=None): 
    file = open(os.path.join(output_dir, "report.html"), "w")
    template = templates.TEMPLATE_HTML_INDEX  % (
        "<h1> %s </h1>" % alert if alert else "", 
        topic, 
        topic, 
        settings.LATEX_HTML_FILE_NAME)
    file.writelines(template)
    file.close() 
    return None 
  
def nickname(n): 
    """Appends the octal [a-h] representation of directory number 
       to the date time stamp folder to make command line navigation easier."""
    return 'a' if n==0 else ''.join([chr(97 + int(i)) for i in oct(n)[1:]]) 


def tex_to_html(output_dir): 
    """Forms an HTML version of the paper, making each of the inputs a clickable href. 
       Following through to plots & figures will take some re-factoring. 
    """
    tex_input_re = r"""\\input{[^}]*}"""
    tex_input_filename_re = r"""{[^}]*"""
    tex_files = [c for c in os.listdir(os.path.join(output_dir, "writeup")) 
                         if re.search(r'.+\.(tex|txt)$', c)]

    for filename in tex_files: 
        sink = open(os.path.join(output_dir, "writeup", filename + ".html"), "w")
        source = open(os.path.join(output_dir, "writeup", filename), "r")
        sink.writelines("<html><pre>")
        for source_line in source:
            m = re.search(tex_input_re,source_line)
            if m: 
                matching_line = m.group(0)
                file_inputed = re.search(tex_input_filename_re, 
                                         source_line).group(0)[1:]
                sink.writelines('</pre>\input{<a href="%s">%s</a>}<pre>' % 
                                (file_inputed + '.html', file_inputed))
            else:
                sink.writelines(source_line)
        sink.writelines("</pre></html>")
        source.close() 
        sink.close() 
    return None 


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

def get_last_execution_time(execution_history_log):
    try:
        f = open(execution_history_log, "r")
        modification_times = f.readlines()
        if not modification_times: 
            return -1.0 
        f.close()
        return float(times[len(times)-1])
    except IOError: 
        print("%s doesn't exist" % execution_history_log)
        return -1.0

def record_execution_time(input_dir): 
    with open(os.path.join(input_dir, settings.SQL_EXECUTION_HISTORY_LOG), "a") as myfile:
        myfile.write("%s" % time.time())
        myfile.write("\n")

def make_datasets(input_dir):   
    last_execution_time = get_last_execution_time(os.path.join(input_dir, settings.SQL_EXECUTION_HISTORY_LOG))
    yaml_file = os.path.join(input_dir, settings.SQL_MAKE_FILE)
    query_plan = yaml.load(open(yaml_file, 'r'))   
    data_location = os.path.join(input_dir, "data")
    query_location = os.path.join(input_dir, "code", "SQL")

    groups_to_run = [] 
    for group_name in query_plan['groups']:
        group = query_plan['groups'][group_name]
        if run_group(group, query_location, last_execution_time):
            groups_to_run.append(group_name)

    if not groups_to_run:
        print("No groups to run")
        return True 

    conn = connect2db.get_db_connection() 
    cur = conn.cursor()       

    for group_name in groups_to_run:
        group = query_plan['groups'][group_name]
        if group['setup']:
            setup_query_file = os.path.join(query_location, group['setup'])
            setup_query = open(setup_query_file, "r").read()
            record_execution_time(input_dir)
            cur.execute(setup_query)
            cur.connection.commit()
        for output_query in group['output']:
            query_file = open(os.path.join(query_location, output_query), "r")
            csv_file = os.path.join(
                data_location, group_name + "-" + output_query + ".csv")
            record_execution_time(input_dir)
            pg_query_to_csv(cur, query_file.read(), csv_file)
             
    return None

def inplace_sanitize(file_name, regex_list):
    """This is supposed to replace inputs like in a latex file that are used to support 
    WYSIWYG editing of subfiles. However, its' not working right now."""
    print file_name, regex_list 
    for line in fileinput.input(file_name, inplace=1):
        matches = [re.search(regex, line) is not None for regex in regex_list]
        if any(matches):
            pass
        else:
            print line,

def parse_terminal_input():
    parser = optparse.OptionParser()

    parser.add_option("-d", "--output_path", dest="output_path", 
                      help="target directory for reports", default = "/tmp")
       
    parser.add_option("-r", "--run_r", dest="run_r", action="store_true", 
                      help="boolean for whether to run r", 
                      default = False)

    parser.add_option("-g", "--get_data", dest="get_data", action="store_true", 
                      help="boolean to get the data from odw", 
                      default = False)
    
    parser.add_option("-f", "--flush", dest="flush", action="store_true", 
                      help="""boolean to flush out execution history 
                              and force a fresh data fetch""", 
                      default = False)

    return parser.parse_args() 

def make_pdf(writeup_folder, topic, seq): 
    os.chdir(writeup_folder)
    for op in seq: 
        print("Doing a %s iteration" % op)         
        if op is 'p':
            pdftex_process = subprocess.Popen(['pdflatex', 
                                               '-interaction=nonstopmode', 
                                               '%s'%topic], 
                                              shell=False, 
                                              stdout=subprocess.PIPE)
            print("PDFTEX return code is %s" % pdftex_process.returncode)
            if pdftex_process.returncode != 0:
                txt = pdftex_process.communicate()[0].split("\n")
                for l in txt:
                    if len(l) > 0 and l[0]=='!':
                        print l
      
        if op is 'b':
            os.system('bibtex %s'%topic)
        if op is 'l':
            os.system('latex %s'%topic)
    return None 


def get_folder_name(output_path): 
    num_dirs = 0
    try:
        num_dirs = len(os.listdir(output_path))
    except OSError:
        print """OSError - trying to find the number of folders 
               in the dictory failed"""
    folder_name = nickname(num_dirs
                           ) + '-' + datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    return os.path.join(output_path, folder_name)    

def run_R(input_dir): 
    yaml_file = os.path.join(input_dir, "code/R", "r_make.yaml")
    execution_plan = yaml.load(open(yaml_file, 'r'))
    r_scripts = execution_plan['scripts']
    os.chdir(os.path.join(input_dir, "code/R/"))
    for script in r_scripts:
        r_process = subprocess.Popen(['Rscript', script], 
                                     shell=False, 
                                     stdout=subprocess.PIPE)
        flush = r_process.communicate()[0]
    return None 

def pull_build_products_back_to_input_dir(input_dir, output_dir): 
    alert = None 
    writeup_folder = os.path.join(output_dir, "writeup")
    for f in os.listdir(writeup_folder): 
        if re.search(r'.+\.(pdf|tex|bbl)$', f):
            source = os.path.join(writeup_folder, f)
            destination_input = os.path.join(input_dir, "submit", f)
            destination_output = os.path.join(output_dir, "submit", f)
            try:
                shutil.copy(source, destination_input)
                shutil.copy(source, destination_output)
            except IOError: 
                print("""PDF Not Built!""")
                alert = "Paper not created!" 

def execute_python_scripts(python_dir): 
    for f in os.listdir(python_dir):
        execfile(os.path.join(python_dir, f))

def all_files_saved(input_dir):
    """Makes sure---before we start doing lots of intense computations---that
       there are not any files w/ hash in front of them (which the shutil utility
       cannot copy for some reason) """
    no_bad_files = True 
    bad_files = []
    for root, subFolders, files in os.walk(input_dir):
        for f in files:
            if re.search('\.#.*', f):
                no_bad_files = False
                bad_files.append(f)                

    if not no_bad_files:
        print("You've got at least one temp file - go save:")
        for f in bad_files:
            print f 
        return False 
    else:
        return True

def main(input_dir, output_path, flush, get_data, run_r):
    assert(all_files_saved(input_dir))
    topic = os.path.basename(input_dir)
    print("The paper topic is %s" % topic)

    if flush: os.remove(os.path.join(input_dir, "code/SQL/execution_history.log"))
    if get_data: make_datasets(input_dir)
    if run_r: run_R(input_dir) 

    python_dir = os.path.join(input_dir, "code/python")
    execute_python_scripts(python_dir)

    output_dir = get_folder_name(output_path)        
    os.mkdir(output_dir)
    d.copy_tree(input_dir,output_dir)
    
    # for testing purposes - needs to iterate over all .tex files
    _inputed_tex_files = tex_files = [c for c in os.listdir(os.path.join(output_dir, "writeup")) 
                         if re.search(r'.+\.tex$', c)]
    inputed_tex_files = [os.path.join(output_dir, "writeup", c) for c in _inputed_tex_files]
    for tex_file in inputed_tex_files: 
        print("Sanitizing file %s" % tex_file)
        inplace_sanitize(tex_file, settings.LATEX_REPLACE_REGEXES)    
    
    base_file = os.path.join(output_dir, "writeup", "%s.tex" % topic)
    combined_file = os.path.join(output_dir, "combined_file.tex")
    
    # choking on a non-tex based input. 
    #flatex.main(base_file, combined_file)
    tex_to_html(output_dir)

    seq = ['p','b','p','b','p','p','p']
    make_pdf(os.path.join(output_dir, "writeup"),topic, seq)
    alert = pull_build_products_back_to_input_dir(input_dir, output_dir)
    make_html_index(output_dir, topic, alert)
  
    # writing_smell(combined_file, dir_name)
    
    #data_location = os.path.join(output_dir, "data")
    #csv_to_html(data_location)

    latex_log = os.path.join(output_dir, "writeup", "%s.log" % topic)
    html_latex_log = l2h.convert_log(latex_log, 
                                    templates.LATEX_LOG_FILE_HEADER,
                                    settings.CSS_HOTLINK)
    # write the log file
    f = open(os.path.join(output_dir, settings.LATEX_HTML_FILE_NAME), "w")
    f.writelines(html_latex_log)
    f.close() 
      
    report_location = os.path.join(output_dir, settings.EXEC_REPORT)
    os.system("%s %s" % (settings.BROWSER, report_location))
    return True    

if __name__ == '__main__':
    input_dir = os.getcwd() 
    options, args = parse_terminal_input() 
    main(input_dir, options.output_path, options.flush, options.get_data, options.run_r)

