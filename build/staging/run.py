import os
import subprocess

root_dir = os.getcwd()

for impl in ['original', 'tensile']:
    impl_dir = root_dir + '/' + impl
    #for order in ['R', 'C']:
    for order in ['R']:
        order_dir = impl_dir + '/' + order
        for a in ['N', 'T']:
            # for b in ['N', 'T']:
            for b in ['N']:
                trans_dir = order_dir + '/' + a + b
#                for size in ['MIXED', 'M64', 'N64', 'K64', 'MN64', 'MK64', 'NK64', 'MNK64']:
#                    size_dir = trans_dir + '/' + size

                work_dir = trans_dir

                if not os.path.exists(work_dir):
                    os.makedirs(work_dir)
                os.chdir(work_dir)
                outputs = 'kernels-perf.log'
                if not os.path.exists(work_dir + '/' + outputs):
                    outputs_file = open(outputs, "wb")
                    environ = {'LD_PRELOAD': impl_dir + '/libclBLAS.so'}
                    command = [root_dir + '/test-performance', '-a', a, '-b', b, '-o', order]
#                    command = [root_dir + '/test-performance', '-mnk', size, '-a', a, '-b', b, '-o', order]

                    print('DIR: ' + work_dir)
                    subprocess.check_call(command, stderr=outputs_file, stdout=outputs_file, env=environ)
