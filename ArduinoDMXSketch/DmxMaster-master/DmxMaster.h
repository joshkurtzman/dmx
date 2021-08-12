/**
* DmxMaster - A simple interface to DMX.
*
* Copyright (c) 2008-2009 Peter Knight, Tinker.it! All rights reserved.
*/

#ifndef DmxMaster_h
#define DmxMaster_h

#include <inttypes.h>

#if RAMEND <= 0x4FF
#define DMX_SIZE 128
#else
#define DMX_SIZE 512
#endif

class DmxMasterClass
{
  public:
    void maxChannel(int);
    void write(int, uint8_t);
    void usePin(uint8_t);
	uint8_t modulate(int, int);     // increase/decrease current channel value by given amount (clipped to interval [0..255])
    uint8_t getValue(int);
};
extern DmxMasterClass DmxMaster;

#endif