import preprocessors
from engine.nexsys2lib import nexsys2

def main(*args):
    """
    Default Nexsys2 solver. Takes a tuple of filepaths and returns a 
    `Generator` containing their solutions, if they exist. 
    """
    for system_file in args:
        with open(system_file, "r", encoding = "utf-8") as f:
            print(nexsys2(f.read()))

if __name__ == "__main__":
    from sys import argv
    main(*(argv[1:]))