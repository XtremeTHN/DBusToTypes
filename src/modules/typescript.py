import xml.etree.ElementTree as ET
from modules.dbus import DBusDataTypes

class TypescriptInterface(list):
    def __init__(self, name: str, child_indentation=1):
        super().__init__()
        class_name = name.strip()
        super().append("export interface " + class_name + " extends Gio.DBusProxy {")
        self.child_indentation = "\t" * child_indentation
        self.append(f"new(...args: unknown[]) => {class_name}")
        
    def __enter__(self):
        return self

    def append(self, item):
        super().append(f"{self.child_indentation}{item}")

    def parse_type(self, dtype, comma=False):
        result = ""
        if len(dtype) == 0:
            return ""
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
                if rest[0] == "{":
                    result = "Map<" + self.parse_type(rest, comma).strip(",") + ">"
                else:
                    elements = self.parse_type(rest, comma)
                    result = "Array<" + elements + ">"
                rest = ""
                
            case DBusDataTypes.TUPLE:
                elements = self.parse_type(rest, comma)
                result = "[" + elements.strip(",") + "]"
                rest = ""
                
            case DBusDataTypes.VARIANT:
                result = "any"

            case "{" | "}" | ")":
                return self.parse_type(rest, comma) 

            case _:
                result = "unknown"

        if rest != "":
            result = result + "," + self.parse_type(rest, comma)
        # return f'{result}{"," if comma else ""}'
        return f'{result}'

    def add_method(self, name, args: dict[str, str], return_type="void"):
        func = f"{name}: ("
        for arg_name, arg_type in args.items():
            func = func + arg_name + ": " + self.parse_type(arg_type, comma=False) + ", "
        func = func.strip(", ") + ") => " + return_type
        self.append(func)
    
    def add_property(self, name, dbus_type, access="public"):
        prop = f"{'readonly ' if access == 'read' else ''}{name}: {self.parse_type(dbus_type)}"
        self.append(prop)
    
    def __exit__(self, *_):
        self.end()

    def end(self):
        super().append("}")

def to_typescript(data: list[str], skip_dbus_interfaces=False):
    classes = ['import Gio from "gi://Gio"\n']
    for x in data:
        xml = ET.fromstring(x)
        for interface in xml:
            if interface.tag != "interface":
                continue
            
            if skip_dbus_interfaces:
                if interface.attrib.get("name", "") in ["org.freedesktop.DBus.Peer", "org.freedesktop.DBus.Introspectable", "org.freedesktop.DBus.Properties"]:
                    continue
                
            name = interface.attrib.get("name", "Unknown").split(".")[-1].title()
            with TypescriptInterface(name) as current_class:
                for child in interface:
                    child_type = child.tag
                    child_name = child.attrib.get("name")

                    match child_type:
                        case "property":
                            prop_type = child.attrib["type"] 
                            current_class.add_property(child_name, prop_type, access=child.attrib["access"])
                        case "method":
                            args = {}
                            for index, argument in enumerate(child):
                                arg_name = argument.attrib.get("name") or f"arg_{index}"
                                if argument.tag != "arg":
                                    continue
                                args[arg_name] = argument.attrib["type"]
                            current_class.add_method(child_name, args)
            classes.append("\n".join(current_class))
    return classes
