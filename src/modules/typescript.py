import xml.etree.ElementTree as ET
from modules.dbus import DBusDataTypes

class TypescriptInterface(list):
    def __init__(self, name: str, child_indentation=1):
        super().__init__()
        
        super().append("export interface " + name.strip() + " extends Gio.DBusProxy {")
        self.child_indentation = "\t" * child_indentation
    def __enter__(self):
        return self

    def append(self, item):
        super().append(f"{self.child_indentation}{item}")

    def parse_type(self, dtype, comma=False):
        result = ""
        first = dtype[0]
        rest = dtype[1:]
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
            
            case DBusDataTypes.ARRAY:
                elements = self.parse_type(rest, comma)
                result = "Array<" + elements + ">"

            # case DBusDataTypes.TUPLE:
            #     result = "["
            #     for x in dtype:
            #         print(x)
            #         result = result + self.parse_type(x, comma=True)
            #     result = result + "]"
            case "{" | "}":
                return self.parse_type(rest, comma) 

            case DBusDataTypes.VARIANT:
                result = "any"
            case _:
                print(first)
                result = "unknown"
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
        super().append("}")

def to_typescript(data: list[str]):
    classes = ['import Gio from "gi://Gio"\n']
    for x in data:
        xml = ET.fromstring(x)
        for interface in xml:
            name = interface.attrib.get("name", "Unknown").split(".")[-1]
            with TypescriptInterface(name) as current_class:
                for child in interface:
                    child_type = child.tag
                    match child_type:
                        case "property":
                            prop_name = child.attrib["name"]
                            prop_type = child.attrib["type"]

                            current_class.add_property(prop_name, prop_type, access=child.attrib["access"])

        classes.append("\n".join(current_class))
    return classes