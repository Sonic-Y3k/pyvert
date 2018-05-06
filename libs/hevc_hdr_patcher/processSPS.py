from .bitstring import BitStream, pack
from .profile_tier_level import profile_tier_level
from .processVuiParameters import processVuiParameters
from .processShortTermRefPicSet import processShortTermRefPicSet
from .processScalingListData import processScalingListData

class processSPS(object):
    def __init__(self, s):
        self.t = '\t'
        self.sps_video_parameter_set_id = s.read('uint:4')
        self.sps_max_sub_layers_minus1 = s.read('uint:3')
        self.sps_temporal_id_nesting_flag = s.read('uint:1')
        self.profile_tier_level = profile_tier_level(s, self.sps_max_sub_layers_minus1) #579
        
        self.sps_seq_parameter_set_id = s.read('ue')
        self.chroma_format_idc = s.read('ue')
        
        if self.chroma_format_idc == 3:
            self.separate_colour_plane_flag = s.read('uint:1')
        else:
            self.separate_colour_plane_flag = 0
            
        self.pic_width_in_luma_samples = s.read('ue')
        self.pic_height_in_luma_samples = s.read('ue')
        self.conformance_window_flag = s.read('uint:1')
        
        if self.conformance_window_flag:
            self.conf_win_left_offset = s.read('ue')
            self.conf_win_right_offset = s.read('ue')
            self.conf_win_top_offset = s.read('ue')
            self.conf_win_bottom_offset = s.read('ue')
        
        self.bit_depth_luma_minus8 = s.read('ue')
        self.bit_depth_chroma_minus8 = s.read('ue')
        self.log2_max_pic_order_cnt_lsb_minus4 = s.read('ue')
        self.sps_sub_layer_ordering_info_present_flag = s.read('uint:1')
        
        self.sps_max_dec_pic_buffering_minus1 = [None] * (self.sps_max_sub_layers_minus1 + 1)
        self.sps_max_num_reorder_pics = [None] * (self.sps_max_sub_layers_minus1 + 1)
        self.sps_max_latency_increase_plus1 = [None] * (self.sps_max_sub_layers_minus1 + 1)
        
        if self.sps_sub_layer_ordering_info_present_flag:
            for idx in range(self.sps_max_sub_layers_minus1+1):
                self.sps_max_dec_pic_buffering_minus1[idx] = s.read('ue')
                self.sps_max_num_reorder_pics[idx] = s.read('ue')
                self.sps_max_latency_increase_plus1[idx] = s.read('ue')
        else:
            self.sps_max_dec_pic_buffering_minus1[0] = s.read('ue')
            self.sps_max_num_reorder_pics[0] = s.read('ue')
            self.sps_max_latency_increase_plus1[0] = s.read('ue')
            
        self.log2_min_luma_coding_block_size_minus3 = s.read('ue')
        self.log2_diff_max_min_luma_coding_block_size = s.read('ue')
        self.log2_min_transform_block_size_minus2 = s.read('ue')
        self.log2_diff_max_min_transform_block_size = s.read('ue')
        self.max_transform_hierarchy_depth_inter = s.read('ue')
        self.max_transform_hierarchy_depth_intra = s.read('ue')
        
        self.scaling_list_enabled_flag = s.read('uint:1')
        if self.scaling_list_enabled_flag:
            self.sps_scaling_list_data_present_flag = s.read('uint:1')
            if self.sps_scaling_list_data_present_flag:
                self.scaling_list_data = processScalingListData(s)
        
        self.amp_enabled_flag = s.read('uint:1')
        self.sample_adaptive_offset_enabled_flag = s.read('uint:1')
        self.pcm_enabled_flag = s.read('uint:1')
        
        if self.pcm_enabled_flag:
            self.pcm_sample_bit_depth_luma_minus1 = s.read('uint:4')
            self.pcm_sample_bit_depth_chroma_minus1 = s.read('uint:4')
            self.log2_min_pcm_luma_coding_block_size_minus3 = s.read('ue')
            self.log2_diff_max_min_pcm_luma_coding_block_size = s.read('ue')
            self.pcm_loop_filter_disabled_flag = s.read('ue')
        
        self.num_short_term_ref_pic_sets = s.read('ue')
        
        self.short_term_ref_pic_set = [None] * self.num_short_term_ref_pic_sets
        for idx in range(self.num_short_term_ref_pic_sets):
            self.short_term_ref_pic_set[idx] = processShortTermRefPicSet(s, idx, self.num_short_term_ref_pic_sets, self.short_term_ref_pic_set, self.sps_max_dec_pic_buffering_minus1, self.sps_max_sub_layers_minus1)
        
        self.long_term_ref_pics_present_flag = s.read('uint:1')
        if self.long_term_ref_pics_present_flag:
            self.num_long_term_ref_pics_sps = s.read('ue')
            self.lt_ref_pic_poc_lsb_sps = [None] * self.num_long_term_ref_pics_sps
            self.used_by_curr_pic_lt_sps_flag = [None] * self.num_long_term_ref_pics_sps
            
            for idx in range(self.num_long_term_ref_pics_sps):
                self.lt_ref_pic_poc_lsb_sps[idx] = s.read('uint:'+str(self.log2_max_pic_order_cnt_lsb_minus4+4))
                self.used_by_curr_pic_lt_sps_flag[idx] = s.read('uint:1')
        
        self.sps_temporal_mvp_enabled_flag = s.read('uint:1')
        self.strong_intra_smoothing_enabled_flag = s.read('uint:1')
        self.vui_parameters_present_flag = s.read('uint:1')
        
        if self.vui_parameters_present_flag:
            self.vui_parameters = processVuiParameters(s,self.sps_max_sub_layers_minus1)
        
        self.sps_extension_flag = s.read('uint:1')
        self.garbage4size = str(len(s)-s.pos)
        self.garbage4 = s.read('uint:'+self.garbage4size)

    def bs(self):
        new_bs = BitStream()
        new_bs += pack('uint:4', self.sps_video_parameter_set_id)
        
        new_bs += pack('uint:3', self.sps_max_sub_layers_minus1)
        new_bs += pack('uint:1', self.sps_temporal_id_nesting_flag)
        new_bs += self.profile_tier_level.bs()
        new_bs += pack('ue', self.sps_seq_parameter_set_id)
        new_bs += pack('ue', self.chroma_format_idc)
        
        if self.chroma_format_idc == 3:
            new_bs += pack('uint:1', self.separate_colour_plane_flag)
            
        new_bs += pack('ue', self.pic_width_in_luma_samples)
        new_bs += pack('ue', self.pic_height_in_luma_samples)
        new_bs += pack('uint:1', self.conformance_window_flag)
        
        if self.conformance_window_flag:
            new_bs += pack('ue', self.conf_win_left_offset)
            new_bs += pack('ue', self.conf_win_right_offset)
            new_bs += pack('ue', self.conf_win_top_offset)
            new_bs += pack('ue', self.conf_win_bottom_offset)
        
        new_bs += pack('ue', self.bit_depth_luma_minus8)
        new_bs += pack('ue', self.bit_depth_chroma_minus8)
        new_bs += pack('ue', self.log2_max_pic_order_cnt_lsb_minus4)
        new_bs += pack('uint:1', self.sps_sub_layer_ordering_info_present_flag)
        
        if self.sps_sub_layer_ordering_info_present_flag:
            for idx in range(self.sps_max_sub_layers_minus1+1):
                new_bs += pack('ue', self.sps_max_dec_pic_buffering_minus1[idx])
                new_bs += pack('ue', self.sps_max_num_reorder_pics[idx])
                new_bs += pack('ue', self.sps_max_latency_increase_plus1[idx])
        else:
            new_bs += pack('ue', self.sps_max_dec_pic_buffering_minus1[0])
            new_bs += pack('ue', self.sps_max_num_reorder_pics[0])
            new_bs += pack('ue', self.sps_max_latency_increase_plus1[0])
            
        new_bs += pack('ue', self.log2_min_luma_coding_block_size_minus3)
        new_bs += pack('ue', self.log2_diff_max_min_luma_coding_block_size)
        new_bs += pack('ue', self.log2_min_transform_block_size_minus2)
        new_bs += pack('ue', self.log2_diff_max_min_transform_block_size)
        new_bs += pack('ue', self.max_transform_hierarchy_depth_inter)
        new_bs += pack('ue', self.max_transform_hierarchy_depth_intra)
        
        new_bs += pack('uint:1', self.scaling_list_enabled_flag)
        if self.scaling_list_enabled_flag:
            new_bs += pack('uint:1', self.sps_scaling_list_data_present_flag)
            if self.sps_scaling_list_data_present_flag:
                new_bs += self.scaling_list_data.bs()
        new_bs += pack('uint:1', self.amp_enabled_flag)
        new_bs += pack('uint:1', self.sample_adaptive_offset_enabled_flag)
        new_bs += pack('uint:1', self.pcm_enabled_flag)
        
        if self.pcm_enabled_flag:
            new_bs += pack('uint:4', self.pcm_sample_bit_depth_luma_minus1)
            new_bs += pack('uint:4', self.pcm_sample_bit_depth_chroma_minus1)
            new_bs += pack('ue', self.log2_min_pcm_luma_coding_block_size_minus3)
            new_bs += pack('ue', self.log2_diff_max_min_pcm_luma_coding_block_size)
            new_bs += pack('ue', self.pcm_loop_filter_disabled_flag)
        
        new_bs += pack('ue', self.num_short_term_ref_pic_sets)
        
        for idx in range(self.num_short_term_ref_pic_sets):
            new_bs += self.short_term_ref_pic_set[idx].bs()
        
        new_bs += pack('uint:1', self.long_term_ref_pics_present_flag)
        if self.long_term_ref_pics_present_flag:
            new_bs += pack('ue', self.num_long_term_ref_pics_sps)
            
            for idx in range(self.num_long_term_ref_pics_sps):
                new_bs += pack('uint:'+str(self.log2_max_pic_order_cnt_lsb_minus4+4), self.lt_ref_pic_poc_lsb_sps[idx])
                new_bs += pack('uint:1', self.used_by_curr_pic_lt_sps_flag[idx])
        
        new_bs += pack('uint:1', self.sps_temporal_mvp_enabled_flag)
        new_bs += pack('uint:1', self.strong_intra_smoothing_enabled_flag)
        new_bs += pack('uint:1', self.vui_parameters_present_flag)
        
        if self.vui_parameters_present_flag:
            new_bs += self.vui_parameters.bs()
        
        new_bs += pack('uint:1', self.sps_extension_flag)
        new_bs += pack('uint:'+self.garbage4size, self.garbage4)
        return new_bs
        
    def show(self):
        print (self.t+'sps_video_parameter_set_id {}'.format(self.sps_video_parameter_set_id))
        print (self.t+'sps_max_sub_layers_minus1 {}'.format(self.sps_max_sub_layers_minus1))
        print (self.t+'sps_temporal_id_nesting_flag {}'.format(self.sps_temporal_id_nesting_flag))
        print (self.t+'profile_tier_level')
        self.profile_tier_level.show()
        
        print (self.t+'sps_seq_parameter_set_id {}'.format(self.sps_seq_parameter_set_id))
        print (self.t+'chroma_format_idc {}'.format(self.chroma_format_idc))
        print (self.t+'separate_colour_plane_flag {}'.format(self.separate_colour_plane_flag))
        print (self.t+'pic_width_in_luma_samples {}'.format(self.pic_width_in_luma_samples))
        print (self.t+'pic_height_in_luma_samples {}'.format(self.pic_height_in_luma_samples))
        print (self.t+'conformance_window_flag {}'.format(self.conformance_window_flag))
        if self.conformance_window_flag:
            print (self.t+'\t','conf_win_left_offset {}'.format(self.conf_win_left_offset))
            print (self.t+'\t','conf_win_right_offset {}'.format(self.conf_win_right_offset))
            print (self.t+'\t','conf_win_top_offset {}'.format(self.conf_win_top_offset))
            print (self.t+'\t','conf_win_bottom_offset {}'.format(self.conf_win_bottom_offset))
        print (self.t+'bit_depth_luma_minus8 {}'.format(self.bit_depth_luma_minus8))
        print (self.t+'bit_depth_chroma_minus8 {}'.format(self.bit_depth_chroma_minus8))
        print (self.t+'log2_max_pic_order_cnt_lsb_minus4 {}'.format(self.log2_max_pic_order_cnt_lsb_minus4))
        print (self.t+'sps_sub_layer_ordering_info_present_flag {}'.format(self.sps_sub_layer_ordering_info_present_flag))
        for idx in range(len(self.sps_max_dec_pic_buffering_minus1)):
            print (self.t+'sps_max_dec_pic_buffering_minus1[{}] {}'.format(idx, self.sps_max_dec_pic_buffering_minus1[idx]))
            print (self.t+'sps_max_num_reorder_pics[{}] {}'.format(idx, self.sps_max_num_reorder_pics[idx]))
            print (self.t+'sps_max_latency_increase_plus1[{}] {}'.format(idx, self.sps_max_latency_increase_plus1[idx]))
        print (self.t+'log2_min_luma_coding_block_size_minus3 {}'.format(self.log2_min_luma_coding_block_size_minus3))
        print (self.t+'log2_diff_max_min_luma_coding_block_size {}'.format(self.log2_diff_max_min_luma_coding_block_size))
        print (self.t+'log2_min_transform_block_size_minus2 {}'.format(self.log2_min_transform_block_size_minus2))
        print (self.t+'log2_diff_max_min_transform_block_size {}'.format(self.log2_diff_max_min_transform_block_size))
        print (self.t+'max_transform_hierarchy_depth_inter {}'.format(self.max_transform_hierarchy_depth_inter))
        print (self.t+'max_transform_hierarchy_depth_intra {}'.format(self.max_transform_hierarchy_depth_intra))
        print (self.t+'scaling_list_enabled_flag {}'.format(self.scaling_list_enabled_flag))
        if self.scaling_list_enabled_flag:
            print (self.t+'\t','sps_scaling_list_data_present_flag {}'.format(self.sps_scaling_list_data_present_flag))
            if self.sps_scaling_list_data_present_flag:
                print (self.t+'\t\t','TODO')
        print (self.t+'amp_enabled_flag {}'.format(self.amp_enabled_flag))
        print (self.t+'sample_adaptive_offset_enabled_flag {}'.format(self.sample_adaptive_offset_enabled_flag))
        print (self.t+'pcm_enabled_flag {}'.format(self.pcm_enabled_flag))
        if self.pcm_enabled_flag:
            print (self.t+'\t','pcm_sample_bit_depth_luma_minus1 {}'.format(self.pcm_sample_bit_depth_luma_minus1))
            print (self.t+'\t','pcm_sample_bit_depth_chroma_minus1 {}'.format(self.pcm_sample_bit_depth_chroma_minus1))
            print (self.t+'\t','log2_min_pcm_luma_coding_block_size_minus3 {}'.format(self.log2_min_pcm_luma_coding_block_size_minus3))
            print (self.t+'\t','log2_diff_max_min_pcm_luma_coding_block_size {}'.format(self.log2_diff_max_min_pcm_luma_coding_block_size))
            print (self.t+'\t','pcm_loop_filter_disabled_flag {}'.format(self.pcm_loop_filter_disabled_flag))
        print (self.t+'num_short_term_ref_pic_sets {}'.format(self.num_short_term_ref_pic_sets))
        for idx in range(len(self.short_term_ref_pic_set)):
            print (self.t+'\t','short_term_ref_pic_set[{}] {}'.format(idx, self.short_term_ref_pic_set[idx]))
        print (self.t+'long_term_ref_pics_present_flag {}'.format(self.long_term_ref_pics_present_flag))
        if self.long_term_ref_pics_present_flag:
            print (self.t+'\t','num_long_term_ref_pics_sps {}'.format(self.num_long_term_ref_pics_sps))
            for idx in range(len(self.num_long_term_ref_pics_sps)):
                print (self.t+'\t\t','lt_ref_pic_poc_lsb_sps[{}] {}'.format(idx, self.lt_ref_pic_poc_lsb_sps[idx]))
                print (self.t+'\t\t','used_by_curr_pic_lt_sps_flag[{}] {}'.format(idx, self.used_by_curr_pic_lt_sps_flag[idx]))
        print (self.t+'sps_temporal_mvp_enabled_flag {}'.format(self.sps_temporal_mvp_enabled_flag))
        print (self.t+'strong_intra_smoothing_enabled_flag {}'.format(self.strong_intra_smoothing_enabled_flag))
        print (self.t+'vui_parameters_present_flag {}'.format(self.vui_parameters_present_flag))
        if self.vui_parameters_present_flag:
            self.vui_parameters.show()
        print (self.t+'sps_extension_flag {}'.format(self.sps_extension_flag))
