import threading

from gx_communication.cobs import cobs
import logging
import serial
import serial.tools.list_ports
from gx_communication import constants
from gx_communication import gx_commands
from gx_communication import RD1055_format as rd
from utils import logger
import win32pipe
import win32file
import pywintypes

SERIAL_PORT = 0
SERIAL_PIPE = 1

class SerialCmd:

    def __init__(self, comport, serialType = SERIAL_PORT):
        self.baud_rate = 115200
        self.com_port = comport
        self.serialPort = None
        self.serial_type = serialType
        if self.serial_type == SERIAL_PORT:
            self.create_serial()
        else:
            self.serialPort = PipeSerial(comport)
            self.connect()



    def create_serial(self):
        try:
            self.serialPort = serial.Serial(
                port=self.com_port,
                baudrate=self.baud_rate,
                bytesize=8,
                stopbits=serial.STOPBITS_ONE)
            self.connect()
        except Exception as err:
            logger.error(f'COM Port {self.com_port} failed to created')
        else:
            logger.info(f'COM Port {self.com_port} created successfully')

    def auto_detect(self):
        comPorts = serial.tools.list_ports.comports()
        logging.info(f"Found {len(comPorts)} device(s)")
        for comPort in comPorts:
            if "FTDI" in comPort.manufacturer:
                logging.info("Ping port: {}".format(comPort.device))
                try:
                    self.serialPort = serial.Serial(
                        port=comPort.device,
                        baudrate=self.baudrate,
                        bytesize=8,
                        timeout=2,
                        stopbits=serial.STOPBITS_ONE)
                    self.connect()
                    whoAmI_cmd = gx_commands.WhoAmICmd()
                    resp = self.send_command(whoAmI_cmd)
                    if resp == constants.WHO_AM_I_RESP:
                        return
                    else:
                        logger.warning("Invalid response from device")
                except:
                    logger.warning("No response from device")
            else:
                logger.warning(f"Device connected at {comPort.device} is not "
                                "a FTDI")
        # BW
        # raise Exception("Unable to find a BSN Stimulator device")

    def connect(self):
        logging.info("connecting to device")
        if self.serialPort.isOpen():
            self.serialPort.close()
            self.serialPort.open()
        else:
            self.serialPort.open()
        return

    def send_command(self, cmd_in):
        logging.debug("Sending command...")
        if isinstance(cmd_in, gx_commands.Command):
            raw_bytes = cmd_in.serialize()
        else:
            raw_bytes = cmd_in
        protocol_4_added_cmd = rd.protocol_4_command(raw_bytes)
        logging.info(f"Tx: {protocol_4_added_cmd.hex()}")
        cobs_cmd = cobs.encode(protocol_4_added_cmd)
        cobs_cmd += b'\x00'
        logging.debug(f"Tx Cobs: {cobs_cmd.hex()}")
        # self.cmd = cobs_cmd
        self.serialPort.flushOutput()
        self.serialPort.write(cobs_cmd)
        response = self.get_response()
        logger.debug(f"Rx: {response.hex()}")
        return response

    def send_response(self, cmd_response):
        logging.info("Sending Response...")
        if isinstance(cmd_response, gx_commands.Response):
            raw_bytes = cmd_response.serialize()
        else:
            raw_bytes = cmd_response
        protocol_4_added_cmd = rd.protocol_4_command(raw_bytes)
        #logger.debug(f"Resp: {protocol_4_added_cmd.hex()}")
        cobs_resp = cobs.encode(protocol_4_added_cmd)
        cobs_resp += b'\x00'
        #logger.debug(f"Resp Cobs: {cobs_resp.hex()}")
        self.cmd = cobs_resp
        self.serialPort.flushOutput()
        self.serialPort.write(cobs_resp)

    # BW - same as above without logging, for stress test
    def send_command_no_log(self, cmd_in):
        # logging.info("Sending command...")
        if isinstance(cmd_in, gx_commands.Command):
            raw_bytes = cmd_in.serialize()
        else:
            raw_bytes = cmd_in
        protocol_4_added_cmd = rd.protocol_4_command(raw_bytes)
        # logging.info(f"Tx: {protocol_4_added_cmd.hex()}")
        cobs_cmd = cobs.encode(protocol_4_added_cmd)
        cobs_cmd += b'\x00'
        # logging.debug(f"Tx Cobs: {cobs_cmd.hex()}")
        self.cmd = cobs_cmd
        self.serialPort.flushOutput()
        self.serialPort.write(cobs_cmd)
        response = self.get_response()
        # logging.info(f"Rx: {response.hex()}")
        return response

    def get_response(self):
        # read until zero is received
        received_data = bytes()
        response = None
        while True:
            try:
                received_data += self.serialPort.read(1)
                if len(received_data) == 0:
                    break

                elif len(received_data) > 1 and received_data[-1] == 0:
                    response = cobs.decode(received_data[:-1])[:]
                    break
                elif len(received_data) == 1 and received_data[-1] == 0:
                    received_data = bytes()

            except serial.SerialException as err:
                logger.warn(f'terminated the serial port read- {err}')
                self.serialPort.flushInput()
                break
            except pywintypes.error as e:
                if e.args[0] == 109:  # ERROR_BROKEN_PIPE
                    logger.warn("Pipe connection broken.")
                else:
                    logger.warn("Error reading from pipe:", e)

        return response

    def get_command(self):
        return self.get_response()

    def disconnect(self):
        logging.info("disconnecting from device")
        self.serialPort.close()
        return True


class PipeSerial():
    def __init__(self,name):
        self.pipe_name = name
        self.pipe = None
        self.is_open = False
        self.thread_open = None
        self.event = threading.Event()

    def open(self):
        # Create the named pipe
        self.pipe = win32pipe.CreateNamedPipe(
            self.pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            0,
            None
        )
        # Connect to the named pipe
        self.thread_open = threading.Thread(target=self.connect_pipe)
        self.thread_open.start()

    def connect_pipe(self):
        self.event.clear()
        win32pipe.ConnectNamedPipe(self.pipe, None)
        print("Pipe connection established.")
        self.is_open = True
        self.event.set()

    def close(self):
        win32pipe.DisconnectNamedPipe(self.pipe)
        win32file.CloseHandle(self.pipe)
        self.is_open = False
        self.event.set()


    def isOpen(self):
        return self.is_open

    def read(self,byte_len):
        if self.is_open is False:
            self.event.wait()
        if self.is_open is False:
            return b''
        received_data = b''
        while True:
            result, data = win32file.ReadFile(self.pipe, 4096, None)
            if result == 0:
                received_data += data[:]
                break
            else:
                logger.error("The ReadFile result is not 0")
                break
        return received_data

    def write(self,bytes):
        win32file.WriteFile(self.pipe, bytes)

    def flushOutput(self):
        win32file.FlushFileBuffers(self.pipe)
