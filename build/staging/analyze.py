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
            for size in sizes:
                size_list = []
                size_dir  = trans_dir + '/' + size
                if os.path.exists(size_dir):
                    os.chdir(size_dir)
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
                            if line.find('FALLBACK') >= 0:
                                test_fallback = True
                            if len(test_name) and len(test_perf) and len(test_params):
                                size_list.append([test_name, float(test_perf), test_params.replace('clblasRowMajor', 'R').replace('clblasColumnMajor', 'C').replace('clblasNoTrans', "N").replace('clblasTrans', 'T').replace('M =', '').replace('N =', '').replace('K =', '').replace(' ', '').split(',')[:6], test_fallback])
                                test_name = ''
                                test_perf = ''
                                test_params = ''
                                test_fallback = False
                    transpose_list.append(size_list)
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
#import plotly
#import plotly.graph_objs as go

for order_idx in [R, C]:
    order = orders[order_idx]
    for transpose_idx in [NN, NT, TN, TT]:
        transpose = transposes[transpose_idx]
        for size_idx in [MIXED, M64, N64, K64, MN64, MK64, NK64, MNK64]:
            size = sizes[size_idx]
            print('\t\t' + order + '/' + transpose + '/' + size)

            tensile_list  = data[TENSILE ][order_idx][transpose_idx][size_idx]
            original_list = data[ORIGINAL][order_idx][transpose_idx][size_idx]

            test_data = [[], [], [], [], [], [], [], [], [], []]
            o = ''
            a = ''
            b = ''
            for test_idx in range(0, len(original_list), 1):
                tensile_test  = tensile_list [test_idx]
                original_test = original_list[test_idx]

                tensile_perf  = tensile_test [PERF]
                original_perf = original_test[PERF]

                [o, a, b, m, n, k] = original_test[PARAMS]
                m = float(m)
                n = float(n)
                k = float(k)

                speedup = tensile_perf / original_perf
                tensile_peak  = tensile_perf  / PEAK_PERF
                original_peak = original_perf / PEAK_PERF
                test_data[TENSILE].append(tensile_perf)
                test_data[ORIGINAL].append(original_perf)
                test_data[SPEEDUP].append(speedup)
                test_data[M].append(m)
                test_data[N].append(n)
                test_data[K].append(k)
                test_data[MN].append(m + n)
                test_data[MK].append(m + k)
                test_data[NK].append(n + k)
                test_data[MNK].append(m + n + k)

            for plot_idx in [M, N, K, MN, MK, NK, MNK]:
                title = o + '/' + a + b + '/' + sizes[size_idx] + ' ' + headers[SPEEDUP] + '(' +  headers[plot_idx] + ')'
                y_data = test_data[SPEEDUP]
                x_data = test_data[plot_idx]
                min_val = min(y_data)
                max_val = max(y_data)
                le_data = []
                gt_data = []
                for point_idx0 in range(0, len(x_data), 1):
                    y_val0 = y_data[point_idx0]
                    x_val0 = x_data[point_idx0]
                    le_cnt = 0
                    gt_cnt = 0
                    le_avg = 0
                    gt_avg = 0

                    for point_idx1 in range(0, len(x_data), 1):
                        y_val1 = y_data[point_idx1]
                        x_val1 = x_data[point_idx1]
                        if x_val1 <= x_val0:
                            le_cnt += 1
                            le_avg += y_val1
                        if x_val1 >= x_val0:
                            gt_cnt += 1
                            gt_avg += y_val1

                    le_data.append(le_avg/le_cnt if le_cnt > 0 else min_val)
                    gt_data.append(gt_avg/gt_cnt if gt_cnt > 0 else max_val)
                # filename = root_dir + '/' + o + '_' + a + b + '_' + sizes[size_idx] + '_' + headers[plot_idx] + '.html'
                # print('Writing file: ' + filename)
                # plotly.offline.plot(
                # {
                #     "data": [
                #                 go.Scatter(x = x_data, y = y_data, mode = 'markers', name = 'Speedup', marker = {'size' : 5}, opacity = 0.5),
                #                 go.Scatter(x = x_data, y = le_data, mode = 'markers', name = 'Average less or equal', marker = {'size' : 10}),
                #                 #go.Scatter(x = x_data, y = eq_data, mode = 'markers', name = 'Average equal', marker = {'size' : 10}),
                #                 go.Scatter(x = x_data, y = gt_data, mode = 'markers', name = 'Average greater or equal' , marker = {'size' : 10}),
                #                 go.Scatter(x = [0, max(x_data)], y = [1, 1], mode = 'lines', name = '1', line = {'width' : 2}, opacity = 0.5),
                #             ],
                #     "layout": go.Layout(title = title),
                # },
                # filename = filename, auto_open = False,)
