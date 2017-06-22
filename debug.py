debug=False
prefix = ""

def debug_print(*obj):
    if (debug):
        if len(obj) == 0:
            print()
        else:
            print(prefix,' '.join(map(str, obj)))

def set_debug(value):
    global debug
    debug=value

def set_debug_prefix(string):
    global prefix
    prefix=string

            

