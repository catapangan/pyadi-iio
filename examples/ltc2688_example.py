# Copyright (C) 2019 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time

import adi

testRaw = 65535  # Test raw DAC code

try:
    myDAC = adi.ltc2688(uri="local:")

    for ch in myDAC._ctrl.channels:
        name = ch.id
        if "toggle_en" in ch.attrs:
            if "symbol" in ch.attrs:
                print("Channel: " + name + " function: " + "sw toggle")
            else:
                print("Channel: " + name + " function: " + "hw toggle")
        elif "dither_en" in ch.attrs:
            print("Channel: " + name + " function: " + "dither")
        else:
            print("Channel: " + name + " function: " + "standard")

except Exception as e:
    print(str(e))
    print("Failed to open LTC2688 device")
    sys.exit(0)

try:
    for ch in range(0, 8):
        if hasattr(myDAC.channel[(ch * 2)], "raw"):
            myDAC.channel[(ch * 2)].raw = 0
            print(
                "Channel: "
                + str(myDAC.channel[(ch * 2)].name)
                + " set to: "
                + str(myDAC.channel[(ch * 2)].raw)
            )

        elif hasattr(myDAC.channel[(ch * 2)], "raw0"):
            myDAC.channel[(ch * 2)].raw0 = 0
            print(
                "Channel: "
                + str(myDAC.channel[(ch * 2)].name)
                + " set to: "
                + str(myDAC.channel[(ch * 2)].raw0)
            )

        if hasattr(myDAC.channel[(ch * 2 + 1)], "raw"):
            myDAC.channel[(ch * 2) + 1].raw = testRaw
            print(
                "Channel: "
                + str(myDAC.channel[(ch * 2) + 1].name)
                + " set to: "
                + str(myDAC.channel[(ch * 2) + 1].raw)
            )

        elif hasattr(myDAC.channel[(ch * 2 + 1)], "raw0"):
            myDAC.channel[(ch * 2) + 1].raw0 = testRaw
            print(
                "Channel: "
                + str(myDAC.channel[(ch * 2) + 1].name)
                + " set to: "
                + str(myDAC.channel[(ch * 2) + 1].raw0)
            )
        time.sleep(0.05)

except Exception as e:
    print(str(e))
    print("Failed to write to LTC2688 DAC")
    sys.exit(0)
