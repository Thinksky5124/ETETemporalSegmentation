###
 # @Author       : Thyssen Wen
 # @Date         : 2022-06-13 16:04:40
 # @LastEditors  : Thyssen Wen
 # @LastEditTime : 2023-10-07 20:28:21
 # @Description  : Test script
 # @FilePath     : /SVTAS/scripts/test.sh
### 

export CUDA_VISIBLE_DEVICES=1

python tools/launch.py  --mode test -c config/models/svtas-rl/svtas_rl_gtea.py
