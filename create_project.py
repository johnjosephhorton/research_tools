import os 
import sys 
sys.path.append("/home/john")
import research_tools.create_paper as cp


if __name__ == '__main__':
    options, args = cp.options_parser() 
    input_dir = os.getcwd() 
    cp.main(input_dir, options, args) 






