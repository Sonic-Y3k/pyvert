from .bitstring import BitStream, pack
from .processHrdParameters import processHrdParameters

class processVuiParameters(object):
    def __init__(self, s, sps_max_sub_layers_minus1):
        self.t = '\t\t'
        
        self.aspect_ratio_info_present_flag = s.read('uint:1')
        if self.aspect_ratio_info_present_flag:
            self.aspect_ratio_idc = s.read('uint:8')
            if self.aspect_ratio_idc == 255:
                self.sar_width = s.read('uint:16')
                self.sar_height = s.read('uint:16')
        
        self.overscan_info_present_flag = s.read('uint:1')
        if self.overscan_info_present_flag:
            self.overscan_appropriate_flag = s.read('uint:1')
        
        
        self.video_signal_type_present_flag = s.read('uint:1')
        if self.video_signal_type_present_flag:
            self.video_format = s.read('uint:3')
            self.video_full_range_flag = s.read('uint:1')
            self.colour_description_present_flag = s.read('uint:1')
            
            if self.colour_description_present_flag:
                self.colour_primaries = s.read('uint:8')
                self.transfer_characteristics = s.read('uint:8')
                self.matrix_coeffs = s.read('uint:8')
        
        self.chroma_loc_info_present_flag = s.read('uint:1')
        if self.chroma_loc_info_present_flag:
            self.chroma_sample_loc_type_top_field = s.read('ue')
            self.chroma_sample_loc_type_bottom_field = s.read('ue')
        
        self.neutral_chroma_indication_flag = s.read('uint:1')
        self.field_seq_flag = s.read('uint:1')
        self.frame_field_info_present_flag = s.read('uint:1')
        self.default_display_window_flag = s.read('uint:1')

        if self.default_display_window_flag:
            self.def_disp_win_left_offset = s.read('ue')
            self.def_disp_win_right_offset = s.read('ue')
            self.def_disp_win_top_offset = s.read('ue')
            self.def_disp_win_bottom_offset = s.read('ue')
        
        self.vui_timing_info_present_flag = s.read('uint:1')
        if self.vui_timing_info_present_flag:
            self.vui_num_units_in_tick = s.read('uint:32')
            self.vui_time_scale = s.read('uint:32')
            self.vui_poc_proportional_to_timing_flag = s.read('uint:1')
            
            if self.vui_poc_proportional_to_timing_flag:
                self.vui_num_ticks_poc_diff_one_minus1 = s.read('ue')
            
            self.vui_hrd_parameters_present_flag = s.read('uint:1')
            
            if self.vui_hrd_parameters_present_flag:
                self.hrd_parameters = processHrdParameters(s, 1, sps_max_sub_layers_minus1)

        self.bitstream_restriction_flag = s.read('uint:1')
        if self.bitstream_restriction_flag:
            self.tiles_fixed_structure_flag = s.read('uint:1')
            self.motion_vectors_over_pic_boundaries_flag = s.read('uint:1')
            self.restricted_ref_pic_lists_flag = s.read('uint:1')
            self.min_spatial_segmentation_idc = s.read('ue')
            self.max_bytes_per_pic_denom = s.read('ue')
            self.max_bits_per_min_cu_denom = s.read('ue')
            self.log2_max_mv_length_horizontal = s.read('ue')
            self.log2_max_mv_length_vertical = s.read('ue')

    def bs(self):
        new_bs = BitStream()
        
        new_bs += pack('uint:1', self.aspect_ratio_info_present_flag)
        if self.aspect_ratio_info_present_flag:
            new_bs += pack('uint:8', self.aspect_ratio_idc)
            if self.aspect_ratio_idc == 255:
                new_bs += pack('uint:16', self.sar_width)
                new_bs += pack('uint:16', self.sar_height)
        
        new_bs += pack('uint:1', self.overscan_info_present_flag)
        if self.overscan_info_present_flag:
            new_bs += pack('uint:1', self.overscan_appropriate_flag)
        
        
        new_bs += pack('uint:1', self.video_signal_type_present_flag)
        if self.video_signal_type_present_flag:
            new_bs += pack('uint:3', self.video_format)
            new_bs += pack('uint:1', self.video_full_range_flag)
            new_bs += pack('uint:1', self.colour_description_present_flag)
            
            if self.colour_description_present_flag:
                new_bs += pack('uint:8', self.colour_primaries)
                new_bs += pack('uint:8', self.transfer_characteristics)
                new_bs += pack('uint:8', self.matrix_coeffs)
        
        new_bs += pack('uint:1', self.chroma_loc_info_present_flag)
        if self.chroma_loc_info_present_flag:
            new_bs += pack('ue', self.chroma_sample_loc_type_top_field)
            new_bs += pack('ue', self.chroma_sample_loc_type_bottom_field)
        
        new_bs += pack('uint:1', self.neutral_chroma_indication_flag)
        new_bs += pack('uint:1', self.field_seq_flag)
        new_bs += pack('uint:1', self.frame_field_info_present_flag)
        new_bs += pack('uint:1', self.default_display_window_flag)

        if self.default_display_window_flag:
            new_bs += pack('ue', self.def_disp_win_left_offset)
            new_bs += pack('ue', self.def_disp_win_right_offset)
            new_bs += pack('ue', self.def_disp_win_top_offset)
            new_bs += pack('ue', self.def_disp_win_bottom_offset)
            
        new_bs += pack('uint:1', self.vui_timing_info_present_flag)
        if self.vui_timing_info_present_flag:
            new_bs += pack('uint:32', self.vui_num_units_in_tick)
            new_bs += pack('uint:32', self.vui_time_scale)
            new_bs += pack('uint:1', self.vui_poc_proportional_to_timing_flag)
            
            if self.vui_poc_proportional_to_timing_flag:
                new_bs += pack('ue', self.vui_num_ticks_poc_diff_one_minus1)
            
            new_bs += pack('uint:1', self.vui_hrd_parameters_present_flag)
            
            if self.vui_hrd_parameters_present_flag:
                new_bs += self.hrd_parameters.bs()

        new_bs += pack('uint:1', self.bitstream_restriction_flag)
        if self.bitstream_restriction_flag:
            new_bs += pack('uint:1', self.tiles_fixed_structure_flag)
            new_bs += pack('uint:1', self.motion_vectors_over_pic_boundaries_flag)
            new_bs += pack('uint:1', self.restricted_ref_pic_lists_flag)
            new_bs += pack('ue', self.min_spatial_segmentation_idc)
            new_bs += pack('ue', self.max_bytes_per_pic_denom)
            new_bs += pack('ue', self.max_bits_per_min_cu_denom)
            new_bs += pack('ue', self.log2_max_mv_length_horizontal)
            new_bs += pack('ue', self.log2_max_mv_length_vertical)
        return new_bs

    def show(self):
        print (self.t+'aspect_ratio_info_present_flag {}'.format(self.aspect_ratio_info_present_flag))
        if self.aspect_ratio_info_present_flag:  
            print (self.t+'\taspect_ratio_idc {}'.format(self.aspect_ratio_idc))
            if self.aspect_ratio_idc == 255:
                print (self.t+'\t\tsar_width {}'.format(self.sar_width))
                print (self.t+'\t\tsar_height {}'.format(self.sar_height))
        print (self.t+'overscan_info_present_flag {}'.format(self.overscan_info_present_flag))
        if self.overscan_info_present_flag:
            print (self.t+'\toverscan_appropriate_flag {}'.format(self.overscan_appropriate_flag))
        
        print (self.t+'video_signal_type_present_flag {}'.format(self.video_signal_type_present_flag))
        if self.video_signal_type_present_flag:
            print (self.t+'\tvideo_format {}'.format(self.video_format))
            print (self.t+'\tvideo_full_range_flag {}'.format(self.video_full_range_flag))
            print (self.t+'\tcolour_description_present_flag {}'.format(self.colour_description_present_flag))
            if self.colour_description_present_flag:
                print (self.t+'\t\tcolour_primaries {}'.format(self.colour_primaries))
                print (self.t+'\t\ttransfer_characteristics {}'.format(self.transfer_characteristics))
                print (self.t+'\t\tmatrix_coeffs {}'.format(self.matrix_coeffs))
        print (self.t+'chroma_loc_info_present_flag {}'.format(self.chroma_loc_info_present_flag))
        if self.chroma_loc_info_present_flag:
            print (self.t+'\tchroma_sample_loc_type_top_field {}'.format(self.chroma_sample_loc_type_top_field))
            print (self.t+'\tchroma_sample_loc_type_bottom_field {}'.format(self.chroma_sample_loc_type_bottom_field))
        print (self.t+'neutral_chroma_indication_flag {}'.format(self.neutral_chroma_indication_flag ))
        print (self.t+'field_seq_flag {}'.format(self.field_seq_flag))
        print (self.t+'frame_field_info_present_flag {}'.format(self.frame_field_info_present_flag))
        print (self.t+'default_display_window_flag {}'.format(self.default_display_window_flag))
        if self.default_display_window_flag:
            print (self.t+'\tdef_disp_win_left_offset {}'.format(self.def_disp_win_left_offset))
            print (self.t+'\tdef_disp_win_right_offset {}'.format(self.def_disp_win_right_offset))
            print (self.t+'\tdef_disp_win_top_offset {}'.format(self.def_disp_win_top_offset))
            print (self.t+'\tdef_disp_win_bottom_offset {}'.format(self.def_disp_win_bottom_offset))
        print (self.t+'vui_timing_info_present_flag {}'.format(self.vui_timing_info_present_flag))
        if self.vui_timing_info_present_flag:
            print (self.t+'\tvui_num_units_in_tick {}'.format(self.vui_num_units_in_tick))
            print (self.t+'\tvui_time_scale {}'.format(self.vui_time_scale))
            print (self.t+'\tvui_poc_proportional_to_timing_flag {}'.format(self.vui_poc_proportional_to_timing_flag))
            if self.vui_poc_proportional_to_timing_flag:
                print (self.t+'\t\tvui_num_ticks_poc_diff_one_minus1 {}'.format(self.vui_num_ticks_poc_diff_one_minus1))
            print (self.t+'\tvui_hrd_parameters_present_flag {}'.format(self.vui_hrd_parameters_present_flag))
            if self.vui_hrd_parameters_present_flag:
                self.hrd_parameters.show()
        print (self.t+'bitstream_restriction_flag {}'.format(self.bitstream_restriction_flag))
        if self.bitstream_restriction_flag:
            print (self.t+'\ttiles_fixed_structure_flag {}'.format(self.tiles_fixed_structure_flag))
            print (self.t+'\tmotion_vectors_over_pic_boundaries_flag {}'.format(self.motion_vectors_over_pic_boundaries_flag))
            print (self.t+'\trestricted_ref_pic_lists_flag {}'.format(self.restricted_ref_pic_lists_flag))
            print (self.t+'\tmin_spatial_segmentation_idc {}'.format(self.min_spatial_segmentation_idc))
            print (self.t+'\tmax_bytes_per_pic_denom {}'.format(self.max_bytes_per_pic_denom))
            print (self.t+'\tmax_bits_per_min_cu_denom {}'.format(self.max_bits_per_min_cu_denom))
            print (self.t+'\tlog2_max_mv_length_horizontal {}'.format(self.log2_max_mv_length_horizontal))
            print (self.t+'\tlog2_max_mv_length_vertical {}'.format(self.log2_max_mv_length_vertical))
