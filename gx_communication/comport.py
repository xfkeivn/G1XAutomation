from cobs import cobs
import logging
import serial
import serial.tools.list_ports
from gx_communication import constants
from gx_communication import gx_commands
from gx_communication import RD1055_format as rd
logger = logging.getLogger("GX1")

class SerialCmd:

    def __init__(self, comport):
        self.baud_rate = 115200
        self.com_port = comport
        self.serialPort = None
        self.create_serial()


    def create_serial(self):
        try:
            self.serialPort = serial.Serial(
                port=self.com_port,
                baudrate=self.baud_rate,
                bytesize=8,
                stopbits=serial.STOPBITS_ONE)
            self.connect()
        except:
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
        logger.debug(f"Resp: {protocol_4_added_cmd.hex()}")
        cobs_resp = cobs.encode(protocol_4_added_cmd)
        cobs_resp += b'\x00'
        logger.debug(f"Resp Cobs: {cobs_resp.hex()}")
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
                logger.warning(f'terminated the serial port read- {err}')
                self.serialPort.flushInput()
                break

        return response

    def get_command(self):
        return self.get_response()

    def disconnect(self):
        logging.info("disconnecting from device")
        self.serialPort.close()
        return True
