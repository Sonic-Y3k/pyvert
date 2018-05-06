import sys
import os
import re
from .bitstring import BitArray, BitStream, pack, Bits
from .processSPS import processSPS

class hdrpatcher(object):
    F = None
    o = None
    parsed_data = None
    gsei = ''
    
    def __init__(self, infile):
        self.chunk = 8388608
        self.infile = infile
        self.F = open (self.infile,'r+b')
        self.s = BitStream(self.F.read(self.chunk))
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
        
    
    def close_streams(self):
        if self.F:
            self.F.close()
        if self.o:
            self.o.close()
    
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
        new_sei_string += pack ('uint:16',int(mdl))
        new_sei_string.replace ('0x0000','0x000003',bytealigned=True)
        new_sei_string = '0x00000001' + new_sei_string + '0x00'
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
        prim_list = ['reserved',
                     'bt709',
                     'undef',
                     'reserved',
                     'bt470m',
                     'bt470bg',
                     'smpte170m',
                     'smpte240m',
                     'film',
                     'bt2020',
                     'smpte-st-428']
        trc_list = ['reserved',
                    'bt709',
                    'undef',
                    'reserved',
                    'bt470m',
                    'bt470bg',
                    'smpte170m',
                    'smpte240m',
                    'linear',
                    'log100',
                    'log316',
                    'iec61966-2-4',
                    'bt1361e',
                    'iec61966-2-1',
                    'bt2020-10',
                    'bt2020-12',
                    'smpte-st-2084',
                    'smpte-st-428',
                    'arib-std-b67']
        mtx_list = ['GBR',
                    'bt709',
                    'undef',
                    'reserved',
                    'fcc',
                    'bt470bg',
                    'smpte170m',
                    'smpte240m',
                    'YCgCo',
                    'bt2020nc',
                    'bt2020c']


        if self.parsed_data:
            if sei:
                """ Patch sei
                """
                if 'G' in sei and 'B' in sei and 'R' in sei and 'WP' in sei and 'L' in sei:
                    sei_string = 'G({},{})B({},{})R({},{})WP({},{})L({},{})'.format(sei['G'][0], sei['G'][1],
                                                                                    sei['B'][0], sei['B'][1],
                                                                                    sei['R'][0], sei['R'][1],
                                                                                    sei['WP'][0], sei['WP'][1],
                                                                                    sei['L'][0], sei['L'][1])
                    self.gsei += self.gen_mastering_display_info(sei_string)
                if 'MDPC' in sei and 'MDL' in sei:
                    self.gsei += self.gen_content_light_info(sei['MDPC'], sei['MDL'])
            if sps:
                """ Patch sps
                """
                if 'colour_primaries' in sps and 'transfer_characteristics' in sps and 'matrix_coeffs' in sps:
                    self.parsed_data.vui_parameters.colour_description_present_flag = 1
                    if not hasattr(self.parsed_data.vui_parameters, 'colour_primaries'):
                        setattr(self.parsed_data.vui_parameters, 'colour_primaries', 9)
                    if not hasattr(self.parsed_data.vui_parameters, 'transfer_characteristics'):
                        setattr(self.parsed_data.vui_parameters, 'transfer_characteristics', 16)
                    if not hasattr(self.parsed_data.vui_parameters, 'matrix_coeffs'):
                        setattr(self.parsed_data.vui_parameters, 'matrix_coeffs', 9)
                    
                    if sps['colour_primaries'] in prim_list:
                        self.parsed_data.vui_parameters.colour_primaries = prim_list.index(sps['colour_primaries'])
                    if sps['transfer_characteristics'] in trc_list:
                        self.parsed_data.vui_parameters.transfer_characteristics = trc_list.index(sps['transfer_characteristics'])
                    if sps['matrix_coeffs'] in mtx_list:
                        self.parsed_data.vui_parameters.matrix_coeffs = mtx_list.index(sps['matrix_coeffs'])
        else:
            return False
    
    def write(self, outfile):
        """
        """
        self.o = open (outfile, 'wb')
        self.s.replace (self.nal_t,self.parsed_data.bs(), bytealigned=True)
        if len(self.gsei) > 1:
            self.s.prepend(self.gsei)
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
