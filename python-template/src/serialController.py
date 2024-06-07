'''
Module to automatically connect to the ESP via serial and send commands to it.
Use the DeviceIdentifierType 'FROM_LIST' for YSP workshop; it checks against an allowed list of devices located in file 'DeviceList.py'.
'''
import serial
import time

from enum import Enum

from serial.tools import list_ports, list_ports_common

from DeviceList import AllowedDevicesNodeIDs

class DeviceIdentifierType(Enum):
    PORT = 1
    SERIAL_NUMBER = 2
    AUTO_DETECT = 3
    # for YSP workshop
    FROM_LIST = 4


class ESPController:
    """
    ESP Controller connection and communication class
    @param identifierType: DeviceIdentifierType - Type of identifier to use for device identification (default: DeviceIdentifierType.AUTO_DETECT) [PORT, SERIAL_NUMBER, AUTO_DETECT, FROM_LIST]
    @param identifierString: str - Identifier string to use for device identification (default: '') [PORT, SERIAL_NUMBER]
    @param baudrate: int - Baudrate to use for serial communication (default: 9600)
    @param timeout: int - Timeout for serial communication (default: 0)
    @param waitTime: int - Wait time for controller to initialize in seconds (default: 2s)
    """

    def __init__(self, identifierType: DeviceIdentifierType = DeviceIdentifierType.AUTO_DETECT, identifierString: str = '', baudrate: int = 9600, timeout: int = 0, waitTime: int = 2):
        """
        ESP Controller connection and communication class
        @param identifierType: DeviceIdentifierType - Type of identifier to use for device identification (default: DeviceIdentifierType.AUTO_DETECT) [PORT, SERIAL_NUMBER, AUTO_DETECT, FROM_LIST]
        @param identifierString: str - Identifier string to use for device identification (default: '') [PORT, SERIAL_NUMBER]
        @param baudrate: int - Baudrate to use for serial communication (default: 9600)
        @param timeout: int - Timeout for serial communication (default: 0)
        @param waitTime: int - Wait time for controller to initialize in seconds (default: 2s)
        """
        self.identifierType = identifierType
        self.identifierString = identifierString
        self.baudrate = baudrate
        self.timeout = timeout
        self.waitTime = waitTime
        self._controllerConnected: bool = False
        self._controllerPort: str = ''
        self._serialNumber: str = ''
        self._connectedDevice: str = ''
        self._nodeID: int = 0
        self._hardwareID: int = 0
        self._allowedDevices: dict[int, int] = {}
        self.controller: serial.Serial | None = self.__connect()
        self.__initSuccess()

    @property
    def isConnected(self) -> str:
        self.controllerConnected = self.controller.is_open  # type: ignore
        return f"Controller Connected: {self.controllerConnected} at {self.controllerPort}"

    @property
    def controllerPort(self) -> str:
        return self._controllerPort
    
    @controllerPort.setter
    def controllerPort(self, value: str) -> None:
        self._controllerPort = value  
    
    @property
    def serialNumber(self) -> str:
        return self._serialNumber
    
    @serialNumber.setter
    def serialNumber(self, value: str) -> None:
        self._serialNumber = value

    @property
    def controllerConnected(self) -> bool:
        return self._controllerConnected

    @controllerConnected.setter
    def controllerConnected(self, value: bool) -> None:
        self._controllerConnected = value

    @property
    def connectedDevice(self) -> str:
        return self._connectedDevice
    
    @connectedDevice.setter
    def connectedDevice(self, value: str) -> None:
        self._connectedDevice = value

    @property
    def nodeID(self) -> int:
        return self._nodeID
    
    @nodeID.setter
    def nodeID(self, value: int) -> None:
        self._nodeID = value

    @property
    def hardwareID(self) -> int:
        return self._hardwareID
    
    @hardwareID.setter
    def hardwareID(self, value: int) -> None:
        self._hardwareID = value

    def __calculateNodeID(self, serialNumber: str) -> int:
        """
        Find the Node ID of the connected controller
        @param serialNumber: str - Serial number of the connected controller
        @return: int - Node ID of the connected controller
        """
        partialMAC: list[str] = serialNumber.split(':')[-4:]
        return int(''.join(partialMAC), 16) + 1

    @staticmethod
    def listConnectedDevices() -> list[dict[str, str | int]] | None:
        """
        @return: list | None - list of all the Serial devices connected to the system in the form of a list of dictionaries or None if no devices are connected
        """
        serialDevices = list_ports.comports()
        if not serialDevices:
            return None
        devices: list[dict[str, str | int]] = []
        for device in serialDevices:
            devices.append(device.__dict__)
        return devices

    def __repr__(self) -> str:
        '''
        @return: str - String representation of the MagnetController object
        '''
        return f"MagnetController Object: {self.identifierType = }, {self.identifierString = }, {self.baudrate = }, {self.timeout = }, {self.waitTime = }, {self.controllerConnected = }, Port: {self.controllerPort}, Serial Number: {self.serialNumber}, Node ID: {self.nodeID}, Controller: {self.controller if self.controllerConnected else None}"

    def __connect(self) -> serial.Serial | None:
        '''
        Private method to connect to the controller based on the identifier type and string
        @return: serial.Serial | None - Serial object if controller connected, None otherwise
        '''

        def __connectDevice(device: list_ports_common.ListPortInfo) -> serial.Serial | None:
            '''
            Private method to connect to the found device
            @param device: list_ports_common.ListPortInfo - Device to connect to
            @return: serial.Serial | None - Serial object if controller connected, None otherwise
            '''
            controller: serial.Serial = serial.Serial(device.device, self.baudrate, timeout=self.timeout)
            time.sleep(self.waitTime)
            self.connectedDevice = device.device
            self.controllerConnected = True
            self.controllerPort = controller.port   # type: ignore
            self.serialNumber = device.serial_number    # type: ignore
            return controller
        
        def __connectDeviceFromList(device: list_ports_common.ListPortInfo) -> serial.Serial | None:
            '''
            Private method to check if device is in allowed list and connect to it
            @param device: list_ports_common.ListPortInfo - Device to check if allowed and connect to
            @return: serial.Serial | None - Serial object if controller connected, None otherwise
            '''
            try:
                nodeID: int = self.__calculateNodeID(device.serial_number)  # type: ignore
            except IndexError:
                print(f"Invalid Serial Number: {device.serial_number}")
                return None
            if nodeID in self._allowedDevices:
                self.nodeID = nodeID
                self.hardwareID = self._allowedDevices[nodeID]
                return __connectDevice(device)
            else:
                print(f"Device with {device.serial_number = }, {nodeID = } not allowed")
                return None

        serialDevices: list[list_ports_common.ListPortInfo] = list_ports.comports()
        if not serialDevices:
            print('No serial devices found')
            return None
        match self.identifierType:
            case DeviceIdentifierType.FROM_LIST:
                self._allowedDevices = AllowedDevicesNodeIDs
                for device in serialDevices:
                    # handle 'None' serial numbers; only allow potential MAC addresses
                    if device.serial_number and ':' in device.serial_number:
                        _returnedDevice: serial.Serial | None = __connectDeviceFromList(device)
                        if not _returnedDevice:
                            continue
                        return _returnedDevice
            case DeviceIdentifierType.AUTO_DETECT:
                if len(serialDevices) > 1:
                    print("Multiple serial devices found")
                    return None
                else:
                    return __connectDevice(serialDevices[0])
            # if specific device identifier is provided
            case DeviceIdentifierType.PORT:
                for device in serialDevices:
                    if device.device == self.identifierString:
                        return __connectDevice(device)
            case DeviceIdentifierType.SERIAL_NUMBER:
                for device in serialDevices:
                    if device.serial_number == self.identifierString:
                        return __connectDevice(device)
        return None
    
    def __initSuccess(self) -> None:
        '''
        Private method to print success message after initialization
        '''
        if self.controllerConnected:
            print(f"ESP Connected: {self.controllerConnected}, at port: {self.controllerPort}")
            print(f"Serial Number: {self.serialNumber}, Node ID: {self.nodeID}, Hardware ID: {self.hardwareID}")
        else:
            print("No suitable ESP found to connect to.")

    def push(self, command: str) -> None:
        '''
        Push a command to the ESP
        @param command: str - Command to send to the ESP
        '''
        if not self.controllerConnected:
            print("Controller not connected")
        self.controller.write(command.encode()) # type: ignore


    def pull(self) -> str:
        '''
        Pull data from the ESP
        @return: str - Data received from the ESP (Only one line at a time). Returns empty string if no data available
        '''
        if not self.controllerConnected:
            print("Controller not connected")
        if self.controller.in_waiting > 0:  # type: ignore
            return self.controller.readline().decode()  # type: ignore
        return ''


if __name__ == '__main__':
    # print(ESPController.listConnectedDevices())
    test = ESPController(identifierType=DeviceIdentifierType.FROM_LIST)
    # print(test)