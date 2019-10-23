# py-si5338-config

##Synopsys
  [Si5338](https://www.silabs.com/documents/public/data-sheets/Si5338.pdf) clock generator configuration utility.

##Requirements

  * Python2.7
  * python-smbus

##How to use

1. Generate C-header file using [Clock Software Development Tools](https://www.silabs.com/products/development-tools/software/clock).
2. Remove comments, parentheses and declaration. The settings file should look like this (addr,value,mask,):
```
 1,0x00,0x1F,
 2,0x00,0x1F,
 3,0x84,0xFF,
 4,0x0C,0x7F,
 5,0x23,0x3F,
```
3. Start application:
```
./si5338.py -b 1 -a 112 -fn dump.reg
```
