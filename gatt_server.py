from __future__ import print_function
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array

import functools
import data

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

from random import randint

import exceptions
import adapters

import data

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

GATT_MANAGER_IFACE = 'org.bluez.GattManager1'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'



class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.add_service(OMirrorService(bus, 0))

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


class Service(dbus.service.Object):
    """
    org.bluez.GattService1 interface implementation
    """
    PATH_BASE = '/org/bluez/example/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_SERVICE_IFACE: {
                        'UUID': self.uuid,
                        'Primary': self.primary,
                        'Characteristics': dbus.Array(
                                self.get_characteristic_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        return self.characteristics

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """
    org.bluez.GattCharacteristic1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        return self.descriptors

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE,
                         signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Descriptor(dbus.service.Object):
    """
    org.bluez.GattDescriptor1 interface implementation
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
                GATT_DESC_IFACE: {
                        'Characteristic': self.chrc.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_DESC_IFACE:
            raise exceptions.InvalidArgsException()

        return self.get_properties()[GATT_DESC_IFACE]

    @dbus.service.method(GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise exceptions.NotSupportedException()

    @dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise exceptions.NotSupportedException()

class OMirrorService(Service):
    OMIRROR_SVC_UUID = '57c6fe8d-4dae-4978-b886-3dabf74c7c00'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.OMIRROR_SVC_UUID, True)
        self.add_characteristic(PQ_ShowChar(bus, 0, self))
        self.add_characteristic(Pota_DelayChar(bus, 1, self))
        self.add_characteristic(Quote_DelayChar(bus, 2, self))
        self.add_characteristic(Name_Char(bus, 3, self))
        self.add_characteristic(Autosleep_Char(bus, 4, self))
        self.add_characteristic(AutosleepTimer_Char(bus, 5, self))
        self.add_characteristic(City_Char(bus, 6, self))
        self.add_characteristic(RGBMode_Char(bus, 7, self))
        self.add_characteristic(RGBSingle_Char(bus, 8, self))
        self.add_characteristic(RGBFlashSeq_Char(bus, 9, self))
        self.add_characteristic(RGBFlashDelay_Char(bus, 10, self))
        self.add_characteristic(RGBFadeDelay_Char(bus, 11, self))
        self.add_characteristic(Wifi_getData(bus, 12, self))
        self.add_characteristic(Wifi_connect(bus, 13, self))
        self.add_characteristic(Akt_getData(bus, 14, self))
        self.add_characteristic(Akt_setData(bus, 15, self))
        self.add_characteristic(Akt_deleteData(bus, 16, self))
        self.add_characteristic(Central_getData(bus, 17, self))
        self.add_characteristic(Central_setData(bus, 18, self))
        self.add_characteristic(Central_deleteData(bus, 19, self))

class PQ_ShowChar(Characteristic):
    CHRC_UUID = '2844'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['write'],
                service)
        self.value = []
    
    def WriteValue(self, value, options):
        self.value = value
        data.setData("pota_quote_show", int(self.value[0]))

class Pota_DelayChar(Characteristic):
    CHRC_UUID = '2845'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        return [dbus.Byte(int(data.getData("pota_delay")))]
    
    def WriteValue(self, value, options):
        self.value = value
        data.setData("pota_delay", int(self.value[0]))

class Quote_DelayChar(Characteristic):
    CHRC_UUID = '2846'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        return [dbus.Byte(int(data.getData("quote_delay")))]
    
    def WriteValue(self, value, options):
        self.value = value
        data.setData("quote_delay", int(self.value[0]))

class Name_Char(Characteristic):
    CHRC_UUID = '2847'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        for c in data.getData("name"):
            databyte.append(dbus.Byte(ord(c)))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        string = ""
        chars = []
        for byte in self.value:
            if isinstance(byte, dbus.Byte):
                chars.append(chr(byte))
        string = string.join(chars)
        data.setData("name", string)

class Autosleep_Char(Characteristic):
    CHRC_UUID = '2848'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        return [dbus.Byte(int(data.getData("autosleep")))]
    
    def WriteValue(self, value, options):
        self.value = value
        data.setData("autosleep", int(self.value[0]))

class AutosleepTimer_Char(Characteristic):
    CHRC_UUID = '2849'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        string = data.getData("autosleep_time")
        string = string.split(",")
        time1 = string[0].split(":")
        time2 = string[1].split(":")
        
        return [dbus.Byte(int(time1[0])), dbus.Byte(int(time1[1])), dbus.Byte(int(time2[0])), dbus.Byte(int(time2[1]))]
    
    def WriteValue(self, value, options):
        self.value = value
        string = "%i:%i,%i:%i" % (int(self.value[0]), int(self.value[1]), int(self.value[2]), int(self.value[3]))
        data.setData("autosleep_time", string)

class City_Char(Characteristic):
    CHRC_UUID = '2850'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        for c in data.getData("weather_city"):
            databyte.append(dbus.Byte(ord(c)))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        string = ""
        chars = []
        for byte in self.value:
            if isinstance(byte, dbus.Byte):
                chars.append(chr(byte))
        string = string.join(chars)
        data.setData("weather_city", string)

class RGBMode_Char(Characteristic):
    CHRC_UUID = '2851'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        return [dbus.Byte(int(data.getData("rgb_mode")))]
    
    def WriteValue(self, value, options):
        self.value = value
        data.setData("rgb_mode", int(self.value[0]))

class RGBSingle_Char(Characteristic):
    CHRC_UUID = '2852'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        string = data.getData("rgb_single").split(",")
        databyte.append(dbus.Byte(int(string[0])))
        databyte.append(dbus.Byte(int(string[1])))
        databyte.append(dbus.Byte(int(string[2])))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        
        string = "%i,%i,%i" % (int(self.value[0]), int(self.value[1]), int(self.value[2]))
        
        data.setData("rgb_single", string)

class RGBFlashSeq_Char(Characteristic):
    CHRC_UUID = '2853'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        string = data.getData("rgb_flash_sequence").split(":")
        for s in string:
            string2 = s.split(",")
            databyte.append(dbus.Byte(int(string2[0])))
            databyte.append(dbus.Byte(int(string2[1])))
            databyte.append(dbus.Byte(int(string2[2])))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        
        string = ""
        
        i = 1
        for byte in self.value:
            if isinstance(byte, dbus.Byte):
                string += "%i" % int(byte)
                if(divmod(i, 3)[1] != 0):
                    string += ","
                else:
                    if i < (len(self.value)):
                        string += ":"
                i +=1
        data.setData("rgb_flash_sequence", string)

class RGBFlashDelay_Char(Characteristic):
    CHRC_UUID = '2854'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        string = data.getData("rgb_flash_delay")
        
        value = int(string)
        
        part_1 = (value>>8) & 0xFF
        
        part_2 = value & 0xFF
        
        return [dbus.Byte(part_1), dbus.Byte(part_2)]
    
    def WriteValue(self, value, options):
        self.value = value
        
        part_1 = int(self.value[0])
        part_2 = int(self.value[1])
        value_c = hex(part_1<<8 | part_2)
        data.setData("rgb_flash_delay", int(value_c, 16))

class Wifissid_Char(Characteristic):
    CHRC_UUID = '2855'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        for c in data.getData("weather_city"):
            databyte.append(dbus.Byte(ord(c)))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        string = ""
        chars = []
        for byte in self.value:
            if isinstance(byte, dbus.Byte):
                chars.append(chr(byte))
        string = string.join(chars)
        data.setData("weather_city", string)

class Wifipass_Char(Characteristic):
    CHRC_UUID = '2856'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.CHRC_UUID,
                ['read', 'write'],
                service)
        self.value = []
    
    def ReadValue(self, options):
        databyte = []
        for c in data.getData("weather_city"):
            databyte.append(dbus.Byte(ord(c)))
        return databyte
    
    def WriteValue(self, value, options):
        self.value = value
        string = ""
        chars = []
        for byte in self.value:
            if isinstance(byte, dbus.Byte):
                chars.append(chr(byte))
        string = string.join(chars)
        data.setData("weather_city", string)

def register_app_cb():
    print('GATT application registered')


def register_app_error_cb(mainloop, error):
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def gatt_server_main(mainloop, bus, adapter_name):
    data.readData()
                     
    adapter = adapters.find_adapter(bus, GATT_MANAGER_IFACE, adapter_name)
    if not adapter:
        raise Exception('GattManager1 interface not found')

    service_manager = dbus.Interface(
            bus.get_object(BLUEZ_SERVICE_NAME, adapter),
            GATT_MANAGER_IFACE)

    app = Application(bus)

    print('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                    reply_handler=register_app_cb,
                                    error_handler=functools.partial(register_app_error_cb, mainloop))

