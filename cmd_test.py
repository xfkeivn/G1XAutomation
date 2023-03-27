from gx_communication import comport as comp
from gx_communication import gx_commands as commands
import random
import logging
import time
import datetime

logging.basicConfig(level=logging.INFO)

com_handle = comp.SerialCmd()

#==== Debug errors ======
def process_error(resp):
    err_code = (resp[7] * 0xFF) + resp[6]
    if err_code == 0:
        err_name = "No error"
    elif err_code == 0x02:
        err_name = "Invalid CRC"
    elif err_code == 0x06:
        err_name = "Unknown Cmd or bad option type"
    elif err_code == 0x0D:
        err_name = "UnsupportedParameter"
    elif err_code == 0x0F:
        err_name = "ParmOutOfRange"
    elif err_code == 0x81:
        err_name = "Cmd Failed"
    else:
        err_name = "<look up code in CmdErr.hpp>"

    print(f"Error Code {hex(err_code)}: {err_name}")
#=======================

req = "init"
while req != 'q':
    req = input("Request (h=help, q=quit): ")

    #=== Help screen ====
    if req == "h" or req == "help":
        print (" 'com'       open/check com port")
        print (" 'who'       device identification")
        print (" 'set_e'     set electrodes")
        print (" 'get_e'     get electrodes")
        print (" 'block'     block channels")
        print (" 'set_stim'  set Stim settings")
        print (" 'set_trf'   set Thermal RF settings")
        print (" 'set_prf'   set Pulsed RF settings")
        print (" 'start'     start therapy")
        print (" 'stop'      stop therapy")
        #print (" 'adj_v'     adjust voltage (WIP)")
        #print (" 'adj_c'     adjust current (WIP)")
        print (" 'meas'      get measured channel (WIP)")
        print ("  Need UNIT_TEST defined for these:")
        print ("   'echo'      echo back the input bytes")
        print ("   'stress1'   send a 1-byte Echo cmd repeatedly")
        print ("   'stress2'   send a random-length Echo cmd repeatedly")

    elif req == "com":
        if com_handle.serialPort.isOpen():
            print(f" {com_handle.serialPort.portstr} Connected")
        else:
            print (" COM Port FAIL")

    elif req == "who":
        cmd = commands.WhoAmICmd()
        resp = com_handle.send_command(cmd)
        devID = resp[8]
        print(f" Device ID = {devID} ({hex(devID)})")
        process_error(resp)

    elif req == "set_e":
        print(" Enter electrode pairs as 'Source,Ref'.  Use ',' or space for separators ")
        print("   Enter 'M' for nominal Monopolar config:  1,0, 2,0, 3,0, 4,0  ")
        print("   Enter 'B' for nominal Bipolar config:  1,2  4,3 ")
        print("   Enter 'U' for nominal Unipolar config:  1 1, 2 2, 3 3, 4 4 ")
        electrodes = input(" -->")
        if electrodes == "M" or electrodes == "m":
            electrodes = "1,0 2,0 3,0 4,0"
        elif electrodes == "B" or electrodes == "b":
            electrodes = "1,2 4,3"
        elif electrodes == "U" or electrodes == "u":
            electrodes = "1 1, 2 2, 3 3, 4 4"
        
        e_str = electrodes.replace(",", " ")
        #print(e_str)
        e_list = e_str.split()
        #print(len(e_list))

        #convert each item in list to an int and verify its value
        for i in range(len(e_list)):
            try:
                e_list[i] = int(e_list[i])
                if e_list[i] < 0 or e_list[i] > 4:
                    print(" Out of range") #can still send this for testing
            except:
                print(" Bad format") # bail out
                continue
        cmd = commands.SetElectrodeSettingCmd()
        cmd.u8_ElectrodePairCount = len(e_list)
        if cmd.u8_ElectrodePairCount > 8:
            print("Too many electrodes")
        else: 
            cmd.u8_ElectrodePairCount = int(cmd.u8_ElectrodePairCount / 2)

        for i in range(len(e_list)):
            cmd.au8_Electrodes.insert(i, e_list[i])
        resp = com_handle.send_command(cmd)
        print(f" Set Electrodes: count = {cmd.u8_ElectrodePairCount}, data = {e_list}")
        print(f" Set Electrodes complete, resp = {resp}")
        process_error(resp)

    elif req == "get_e":
        cmd = commands.GetElectrodesCmd()
        resp = com_handle.send_command(cmd)
        print(f" Get Electrodes resp = {resp}")
        process_error(resp)
        offset_count = 8
        offset_elecs = 9
        num_pairs = resp[offset_count]
        print(f"{num_pairs} Electrode Configs:")
        for i in range(num_pairs):
            print(f"  Config {i} : {resp[offset_elecs+(2*i)]}, {resp[offset_elecs+(2*i)+1]}")

    elif req == "set_stim":
        cmd = commands.SetStimulationSettingCmd()
        print(" Enter Stim Setup:")
        print("   Enter '1' for Min values: VoltageControl, Sensory, Rate 0 (One-shot), Width 1 (0.1ms), ")
        print("             Amplitude 0 (AutoRamp Off), RampSpeed 0, MaxV 1 (0.1mV), MaxCurrent 1 (0.1mA)")
        print("   Enter '2' for Max values: CurrentControl, Motor, Rate 200, Width 30, ")
        print("             Amplitude 100 (10mA), RampSpeed 3, MaxV 50, MaxCurrent 100")
        print("   Enter '3' for custom settings")
        stim_input = input(" -->")
        if stim_input == "1":
            cmd.u8_ControlSetting = 1
            cmd.u8_SensoryMotor = 0
            cmd.u8_Rate = 0
            cmd.u8_Width = 1
            cmd.u8_Amplitude = 0
            cmd.u8_RampSpeed = 0
            cmd.u8_MaxVoltage = 1
            cmd.u8_MaxCurrent = 1
        elif stim_input == "2":
            cmd.u8_ControlSetting = 0
            cmd.u8_SensoryMotor = 1
            cmd.u8_Rate = 200
            cmd.u8_Width = 30
            cmd.u8_Amplitude = 100
            cmd.u8_RampSpeed = 3
            cmd.u8_MaxVoltage = 50
            cmd.u8_MaxCurrent = 100
        elif stim_input == "3":
            cmd.u8_ControlSetting = int(input("  Enter Voltage(0) or Current(1) control: "))
            cmd.u8_SensoryMotor = int(input("  Enter Sensory(0) or Motor(1):  "))
            cmd.u8_Rate = int(input("  Enter Rate (0-200): "))
            cmd.u8_Width = int(input("  Width (1-30): "))
            cmd.u8_Amplitude = int(input("  Enter Amplitude: 0-50 (in 0.1mV) or 0-100 (in 0.1mA): "))
            cmd.u8_RampSpeed = int(input("  Enter Ramp Speed (0-3): "))
            cmd.u8_MaxVoltage = int(input("  Enter Max Voltage (1-50) in 0.1V: "))
            cmd.u8_MaxCurrent = int(input("  Enter Max Current (1-100) in 0.1mA: "))
        else:
            print(" ** Bad input")
            continue
        resp = com_handle.send_command(cmd)
        print(f" Set Stim complete, resp = {resp.hex()}")
        process_error(resp)

    elif req == "block":
        print(" Enter channel #s to block.  Use ',' or space for separators ")
        chans = input(" -->")
        chan_str = chans.replace(",", " ")
        print(chan_str)
        chan_list = chan_str.split()
        #convert each item in list to an int and verify its value
        for i in range(len(chan_list)):
            try:
                chan_list[i] = int(chan_list[i])
                if chan_list[i] < 0 or chan_list[i] > 4:
                    print(" Out of range") #can still send this for testing
            except:
                print(" Bad format") # bail out
                continue
        
        cmd = commands.BlockChannelCmd()
        cmd.u8_BlockCount = len(chan_list) 
        if cmd.u8_BlockCount > 4:
            print("Too many channels")
        for i in range(cmd.u8_BlockCount):
            cmd.au8_BlockedChannels.insert(i, chan_list[i])
        resp = com_handle.send_command(cmd)
        print(f" Blocked: count = {cmd.u8_BlockCount}, data = {chan_list}")
        print(f" Block Channel complete, resp = {resp}")
        process_error(resp)

    elif req == "set_prf":
        cmd = commands.SetPulsedRFSettingCmd()
        print(" Enter 1 for MINIMUM values or 2 for MAX values:  ")
        prf_input = int(input(" Enter 1 or 2: "))
        if prf_input < 1 or prf_input > 2:
            print(" Bad value") 
            continue
        elif prf_input == 1: # minimum values
            cmd.u8_PRFMode = 0
            cmd.u8_AutoRamp = 0
            cmd.u16_SetTime = 5
            cmd.u8_MaxTemp = 0
            cmd.u8_PulseRate = 0
            cmd.u16_StaggerStartTime = 0
            cmd.u16_Voltage = 5
            cmd.u16_PulseWidth = 2
            cmd.u16_ElectrodePower = 1
        else:  # max values
            cmd.u8_PRFMode = 1
            cmd.u8_AutoRamp = 1
            cmd.u16_SetTime = 0xFFFF
            cmd.u8_MaxTemp = 0xFF
            cmd.u8_PulseRate = 10
            cmd.u16_StaggerStartTime = 0xFFFF
            cmd.u16_Voltage = 100
            cmd.u16_PulseWidth = 50
            cmd.u16_ElectrodePower = 100
        resp = com_handle.send_command(cmd)
        print(f" Set PRF complete, resp = {resp.hex()}")
        process_error(resp) 


    elif req == "set_trf":
        cmd = commands.SetThermalRFSettingCmd()
        print(" Enter 1 for: Mode Std(0), AutoRamp 0, Time 5, Temp 37, Stagger 0, Power 1, Ramp 1")
        print("             StepTime 5, FinalTime 5, StartTemp 37, StepTemp 1, FinalTemp 37, Voltage 5")
        print(" Enter 2 for: Mode Voltage(2), AutoRamp 1, Time 1800, Temp 90, Stagger 999, Power 500, Ramp 50")
        print("             StepTime 1800, FinalTime 1800, StartTemp 90, StepTemp 53, FinalTemp 90, Voltage 25")
        trf_input = int(input(" Enter 1 or 2: "))   
        if trf_input == 1:
            cmd.u8_TRFMode = 0x00
            cmd.u8_AutoRamp = 0x00
            cmd.u16_SetTime = 5
            cmd.u8_SetTemp = 37
            cmd.u16_StaggerStartTime = 0
            cmd.u16_ElectrodePower = 1
            cmd.u8_RampRate = 1
            cmd.u16_StepTime = 5
            cmd.u16_FinalTime = 5
            cmd.u8_StartTemp = 37
            cmd.u8_StepTempInc = 1
            cmd.u8_FinalTemp = 37
            cmd.u8_SetVoltage = 5
        elif trf_input == 2:
            cmd.u8_TRFMode = 0x02
            cmd.u8_AutoRamp = 0x01
            cmd.u16_SetTime = 1800
            cmd.u8_SetTemp = 90
            cmd.u16_StaggerStartTime = 999
            cmd.u16_ElectrodePower = 500
            cmd.u8_RampRate = 50
            cmd.u16_StepTime = 1800
            cmd.u16_FinalTime = 1800
            cmd.u8_StartTemp = 90
            cmd.u8_StepTempInc = 53
            cmd.u8_FinalTemp = 90
            cmd.u8_SetVoltage = 25 
        else:
            print(" Bad value")
            continue
        resp = com_handle.send_command(cmd)
        print(f" Set TRF complete, resp = {resp.hex()}")
        process_error(resp) 


    elif req == "adj_v":
        deltaV = int(input(" Enter amount (pos or neg) in 10mV counts: "))
        if deltaV < -3276 or deltaV > 3276:
            print(" entered value is out of range") 
        else:
            cmd = commands.AdjustVoltageCmd()
            cmd.i16_DeltaVoltage = deltaV
            resp = com_handle.send_command(cmd)
            print(f" Adjust Voltage, resp = {resp.hex()}")
            process_error(resp)  

    elif req == "adj_c":
        deltaC = int(input(" Enter amount (pos or neg) in 100mA counts: "))
        if deltaC >= -327 and deltaC <= 327:
            print(" entered value is out of range") 
        else:
            cmd = commands.AdjustCurrentCmd()
            cmd.i16_DeltaCurrent = deltaC
            resp = com_handle.send_command(cmd)
            print(f" Adjust Current, resp = {resp.hex()}")
            process_error(resp)
               
    elif req == "start":
        cmd = commands.CtrlStartCmd()
        resp = com_handle.send_command(cmd)
        process_error(resp)

    elif req == "stop":
        cmd = commands.CtrlStopCmd()
        resp = com_handle.send_command(cmd)
        process_error(resp)

    elif req == "meas":
        channel = int(input(" Enter channel #: "))
        if channel < 1 or channel > 4:
           print(" enter Channel between 1-4")  
        else:
            cmd = commands.GetMeasuredChannelCmd()
            cmd.u8_Channel = channel
            resp = com_handle.send_command(cmd)
            print(f" Get Electrodes resp = {resp}")
            process_error(resp)
            print(f"  Source Electode: {resp[8]}")
            print(f"  Ref Electode: {resp[9]}")
            print(f"  Blocked: {resp[10]}")
            print(f"  Imped Avail: {resp[11]}")
            print(f"  Impedance: {resp[12] + resp[13]*0xFF}")
            print(f"  Source Temp Avail: {resp[14]}")
            print(f"  Source Temp: {resp[15] + resp[16]*0xFF}")
            print(f"  Ref Temp Avail: {resp[17]}")
            print(f"  Ref Temp: {resp[18] + resp[19]*0xFF}")
            print(f"  Timer:   {resp[20] + resp[21]*0xFF}")
            print(f"  Elec Summ Avail: {resp[22]}")
            print(f"  Current: {resp[23] + resp[24]*0xFF}")
            print(f"  Voltage: {resp[25] + resp[26]*0xFF}")
            print(f"  Power: {resp[27] + resp[28]*0xFF}")
            print(f"  Width: {resp[29] + resp[30]*0xFF}")
            
    elif req == "read":
        cmd = commands.GetCPLDRegCmd()
        cmd.u16_Address = int(input(" Starting address (in hex): "), 16)
        cmd.u16_NumberOfRegisters = int(input(" Number of registers: "))            
        resp = com_handle.send_command(cmd)
        for i_reg in range(0, cmd.u16_NumberOfRegisters, 1):
            print (f" reg addr[{hex(cmd.u16_Address + (i_reg))}]:", end=" ")
            for i_byte in range(0, 4, 1):  # 4 bytes per register 
                resp_offset = 12 + (i_reg*4) + i_byte
                print (hex(resp[resp_offset]), end=" ")   # return values start at resp[12]
            print(" ") # each 32-bit register has its own line

    elif req == "echo":
        echo_input = input(" Enter echo bytes XX XX XX... --> ")
        echo_list= echo_input.split()
        echo_in = list(map(int, echo_list))
        cmd = commands.UT_EchoCmd()
        cmd.u16_NumberOfBytes = len(echo_in)
        for idx in range(0, len(echo_in), 1):
            cmd.au8_Data.insert(idx, echo_in[idx])
        try:
            resp = com_handle.send_command_no_log(cmd)
            rstr = f"{resp.hex()}"
            resp_str= rstr[12:16] +" "+ rstr[24:]
            print (resp_str)
        except:
            print ("command failed - is UNIT_TEST defined?")
            break

    elif req == "stress":
        print ("Enter stress1 or stress2")

    elif req == "stress1" or req == "stress2":
        num_cycles = int(input(" Enter number of Echo cycles: "))
        start_time = time.time() # in seconds since epoch

        cycle_count = 1
        while cycle_count <= num_cycles:
            cmd = commands.UT_EchoCmd()
            if req == "stress1":
                cmd.u16_NumberOfBytes = 1
                data_value = 0xAA
            else:
                # Stress2 uses a random-sized payload
                cmd.u16_NumberOfBytes = random.randint(1, cmd.MAX_CMD_SIZE)
                data_value = cmd.u16_NumberOfBytes #  use the random number as payload

            for x in range(cmd.u16_NumberOfBytes):
                cmd.au8_Data.insert(x, data_value)
            try:
                resp = com_handle.send_command_no_log(cmd)
            except:
                print (" *** Command Failed ***")
                break  
            # I don't think the response CRC is checked. Need to confirm.
            # So check accuracy of response here.
            for y in range(cmd.u16_NumberOfBytes):
                if resp[12+y] != data_value:
                    print(" *** Mismatched Response Data ***")
                    break
            if cycle_count % 1000 == 0:
                print (int(cycle_count / 1000), end="k ",) 
            elif cycle_count == num_cycles:
                print (cycle_count) 
            cycle_count = cycle_count+1
        print ("done")
        end_time = time.time()
        duration_formatted = str(datetime.timedelta(seconds=int((end_time-start_time))))
        print(f" {cycle_count} commands; duration = {duration_formatted} (h:m:s)")


    elif req == "q":
        exit

    else:
        print(" ** Bad Input **")