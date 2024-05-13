from enum import Enum

from dbus import SessionBus, SystemBus

class DBusDataTypes(Enum):
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


def introspect(bus_name, object_path, system=False) -> str:
    bus = SessionBus() if not system else SystemBus()

    obj = bus.get_object(bus_name, object_path)
    return obj.get_dbus_method("introspect", dbus_interface="org.freedesktop.DBus.Introspectable")()