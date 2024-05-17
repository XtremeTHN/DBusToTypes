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
    object_paths: list[str]
    filter_dbus_interfaces: bool
    
    system: str
    
    file: str

    dtype: str
    output: str


parser = argparse.ArgumentParser(prog="dbus-to-types")

parser.add_argument("-b", "--bus", type=str, action="store", help="The bus name of the bus you want to introspect.")
parser.add_argument("-p", "--object-path", "--object-paths", dest="object_paths", type=str, nargs="*", help="Introspect one or more object paths")
parser.add_argument("-i", "--filter-dbus-interfaces", dest="filter_dbus_interfaces", action="store_true", help="Pass it if you don't want the dbus interfaces on your source output")
parser.add_argument("-s", "--system", action="store_true", help="Use the system bus")

parser.add_argument("-f", "--file", "--files", nargs="*", help="One or more already introspected dbus xml file")

parser.add_argument("-t", "--type", dest="dtype", action="store", type=str, help="The source type the types will be outputed")
parser.add_argument("-o", "--output", type=str, action="store", help="The output file name. Default: stdout")


if __name__ == "__main__":
    args: Arguments = parser.parse_args()
    
    if args.output is None:
        args.output = sys.stdout
    else:
        try:
            args.output = open(args.output, "w")
        except Exception as e:
            exit("Error: " + str(e))

    data = ""
    if args.bus is not None:
        if args.object_paths is not None:
            data = [introspect(args.bus, x, system=args.system) for x in args.object_paths]
        else:
            exit("specify the object path you want to inspect. Either with -m or with -p")
    
    elif args.file is not None:
        data = [open(x, "r").read() for x in args.file]
    else:
        exit("no bus or file specified", 1)

    match args.dtype:
        case "typescript":
            print(*to_typescript(data, skip_dbus_interfaces=args.filter_dbus_interfaces), sep="\n", file=args.output)
        case _:
            exit("language not implemented yet", 1)
