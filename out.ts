import Gio from "gi://Gio"

export interface Notifications extends Gio.DBusProxy {
	Notify: (arg_0: string, arg_1: number, arg_2: string, arg_3: string, arg_4: string, arg_5: Array<string>, arg_6: Map<string,any>, arg_7: number, arg_8: number, ) => void
	CloseNotification: (id: number, ) => void
	GetCapabilities: (arg_0: Array<string>, ) => void
	GetServerInformation: (arg_0: string, arg_1: string, arg_2: string, arg_3: string, ) => void
}
