from .bitstring import BitStream, pack
from .processSubLayerHrdParameters import processSubLayerHrdParameters

class processHrdParameters(object):
    def __init__(self, s, commonInfPresentFlag, maxNumSubLayersMinus1):
        self.t = '\t\t\t'
        self.commonInfPresentFlag = commonInfPresentFlag
        self.maxNumSubLayersMinus1 = maxNumSubLayersMinus1
        if commonInfPresentFlag:
            self.nal_hrd_parameters_present_flag = s.read('uint:1')
            self.vcl_hrd_parameters_present_flag = s.read('uint:1')
            if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
                self.sub_pic_hrd_params_present_flag = s.read('uint:1')
                if self.sub_pic_hrd_params_present_flag:
                    self.tick_divisor_minus2 = s.read('uint:8')
                    self.du_cpb_removal_delay_increment_length_minus1 = s.read('uint:5')
                    self.sub_pic_cpb_params_in_pic_timing_sei_flag = s.read('uint:1')
                    self.dpb_output_delay_du_length_minus1 = s.read('uint:5')
                self.bit_rate_scale = s.read('uint:4')
                self.cpb_size_scale = s.read('uint:4')
                if self.sub_pic_hrd_params_present_flag:
                    self.cpb_size_du_scale = s.read('uint:4')
                self.initial_cpb_removal_delay_length_minus1 = s.read('uint:5')
                self.au_cpb_removal_delay_length_minus1 = s.read('uint:5')
                self.dpb_output_delay_length_minus1 = s.read('uint:5')
        self.fixed_pic_rate_general_flag = [None] * (maxNumSubLayersMinus1 + 1)
        self.fixed_pic_rate_within_cvs_flag = [None] * (maxNumSubLayersMinus1 + 1)
        self.elemental_duration_in_tc_minus1 = [None] * (maxNumSubLayersMinus1 + 1)
        self.low_delay_hrd_flag = [None] * (maxNumSubLayersMinus1 + 1)
        self.cpb_cnt_minus1 = [None] * (maxNumSubLayersMinus1 + 1)
        
        if self.nal_hrd_parameters_present_flag:
            self.nal_sub_layer_hrd_parameters = [None] * (maxNumSubLayersMinus1 + 1)
        if self.vcl_hrd_parameters_present_flag:
            vcl_sub_layer_hrd_parameters = [None] * (maxNumSubLayersMinus1 + 1)
        
        for idx in range(maxNumSubLayersMinus1+1):
            self.fixed_pic_rate_general_flag[idx] = s.read('uint:1')
            
            if self.fixed_pic_rate_general_flag[idx]:
                self.fixed_pic_rate_within_cvs_flag[idx] = 1
            
            if not self.fixed_pic_rate_general_flag[idx]:
                self.fixed_pic_rate_within_cvs_flag[idx] = s.read('uint:1')
            
            if self.fixed_pic_rate_within_cvs_flag[idx]:
                self.elemental_duration_in_tc_minus1[idx] = s.read('ue')
            else:
                self.low_delay_hrd_flag[idx] = s.read('uint:1');
            
            if not self.low_delay_hrd_flag[idx]:
                self.cpb_cnt_minus1[idx] = s.read('ue')
                
            if self.nal_hrd_parameters_present_flag:
                self.nal_sub_layer_hrd_parameters[idx] = processSubLayerHrdParameters(s, self.sub_pic_hrd_params_present_flag, self.cpb_cnt_minus1[idx]);
            if self.vcl_hrd_parameters_present_flag:
                self.vcl_sub_layer_hrd_parameters[idx] = processSubLayerHrdParameters(s, self.sub_pic_hrd_params_present_flag, self.cpb_cnt_minus1[idx]);
    
    def bs(self):
        new_bs = BitStream()
        if self.commonInfPresentFlag:
            new_bs += pack('uint:1', self.nal_hrd_parameters_present_flag)
            new_bs += pack('uint:1', self.vcl_hrd_parameters_present_flag)
            if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
                new_bs += pack('uint:1', self.sub_pic_hrd_params_present_flag)
                if self.sub_pic_hrd_params_present_flag:
                    new_bs += pack('uint:8', self.tick_divisor_minus2)
                    new_bs += pack('uint:5', self.du_cpb_removal_delay_increment_length_minus1)
                    new_bs += pack('uint:1', self.sub_pic_cpb_params_in_pic_timing_sei_flag)
                    new_bs += pack('uint:5', self.dpb_output_delay_du_length_minus1)
                new_bs += pack('uint:4', self.bit_rate_scale)
                new_bs += pack('uint:4', self.cpb_size_scale)
                if self.sub_pic_hrd_params_present_flag:
                    new_bs += pack('uint:4', self.cpb_size_du_scale)
                new_bs += pack('uint:5', self.initial_cpb_removal_delay_length_minus1)
                new_bs += pack('uint:5', self.au_cpb_removal_delay_length_minus1)
                new_bs += pack('uint:5', self.dpb_output_delay_length_minus1)
        
        for idx in range(self.maxNumSubLayersMinus1+1):
            new_bs += pack('uint:1', self.fixed_pic_rate_general_flag[idx])
            
            if not self.fixed_pic_rate_general_flag[idx]:
                new_bs += pack('uint:1', self.fixed_pic_rate_within_cvs_flag[idx])
            
            if self.fixed_pic_rate_within_cvs_flag[idx]:
                new_bs += pack('ue', self.elemental_duration_in_tc_minus1[idx])
            else:
                new_bs += pack('uint:1', self.low_delay_hrd_flag[idx])
            
            if not self.low_delay_hrd_flag[idx]:
                new_bs += pack('ue', self.cpb_cnt_minus1[idx])
                
            if self.nal_hrd_parameters_present_flag:
                new_bs += self.nal_sub_layer_hrd_parameters[idx].bs()
            if self.vcl_hrd_parameters_present_flag:
                new_bs += self.vcl_sub_layer_hrd_parameters[idx].bs()
        return new_bs
    
    def show(self):
        """
        """
        if self.commonInfPresentFlag:
            print (self.t+'nal_hrd_parameters_present_flag {}',format(self.nal_hrd_parameters_present_flag))
            print (self.t+'vcl_hrd_parameters_present_flag {}',format(self.vcl_hrd_parameters_present_flag))
            if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
                print (self.t+'sub_pic_hrd_params_present_flag {}',format(self.sub_pic_hrd_params_present_flag))
                if self.sub_pic_hrd_params_present_flag:
                    print (self.t+'tick_divisor_minus2 {}',format(self.tick_divisor_minus2))
                    print (self.t+'du_cpb_removal_delay_increment_length_minus1 {}',format(self.du_cpb_removal_delay_increment_length_minus1))
                    print (self.t+'sub_pic_cpb_params_in_pic_timing_sei_flag {}',format(self.sub_pic_cpb_params_in_pic_timing_sei_flag))
                    print (self.t+'dpb_output_delay_du_length_minus1 {}',format(self.dpb_output_delay_du_length_minus1))
                print (self.t+'bit_rate_scale {}',format(self.bit_rate_scale))
                print (self.t+'cpb_size_scale {}',format(self.cpb_size_scale))
                
                if self.sub_pic_hrd_params_present_flag:
                    print (self.t+'cpb_size_du_scale {}',format(self.cpb_size_du_scale))
                print (self.t+'initial_cpb_removal_delay_length_minus1 {}',format(self.initial_cpb_removal_delay_length_minus1))
                print (self.t+'au_cpb_removal_delay_length_minus1 {}',format(self.au_cpb_removal_delay_length_minus1))
                print (self.t+'dpb_output_delay_length_minus1 {}',format(self.dpb_output_delay_length_minus1))
        for idx in range(self.maxNumSubLayersMinus1+1):
            print (self.t+'fixed_pic_rate_general_flag[{}] {}'.format(idx, self.fixed_pic_rate_general_flag[idx]))
            print (self.t+'fixed_pic_rate_within_cvs_flag[{}] {}'.format(idx, self.fixed_pic_rate_within_cvs_flag[idx]))
            
            if self.fixed_pic_rate_within_cvs_flag[idx]:
                print (self.t+'elemental_duration_in_tc_minus1[{}] {}'.format(idx, self.elemental_duration_in_tc_minus1[idx]))
            else:
                print (self.t+'low_delay_hrd_flag[{}] {}'.format(idx, self.low_delay_hrd_flag[idx]))
            
            if not self.low_delay_hrd_flag[idx]:
                print (self.t+'cpb_cnt_minus1[{}] {}'.format(idx, self.cpb_cnt_minus1[idx]))
                
            if self.nal_hrd_parameters_present_flag:
                self.nal_sub_layer_hrd_parameters[idx].show()
            if self.vcl_hrd_parameters_present_flag:
                self.vcl_sub_layer_hrd_parameters[idx].show()
