import sys
import os
import re
from .bitstring import BitArray, BitStream, pack, Bits
from .processSPS import processSPS

class hdrpatcher(object):
    F = None
    o = None
    parsed_data = None
    gsei = BitStream()
    NALS = []
    
    def __init__(self):
        self.chunk = 8388608
        
    def load(self, infile):
        self.infile = infile
        self.F = open (self.infile,'r+b')
        self.s = BitStream(self.F.read(self.chunk))
        return
        
        nals = list(self.s.findall('0x000001', bytealigned=True))
        sps_nals = list(self.s.findall('0x00000142', bytealigned=True))
        sei_pref_nals = list (self.s.findall('0x0000014e', bytealigned=True))
        size = [y - x for x,y in zip(nals,nals[1:])]
        sps_pos = list(set(nals).intersection(sps_nals))
        sei_pref_nals_pos = list(set(nals).intersection(sei_pref_nals))
        sps_size = size[nals.index(sps_nals[0])]
        self.s.pos = sps_pos[0] + 40
        t = self.s.peek(sps_size)
        self.nal_t = t[:]
        t.replace ('0x000003','0x0000',bytealigned=True)
        self.parsed_data = processSPS(t)
        t.replace ('0x0000','0x000003',bytealigned=True)
    
    def process(self, offset):
        parseFailed = False
        while (self.s.pos+3) < 20000:
            startOffset = 3
            
            naluFinded = self.s.peek(24) == '0x000001'

            if not naluFinded:
                if self.s.len - self.s.pos >= 4 and self.s.peek(32) == '0x00000001':
                    naluFinded = True
                    startOffset = 4
            if naluFinded:
                self.NALS.append(self.s.pos)
                self.s.pos += 32
            else:
                self.s.pos += 8
        
        for i in self.NALS:
            self.s.pos = i+32
            type = self.processNALUnitHeader()
            if type == 33:
                size = self.NALS[self.NALS.index(i)+1]-i
                self.s.pos = i
                self.nal_t = self.s.peek(size)
                self.parsed_data = processSPS(self.s.peek(size))

    def processNALUnitHeader(self):
        self.s.read('uint:1') #forbidden_zero_bid
        type = self.s.read('uint:6') #nal unit type
        self.s.read('uint:6') #nuh_layer_id
        self.s.read('uint:3') #nuh_temporal_id_plus1
        return type
    
    def close_streams(self):
        if self.F:
            self.F.close()
        if self.o:
            self.o.close()
        
        self.F = None
        self.o = None
        self.parsed_data = None
        self.gsei = BitStream()
        self.NALS = []
    
    def gen_content_light_info(self, mdpc, mdl):
        """
        """
        sei_forbidden_zero_bit  = 0
        sei_nal_unit_type = 39
        sei_nuh_layer_id = 0
        sei_nuh_temporal_id_plus1 = 1
        new_sei_string = pack ('uint:1,2*uint:6,uint:3',sei_forbidden_zero_bit,sei_nal_unit_type,sei_nuh_layer_id,sei_nuh_temporal_id_plus1)
        md_sei_last_payload_type_byte = 144
        md_sei_last_payload_size_byte = 4
        new_sei_string += pack ('2*uint:8',md_sei_last_payload_type_byte,md_sei_last_payload_size_byte)
        new_sei_string += pack ('uint:16',int(mdpc))
        #new_sei_string +=  '0x'+hex(mdpc).split('x')[-1].zfill(4)
        #new_sei_string +=  '0x'+hex(mdl).split('x')[-1].zfill(4)
        new_sei_string += pack ('uint:16',int(mdl))
        new_sei_string = '0x00000001' + new_sei_string + '0x80'
        return new_sei_string
        
    def gen_mastering_display_info(self, md_arg_str):
        """
        """
        sei_forbidden_zero_bit  = 0
        sei_nal_unit_type = 39
        sei_nuh_layer_id = 0
        sei_nuh_temporal_id_plus1 = 1
        new_sei_string = pack ('uint:1,2*uint:6,uint:3',sei_forbidden_zero_bit,sei_nal_unit_type,sei_nuh_layer_id,sei_nuh_temporal_id_plus1)
        md_sei_last_payload_type_byte = 137
        md_sei_last_payload_size_byte = 24
        #MD string ref
        #G(13250,34500)B(7500,3000)R(34000,16000)WP(15635,16450)L(10000000,1)
        md = re.findall('\d+',md_arg_str)
        new_sei_string += pack ('2*uint:8',md_sei_last_payload_type_byte,md_sei_last_payload_size_byte)
        for i in range (len(md)-2) :
            new_sei_string += pack ('uint:16',int(md[i]))
        new_sei_string += pack ('uint:32',int(md[8]))
        new_sei_string += pack ('uint:32',int(md[9]))
        new_sei_string.replace ('0x0000','0x000003',bytealigned=True)
        new_sei_string = '0x00000001' + new_sei_string + '0x00'
        return new_sei_string
        
    
    def patch(self, sei=None, sps=None):
        """
        """
        if self.parsed_data:
            if sei:
                """ Patch sei
                """
                if hasattr(sei, 'MCLL') and hasattr(sei, 'MFLL'):
                    self.gsei += self.gen_content_light_info(sei.MCLL, sei.MFLL)
                    
                if hasattr(sei, 'G') and hasattr(sei, 'B') and hasattr(sei, 'R') and hasattr(sei, 'WP') and hasattr(sei, 'L'):
                    sei_string = 'G({},{})B({},{})R({},{})WP({},{})L({},{})'.format(sei.G[0], sei.G[1],
                                                                                    sei.B[0], sei.B[1],
                                                                                    sei.R[0], sei.R[1],
                                                                                    sei.WP[0], sei.WP[1],
                                                                                    int(sei.L[0]*10000), int(sei.L[1]*10000))
                    self.gsei += self.gen_mastering_display_info(sei_string)
            if sps:
                """ Patch sps
                """
                if hasattr(sps, 'colour_primaries') and hasattr(sps, 'transfer_characteristics') and hasattr(sps, 'matrix_coeffs'):
                    if getattr(self.parsed_data.vui_parameters, 'video_signal_type_present_flag') == 0:
                        setattr(self.parsed_data.vui_parameters, 'video_signal_type_present_flag', 1)
                        setattr(self.parsed_data.vui_parameters, 'video_format', 5)
                        setattr(self.parsed_data.vui_parameters, 'video_full_range_flag', 0)
                        setattr(self.parsed_data.vui_parameters, 'colour_description_present_flag', 1)
                        
                    
                    if not hasattr(self.parsed_data.vui_parameters, 'colour_primaries'):
                        setattr(self.parsed_data.vui_parameters, 'colour_primaries', 9)
                    if not hasattr(self.parsed_data.vui_parameters, 'transfer_characteristics'):
                        setattr(self.parsed_data.vui_parameters, 'transfer_characteristics', 16)
                    if not hasattr(self.parsed_data.vui_parameters, 'matrix_coeffs'):
                        setattr(self.parsed_data.vui_parameters, 'matrix_coeffs', 9)
                    
                    self.parsed_data.vui_parameters.colour_primaries = sps.colour_primaries
                    self.parsed_data.vui_parameters.transfer_characteristics = sps.transfer_characteristics
                    self.parsed_data.vui_parameters.matrix_coeffs = sps.matrix_coeffs
        else:
            return False
    
    def write(self, outfile):
        """
        """
        self.s.pos = 0
        self.o = open (outfile, 'wb')
        #abc.replace('0x0000014401', '', bytealigned=True)
        #self.nal_t.replace('0x000000014401', '', bytealigned=True)
        #print(str(self.nal_t))
        #exit(1)
        #self.s.replace (self.nal_t,self.parsed_data.bs()+'0x000000014401', bytealigned=True)
        self.s.replace (self.nal_t,'', bytealigned=True)
        #if len(self.gsei) > 1:
        #    self.s.prepend(self.gsei)
        self.gsei.tofile(self.o)
        self.parsed_data.bs().tofile(self.o)
        self.s.tofile(self.o)
        progr = self.chunk
        while True:
            self.s = self.F.read(self.chunk)
            self.o.write(self.s)
            if progr < os.path.getsize(self.infile):
                #print ('\rProgress ',int(round((progr/os.path.getsize(self.infile))*100)),'%',end='')
                yield int(round((progr/os.path.getsize(self.infile))*100))
            progr = progr + self.chunk
            if not self.s:
                break
        
    def show(self):
        """
        """
        self.parsed_data.show()
