import pandas as pd
import os
import sys


colors = ['red', 'green', 'white', 'yellow', 'blue']
nationalities = ['brit', 'swede', 'dane', 'norwegian', 'german']
pets = ['dog', 'bird', 'cat', 'horse', 'fish']
drinks = ['tea', 'coffee', 'milk', 'beer', 'water']
smokes = ['pallmall', 'dunhill', 'blends', 'bluemasters', 'prince']

letter_mapping = {'c':0, 'n':1, 'p':2, 'd':3, 's':4}

def next_to(p1, p2):
    # encodes the condition that p1 is next to p2
    to_ret = []
    for i in range(1, 6):
        for j in range(1, 6):
            if abs(i-j) == 1:
                continue
            to_ret.append((p1+str(i),p2+str(j)))
    return to_ret

def condition(p1, p2):
    # encodes the condition that p1 and p2 belong to the same household
    to_ret = []
    negate_ = int(p2[1])
    prop = p2[0]
    for house in range(1, 6):
        for idx in range(1, 6):
            if idx == negate_:
                continue
            to_ret.append((p1+str(house),prop+str(idx)+str(house)))
    return to_ret

def invert(dnf):    
    # converts a not(dnf) to cnf
    final = []
    for p in dnf:
        # for p in x:
        final.append(['!'+p[0], '!'+p[1]])    
    return final

def conditions():
    # Brit lives in the red house = brit not in green and brit not in white and  ...
    brit_red = condition('n1', 'c1')
    # Swede keeps dogs as pets = swede does not keep bird and swede does not keep cat and ...    
    swede_dog = condition('n2', 'p1')
    # Dane drinks tea = dane does not drink coffee and dane does not drink milk and ...    
    dane_tea = condition('n3', 'd1')    
    # Green house is on the left of the white house = NOT(green house on the right of the white house)
    green_white = [('c31', 'c22'), ('c31', 'c23'), ('c31', 'c24'), ('c31', 'c25'), ('c32', 'c23'), ('c32', 'c24'), ('c32', 'c25'),
                    ('c33', 'c21'), ('c33', 'c24'), ('c33', 'c25'),
                    ('c34', 'c21'), ('c34', 'c22'), ('c34', 'c25'),
                    ('c35', 'c21'), ('c35', 'c22'), ('c35', 'c23')]    
    # Green house owner drinks coffee = green house owner does not drink tea and green house owner does not drink milk and ...    
    green_coffee = condition('c2', 'd2')
    # Person who smokes Pall Mall rears birds = Person who smokes pall malls does not rear dogs and Person who smokes pall malls does not rear cats and ...    
    pallmall_bird = condition('s1', 'p2')
    # Owner of the yellow house smokes Dunhill = Owner of the yellow house does not smoke pall mall and Owner of the yellow house does not smoke blends and ...    
    yellow_dunhill = condition('c4', 's2')
    # Man living in the centre drinks milk
    centre_milk = [['d33']]
    # Norwegian lives in the first house
    norwegian_first = [['n41']]
    # Man who smokes Blends lives next to the one who keeps cats = NOT(Man who smokes blends lives next to the one who keeps dogs) and NOT()
    blends_cat = next_to('s3', 'p3')                  
    # Man who keeps the horse lives next to the man who smokes Dunhill = NOT(Man who keeps horse lives next to pallmall) and 
    horse_dunhill = next_to('p4', 's2')
    # The owner who smokes Bluemasters drinks beer = The owner who smokes bluemasters does not drink tea and The owner who smokes bluemasters does not drink coffee and ...    
    bluemasters_beer = condition('s4', 'd4')
    # German smokes Prince = German does not smoke pall mall and German does not smoke blends and ...    
    german_prince = condition('n5', 's5')
    # Norwegian lives next to the blue house = NOT(norweigan not next to blue house)
    norwegian_blue = next_to('n4', 'c5')
    # norwegian_blue = [['c52']]
    # Man who smokes Blends has a neighbour who drinks water
    blends_water = next_to('s3', 'd5')

    # invert the negations of the statements
    to_invert = [brit_red, swede_dog, dane_tea, green_white, green_coffee, pallmall_bird, yellow_dunhill, bluemasters_beer, german_prince, blends_cat, horse_dunhill, norwegian_blue, blends_water]
    
    cnfs = [invert(dnf) for dnf in to_invert]
    to_ret = centre_milk + norwegian_first
    for c in cnfs:
        to_ret += c    
    return to_ret


def exactly_one(elems):
    # generate clauses which ensure that each element is picked exactly once
    # atleast one
    l = [elems]
    n = len(elems)
    # not more than one
    for i in range(n):
        for j in range(i+1, n):
                l.append(['!'+elems[i], '!'+elems[j]])
    return l

def exactly_one_group(letter, u, v):
    # generate all the clauses for a group of variables
    l = []
    for i in range(1, u+1):
        row_major = []
        for j in range(1, v+1):
            row_major.append(letter+str(i)+str(j))
        l += exactly_one(row_major)
        col_major = []
        for j in range(1, v+1):
            col_major.append(letter+str(j)+str(i))
        l += exactly_one(col_major)
    return l

def all_groups():
    l = []
    l += exactly_one_group('c', 5, 5)
    l += exactly_one_group('n', 5, 5)
    l += exactly_one_group('p', 5, 5)
    l += exactly_one_group('d', 5, 5)
    l += exactly_one_group('s', 5, 5)
    return l

def convert_to_ints(list_of_clauses):    
    # converts the props to integers for DIMACS format
    final = []
    for l in list_of_clauses:
        temp = []
        for elem in l:
            if elem[0] == '!':
                idx = 5*5*letter_mapping[elem[1]] + 5*(int(elem[2])-1) + (int(elem[3])-1)
                temp.append(-idx-1)
            else:
                idx = 5*5*letter_mapping[elem[0]] + 5*(int(elem[1])-1) + (int(elem[2])-1)
                temp.append(idx+1)
        final.append(temp)
    return final
    

def final_string(path='einstein.cnf'):
    # generate the final string for DIMACS format
    all_clauses = convert_to_ints(all_groups())
    all_clauses += convert_to_ints(conditions())
    vars = set()
    formulas = ''
    num_clauses = len(all_clauses)
    for l in all_clauses:
        for elem in l:
            formulas += str(elem) + ' '
            vars.add(abs(elem))
        formulas += '0\n'
    final = 'c Einstein encoding\n' + 'p cnf ' + str(len(vars)) + ' ' + str(num_clauses) + '\n' + formulas
    with open(path, 'w') as f:
        f.write(final)


def decode_result(path):
    # decode the result from the SAT solver
    with open(path, 'r') as f:
        ans = f.read()    
    ans = ans.strip().split(' ')
    # idx where split = 1
    idx = [int(x)-1 for i, x in enumerate(ans) if int(x) > 0]
    group = [(i//25, (i%25)//5, i%5) for i in idx]
    # make a dataframe and assign the values
    df = pd.DataFrame(index=range(1,6), columns=range(1,6))
    idx_to_list_map = {0:colors, 1:nationalities, 2:pets, 3:drinks, 4:smokes}
    for g in group:
        cat = idx_to_list_map[g[0]]
        df.iloc[g[0], g[2]] = cat[g[1]]
    df.to_csv('einstein_solution.csv')
    print(df)

if __name__ == "__main__":  
    task = sys.argv[1]
    if task == 'encode':      
        final_string()
    elif task == 'decode':
        if os.path.exists('einstein_solution.txt'):
            decode_result(path='einstein_solution.txt')
        else:
            print('Cannot find the solution file einstein_solution.txt')
    else:
        print('Invalid task')