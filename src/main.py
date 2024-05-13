import xml.etree.ElementTree as ET

import argparse
import sys
import os

from modules.typescript import to_typescript
from modules.dbus import introspect

def exit(msg, code=0):
    print(msg)
    sys.exit(1)

class Arguments:
    # bus_data: str

    # source_type: str
    # file: str
    bus: str
    object_path: str
    system: str
    
    file: str

    dtype: str
    output: str


parser = argparse.ArgumentParser(prog="dbus-to-types")

parser.add_argument("-b", "--bus", type=str, action="store", help="The bus name of the bus you want to introspect.")
parser.add_argument("-p", "--object-path", dest="object_path", type=str, action="store", help="The object path you want to introspect.")
parser.add_argument("-s", "--system", action="store_true", help="Use the system bus")

parser.add_argument("-f", "--file", type=str, action="store", help="The input file. Generally an already introspected dbus xml file")

parser.add_argument("-t", "--type", dest="dtype", action="store", type=str, help="The source type the types will be outputed")
parser.add_argument("-o", "--output", type=str, action="store", help="The output file name. Default: stdout")

# parser.add_argument("bus_or_file", nargs="?", type=str, help="The bus name of the bus you want to introspect. Or a xml file of the bus")
# parser.add_argument("object_path", nargs="?", type=str, help="The object path you want to introspect. Required if the bus_or_file arg is a bus")

# parser.add_argument("source_type", type=str, help="The source type the types will be outputed")
# parser.add_argument("file", type=str, nargs="?", help="The output file name. Default: stdout")


if __name__ == "__main__":
    args: Arguments = parser.parse_args()
    
    if args.output is None:
        args.output = sys.stdout
    else:
        try:
            args.output = open(args.output, "w")
        except Exception as e:
            print("Error: " + str(e))

    data = ""
    if args.bus is not None:
        data = introspect(args.bus, args.object_path, system=args.system)
    elif args.file is not None:
        data = open(args.file, "r").read()
    else:
        exit("no bus or file specified", 1)

    xml = ET.fromstring(data)   
    match args.dtype:
        case "javascript":
            print(*to_typescript(xml), sep="", file=args.output)
        case _:
            exit("language not implemented yet", 1)
