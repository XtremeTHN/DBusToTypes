import xml.etree.ElementTree as ET

import argparse
import sys
import os
import re

class DBusDataTypes:
    INT16="n"
    UINT16="q"
    INT32="i"
    UINT32="u"
    INT64="x"
    UINT64="t"
    DOUBLE="d"
    BYTE="y"
    STRING="s"
    BOOLEAN="b"
    ARRAY="a"
    TUPLE="("

    VARIANT="v"

def exit(msg, code=0):
    print(msg)
    sys.exit(1)

class Arguments:
    bus_data: str

    source_type: str
    file: str

class TypescriptInterface(list):
    def __init__(self, name: str, child_indentation=1):
        super().__init__()
        
        self.child_indentation = ""
        self.append("export interface " + name.strip() + " extends Gio.DBusProxy {")
        self.child_indentation = "\t" * child_indentation
    def __enter__(self):
        return self

    def append(self, item):
        super().append(f"{self.child_indentation}{item}")

    def parse_type(self, dtype, comma=False):
        result = ""
        first = dtype[0]
        rest = dtype[1:]
        print(first, rest)
        match first:
            case DBusDataTypes.INT16 | DBusDataTypes.UINT16 | \
                DBusDataTypes.INT32 | DBusDataTypes.UINT32 | \
                DBusDataTypes.INT64 | DBusDataTypes.UINT64 | \
                DBusDataTypes.DOUBLE | DBusDataTypes.BYTE:

                result = "number"

            case DBusDataTypes.STRING:
                result = "string"

            case DBusDataTypes.BOOLEAN:
                result = "boolean"

                #case DBusDataTypes.ARRAY:
                #    print(dtype)
                #    result = "["
                #    index = 0
                #    if dtype[1] == "{":
                #        index = 2
                #    else:
                #        index = 1

                #    for x in dtype[index:]:
                #        if x == "}":
                #            break
                #        result = result + self.parse_type(x, comma=True)
                #    result = result + "]"
            
            case DBusDataTypes.ARRAY:
                elements = self.parse_type(rest, comma)
                result = "Array<" + elements + ">"

            case DBusDataTypes.TUPLE:
                result = "["
                for x in dtype:
                    print(x)
                    result = result + self.parse_type(x, comma=True)
                result = result + "]"
            case "{" | "}":
                return 

            case DBusDataTypes.VARIANT:
                result = "any"
            case _:
                result = "unknown"
        print("parsed")
        return f'{result}{"," if comma else ""}'

    def add_method(self, name, args: dict[str, str], return_type):
        func = f"{name}: ("
        for arg_name, arg_type in args.items():
            func = func + arg_name + ": " + self.parse_type(arg_type)
        
        self.append(func)
    
    def add_property(self, name, dbus_type, access="public"):
        prop = f"{'readonly ' if access == 'read' else ''}{name}: {self.parse_type(dbus_type)}"
        self.append(prop)
    
    def __exit__(self, *_):
        self.end()

    def end(self):
        self.append("}")

def to_javascript(root: ET.Element):
    classes = ["import Gio from gi://Gio\n"]
    for interface in root:
        with TypescriptInterface(interface.attrib["name"]) as current_class:
            name = interface.attrib.get("name", "Unknown").split(".")[-1]

            for child in interface:
                child_type = child.tag
                match child_type:
                    case "property":
                        prop_name = child.attrib["name"]
                        prop_type = child.attrib["type"]

                        current_class.add_property(prop_name, prop_type, access=child.attrib["access"])

            classes.append("\n".join(current_class))

    return classes
parser = argparse.ArgumentParser(prog="dbus-to-types")

parser.add_argument("bus_data", nargs="?", type=str, help="The bus name of the bus you want to introspect. Or a xml file of the bus")

parser.add_argument("source_type", type=str, help="The source type the types will be outputed")
parser.add_argument("file", type=str, nargs="?", default=sys.stdout, help="The output file name")

args: Arguments = parser.parse_args()

if __name__ == "__main__":
    data = ""
    if os.path.exists(args.bus_data) is True:
        data = open(args.bus_data).read()
    else:
        exit("dbus introspection not implemented yet", 1)

    xml = ET.fromstring(data)   
    match args.source_type:
        case "javascript":
               print(*to_javascript(xml))
        case _:
            exit("language not implemented yet", 1)
