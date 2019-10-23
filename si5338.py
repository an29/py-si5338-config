#!/usr/bin/python2.7

import sys
import smbus
import re
from time import sleep
import argparse

si5326_bus  = 1
si5326_addr = 0x70
si5326_i2c = smbus.SMBus(si5326_bus)

def rd_reg( addr ):
  value = 0
  try:
    value = si5326_i2c.read_byte_data(si5326_addr, addr )
  except IOError:
    return rd_reg( addr )
  return value


def wr_reg( addr, value ):
  try:
    si5326_i2c.write_byte_data(si5326_addr, addr, value )
  except IOError:
    return wr_reg( addr, value )


def set_page( pagenum ):
  wr_reg( 255, pagenum )

def set_mask( addr, setval, mask ):
  if mask == 0x0:
    return

  tx = setval

  if mask != 0xFF:
    rx = rd_reg( addr )
    tx = ( rx & ~mask ) | ( setval & mask )

  wr_reg( addr, tx )

def get_mask( addr, mask ):
  return rd_reg( addr ) & mask

def set_bit( addr, bitnum, value ):
  rx = rd_reg( addr )
  tx = ( rx & ~( 1 << bitnum ) ) | ( value << bitnum )
  wr_reg( addr, tx )


def before_write():
  set_bit( 230, 4, 1 )
  set_bit( 241, 7, 1 )

def continued_after_write():
  set_page( 0 )

  reg = rd_reg( 218 )
  while( reg & 0x4 ):
    reg = rd_reg( 218 )
    sleep( 0.5 )


  #Configure PLL for locking; reg49[7]; FCAL_OVRD_EN = 0
  set_bit( 49, 7, 0 )

  #Initiate locking of PLL; reg246[1]; SOFT_RESET = 1
  set_bit( 246, 1, 1 )

  sleep( 0.25 )

  #Restart LOL; reg241[7]; DIS_LOL = 0
  set_bit( 241, 7, 0 )

  reg = rd_reg( 218 )
  while( reg & 0x15 ):
    reg = rd_reg( 218 )
    sleep( 0.5 )


  reg = get_mask( 237, 0x03 )
  set_mask( 47, reg, 0x03 )

  reg = get_mask( 236, 0xff )
  set_mask( 46, reg, 0xff )

  reg = get_mask( 235, 0xff )
  set_mask( 45, reg, 0xff )

  set_mask( 47, 0x5 << 2, 0xfc )

  set_bit( 49, 7, 1 )
  set_bit( 230, 4, 0 )


def set_clk( reg_dump ):

  before_write()
  for command in reg_dump:
    addr = command[0]
    data = command[1]
    mask = command[2]

    set_mask( addr, data, mask )
  set_page( 0 )
  continued_after_write()

def parse_cfg( fn ):
  reg_dump = list()
  with open( fn, "r") as f:
    lines = f.readlines()
    for line in lines:
      line_s = line.split(',')
      reg_dump.append( [int(line_s[0]), int(line_s[1],16), int(line_s[2],16)] )
  return reg_dump

def parse_params():
  parser = argparse.ArgumentParser( description = "Si5338 configuration script" )
  parser.add_argument( "-b",   type=int, help="Si5338 I2C bus",       default = 0            )
  parser.add_argument( "-a",   type=int, help="Si5338 I2C address",   default = 0x70         )
  parser.add_argument( "-fn",  type=str, help="File name whith regs", default = "si5338.reg" )
  parser.add_argument( "-d",             help="Si5338 dump regs",     action = "store_true"  )
  return  parser.parse_args()



if __name__ == "__main__":
  args = parse_params()

  si5326_bus  = args.b
  si5326_addr = args.a
  si5326_i2c = smbus.SMBus(si5326_bus)

  if args.d:
    for i in range(0,256):
      print("%d: %4s" % ( i, hex( rd_reg(i) ) ) )
    return 0

  set_clk( parse_cfg(args.f) )
