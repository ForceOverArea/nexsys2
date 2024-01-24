from sys import argv
from engine.nexsys2lib import nexsys2
import engine.nexsys2preproc as nexsys2preproc

preprocs = [ # Preprocessor list - This can be extended as desired to add more syntax sugar
    nexsys2preproc.comments,
    nexsys2preproc.const_values,
    nexsys2preproc.domains,
    nexsys2preproc.guess_values,
    nexsys2preproc.conditionals 
]

def main(*args):
    """
    Default Nexsys2 solver. Takes a tuple of filepaths and returns a 
    `Generator` containing their solutions, if they exist. 
    """
    for system_file in args:
        with open(system_file, "r", encoding = "utf-8") as f:
            print(nexsys2(f.read(), preprocs))

if __name__ == "__main__":
    main(*(argv[1:]))