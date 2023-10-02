import os
import random
import matplotlib.pyplot as plt
import numpy as np

random.seed(0)

N = 20
K = 3
L = 200
M = 100

def gen_random(N, K, L):    
    # generate random clauses
    clauses = []
    for i in range(L):
        clause = []
        for j in range(K):
            x = random.randint(1, N)
            if random.random() < 0.5:
                clause.append(-x)
            else:
                clause.append(x)
        clauses.append(clause)
    return clauses

def write_to_file(clauses, path):
    # write the clauses to a file
    with open(path, 'w') as f:
        f.write('p cnf {} {}\n'.format(N, len(clauses)))
        for clause in clauses:
            f.write(' '.join(map(str, clause)) + ' 0\n')


def run_exp():    
    for N in [100, 150, 200, 250, 300]:
        for ratio in [3 + x*0.2 for x in range(int((6-3)/0.2)+1)]:
            L = int(N * ratio)
            print('N = {}, L = {}'.format(N, L))
            # call the solver
            for solver in ['random', 'two', 'custom']:
                os.system('./a.out {} {} {}'.format(N, L, solver))

def read_results(solver):
    res_dir = 'results'
    res = {}
    for dir in os.listdir(res_dir):
        # check if dir
        if not os.path.isdir(os.path.join(res_dir, dir)):
            continue
        # get N and L
        N, L = map(int, dir.split('_'))
        # if N == 100:
        #     continue
        # get the result
        if N not in res:
            res[N] = {}
        if L not in res[N]:
            res[N][L] = []
        for file in os.listdir(os.path.join(res_dir, dir)):
            if file.endswith('.txt') and file.startswith(solver):
                with open(os.path.join(res_dir, dir, file), 'r') as f:
                    for line in f:
                        time, sat, splits = line.split()
                        res[N][L].append((float(time), sat, int(splits)))    
    # extract medians
    times_dict, splits_dict, prob_dict = {}, {}, {}
    for N, d in res.items():
        times_dict[N] = {}
        splits_dict[N] = {}
        prob_dict[N] = {}
        for L, l in d.items():            
            if not len(l):
                continue
            times = [x[0] for x in l]            
            med_time = sorted(times)[len(times)//2]/(10**6)            
            # med_time = sum(times)
            times_dict[N][L] = med_time
            sats = [x[1] for x in l]
            prob_dict[N][L] = sats.count("1")/len(sats)
            splits = [x[2] for x in l]
            med_splits = sorted(splits)[len(splits)//2]
            splits_dict[N][L] = med_splits

    
    return times_dict, splits_dict, prob_dict


def plot_results(times_dicts, splits_dicts, probs_dicts):
    # plot one graph for each N   
    for times_dict, splits_dict, probs_dict in zip(times_dicts, splits_dicts, probs_dicts): 
        for N, d in times_dict.items():        
            if N == 100:
                continue
            keys_sorted = np.array(sorted(d.keys()))
            vals = [d[k] for k in keys_sorted]
            keys_sorted = keys_sorted/N
            plt.plot(keys_sorted, vals, label='N = {}'.format(N), marker='o')
    # plt.yscale('log')
    plt.legend()
    # plt.title('Number of splits for custom heuristic\nfor random 3-SAT instances\n')
    plt.title('Time taken (s) for custom heuristic\nfor random 3-SAT instances\n')
    plt.xlabel('L/N')
    # plt.ylabel('Splits')
    plt.ylabel('Median time taken (s)')
    plt.show()

def plot_splits_time(times_dict, splits_dict):
    # plot one graph for each N       
    N = 150
    d = times_dict[N]
    fig, ax1 = plt.subplots()
    keys_sorted = np.array(sorted(d.keys()))
    times = [d[k] for k in keys_sorted]
    splits = [splits_dict[N][k] for k in keys_sorted]
    keys_sorted = keys_sorted/N
    ax1.plot(keys_sorted, times, label='Median time', marker='o')
    ax2 = ax1.twinx()
    ax2.plot(keys_sorted, splits, label='Median splits', marker='x')
    print(keys_sorted, splits, times)
    # plt.yscale('log')
    # ax1.legend()
    # ax2.legend()
    # plt.title('Number of splits for custom heuristic\nfor random 3-SAT instances\n')
    plt.title('Performance of custom heuristic\nfor random 3-SAT instances\nx - time, o - splits')
    ax1.set_xlabel('L/N')
    # plt.ylabel('Splits')
    ax1.set_ylabel('Median time taken (s)')
    ax2.set_ylabel('Median number of splits')
    plt.show()

def plot_prob(probs_dict):
    # plot one graph for each N
    c = {100: 'r', 150: 'g'}
    for N, d in probs_dict.items():
        # print(N)
        keys_sorted = sorted(d.keys())      
        # print(keys_sorted)  
        vals = [d[k] for k in keys_sorted]
        # print(vals, [x/N for x in keys_sorted])
        plt.plot([x/N for x in keys_sorted], vals, label='Empirical, N = {}'.format(N), marker='o', color=c[N])
        thoeretical = [np.exp(min(0, x*np.log(0.875) + N*np.log(2))) for x in keys_sorted]
        plt.plot([x/N for x in keys_sorted], thoeretical, label='Theoretical, N = {}'.format(N), marker='x', color=c[N])
    # plt.yscale('log')    
    plt.legend()
    plt.title('Probability of satisfiability\nfor random 3-SAT instances\n')
    plt.xlabel('L/N')
    plt.ylabel('Probability')
    plt.show()

def plot_ratio(times_dict, splits_dict, denom_times, denom_splits):
    # plot one graph for each N       
    N = 150
    d = times_dict[N]
    fig, ax1 = plt.subplots()
    keys_sorted = np.array(sorted(d.keys()))
    # remove 750
    keys_sorted = keys_sorted[keys_sorted != 750]
    times = [d[k]/denom_times[N][k] for k in keys_sorted]
    splits = [splits_dict[N][k]/denom_splits[N][k] for k in keys_sorted]
    keys_sorted = keys_sorted/N
    ax1.plot(keys_sorted, times, label='Median time', marker='o')
    ax2 = ax1.twinx()
    ax2.plot(keys_sorted, splits, label='Median splits', marker='x')
    print(keys_sorted, splits, times)
    # plt.yscale('log')
    plt.legend()
    # plt.title('Number of splits for custom heuristic\nfor random 3-SAT instances\n')
    plt.title('Ratio of performance of custom heuristic\nto 2-clause\n')
    ax1.set_xlabel('L/N')
    # plt.ylabel('Splits')
    ax1.set_ylabel('Ratio of time taken (s)')
    ax2.set_ylabel('Ratio of number of splits')
    plt.show()


if __name__ == '__main__':        
    times_dict_rand, splits_dict_rand, probs_dict_rand = read_results('random')    
    times_dict_two, splits_dict_two, probs_dict_two = read_results('two')
    times_dict_custom, splits_dict_custom, probs_dict_custom = read_results('custom')    
    # plot_splits_time(times_dict_custom, splits_dict_custom)
    # plot_ratio(times_dict_custom, splits_dict_custom, times_dict_rand, splits_dict_rand)
    # plot_ratio(times_dict_custom, splits_dict_custom, times_dict_two, splits_dict_two)
    # plot_prob(probs_dict_two)    
    
    
    # generate random instances
    # for N in [100, 150]:
    #     for ratio in [3 + x*0.2 for x in range(int((6-3)/0.2)+1)]:
    #         L = int(N * ratio)
    #         folder_path = os.path.join('examples', '{}_{}'.format(N, L))
    #         if not os.path.exists(folder_path):
    #             os.makedirs(folder_path)
    #         res_path = os.path.join('results', '{}_{}'.format(N, L))
    #         if not os.path.exists(res_path):
    #             os.makedirs(res_path)
    #         for i in range(M):
    #             clauses = gen_random(N, K, L)
    #             write_to_file(clauses, os.path.join(folder_path, '{}.cnf'.format(i)))
    # run_exp()