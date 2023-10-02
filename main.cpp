#include <vector>
#include <iostream>
#include <fstream>
#include <stack>
#include <set>
#include <cstdlib>
#include <map>
#include <ctime>
#include <chrono>
#include <cassert>

using namespace std;
using namespace std::chrono;

int global_dpll_splits = 0;

void printCNF(vector<set<int>> clauses){
    cout << "CNF: " << endl;
    for (auto c: clauses){
        for (auto l: c)
            cout << l << " ";
        cout << endl;
    }
}

class Solver
{
public:
    Solver(string path);
    ~Solver();

    int n, m;
    vector< set<int> > cnf_input;
    vector<int> assigned;

    int solver = 0;

    int FindUnitClause(vector<set<int>> cnf);
    bool EmptyClause(vector<set<int>> cnf);
    vector<set<int>> Simplify(vector<set<int>> cnf, int assignment);
    
    int SplittingRuleRandom(vector<set<int>> cnf);
    int SplittingRuleTwoClause(vector<set<int>> cnf);
    int SplittingRuleCustom(vector<set<int>> cnf);
    bool RecursiveDPLL(vector<set<int>> cnf);    
    
};

Solver::Solver(string path)
{
    srand(69);
    ifstream file(path);
    if (!file.is_open())
    {
        cout << "File not found" << endl;
        return;
    }
    string line;
    vector<int> tokens;
    this->cnf_input = vector< set<int> > ();
    for(string line; getline(file, line );)
    {
        if (line[0] == 'c')
            continue;
        else if (line[0] == 'p'){
            // split string into 4 words across spaces
            string word;
            vector<string> words;
            for(int i = 0; i < line.length(); i++){
                if(line[i] == ' '){
                    words.push_back(word);
                    word = "";
                }
                else{
                    word += line[i];
                }
            }
            words.push_back(word);
            this->n = stoi(words[2]);
            this->m = stoi(words[3]);
            assert (words[1] == "cnf");
            // cout << "n: " << this->n << endl;
            // cout << "m: " << this->m << endl;
        }
        else{
            string word;
            for(int i = 0; i < line.length(); i++){
                if(line[i] == ' '){
                    // cout << tokens << " space" << endl;
                    if (word.length() > 0){
                        tokens.push_back(stoi(word));
                        word = "";
                    }                        
                }                
                else if (line[i] == '\n'){
                    continue;
                }
                else{
                    word += line[i];
                }
            }
            tokens.push_back(stoi(word));
        }        
    }    
    // split tokens across 0
    set<int> cur_clause;
    for(int i = 0; i < tokens.size(); i++){
        if(tokens[i] == 0){
            this->cnf_input.push_back(cur_clause);
            cur_clause = set<int>();
        }
        else{
            cur_clause.insert(tokens[i]);
        }
    }
    if (cur_clause.size() > 0){
        this->cnf_input.push_back(cur_clause);
    }
    file.close();            
}

int Solver::FindUnitClause(vector<set<int>> cnf){
    for (auto clause : cnf) {
        if (clause.size() == 1)            
            return *clause.begin();        
    }
    return 0;
}

bool Solver::EmptyClause(vector<set<int>> cnf){
    for (auto clause : cnf) {
        if (clause.empty())            
            return true;
    }
    return false;
}


int Solver::SplittingRuleRandom(vector<set<int>> cnf){
    return *cnf[0].begin();
}

int Solver::SplittingRuleTwoClause(vector<set<int>> cnf){
    map<int, int> lit_count;
    for (auto clause : cnf) {
        if (clause.size() != 2)
            continue;
        for (int l : clause) {            
            lit_count[l] += 1;
        }
    }
    if (lit_count.empty())
        return SplittingRuleRandom(cnf);
    int max_lit = 0;
    int max_count = 0;
    for (auto it = lit_count.begin(); it != lit_count.end(); it++) {
        if (it->second > max_count) {
            max_lit = it->first;
            max_count = it->second;
        }
    }
    return max_lit;
}

// int Solver::SplittingRuleCustom(vector<set<int>> cnf){
//     // map<int, float> pos_lit_weight, neg_lit_weight;
//     // for (auto clause : cnf) {        
//     //     for (int l : clause) {
//     //         if (l > 0){
//     //             if (pos_lit_weight.find(l) == pos_lit_weight.end())
//     //                 pos_lit_weight[l] = 1.0;
//     //             else
//     //                 pos_lit_weight[l] += 1.0/(1 << clause.size());
//     //         }
//     //         else{
//     //             if (neg_lit_weight.find(l) == neg_lit_weight.end())
//     //                 neg_lit_weight[l] = 1.0;
//     //             else
//     //                 neg_lit_weight[l] += 1.0/(1 << clause.size());
//     //         }
//     //     }
//     // }
//     map<int, int> pos_lit_weight, neg_lit_weight;    
//     for (auto clause : cnf) {        
//         for (int l : clause) {
//             if (l > 0)                
//                 pos_lit_weight[l] += 1;            
//             else
//                 neg_lit_weight[l] += 1;
//         }
//     }
//     // check if some literal has only positive or only negative
//     for (auto it: pos_lit_weight) {
//         if (neg_lit_weight[-it.first] == 0)
//             return it.first;
//     }
//     for (auto it: neg_lit_weight) {
//         if (pos_lit_weight[-it.first] == 0)
//             return it.first;
//     }
//     // else sort them in descending order of absolute value of the difference between the weights
//     vector<pair<int, float>> diff;
//     for (auto it: pos_lit_weight) {
//         diff.push_back(make_pair(it.first, it.second - neg_lit_weight[it.first]));
//     }
//     // sort in descending order by absolute value
//     sort(diff.begin(), diff.end(), [](pair<int, float> a, pair<int, float> b) {
//         return abs(a.second) < abs(b.second);
//     });
//     if (pos_lit_weight[diff[0].first] > neg_lit_weight[diff[0].first])
//         return diff[0].first;
//     else
//         return -diff[0].first;    
// }

// int Solver::SplittingRuleCustom(vector<set<int>> cnf){
//     float gamma = 1;
//     map<int, float> h;
//     // for (int i = 1; i < n+1; i++){
//     //     h[i] = 1;
//     //     h[-i] = 1;  
//     // }
//     for (auto clause : cnf) {
//         for (auto l: clause)
//             h[l] += 1;
//     }
//     for (int i = 0; i < 2; i++){
//         float mu = 0;
//         map<int, float> h_new;
//         for (int i = 1; i < n+1; i++)
//             mu += h[i] + h[-i];
//         mu /= 2*n;
//         for (auto clause : cnf) {
//             if (clause.size() == 2){
//                 // get both literals
//                 int l1 = *clause.begin();
//                 int l2 = *clause.rbegin();
//                 // update h for l1
//                 h_new[l1] += gamma*h[-l2]/mu;
//                 h_new[l2] += gamma*h[-l1]/mu;
//             }
//             else{
//                 int c1 = *clause.begin();
//                 int c2 = *(++clause.begin());
//                 int c3 = *clause.rbegin();
//                 h_new[c1] += h[-c2]*h[-c3]/(mu*mu);
//                 h_new[c2] += h[-c1]*h[-c3]/(mu*mu);
//                 h_new[c3] += h[-c1]*h[-c2]/(mu*mu);
//             }
//         }
//         h = h_new;
//     }
//     // print h
//     // for (auto it: h) {
//     //     cout << it.first << " " << it.second << endl;
//     // }
//     // return largestvalue
//     float max_val = 0;
//     int max_lit = SplittingRuleRandom(cnf);
//     for (auto it: h) {
//         if (it.second > max_val){
//             max_val = it.second;
//             max_lit = it.first;
//         }
//     }
//     return max_lit;
// }

int Solver::SplittingRuleCustom(vector<set<int>> cnf){            
    int try_ = SplittingRuleTwoClause(cnf);
    if (try_ != 0)
        return try_;

    map<int, int> lit_count_three, lit_count_two;    
    for (auto clause : cnf) {
        // if (clause.size() == 2){
        //     for (int l : clause)          
        //         lit_count_two[l] += 1;                    
        // }
        // else{
        //     for (int l : clause)          
        //         lit_count_three[l] += 1;
        // }
        for (int l : clause)          
            lit_count_three[l] += 1;
        
    }

    int max_lit_3 = 0;
    int max_count_3 = 0;
    for (auto it: lit_count_three) {        
        if (it.second > max_count_3) {
            max_lit_3 = it.first;
            max_count_3 = it.second;
        }
    }
    return max_lit_3;
    // int max_lit_2 = 0;
    // int max_count_2 = 0;
    // for (auto it: lit_count_two) {        
    //     if (it.second > max_count_2) {
    //         max_lit_2 = it.first;
    //         max_count_2 = it.second;
    //     }
    // }

    // if (max_count_3 > 5*max_count_2)
    //     return max_lit_3;
    // else
    //     return max_lit_2;    
}


vector<set<int>> Solver::Simplify(vector<set<int>> cnf, int assignment) {
    // cout << "Assigning " << assignment << endl;
    // printCNF(cnf);
    
    vector<set<int>> simplifiedClauses;
    for (auto clause : cnf) {
        set<int> updated;
        bool is_ass = false;
        for (int l : clause) {
            if (l == assignment){
                is_ass = true;
                break;
            }                
            if (l != -assignment) {
                updated.insert(l);
            }
        }
        if (!is_ass)
            simplifiedClauses.push_back(updated);
    }
    // cout << "Updated:" << endl;
    // printCNF(simplifiedClauses);
    return simplifiedClauses;
}

bool Solver::RecursiveDPLL(vector<set<int>> cnf) {
    // if no clauses, always true
    if (cnf.empty()) {
        // cout << "No clauses left to satisfy" << endl;
        return true;
    }
    
    if (EmptyClause(cnf)) {
        // cout << "Empty clause present" << endl;
        return false;
    }
    // look for unit clauses
    int next_lit = FindUnitClause(cnf);
    int new_split = 0;
    if (next_lit == 0){
        new_split++;
        global_dpll_splits++;
        if (solver == 0)
            next_lit = SplittingRuleRandom(cnf);
        else if (solver == 1)
            next_lit = SplittingRuleTwoClause(cnf);
        else
            next_lit = SplittingRuleCustom(cnf);
    }        
    
    // cout << next_lit << endl;
    
    vector<set<int>> cnf_1 = Simplify(cnf, next_lit);
    assigned.push_back(next_lit);

    bool try1 = RecursiveDPLL(cnf_1);

    if (try1) {        
        return true;
    }
    else{
        assigned.pop_back();
        assigned.push_back(-next_lit);
        vector<set<int>> cnf_2 = Simplify(cnf, -next_lit);
        bool try_again = RecursiveDPLL(cnf_2);
        if (try_again)
            return true;
        else{
            assigned.pop_back();
            return false;
        }
    }
    
}

Solver::~Solver()
{
}

void exp_one(string input_path, string output_path, string solver_method){
    if (std::__fs::filesystem::exists(output_path)){
        cout << "Already done" << endl;
        return;
    } 
    float time;    
    Solver solver = Solver(input_path);
    if (solver_method == "random")
        solver.solver = 0;
    else if (solver_method == "two")
        solver.solver = 1;
    else if (solver_method == "custom")
        solver.solver = 2;
    else
        cout << "Couldn't detect solver; using default random solver" << endl;
    auto beg = high_resolution_clock::now();
    bool solvable = solver.RecursiveDPLL(solver.cnf_input);
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end - beg);
    time = duration.count();    
    // dump to file
    std::ofstream out(output_path);    
    out << time << " " << solvable << " " << global_dpll_splits << endl;
    global_dpll_splits = 0;

}

void exp(int N, int L, string solver_method){
    cout << "N = " << N << ", L = " << L << endl;       
    int M = 100;
    for (int i = 0; i < M; i++){        
        string inp = "examples/" + to_string(N) + "_" + to_string(L) + "/" + to_string(i) + ".cnf";
        string output = "results/" + to_string(N) + "_" + to_string(L) + "/" + solver_method + "_" + to_string(i) + ".txt";
        exp_one(inp, output, solver_method);
        if (i % 20 == 0)
            cout << i << endl;
    }    
}

void run_all(){
    vector<string> solvers = {"random", "two", "custom"};
    // vector<string> solvers = {"custom"};
    int N = 150;
    // for (int N = 100; N <= 300; N += 50){
        for (float ratio = 3; ratio <= 6; ratio += 0.2){
            int L = N * ratio;
            if (L % 10 == 9)
                L += 1;
            // if (N == 100 && L <= 400)
            //     continue;            
            // call the solver
            for (string solver: solvers){
                exp(N, L, solver);
            }
        }
    // }        
}

void run_150(){    
    int N = 150;
    // for (int N = 100; N <= 300; N += 50){
        for (float ratio = 6; ratio >= 3; ratio -= 0.2){
            int L = N * ratio;
            if (L % 10 == 9)
                L += 1;
            // if (N == 100 && L <= 400)
            //     continue;            
            // call the solver
            exp(N, L, "two");            
        }
    // }        
}

int main(int argc, char* argv[]){

    run_all();
    // run_150();


    // int N = stoi(argv[1]);
    // int L = stoi(argv[2]);
    // string solver = argv[3];
    // exp(N, L, solver);

    // Solver solver = Solver("examples/150_480/0.cnf");
    // // Solver solver = Solver(argv[1]);
    // if (argc > 2){
    //     string arg = argv[2];
    //     if (arg == "random")
    //         solver.solver = 0;
    //     else if (arg == "two")
    //         solver.solver = 1;
    //     else if (arg == "custom")
    //         solver.solver = 2;
    //     else
    //         cout << "Couldn't detect solver; using default random solver" << endl;            
    // }
        
    // time_t start = time(NULL);
    // // cout << start << endl;
    
    // bool solvable = solver.RecursiveDPLL(solver.cnf_input);
    // if (solvable){
    //     cout << "SAT" << endl << "Literals: " << endl;
    //     // std::ofstream out("einstein_solution.txt");
    //     sort(solver.assigned.begin(), solver.assigned.end());
    //     for (int l: solver.assigned){
    //         cout << l << " ";
    //         // out << l << " ";
    //     }            
    //     cout << endl;        
    // }
    // else{
    //     cout << "UNSAT" << endl;        
    // }
    // time_t end = time(NULL);
    // // cout << end << endl;
    // cout << "Time taken: " << end - start << endl;
    // cout << "Number of splits: " << global_dpll_splits << endl;
}

