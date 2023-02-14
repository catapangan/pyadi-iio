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

from decimal import Decimal

import numpy as np
import adi

class cn0554():
    """ CN0554 Mixed Signal Raspberry Pi Hat """
    
    _out_reference_available = [4.096, 2.5]
    
    def __init__(self, uri=""):
        self._adc = adi.ad7124(uri=uri)
        
        self.inputs = []
        for ch_index, ch in enumerate(self._adc.channel):
            self.inputs.append(self.input_channel(ch.name, ch_index, self._adc))
        
        self._dac = adi.ltc2688(uri=uri)
        self.out_reference = self._out_reference_available[0]
        self.outputs = self._dac.channel
        
    @property
    def out_reference(self):
        return self._dac.vref
        
    @out_reference.setter
    def out_reference(self, value):
        if value in self._out_reference_available:
            self._dac.vref = value
        
    class input_channel():
        """CN0554 ADC Channels (AD7124-8)"""
        
        _in_range_available = ['+/-13.75', '+27.5', '+2.5']
        
        def __init__(self, ch_name, ch_index, adc):
            self.name = ch_name
            self.index = ch_index
            self._adc = adc
            self.settings = adc.channel[ch_index]
            self._in_range = self._in_range_available[0]
        
        @property
        def volt(self):
            in_voltage = self._adc.to_volts(self.index, self.settings.raw)
            if self._in_range == self._in_range_available[0]:
                return ((in_voltage - 1.25) * 11)
            elif self._in_range == self._in_range_available[1]:
                return (in_voltage * 11)
            elif self._in_range == self._in_range_available[2]:
                return in_voltage
            else:
                return None
        
        @property
        def in_range(self):
            return self._in_range
        
        @in_range.setter
        def in_range(self, value):
            if value in self._in_range_available:
                self._in_range = value