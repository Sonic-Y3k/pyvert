import sys
from hevc_hdr_patcher import hdrpatcher

new_sei = {
    'G': (13250, 34500),
    'B': (7500, 3000),
    'R': (34000, 16000),
    'WP': (15635,16450),
    'L': (10000000, 1),
    'MDPC': 1000,
    'MDL': 50
}

#test.show()

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
             'smpte240m']

prim_list = ['smpte240m']
             
for i in prim_list:
    test = hdrpatcher()
    test.load('/mnt/Wastelands/Downloads/ToConvert/test/orig.hevc') 
    test.process(0)
    new_sps = {
        'colour_primaries': i,
        'transfer_characteristics': 'smpte-st-2084',
        'matrix_coeffs': 'bt2020nc'
    }
    print('SPS: {}'.format(test.parsed_data.bs()))
    test.patch(sei=new_sei, sps=new_sps)
    #print('NBS: {}'.format(test.parsed_data.bs()))
    
    #o = open ('/mnt/Wastelands/Downloads/ToConvert/t.hevc', 'wb')
    #test.gsei.tofile(o)
    #test.parsed_data.bs().tofile(o)
    #o.close()
    
    #test.show()
    #exit(1)
    
    for i in test.write('/mnt/Wastelands/Downloads/ToConvert/output/out_{}.hevc'.format(i)):
        print ('{}%'.format(i))
    test.close_streams()
    test = None
    del test
    #exit(1)
