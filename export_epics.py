from mps_config import MPSConfig, models
from sqlalchemy import func
import sys
import argparse

#
# Sample Device Input (i.e. Digital Channel) record:
#
# record(bi, "CentralNode:DIGIN0") {
#     field(DESC, "Test input")
#     field(DTYP, "asynInt32")
#     field(SCAN, "1 second")
#     field(ZNAM, "OK")
#     field(ONAM, "FAULTED")
#     field(INP, "@asyn(CENTRAL_NODE 0 3)DIGITAL_CHANNEL")
#}

def printRecord(file, recType, recName, fields):
  file.write("record({0}, \"{1}\") {{\n".format(recType, recName))
  for name, value in fields:
    file.write("  field({0}, \"{1}\")\n".format(name, value))
  file.write("}\n\n")

#
# Create one bi record for each device input (digital device)
# Also creates:
#  ${DEV}_LATCHED
#  ${DEV}_BYPV (bypass value)
#  ${DEV}_BYPS (bypass status)
#  ${DEV}_BYPEXP (bypass expiration date?)
#
def exportDeviceInputs(file, deviceInputs):
  for deviceInput in deviceInputs:
    fields=[]
    fields.append(('DESC', 'Crate[{0}], Card[{1}], Channel[{2}]'.
                   format(deviceInput.channel.card.crate.number,
                          deviceInput.channel.card.number,
                          deviceInput.channel.number)))
    fields.append(('DTYP', 'asynUInt32Digital'))
    fields.append(('SCAN', '1 second'))
    fields.append(('ZNAM', '{0}'.format(deviceInput.channel.z_name)))
    fields.append(('ONAM', '{0}'.format(deviceInput.channel.o_name)))
    fields.append(('INP', '@asynMask(CENTRAL_NODE {0} 1 0)DEVICE_INPUT'.format(deviceInput.id)))
    printRecord(file, 'bi', '$(BASE):{0}'.format(deviceInput.channel.name), fields)

    fields[0]=(('DESC', 'Crate[{0}], Card[{1}], Channel[{2}] Latched'.
                format(deviceInput.channel.card.crate.number,
                       deviceInput.channel.card.number,
                       deviceInput.channel.number)))
    fields[5]=(('INP', '@asynMask(CENTRAL_NODE {0} 1 0)DEVICE_INPUT_LATCHED'.format(deviceInput.id)))
    printRecord(file, 'bi', '$(BASE):{0}_LATCHED'.format(deviceInput.channel.name), fields)

  file.close()

#
# Create one bi record for each device state for each analog device
#
# For example, the BPMs have threshold bits for X, Y and TMIT. Each
# one of them has a bit mask to identify the fault. The mask
# is passed to asyn as the third parameter within the 
# '@asynMask(PORT ADDR MASK TIMEOUT)' INP record field
#
def exportAnalogDevices(file, analogDevices):
  for analogDevice in analogDevices:
    for state in analogDevice.device_type.states:
      fields=[]
      fields.append(('DESC', 'Crate[{0}], Card[{1}], Channel[{2}]'.
                     format(analogDevice.channel.card.crate.number,
                            analogDevice.channel.card.number,
                            analogDevice.channel.number)))
      fields.append(('DTYP', 'asynUInt32Digital'))
      fields.append(('SCAN', '1 second'))
      fields.append(('ZNAM', 'IS_EXCEEDED'))
      fields.append(('ONAM', 'IS_OK'))
      fields.append(('INP', '@asynMask(CENTRAL_NODE {0} {1} 0)ANALOG_DEVICE'.format(analogDevice.id, state.value)))
      printRecord(file, 'bi', '$(BASE):{0}_{1}'.format(analogDevice.channel.name, state.name), fields)
    
  file.close()

def exportMitiagationDevices(file, mitigationDevices, beamClasses):
  fields=[]
  fields.append(('DESC', 'Number of beam classes'))
  fields.append(('PINI', 'YES'))
  fields.append(('VAL', '{0}'.format((len(beamClasses)))))
  printRecord(file, 'ao', '$(BASE):NUM_BEAM_CLASSES', fields)

  for beamClass in beamClasses:
    fields=[]
    fields.append(('DESC', '{0}'.format(beamClass.description)))
    fields.append(('PINI', 'YES'))
    fields.append(('VAL', '{0}'.format(beamClass.number)))
    printRecord(file, 'ao', '$(BASE):BEAM_CLASS_{0}'.format(beamClass.number), fields)

  for mitigationDevice in mitigationDevices:
    fields=[]
    fields.append(('DESC', 'Mitigation Device: {0}'.format(mitigationDevice.name)))
    fields.append(('DTYP', 'asynInt32'))
    fields.append(('SCAN', '1 second'))
    fields.append(('INP', '@asyn(CENTRAL_NODE {0} 0)MITIGATION_DEVICE'.format(mitigationDevice.id)))
    printRecord(file, 'ai', '$(BASE):{0}_ALLOWED_CLASS'.format(mitigationDevice.name.upper()), fields)
    

  file.close()

def exportFaults(file, faults):
  for fault in faults:
    fields=[]
    fields.append(('DESC', '{0}'.format(fault.description)))
    fields.append(('DTYP', 'asynUInt32Digital'))
    fields.append(('SCAN', '1 second'))
    fields.append(('ZNAM', 'OK'))
    fields.append(('ONAM', 'FAULTED'))
    fields.append(('INP', '@asynMask(CENTRAL_NODE {0} 1 0)FAULT'.format(fault.id)))
    printRecord(file, 'bi', '$(BASE):{0}'.format(fault.name), fields)

  file.close()

#=== MAIN ==================================================================================

parser = argparse.ArgumentParser(description='Export EPICS template database')
parser.add_argument('database', metavar='db', type=file, nargs=1, 
                    help='database file name (e.g. mps_gun.db)')
parser.add_argument('--device-inputs', metavar='file', type=argparse.FileType('w'), nargs='?',
                    help='epics template file name for digital channels (e.g. device-inputs.template)')
parser.add_argument('--analog-devices', metavar='file', type=argparse.FileType('w'), nargs='?', 
                    help='epics template file name for analog channels (e.g. analog-devices.template)')
parser.add_argument('--mitigation-devices', metavar='file', type=argparse.FileType('w'), nargs='?', 
                    help='epics template file name for mitigation devices and beam classes (e.g. mitigation.template)')
parser.add_argument('--faults', metavar='file', type=argparse.FileType('w'), nargs='?', 
                    help='epics template file name for faults (e.g. faults.template)')

args = parser.parse_args()

mps = MPSConfig(args.database[0].name)
session = mps.session

if (args.device_inputs):
  exportDeviceInputs(args.device_inputs, session.query(models.DeviceInput).all())

if (args.analog_devices):
  exportAnalogDevices(args.analog_devices, session.query(models.AnalogDevice).all())

if (args.mitigation_devices):
  exportMitiagationDevices(args.mitigation_devices,
                           session.query(models.MitigationDevice).all(),
                           session.query(models.BeamClass).all())

if (args.faults):
  exportFaults(args.faults, session.query(models.Fault).all())

session.close()

