
class ElementConfig:    
    def add(self, name, value):
        setattr(self, name, value)
    
    def get(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return None
    
    def add_sps(self, cp, tc, mc):
        self.SPS = SPS(cp, tc, mc)
    
    def add_sei(self, l=None, wp=None, g=None, b=None, r=None, mcll=None, mfll=None):
        if not self.has_sei():
            self.SEI = SEI()
            
        self.SEI.add(cmcll=mcll, cmfll=mfll, cl=l, cwp=wp, cg=g, cb=b, cr=r)
    
    def has_hdr(self):
        return (self.has_sei() or self.has_sps())
    
    def has_sei(self):
        return hasattr(self, 'SEI')
    
    def has_sps(self):
        return hasattr(self, 'SPS')
    
    def gen_dict(self):
        result = {}
        for i in vars(self):
            if i not in ['SEI', 'SPS']:
                result[i] = getattr(self, i)
                
        return result
    
    def get_hdr(self):
        result = []
        
        if self.has_sps():
            result.extend(self.SPS.get())
            
        if self.has_sei():
            result.extend(self.SEI.get())
        
        return result
        
class SPS:
    mcl = ['Identity',
           'BT.709',
           'undef',
           'reserved',
           'FCC 73.682',
           'BT.470 System B/G',
           'BT.601',
           'SMPTE 240M',
           'YCgCo',
           'BT.2020 non-constant',
           'BT.2020 constant',
           'Y\'D\'zD\'x',
           'Chromaticity-derived non-constant',
           'Chromaticity-derived constant']
    
    tcl = ['reserved',
           'BT.709',
           'undef',
           'reserved',
           'BT.470 System M',
           'BT.470 System B/G',
           'BT.601',
           'SMPTE 240M',
           'Linear',
           'Logarithmic (100:1)',
           'Logarithmic (316.22777:1)',
           'xvYCC',
           'BT.1361',
           'sRGB/sYCC',
           'BT.2020 (10-bit)',
           'BT.2020 (12-bit)',
           'PQ',
           'SMPTE 428M',
           'HLG']
          
    cpl = ['reserved',
           'BT.709',
           'undef',
           'reserved',
           'BT.470 System M',
           'BT.601 PAL',
           'BT.601 NTSC',
           'SMPTE 240M',
           'Generic film',
           'BT.2020',
           'XYZ',
           'DCI P3',
           'Display P3']
          
    def __init__(self, cp, tc, mc):
        if cp in self.cpl:
            self.colour_primaries = self.cpl.index(cp)
         
        if tc in self.tcl:
            self.transfer_characteristics = self.tcl.index(tc)
        
        if mc in self.mcl:
            self.matrix_coeffs = self.mcl.index(mc)
        
                    
    def get(self):
        result = []
        if hasattr(self, 'colour_primaries'):
            result.extend(['--colour-primaries', '0:{}'.format(self.colour_primaries)])
        if hasattr(self, 'transfer_characteristics'):
            result.extend(['--colour-transfer-characteristics', '0:{}'.format(self.transfer_characteristics)])
        if hasattr(self, 'matrix_coeffs'):
            result.extend(['--colour-matrix', '0:{}'.format(self.matrix_coeffs)])
        return result
    
class SEI:
    def add(self, cmcll=None, cmfll=None, cl=None, cwp=None, cg=None, cb=None, cr=None):
        if cl:
            if len(cl) == 2:
                self.L = (int(cl[1]), float(cl[0]))
        
        if cwp:
            self.WP = cwp
            
        if cg and cb and cr:
            self.G = cg
            self.B = cb
            self.R = cr
    
        if cmcll:
            self.MCLL = int(cmcll[0])
            
        if cmfll:
            self.MFLL = int(cmfll[0])
    
    def get(self):
        result = []
        if hasattr(self, 'L'):
            result.extend(['--min-luminance', '0:{0:.4f}'.format(self.L[1])])
            result.extend(['--max-luminance', '0:{}'.format(self.L[0])])
        
        if hasattr(self, 'WP'):
            result.extend(['--white-colour-coordinates', '0:0.{},0.{}'.format(self.WP[0], self.WP[1])])
            
        if hasattr(self, 'G') and \
           hasattr(self, 'B') and \
           hasattr(self, 'R'):
            result.extend(['--chromaticity-coordinates',
                           '0:0.{},0.{},0.{},0.{},0.{},0.{}'.format(self.G[0], self.G[1],
                                                                    self.B[0], self.B[1],
                                                                    self.R[0], self.R[1])])

        if hasattr(self, 'MCLL'):
            result.extend(['--max-content-light', '0:{}'.format(self.MCLL)])
        
        if hasattr(self, 'MFLL'):
            result.extend(['--max-frame-light', '0:{}'.format(self.MFLL)])
                                                                    
        return result