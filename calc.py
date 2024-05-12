# client code goes here
import sys

usage_string = "usage:\n\tcalc.py add 4 5\n\tcalc.py mult 5 6"

try:
    op = sys.argv[1]
    if op not in ["add", "mult"]:
        raise ValueError("invalid operation")
    if op == None:
        raise ValueError("missing operation")
    
except ValueError as err:
    print(err)
except IndexError as err:
    print("please provide an operation")
finally:
        print(usage_string)


# TODO: enforce each numbber is only 4 bytes