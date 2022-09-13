from ortools.algorithms import pywrapknapsack_solver


def main():
    # Create the solver.
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')
    for i in range(1, 3):
        values = [
            i, 2
        ]
        weights = [[
            1, 3
        ]]
        capacities = [4]

        solver.Init(values, weights, capacities)
        computed_value = solver.Solve()

        packed_items = []
        packed_weights = []
        total_weight = 0
        print('Total value =', computed_value)
        for i in range(len(values)):
            if solver.BestSolutionContains(i):
                packed_items.append(i)
                packed_weights.append(weights[0][i])
                total_weight += weights[0][i]
        print('Total weight:', total_weight)
        print('Packed items:', packed_items)
        print('Packed_weights:', packed_weights)


if __name__ == '__main__':
    main()
