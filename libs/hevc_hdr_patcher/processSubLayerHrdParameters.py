from .bitstring import BitStream, pack

class processSubLayerHrdParameters(object):
    def __init__(self, s, sub_pic_hrd_params_present_flag, cpb_cnt_minus1):
        self.t = '\t\t\t\t'
        self.sub_pic_hrd_params_present_flag = sub_pic_hrd_params_present_flag
        self.cpb_cnt_minus1 = cpb_cnt_minus1
        
        self.bit_rate_value_minus1 = [None] * (cpb_cnt_minus1+1)
        self.cpb_size_value_minus1 = [None] * (cpb_cnt_minus1+1)
        self.cpb_size_du_value_minus1 = [None] * (cpb_cnt_minus1+1)
        self.bit_rate_du_value_minus1 = [None] * (cpb_cnt_minus1+1)
        self.cbr_flag = [None] * (cpb_cnt_minus1+1)
        
        for idx in range(cpb_cnt_minus1+1):
            self.bit_rate_value_minus1[idx] = s.read('ue')
            self.cpb_size_value_minus1[idx] = s.read('ue')
            
            if sub_pic_hrd_params_present_flag:
                self.cpb_size_du_value_minus1[idx] = s.read('ue')
                self.bit_rate_du_value_minus1[idx] = s.read('ue')
            
            self.cbr_flag[idx] = s.read('uint:1')

    def bs(self):
        new_bs = BitStream()
        for idx in range(self.cpb_cnt_minus1+1):
            new_bs += pack('ue', self.bit_rate_value_minus1[idx])
            new_bs += pack('ue', self.cpb_size_value_minus1[idx])
            
            if self.sub_pic_hrd_params_present_flag:
                new_bs += pack('ue', self.cpb_size_du_value_minus1[idx])
                new_bs += pack('ue', self.bit_rate_du_value_minus1[idx])
            
            new_bs += pack('uint:1', self.cbr_flag[idx])
        return new_bs

    def show(self):
        for idx in range(self.cpb_cnt_minus1+1):
            print (self.t+'bit_rate_value_minus1[{}] {}'.format(idx, self.bit_rate_value_minus1[idx]))
            print (self.t+'cpb_size_value_minus1[{}] {}'.format(idx, self.cpb_size_value_minus1[idx]))

            if self.sub_pic_hrd_params_present_flag:
                print (self.t+'cpb_size_du_value_minus1[{}] {}'.format(idx, self.cpb_size_du_value_minus1[idx]))
                print (self.t+'bit_rate_du_value_minus1[{}] {}'.format(idx, self.bit_rate_du_value_minus1[idx]))
            
            print (self.t,'cbr_flag[{}] {}'.format(idx, self.cbr_flag[idx]))
