#!/usr/bin/python

import os
import sys
import fileinput
import argparse

parser = argparse.ArgumentParser(description="This utility is to program multiple Afro ESCs with different I2C addresses on the SimonK firmware")

parser.add_argument("path", type=str, help="The device location for the Afro USB programmer")
group = parser.add_mutually_exclusive_group()
group.add_argument("-id", type=int, help="The PX4 motor ID (1-8)")
group.add_argument("-a", type=int, help="The general 7-bit I2C address")
parser.add_argument("-r", action="store_true", help="Reverse motor direction")
parser.add_argument("-b", action="store_true", help="Enable active braking")

args = parser.parse_args()
        
#****** Open the 'main.asm' file and the new ID one to write to****** 
mainfile = open("tgy.asm")
newfile = open("/tmp/tgy.asm","a")

#****** Decipher the user input ****** 
if args.id == None and args.a == None:
    I2C_ID8b = str(0x50)
    
    bit7addr = int(I2C_ID8b) >> 1
    print "DEFAULT: I2C 7 Bit General Address = " + str(bit7addr)
    
elif args.a != None: # We have a direct address
    if args.a < 8: # Have been given an odd ID, thus shall exit
        sys.exit("ERROR: I2C addresses below 8 are not allowed")
        
    I2C_ID8b = str(args.a << 1) 
    
    print "I2C 7 Bit General Address = " + str(args.a)
    
elif args.id != None: # We have a PX4 ID
    if args.id > 8: # Have been given an ID above 8, thus shall exit
        sys.exit("ERROR: ID Above 8")
        
    I2C_ID8b = str((args.id + 10) << 1) #Thus the addresses are the IDs + 10
    print "PX4 Motor ID = " + str(args.id)
    print "7 Bit I2C General Address = " + str(args.id + 10)
    
if args.r == True:
    reverse = 1
    print "Motor direction reversed"
else:
    reverse = 0
    
if args.b == True:
    braking = 1
    print "Active braking enabled"
else:
    braking = 0
    
#****** Find ID definition in code and replace the ID with the new ID ****** 
while 1:
  line = mainfile.readline()
  if not line: break
  line = line.replace(".equ I2C_ADDR =",".equ I2C_ADDR = " + I2C_ID8b + ';')
  line = line.replace(".equ	COMP_PWM	=",".equ	COMP_PWM = " + str(braking) + ';')
  line = line.replace(".equ	MOTOR_REVERSE	=",".equ	MOTOR_REVERSE = " + str(reverse) + ';')
  newfile.write(line)
  
newfile.close()

#****** Compile and Program ****** 
os.system('cd /tmp && avra tgy.asm')

os.system('avrdude -p m8 -P ' + args.path + ' -c avrispv2 -b 9600 -e -U flash:w:/tmp/tgy.hex:i') # The AVRISP with a baud rate of 9600 has the same ISP settings as the AfroUSB programmer, as verifid by KK-Coptertool

