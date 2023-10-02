## Description

*main.cpp* contains the main SAT solver code.

*einstein_prob.py* contains the function for generating the CNF encoding of the Einstein puzzle and a function to convert the SAT solution to a table.

*generate_random.py* contains functions for generating random 3-SAT instances and plotting the results

## Instructions for Part 1

1. Compile the code by running `g++ -std=c++14 main.cpp`
2. Encode the Einstein problem by running `python einstein_prob.py encode`. This will dump a cnf file called *einstein.cnf* which will be used by the SAT solver in the next stage.
3. Run the executable `./a.out x` to run the SAT solver. x = 0 uses the random heuristic to randomly pick a proposition at each stage of the DPLL, x = 1 uses the 2-clause heuristic while x = 2 uses the custom heuristic defined in the report e.g. `./a.out 1` will use the 2-clause heuristic to pick literals. If x is not specified, the program uses the random heuristic by default. The satisfying assignment of literals is dumped in a file called *einstein_solution.txt*.
4. Decode the solution by running `python einstein_prob.py decode`, which will output a Pandas dataframe with the required solution.

## Instructions for Part 2

1. Compile the code by running `g++ -std=c++14 main.cpp`
2. Generate random instances by running `python generate_random.py` and uncommenting the code in __main__
3. Run `./a.out` to run random, 2-clause and custom heuristic on the random 3-clause CNF problems
4. Plot the results using various functions in *generate_random.py*