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
from adi.attribute import attribute
from adi.context_manager import context_manager


class ltc2688(context_manager, attribute):
    """ LTC2688 DAC """

    _complex_data = False
    channel = []
    _device_name = "LTC2688"

    def __init__(self, uri="", device_index=0):
        context_manager.__init__(self, uri, self._device_name)
        
        self._ctrl = self._ctx.find_device("ltc2688")

        for ch in self._ctrl.channels:
            name = ch.id
            if "toggle_en" in ch.attrs:
                if "symbol" in ch.attrs:
                    self.channel.append(self._channel_sw_toggle(self._ctrl, name))
                else:
                    self.channel.append(self._channel_toggle(self._ctrl, name))
            elif "dither_en" in ch.attrs:
                self.channel.append(self._channel_dither(self._ctrl, name))
            else:
                self.channel.append(self._channel_standard(self._ctrl, name))

        self.channel.sort(key=lambda x: int(x.name[7:]))

    class _channel_base(attribute):
        """ LTC2688 base channel class """

        # Default reference voltage
        vref = 4.096

        def __init__(self, ctrl, channel_name):
            self.name = channel_name
            self._ctrl = ctrl

        @property
        def scale(self):
            """ Get LTC2688 channel span scale """
            return self._get_iio_attr(self.name, "scale", True, self._ctrl)

        @property
        def offset(self):
            """ Get LTC2688 channel offset """
            return self._get_iio_attr(self.name, "offset", True, self._ctrl)

        @property
        def calibbias(self):
            """ Get LTC2688 calibration bias """
            return self._get_iio_attr(self.name, "calibbias", True, self._ctrl)

        @property
        def calibscale(self):
            """ Get LTC2688 calibration scale """
            return self._get_iio_attr(self.name, "calibscale", True, self._ctrl)

        @property
        def powerdown(self):
            """ Get LTC2688 channel powerdown setting """
            return self._get_iio_attr_str(self.name, "powerdown", True)

        @powerdown.setter
        def powerdown(self, val):
            """ Set LTC2688 channel powerdown """
            self._set_iio_attr_str(self.name, "powerdown", True, val)

    class _channel_standard(_channel_base):
        """ LTC2688 standard output channel """
        def __init__(self, ctrl, channel_name):
            super().__init__(ctrl, channel_name)

        @property
        def raw(self):
            """ Get LTC2688 channel 16-bit raw output code """
            return self._get_iio_attr(self.name, "raw", True, self._ctrl)

        @raw.setter
        def raw(self, val):
            """ Set LTC2688 channel 16-bit raw output code """
            raw_span = self._get_iio_attr(self.name, "raw_available", True, self._ctrl)
            if val >= raw_span[0] and val <= raw_span[2] and val % raw_span[1] == 0:
                self._set_iio_attr(self.name, "raw", True, str(int(val)))

        @property
        def volt(self):
            """ Get LTC2688 computed channel output voltage """
            return ((self.raw + self.offset) * self.scale) * (self.vref / 4.096)

        @volt.setter
        def volt(self, val):
            """ Set LTC2688 channel output voltage """
            self.raw = ((val / self.scale) - self.offset) * (self.vref / 4.096)

    class _channel_dither(_channel_standard):
        """ LTC2688 dither channel """
        def __init__(self, ctrl, channel_name):
            super().__init__(ctrl, channel_name)

        @property
        def dither_en(self):
            """ Get LTC2688 channel dither setting """
            return self._get_iio_attr(self.name, "dither_en", True, self._ctrl)

        @dither_en.setter
        def dither_en(self, val):
            """ Set LTC2688 channel dither """
            self._set_iio_attr(self.name, "dither_en", True, val)

        @property
        def dither_frequency(self):
            """ Get LTC2688 channel dither frequency """
            return self._get_iio_attr(self.name, "dither_frequency", True, self._ctrl)

        @dither_frequency.setter
        def dither_frequency(self, val):
            """ Set LTC2688 channel dither frequency """
            dither_frequency_span = self._get_iio_attr(
                self.name, "dither_frequency_available", True, self._ctrl
            )
            for freq in dither_frequency_span:
                if val == freq:
                    self._set_iio_attr(self.name, "dither_frequency", True, val)
                    break

        @property
        def dither_phase(self):
            """ Get LTC2688 channel dither phase """
            return self._get_iio_attr(self.name, "dither_phase", True, self._ctrl)

        @dither_phase.setter
        def dither_phase(self, val):
            """ Set LTC2688 channel dither phase """
            dither_phase_span = self._get_iio_attr(
                self.name, "dither_phase_available", True, self._ctrl
            )
            for phase in dither_phase_span:
                if val == phase:
                    self._set_iio_attr(self.name, "dither_phase", True, val)
                    break

        @property
        def dither_raw(self):
            """ Get LTC2688 channel dither amplitude """
            return self._get_iio_attr(self.name, "dither_raw", True, self._ctrl)

        @dither_raw.setter
        def dither_raw(self, val):
            """ Set LTC2688 channel dither amplitude """
            dither_raw_span = self._get_iio_attr(
                self.name, "dither_raw_available", True, self._ctrl
            )
            if (
                val >= dither_raw_span[0]
                and val <= dither_raw_span[2]
                and val % dither_raw_span[1] == 0
            ):
                self._set_iio_attr(self.name, "dither_raw", True, str(int(val)))

        @property
        def dither_offset(self):
            """ Get LTC2688 channel dither offset """
            return self._get_iio_attr(self.name, "dither_offset", True, self._ctrl)

        @dither_offset.setter
        def dither_offset(self, val):
            """ Set LTC2688 channel dither offset """
            self._set_iio_attr(self.name, "dither_offset", True, str(int(val)))

    class _channel_toggle(_channel_base):
        """ LTC2688 toggle channel """
        def __init__(self, ctrl, channel_name):
            super().__init__(ctrl, channel_name)

        @property
        def toggle_en(self):
            """ Get LTC2688 channel toggle setting """
            return self._get_iio_attr(self.name, "toggle_en", True, self._ctrl)

        @toggle_en.setter
        def toggle_en(self, val):
            """ Set LTC2688 channel toggle """
            self._set_iio_attr(self.name, "toggle_en", True, val)

        @property
        def raw0(self):
            """ Get LTC2688 channel raw output code for 1st toggle value """
            return self._get_iio_attr(self.name, "raw0", True, self._ctrl)

        @raw0.setter
        def raw0(self, val):
            """ Set LTC2688 channel raw output code for 1st toggle value """
            raw_span = self._get_iio_attr(self.name, "raw_available", True, self._ctrl)
            if val >= raw_span[0] and val <= raw_span[2] and val % raw_span[1] == 0:
                self._set_iio_attr(self.name, "raw0", True, str(int(val)))

        @property
        def raw1(self):
            """ Get LTC2688 channel raw output code for 2nd toggle value """
            return self._get_iio_attr(self.name, "raw1", True, self._ctrl)

        @raw1.setter
        def raw1(self, val):
            """ Set LTC2688 channel raw output code for 2nd toggle value """
            raw_span = self._get_iio_attr(self.name, "raw_available", True, self._ctrl)
            if val >= raw_span[0] and val <= raw_span[2] and val % raw_span[1] == 0:
                self._set_iio_attr(self.name, "raw1", True, str(int(val)))

        @property
        def volt0(self):
            """ Get LTC2688 channel 1st toggle voltage """
            return ((self.raw0 + self.offset) * self.scale) * (self.vref / 4.096)

        @volt0.setter
        def volt0(self, val):
            """ Set LTC2688 channel 1st toggle voltage """
            self.raw0 = ((val / self.scale) - self.offset) * (self.vref / 4.096)

        @property
        def volt1(self):
            """ Get LTC2688 channel 2nd toggle voltage """
            return ((self.raw1 + self.offset) * self.scale) * (self.vref / 4.096)

        @volt1.setter
        def volt1(self, val):
            """ Set LTC2688 channel 2nd toggle voltage """
            self.raw1 = ((val / self.scale) - self.offset) * (self.vref / 4.096)

    class _channel_sw_toggle(_channel_toggle):
        """ LTC2688 software toggle channel """
        def __init__(self, ctrl, channel_name):
            super().__init__(ctrl, channel_name)

        @property
        def symbol(self):
            """ Get LTC2688 channel current toggle state """
            return self._get_iio_attr(self.name, "symbol", True, self._ctrl)

        @symbol.setter
        def symbol(self, val):
            """ Set LTC2688 channel current toggle state """
            self._set_iio_attr(self.name, "symbol", True, str(int(val)))
