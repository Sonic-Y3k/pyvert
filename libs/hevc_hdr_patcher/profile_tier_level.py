from .bitstring import BitStream, pack

class profile_tier_level(object):
    def __init__(self, s, sps_max_sub_layers_minus1):
        self.t = '\t\t'
        self.sps_max_sub_layers_minus1 = sps_max_sub_layers_minus1 
        self.general_profile_space = s.read('uint:2')
        self.general_tier_flag = s.read('uint:1')
        self.general_profile_idc = s.read('uint:5')

        self.general_profile_compatibility_flag = [None] * 32
        for idx in range(32):
            self.general_profile_compatibility_flag[idx] = s.read('uint:1')
        
        self.general_progressive_source_flag = s.read('uint:1')
        self.general_interlaced_source_flag = s.read('uint:1')
        self.general_non_packed_constraint_flag = s.read('uint:1')
        self.general_frame_only_constraint_flag = s.read('uint:1')
        self.garbage1 = s.read('uint:44')
        self.general_level_idc = s.read('uint:8')
        
        self.sub_layer_profile_present_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_level_present_flag = [None] * sps_max_sub_layers_minus1
        
        for idx in range(sps_max_sub_layers_minus1):
            sub_layer_profile_present_flag[idx] = s.read('uint:1')
            sub_layer_level_present_flag[idx] = s.read('uint:1')
        
        if sps_max_sub_layers_minus1 > 0:
            self.garbage1 = ""
            for idx in range(8-sps_max_sub_layers_minus1):
                self.garbage1 += s.read('uint:2')
        
        self.sub_layer_profile_space = [None] * sps_max_sub_layers_minus1
        self.sub_layer_tier_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_profile_idc = [None] * sps_max_sub_layers_minus1
        self.sub_layer_profile_compatibility_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_progressive_source_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_interlaced_source_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_non_packed_constraint_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_frame_only_constraint_flag = [None] * sps_max_sub_layers_minus1
        self.sub_layer_level_idc = [None] * sps_max_sub_layers_minus1
        
        for idx in range(sps_max_sub_layers_minus1):
            if self.sub_layer_profile_present_flag[idx]:
                self.sub_layer_profile_space[idx] = s.read('uint:2')
                self.sub_layer_tier_flag[idx] = s.read('uint:1')
                self.sub_layer_profile_idc[idx] = s.read('uint:5')
                self.sub_layer_profile_compatibility_flag[idx] = [None] * 32
                
                for jdx in range(32):
                    self.sub_layer_profile_compatibility_flag[idx][jdx] = s.read('uint:1')
                
                self.sub_layer_progressive_source_flag[idx] = s.read('uint:1')
                self.sub_layer_interlaced_source_flag[idx] = s.read('uint:1')
                self.sub_layer_non_packed_constraint_flag[idx] = s.read('uint:1')
                self.sub_layer_frame_only_constraint_flag[idx] = s.read('uint:1')
                self.garbage3 = s.read(44)
        
            if self.sub_layer_level_present_flag[idx]:
                self.sub_layer_level_idc[idx] = s.read('uint:8')
            else:
                self.sub_layer_level_idc[idx] = 1;

    def bs(self):
        new_bs = BitStream()
        new_bs += pack('uint:2', self.general_profile_space)
        new_bs += pack('uint:1', self.general_tier_flag)
        new_bs += pack('uint:5', self.general_profile_idc)

        for idx in range(32):
            new_bs += pack('uint:1', self.general_profile_compatibility_flag[idx])
        
        new_bs += pack('uint:1', self.general_progressive_source_flag)
        new_bs += pack('uint:1', self.general_interlaced_source_flag)
        new_bs += pack('uint:1', self.general_non_packed_constraint_flag)
        new_bs += pack('uint:1', self.general_frame_only_constraint_flag)
        new_bs += pack('uint:44', self.garbage1)
        new_bs += pack('uint:8', self.general_level_idc)
        
        for idx in range(self.sps_max_sub_layers_minus1):
            new_bs += pack('uint:1', self.sub_layer_profile_present_flag[idx])
            new_bs += pack('uint:1', self.sub_layer_level_present_flag[idx])
        
        if self.sps_max_sub_layers_minus1 > 0:
            new_bs += pack('uint:'+str(len(self.garbage2)), self.garbage2)
        
        for idx in range(self.sps_max_sub_layers_minus1):
            if self.sub_layer_profile_present_flag[idx]:
                new_bs += pack('uint:2', self.sub_layer_profile_space[idx])
                new_bs += pack('uint:1', self.sub_layer_tier_flag[idx])
                new_bs += pack('uint:5', self.sub_layer_profile_idc[idx])
                
                for jdx in range(32):
                    new_bs += pack('uint:1', self.sub_layer_profile_compatibility_flag[idx][jdx])
                
                new_bs += pack('uint:1', self.sub_layer_progressive_source_flag[idx])
                new_bs += pack('uint:1', self.sub_layer_interlaced_source_flag[idx])
                new_bs += pack('uint:1', self.sub_layer_non_packed_constraint_flag[idx])
                new_bs += pack('uint:1', self.sub_layer_frame_only_constraint_flag[idx])
                new_bs += pack('uint:44', self.garbage3)
        
            if self.sub_layer_level_present_flag[idx]:
                new_bs += pack('uint:8', self.sub_layer_level_idc[idx])
        return new_bs

    def show(self):
        print (self.t+'general_profile_space {}'.format(self.general_profile_space))
        print (self.t+'general_tier_flag {}'.format(self.general_tier_flag))
        print (self.t+'general_profile_idc {}'.format(self.general_profile_idc))
        
        print (self.t+'general_profile_compatibility_flag')
        for idx in range(4):
            print (self.t+'\t{0},{1},{2},{3},{4},{5},{6},{7}'.format(self.general_profile_compatibility_flag[0+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[1+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[2+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[3+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[4+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[5+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[6+(idx*(7+1))],
                                                                    self.general_profile_compatibility_flag[7+(idx*(7+1))]))
        print (self.t+'general_progressive_source_flag {}'.format(self.general_progressive_source_flag))
        print (self.t+'general_interlaced_source_flag {}'.format(self.general_interlaced_source_flag))
        print (self.t+'general_non_packed_constraint_flag {}'.format(self.general_non_packed_constraint_flag))
        print (self.t+'general_frame_only_constraint_flag {}'.format(self.general_frame_only_constraint_flag))
        print (self.t+'general_level_idc {}'.format(self.general_level_idc))
        print (self.t+'sub_layer_profile_present_flag {}'.format(self.sub_layer_profile_present_flag))
        print (self.t+'sub_layer_level_present_flag {}'.format(self.sub_layer_level_present_flag))

        for idx in range(self.sps_max_sub_layers_minus1):
            print (self.t+'sub_layer_profile_present_flag[{}] {}'.format(idx, self.sub_layer_profile_present_flag[idx]))
            print (self.t+'sub_layer_level_present_flag[{}] {}'.format(idx, self.sub_layer_level_present_flag[idx]))
            if self.sub_layer_profile_present_flag[idx]:
                print (self.t+'\t','sub_layer_profile_space[{}] {}'.format(idx, self.sub_layer_profile_space[idx]))
                print (self.t+'\t','sub_layer_tier_flag[{}] {}'.format(idx, self.sub_layer_tier_flag[idx]))
                print (self.t+'\t','sub_layer_profile_idc[{}] {}'.format(idx, self.sub_layer_profile_idc[idx]))
                
                print (self.t+'\t','sub_layer_profile_compatibility_flag[{}]'.format(idx))
                for jdx in range(4):
                    print (self.t+'\t\t{0},{1},{2},{3},{4},{5},{6},{7}'.format(self.sub_layer_profile_compatibility_flag[idx][0+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][1+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][2+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][3+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][4+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][5+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][6+(jdx*8)],
                                                                               self.sub_layer_profile_compatibility_flag[idx][7+(jdx*8)]))
                print (self.t+'\t','sub_layer_progressive_source_flag[{}] {}'.format(idx, self.sub_layer_progressive_source_flag[idx]))
                print (self.t+'\t','sub_layer_interlaced_source_flag[{}] {}'.format(idx, self.sub_layer_interlaced_source_flag[idx]))
                print (self.t+'\t','sub_layer_non_packed_constraint_flag[{}] {}'.format(idx, self.sub_layer_non_packed_constraint_flag[idx]))
                print (self.t+'\t','sub_layer_frame_only_constraint_flag[{}] {}'.format(idx, self.sub_layer_frame_only_constraint_flag[idx]))    
                print (self.t+'\t','sub_layer_level_idc[{}] {}'.format(idx, self.sub_layer_level_idc[idx]))
