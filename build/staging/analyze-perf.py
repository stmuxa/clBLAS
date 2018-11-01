import glob

for filename in glob.glob('*.log'):
    with open(filename) as f:
        lines = f.readlines()
        test_name = ''
        test_perf = ''
        test_params = ''
        for line in lines:
            line = line.strip()
            if line.find('RUN') >= 0:
                test_name_start_index = line.find('] ')
                test_name = line[test_name_start_index + 2:]
            if line.find('PARAMS') >= 0:
                test_params_start_index = line.find(': ')
                test_params = line[test_params_start_index + 2:]
            if line.find('GFLOPS') >= 0:
                test_perf_start_index = line.find(': ')
                test_perf = line[test_perf_start_index + 2:]
                print(test_name + ',' + test_perf + ',' + test_params)
