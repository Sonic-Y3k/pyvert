from .bitstring import BitStream, pack

class processShortTermRefPicSet(object):
    def __init__(self, s, stRpsIdx, num_short_term_ref_pic_sets, short_term_ref_pic_set, sps_max_dec_pic_buffering_minus1, sps_max_sub_layers_minus1):
        self.t = '\t\t'
        self.stRpsIdx = stRpsIdx
        self.sps_max_dec_pic_buffering_minus1 = sps_max_dec_pic_buffering_minus1
        self.sps_max_sub_layers_minus1 = sps_max_sub_layers_minus1
        self.num_short_term_ref_pic_sets = num_short_term_ref_pic_sets
        self.short_term_ref_pic_set = short_term_ref_pic_set
        self.inter_ref_pic_set_prediction_flag = 0
        self.delta_idx_minus1 = 0
        
        if stRpsIdx:
            self.inter_ref_pic_set_prediction_flag = s.read('uint:1')
        
        if self.inter_ref_pic_set_prediction_flag:
            if stRpsIdx == num_short_term_ref_pic_sets:
                self.delta_idx_minus1 = s.read('ue')
            
            self.delta_rps_sign = s.read('uint:1')
            self.abs_delta_rps_minus1 = s.read('ue')
            
            RefRpsIdx = stRpsIdx - (self.delta_idx_minus1 + 1);
            NumDeltaPocs = 0
            
            if short_term_ref_pic_set[RefRpsIdx].inter_ref_pic_set_prediction_flag:
                for idx in range(len(short_term_ref_pic_set[RefRpsIdx].used_by_curr_pic_flag)):
                    if short_term_ref_pic_set[RefRpsIdx].used_by_curr_pic_flag[idx] or short_term_ref_pic_set[RefRpsIdx].use_delta_flag[idx]:
                        NumDeltaPocs += 1;
            else:
                NumDeltaPocs = short_term_ref_pic_set[RefRpsIdx].num_negative_pics + short_term_ref_pic_set[RefRpsIdx].num_positive_pics;
            
            self.used_by_curr_pic_flag = [None] * (NumDeltaPocs + 1)
            self.use_delta_flag = [None] * (NumDeltaPocs + 1)
           
            for idx in range(NumDeltaPocs):
                self.used_by_curr_pic_flag[idx] = s.read('uint:1')
                if not self.used_by_curr_pic_flag[idx]:
                    self.use_delta_flag[idx] = s.read('uint:1')
            
        else:
            self.num_negative_pics = s.read('ue')
            self.num_positive_pics = s.read('ue')
            
            if self.num_negative_pics > sps_max_dec_pic_buffering_minus1[sps_max_sub_layers_minus1]:
                return
            if self.num_positive_pics > sps_max_dec_pic_buffering_minus1[sps_max_sub_layers_minus1]:
                return
            
            self.delta_poc_s0_minus1 = [None] * self.num_negative_pics
            self.used_by_curr_pic_s0_flag = [None] * self.num_negative_pics
            
            for idx in range(self.num_negative_pics):
                self.delta_poc_s0_minus1[idx] = s.read('ue')
                self.used_by_curr_pic_s0_flag[idx] = s.read('uint:1')
                
            self.delta_poc_s1_minus1 = [None] * self.num_positive_pics
            self.used_by_curr_pic_s1_flag = [None] * self.num_positive_pics
            
            for idx in range(self.num_positive_pics):
                self.delta_poc_s1_minus1[idx] = s.read('ue')
                self.used_by_curr_pic_s1_flag[idx] = s.read('uint:1')

    def bs(self):
        new_bs = BitStream()
        
        if self.stRpsIdx:
            new_bs += pack('uint:1', self.inter_ref_pic_set_prediction_flag)
        
        if self.inter_ref_pic_set_prediction_flag:
            if stRpsIdx == num_short_term_ref_pic_sets:
                new_bs += pack('ue', self.delta_idx_minus1)
            
            new_bs += pack('uint:1', self.delta_rps_sign)
            new_bs += pack('ue', self.abs_delta_rps_minus1)
            
            RefRpsIdx = stRpsIdx - (self.delta_idx_minus1 + 1);
            NumDeltaPocs = 0
            
            if short_term_ref_pic_set[RefRpsIdx].inter_ref_pic_set_prediction_flag:
                for idx in range(len(short_term_ref_pic_set[RefRpsIdx].used_by_curr_pic_flag)):
                    if short_term_ref_pic_set[RefRpsIdx].used_by_curr_pic_flag[idx] or short_term_ref_pic_set[RefRpsIdx].use_delta_flag[idx]:
                        NumDeltaPocs += 1;
            else:
                NumDeltaPocs = short_term_ref_pic_set[RefRpsIdx].num_negative_pics + short_term_ref_pic_set[RefRpsIdx].num_positive_pics;
            
            for idx in range(NumDeltaPocs):
                new_bs += pack('uint:1', self.used_by_curr_pic_flag[idx])
                if not self.used_by_curr_pic_flag[idx]:
                    new_bs += pack('uint:1', self.use_delta_flag[idx])
            
        else:
            new_bs += pack('ue', self.num_negative_pics)
            new_bs += pack('ue', self.num_positive_pics)
            
            if self.num_negative_pics > self.sps_max_dec_pic_buffering_minus1[self.sps_max_sub_layers_minus1]:
                return
            if self.num_positive_pics > self.sps_max_dec_pic_buffering_minus1[self.sps_max_sub_layers_minus1]:
                return
            
            for idx in range(self.num_negative_pics):
                new_bs += pack('ue', self.delta_poc_s0_minus1[idx])
                new_bs += pack('uint:1', self.used_by_curr_pic_s0_flag[idx])
            
            for idx in range(self.num_positive_pics):
                new_bs += pack('ue', self.delta_poc_s1_minus1[idx])
                new_bs += pack('uint:1', self.used_by_curr_pic_s1_flag[idx])
        return new_bs
        
    def show(self):
        """
        """
