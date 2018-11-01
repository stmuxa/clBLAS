import os

ORIGINAL = 0
TENSILE = 1
SPEEDUP = 2
M   = 3
N   = 4
K   = 5
MN  = 6
MK  = 7
NK  = 8
MNK = 9

implementations = ['original', 'tensile']
headers = ['ORIGINAL', 'TENSILE', 'SPEEDUP', 'M', 'N', 'K', 'MN', 'MK', 'NK', 'MNK']


R = 0
C = 1
orders =  ['R', 'C']

NN = 0
NT = 1
TN = 2
TT = 3
transposes =  ['NN', 'NT', 'TN', 'TT']

MIXED = 0
M64   = 1
N64   = 2
K64   = 3
MN64  = 4
MK64  = 5
NK64  = 6
MNK64 = 7
sizes = ['MIXED', 'M64', 'N64', 'K64', 'MN64', 'MK64', 'NK64', 'MNK64']

data = []
root_dir = os.getcwd()

print('Processing log-files...')
for impl in implementations:
    impl_list = []
    impl_dir = root_dir + '/' + impl
    for order in orders:
        order_list = []
        order_dir = impl_dir + '/' + order
        for transpose in transposes:
            transpose_list = []
            trans_dir = order_dir + '/' + transpose
            print('\t\t' + impl + '/' + order + '/' + transpose)
            work_dir = trans_dir
            if os.path.exists(work_dir):
                os.chdir(work_dir)
                input = 'kernels-perf.log'

                with open(input) as f:
                    lines = f.readlines()
                    test_name = ''
                    test_perf = ''
                    test_params = ''
                    test_fallback = False
                    for line in lines:
                        line = line.strip()
                        if line.find('RUN') >= 0 and line.find('Generic') >= 0:
                            test_name_start_index = line.find('] ')
                            test_name = line[test_name_start_index + 2:]
                        if line.find('PARAMS') >= 0:
                            test_params_start_index = line.find(': ')
                            test_params = line[test_params_start_index + 2:]
                        if line.find('GFLOPS') >= 0:
                            test_perf_start_index = line.find(': ')
                            test_perf = line[test_perf_start_index + 2:]
                        if len(test_name) and len(test_perf) and len(test_params):
                            transpose_list.append([test_name, float(test_perf), test_params.replace('clblasRowMajor', 'R').replace('clblasColumnMajor', 'C').replace('clblasNoTrans', "N").replace('clblasTrans', 'T').replace('M =', '').replace('N =', '').replace('K =', '').replace(' ', '').split(',')[:6]])
                            test_name = ''
                            test_perf = ''
                            test_params = ''
            order_list.append(transpose_list)
        impl_list.append(order_list)
    data.append(impl_list)

os.chdir(root_dir)

NAME = 0
PERF = 1
PARAMS = 2
FALLBACK = 3

PEAK_PERF = 12583 # GFLOPS (VEGA10)

print('Processing data collected...')
import plotly
import plotly.graph_objs as go

tests_total = 0
tests_fallback = 0

tests_speedup_tensile_avg = 1
tests_speedup_total_avg = 0

for order_idx in [R]: # [R, C]
    order = orders[order_idx]
    for transpose_idx in [NN, TN]: # [NN, NT, TN, TT]
        transpose = transposes[transpose_idx]
        print('\t\t' + order + '/' + transpose)

        tensile_list  = data[TENSILE ][order_idx][transpose_idx]
        original_list = data[ORIGINAL][order_idx][transpose_idx]

        test_data = [[], [], [], [], [], [], [], [], [], []]
        o = ''
        a = ''
        b = ''
        for test_idx in range(0, len(original_list), 1):
            tensile_test  = tensile_list [test_idx]
            original_test = original_list[test_idx]

            [o, a, b, m, n, k] = original_test[PARAMS]
            m = float(m)
            n = float(n)
            k = float(k)

            tensile_perf  = tensile_test [PERF]
            original_perf = original_test[PERF]

            test_data[TENSILE].append(tensile_perf)
            test_data[ORIGINAL].append(original_perf)
            test_data[M].append(m)

        filename = root_dir + '/' + o + '_' + a + b + '.html'
        print('Writing file: ' + filename)
        plotly.offline.plot(
        {
            "data": [
                        go.Scatter(x = test_data[M], y = test_data[ORIGINAL], mode = 'markers', name = 'Before', marker = {'size' : 5}, opacity = 0.5),
                        go.Scatter(x = test_data[M], y = test_data[TENSILE], mode = 'markers', name = 'After', marker = {'size' : 5}, opacity = 0.5),
                    ],
            "layout": go.Layout(title = 'clBLAS DGEMM problem performance optimization: ' + o + '/' + a + b + ' (square matrices)', xaxis={'title': 'Matrix size'}, yaxis={'title': 'GFLOPs'}),
        },
        filename = filename, auto_open = False,)
