import os 
import sys 
#sys.path.append("/home/john")
import templates
import settings 

def create_file_structure(project_name, project_dir):
    """This creates basic file structure for the project.
    """
    dirs = [
        'literature', 
        'code/R', 
        'code/SQL', 
        'code/python', 
        'data',
        'models',    
        'submit', 
        'writeup/images', 
        'writeup/numbers', 
        'writeup/plots', 
        'writeup/tables',
        'writeup/diagrams', 
        ]
    os.mkdir(os.path.join(project_dir, project_name))
    for d in dirs:
        os.makedirs(os.path.join(project_dir, project_name, d))

def create_stub_files(project_name, project_dir): 
    # (template, name, location) 
    files_to_create = [(templates.LATEX_BASE_PAPER % project_name, 
                        "%s.tex" % project_name, 
                        "writeup"), 
                       (templates.BIBTEX, 
                        "%s.bib" % project_name, 
                        "writeup"), 
                       (templates.LOCAL_MAKE % settings.RESEARCH_TOOL_LOCATION, 
                        "make.py", 
                        "."), 
                       (templates.RCODE % settings.R_DB_CONNECT_STRING, 
                        "%s.R" % project_name, 
                        "code/R"), 
                       (templates.RMAKE % project_name, 
                        "r_make.yaml",
                        "code/R"), 
                       (templates.SQLMAKE, 
                        "sql_make.yaml", 
                        "code/SQL/"), 
                       (templates.SQLCODE_SETUP, 
                        "one_plus_one.sql", 
                        "code/SQL/"), 
                       (templates.SQLCODE_OUTPUT, 
                        "get_one_plus_one.sql", 
                        "code/SQL/") 
                       ]
    for template, file_name, location in files_to_create: 
        f = open(os.path.join(project_dir, project_name, location, file_name), "w")
        f.write(template)
        f.close() 
  

if __name__ == '__main__':
    project_name, project_dir = sys.argv[1:] 
    create_file_structure(project_name, project_dir)
    create_stub_files(project_name, project_dir)

    # do a build
    #print("Doing PDF build")
    os.chdir(os.path.join(project_dir, project_name))
    #os.system("python make.py")
    print("Doing R build")
    os.system("python make.py -r")
    print("Doing SQL build")
    #os.system("python make.py -r -g")

