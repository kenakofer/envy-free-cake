debug=False

def debug_print(*obj):
    if (debug):
        if len(obj) == 0:
            print()
        else:
            print(' '.join(map(str, obj)))
            

