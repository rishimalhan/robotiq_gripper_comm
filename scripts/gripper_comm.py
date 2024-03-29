# Authored by Rishi Malhan, Center for Advanced Manufacturing, University of Southern California 
# Email: rmalhan@usc.edu
# Use Python 2

import serial
import binascii
import time

class GripperIO:
	def __init__(self,_port):
		self.sleep = 2
		self.comm_port = _port
		
		# for windows
		# self.ser = serial.Serial(port="COM"+str(self.comm_port), baudrate=115200, timeout=0.1,
		#                     parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		
		# for linux
		self.ser = serial.Serial(port="/dev/ttyUSB"+str(self.comm_port), baudrate=115200, timeout=0.1,
		                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		
		self.speed = 255	# Default Speed
		self.force = 255	# Default Force
	# Calculate CRC16 for Modbus
		self.table = (
		0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241, 0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
		0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40, 0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
		0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40, 0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
		0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641, 0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
		0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240, 0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
		0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41, 0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
		0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41, 0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
		0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640, 0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
		0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240, 0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
		0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41, 0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
		0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41, 0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
		0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640, 0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
		0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241, 0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
		0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40, 0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
		0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40, 0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
		0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641, 0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )

	def calcString( self, st, crc):
		"""Given a bunary string and starting CRC, Calc a final CRC-16 """
		for ch in st:
			crc = (crc >> 8) ^ self.table[(crc ^ ord(ch)) & 0xFF]
		return crc

	def calc_Crc(self, _req):
		init_modbus = 0xFFFF
		crc = self.calcString( _req, init_modbus )
		upd_crc = ("{:10X}".format(crc)).lstrip()
		return upd_crc

	def activate(self):
		self.ser.write("\x09\x10\x03\xE8\x00\x03\x06\x00\x00\x00\x00\x00\x00\x73\x30")
		self.ser.read(100)
		self.ser.write("\x09\x10\x03\xE8\x00\x03\x06\x01\x00\x00\x00\x00\x00\x72\xE1")
		self.ser.read(100)
		time.sleep(self.sleep)

	def set_speed(self, _speed):
		self.speed = _speed

	def set_force(self, _force):
		self.force = _force

	def go_to(self, _pos):
		self.pos = _pos
		if self.pos == 0:
			self.pos = 00
		self.a, self.b, self.c = ["","",""]
		if len(hex(self.pos)[2:]) == 1:
			self.a = "0"
		if len(hex(self.speed)[2:]) == 1:
			self.b = "0"
		if len(hex(self.force)[2:]) == 1:
			self.c = "0"
		self.req = "091003E8000306090000" + self.a + str(hex(self.pos)[2:]) + self.b + str(hex(self.speed)[2:]) + self.c + str(hex(self.force)[2:])
		self.res =  self.calc_Crc( self.req.decode("hex") )
		for i in range (0,4-len(self.res)):
			self.res = "0" + str(self.res) 
		self.req += str(self.res[2:]) + str(self.res[0:2])
		self.updt_req = self.req.decode("hex")
		self.ser.write( self.updt_req )
		self.ser.read(100)
		time.sleep(0.1)
		while self.is_reached() != bin( int("f9",16) )[2:]:
			pass

	def is_reached(self):
		self.req = "\x09\x03\x07\xD0\x00\x03\x04\x0E"
		self.ser.write( self.req )
		self.reply = binascii.hexlify( self.ser.read(100) )
		time.sleep(0.1)
		binary = bin( int(self.reply[6:8],16) )[2:]
		return binary

	def get_pos(self):
		self.req = "\x09\x03\x07\xD0\x00\x03\x04\x0E"
		self.ser.write( self.req )
		self.reply = binascii.hexlify( self.ser.read(100) )
		time.sleep(0.1)
		return int(self.reply[14:16],16)

	def get_gripper_status(self):
		self.req = "\x09\x03\x07\xD0\x00\x03\x04\x0E"
		self.ser.write( self.req )
		self.reply = binascii.hexlify( self.ser.read(100) )
		self.status = "Reading Gripper Status......" + "\n"
		time.sleep(0.1)
		binary = bin( int(self.reply[6:8],16) )[2:]
		binary = str(binary)
		for i in range(0,8-len(binary)):
			binary = "0" + binary
		init_status = binary[7]
		if init_status=="0":
			self.status += "Gripper Reset" + "\n"
		if init_status=="1":
			self.status += "Gripper Activated" + "\n"

		got_to_status = binary[4]
		if got_to_status=="0":
			self.status += "StandBy" + "\n"
		if got_to_status=="1":
			self.status += "Go To is active" + "\n"

		gripper_status = binary[2:4]
		if gripper_status=="00":
			self.status += "Gripper is in Reset State" + "\n"
		if gripper_status=="10":
			self.status += "Activation in Progress" + "\n"
		if gripper_status=="01":
			self.status += "Gripper is not in Use" + "\n"
		if gripper_status=="11":
			self.status += "Activation is completed" + "\n"

		obj_status = binary[0:2]
		if obj_status=="00":
			self.status += "Fingers are at standby" + "\n"
		if obj_status=="10":
			self.status += "Fingers have stopped due to a contact while opening" + "\n"
		if obj_status=="01":
			self.status += "Fingers have stopped due to a contact while closing" + "\n"
		if obj_status=="11":
			self.status += "Fingers are at requested Position" + "\n"

		# print self.status

	def get_fault_status(self):
		self.req = "\x09\x03\x07\xD0\x00\x03\x04\x0E"
		self.ser.write( self.req )
		self.reply = binascii.hexlify( self.ser.read(100) )
		self.status = "Reading Fault Status......" + "\n"
		time.sleep(0.1)
		fault = self.reply[10:12]
		if fault=="00":
			self.status += "No Fault" + "\n"
		if fault=="07" or fault=="05":
			self.status += "Priority Fault" + "\n"
		if fault=="0B" or fault=="09":
			self.status += "Minor Fault" + "\n"
		if fault=="0F" or fault=="0E":
			self.status += "Major Fault" + "\n"
		return self.status