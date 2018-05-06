from .bitstring import BitStream, pack

class processScalingListData(object):
    def __init__(self, s):
        self.scaling_list_pred_mode_flag = [None] * 4
        self.scaling_list_pred_matrix_id_delta = [None] * 4
        self.scaling_list_dc_coef_minus8 = [None] * 2
        self.scaling_list_delta_coef = [None] * 4

        for sizeId in range(4):
            if sizeId == 3:
                self.scaling_list_pred_mode_flag[sizeId] = [None] * 2
                self.scaling_list_pred_matrix_id_delta[sizeId] = [None] * 2
                self.scaling_list_dc_coef_minus8[sizeId-2] = [None] * 2
                self.scaling_list_delta_coef[sizeId] = [None] * 2
            else:
                self.scaling_list_pred_mode_flag[sizeId] = [None] * 6
                self.scaling_list_pred_matrix_id_delta[sizeId] = [None] * 6
                self.scaling_list_delta_coef[sizeId] = [None] * 6
                if sizeId >= 2:
                  self.scaling_list_dc_coef_minus8[sizeId-2] = [None] * 6
            

            for matrixId in range(2 if sizeId == 3 else 6):
              self.scaling_list_pred_mode_flag[sizeId][matrixId] = s.read('uint:1');
              if not self.scaling_list_pred_mode_flag[sizeId][matrixId]:
                  self.scaling_list_pred_matrix_id_delta[sizeId][matrixId] = s.read('ue');
              else:
                  nextCoef = 8;
                  coefNum = min(64, pow(4,sizeId+2));
                  if sizeId > 1:
                      self.scaling_list_dc_coef_minus8[sizeId-2][matrixId] = s.read('ue');

                  self.scaling_list_delta_coef[sizeId][matrixId] = [None] * coefNum;
                  for i in range(coefNum):
                      self.scaling_list_delta_coef[sizeId][matrixId][i] = s.read('ue');

    def bs(self):
        new_bs = BitStream()
        for matrixId in range(2 if sizeId == 3 else 6):
            new_bs += pack('uint:1', self.scaling_list_pred_mode_flag[sizeId][matrixId])
            if not self.scaling_list_pred_mode_flag[sizeId][matrixId]:
                new_bs += pack('ue', self.scaling_list_pred_matrix_id_delta[sizeId][matrixId])
            else:
                nextCoef = 8;
                coefNum = min(64, pow(4,sizeId+2));
                if sizeId > 1:
                    new_bs += pack('ue', self.scaling_list_dc_coef_minus8[sizeId-2][matrixId])

                for i in range(coefNum):
                    new_bs += pack('ue', self.scaling_list_delta_coef[sizeId][matrixId][i])
        return new_bs
            

    def show(self):
        """
        """
