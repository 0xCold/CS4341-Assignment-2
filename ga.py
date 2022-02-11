import math
import random
import argparse
import time

NUM_BINS = 4
MUTATION_ODDS = 1  # Odds out of 100 for an individual bin to mutate


# Get input from user
def parse_args():
    parser = argparse.ArgumentParser(description='Use a genetic algorithm to solve number allocation or tower building')
    parser.add_argument('puzzle', help='Puzzle to use the algorithm to solve [1 (Numbers), 2 (Towers)]')
    parser.add_argument('info', help='A file that contains the puzzle information')
    parser.add_argument('seconds', help='The number of seconds it has to find a solution')
    args = parser.parse_args()
    return int(args.puzzle), args.info, args.seconds


# Check if timer has run out, returns true is overtime, false otherwise
def timeRunOut(start, seconds):
    end = time.time()
    elapsed_time = end - start
    return elapsed_time > float(seconds)


# Generate random float values in [-10, 10] for use in the Bin puzzle
def genRandomNumberSets(length):
    rand_nums = []
    for _ in range(length):
        rand_nums.append(random.uniform(-10, 10))
    return rand_nums


# Divide the available float values into random bins
def genRandomBins(nums):
    nums_copy = list(nums)
    nums_per_bin = math.floor(len(nums_copy) / NUM_BINS)
    bins = []
    for bin_count in range(NUM_BINS):
        a_bin = []
        for bin_nums_count in range(int(nums_per_bin)):
            random.shuffle(nums_copy)
            a_bin.append(nums_copy.pop())
        bins.append(a_bin)
    return bins


# Calculate the fitness score for a set of bins
def calcBinsFitness(bins):
    bin_one_score = 1
    for num in bins[0]:
        bin_one_score *= num
    bin_two_score = 0
    for num in bins[1]:
        bin_two_score += num
    bin_three_score = max(bins[2]) - min(bins[2])
    return bin_one_score + bin_two_score + bin_three_score


# From a list of sets of bins, return the N best-scoring sets (by fitness), along with the remaining boards
def getAndPopBestNBinSets(bin_sets, n):
    best_bin_sets = []
    for _ in range(n):
        best_fitness = -1
        best_bin_set_index = 0
        for index, bins in enumerate(bin_sets):
            bin_set_fitness = calcBinsFitness(bins)
            if bin_set_fitness > best_fitness:
                best_fitness = bin_set_fitness
                best_bin_set_index = index
        best_bin_sets.append(bin_sets[best_bin_set_index])
        del bin_sets[best_bin_set_index]
    return [best_bin_sets, bin_sets]


# From a list of sets of bins, return the N worst-scoring sets (by fitness), along with the remaining boards
def getAndPopWorstNBinSets(bin_sets, n):
    worst_bin_sets = []
    for _ in range(n):
        worst_fitness = -1
        worst_bin_set_index = 0
        for index, bins in enumerate(bin_sets):
            bin_set_fitness = calcBinsFitness(bins)
            if bin_set_fitness < worst_fitness:
                worst_fitness = bin_set_fitness
                worst_bin_set_index = index
        worst_bin_sets.append(bin_sets[worst_bin_set_index])
        del bin_sets[worst_bin_set_index]
    return [worst_bin_sets, bin_sets]


# pass in culled list of bin sets
def assignSelection(bin_sets):
    bin_fitness = []

    # calculate bin fitness of 4 bins
    for bin_set in bin_sets:
        bin_fitness.append(calcBinsFitness(bin_set))

    min_bin_fitness = min(bin_fitness)
    if min_bin_fitness < 0:
        min_bin_fitness = abs(min_bin_fitness) + 1
        shifted_bin_fitness = []
        for bin_fit in bin_fitness:
            shifted_bin_fitness.append(bin_fit + min_bin_fitness)

        bin_fitness = shifted_bin_fitness

    # find sum of all fitness's
    sum_bin_fitness = sum(bin_fitness)
    print("SUM OF BIN FITNESS", sum_bin_fitness)
    print('\n')

    bin_selection = []
    total_percentage = 0
    for i in range(len(bin_sets)):
        cumulative_percentage = (bin_fitness[i] / sum_bin_fitness) + total_percentage
        total_percentage = cumulative_percentage
        selection_bin = (cumulative_percentage, bin_sets[i])
        bin_selection.append(selection_bin)
        # print(selection_bin)
        # print('\n')

    return bin_selection  # List of tuple + list: [(probability, [bin_set])]


# Randomly mutates bins in a list of bin sets, based on the mutation odds global variable
def mutateBins(bin_sets):
    # Loop for all bin sets
    for bin_set in bin_sets:
        # Loop for bins in a bin set
        for a_bin in bin_set:
            # Do mutation odds
            do_mutate = random.randint(0, 100) <= MUTATION_ODDS
            # If mutation is true, swap a random number in this bin with a number from a different, random bin
            if do_mutate:
                # Get mutator number and index
                mutator_num = random.choice(a_bin)
                mutator_index = a_bin.index(mutator_num)
                # Get a bin to swap with
                mutated_bin = random.choice(bin_set)
                # Make sure the bins are different
                while mutated_bin == a_bin:
                    mutated_bin = random.choice(bin_set)
                # Get mutated number and index
                mutated_num = random.choice(mutated_bin)
                mutated_index = mutated_bin.index(mutated_num)
                # Swap the numbers
                a_bin[mutator_index] = mutated_num
                mutated_bin[mutated_index] = mutator_num


# bin_sets = list of tuples
def crossoverBins(bin_sets, bins_to_swap):
    parent_1 = random.uniform(0, 1)
    parent_2 = random.uniform(0, 1)

    # Find parent 1 and parent 2
    bin_sets_to_crossover = []
    counter_1 = 0
    for tuple_set in bin_sets:
        if parent_1 <= tuple_set[0]:
            bin_sets_to_crossover.append(tuple_set[1])
            break
        counter_1 += 1

    counter_2 = 0
    while True:
        for tuple_set in bin_sets:
            if parent_2 <= tuple_set[0]:
                if counter_1 == counter_2:
                    parent_2 = random.uniform(0, 1)
                else:
                    bin_sets_to_crossover.append(tuple_set[1])
                break
            counter_2 += 1
        if counter_1 != counter_2:
            break

    crossed_over_bin_sets = []

    bin_set_a = bin_sets_to_crossover[0]
    bin_set_b = bin_sets_to_crossover[1]

    bin_set_a_copy = list(bin_set_a)
    bin_set_b_copy = list(bin_set_b)

    bin_set_a_copy[bins_to_swap[0]] = bin_set_b[bins_to_swap[0]]
    bin_set_a_copy[bins_to_swap[1]] = bin_set_b[bins_to_swap[1]]
    bin_set_b_copy[bins_to_swap[0]] = bin_set_a[bins_to_swap[0]]
    bin_set_b_copy[bins_to_swap[1]] = bin_set_a[bins_to_swap[1]]

    crossed_over_bin_sets.append(bin_set_a_copy)
    crossed_over_bin_sets.append(bin_set_b_copy)

    printBins(crossed_over_bin_sets[0])
    printBins(crossed_over_bin_sets[1])

    return crossed_over_bin_sets


# Print out the beautified set of bins to the console
def printBins(bins):
    for a_bin in bins:
        for num in a_bin:
            print(round(num, 1))
        print('\n')


# Write the representation of a set of bins to a file
def exportBins(bins, file_name_suffix):
    with open("puzzles/bins/bins-" + str(file_name_suffix) + ".txt", "w+") as f:
        for a_bin in bins:
            for num in a_bin:
                f.write(str(num) + " ")
            f.write("\n")


# Read the representation of a set of bins from a specified file path
def parseBins(bins_file_path):
    parsed_bins = []
    with open(bins_file_path, "r") as f:
        bins_text = f.readlines()
        for a_bin in bins_text:
            a_bin_nums = a_bin.split()
            parsed_bins.append([float(i) for i in a_bin_nums])
    return parsed_bins


def genRandomTower():
    pass


def calcTowerFitness(tower):
    if (tower[0][0] != "Door") or (tower[len(tower) - 1][0] != "Lookout"):
        return 0

    previous_piece_wideness = 0
    for index, piece in enumerate(tower):
        if (piece[0] == "Door" and index != 0) or (piece[0] == "Lookout" and index != (len(tower) - 1)):
            return 0

        if (piece[1] > previous_piece_wideness) and (previous_piece_wideness > 0):
            return 0

        previous_piece_wideness = piece[1]

    return 1


def printTower(tower):
    for piece in tower:
        for spec in piece:
            print(spec, " ")
        print('\n')


if __name__ == "__main__":
    # Get user input
    puzzle_num, info_file, num_seconds = parse_args()

    # TIMER STUFF TO BE MOVED
    start_time = time.time()
    timeRunOut(start_time, num_seconds)

    # Number Allocation
    if puzzle_num == 1:
        test_bins_set = []
        for bins_set_count in range(10):
            print("Bins Set #" + str(bins_set_count) + ":")
            test_nums = genRandomNumberSets(40)
            test_bins = genRandomBins(test_nums)
            printBins(test_bins)
            exportBins(test_bins, bins_set_count)
            test_bins_fitness = calcBinsFitness(test_bins)

            print(" > Fitness:", test_bins_fitness)
            print('\n')
            test_bins_set.append(test_bins)

        best_bins, remaining_bins_b = getAndPopBestNBinSets(test_bins_set, 2)
        print("Top 2 Bins:")
        for the_best_bins in best_bins:
            printBins(the_best_bins)
            the_best_bins_fitness = calcBinsFitness(the_best_bins)
            print(" > Fitness:", the_best_bins_fitness)
            print('\n')

        worst_bins, remaining_bins_w = getAndPopWorstNBinSets(test_bins_set, 2)
        print("Worst 2 Bins:")
        for the_worst_bins in worst_bins:
            printBins(the_worst_bins)
            the_worst_bins_fitness = calcBinsFitness(the_worst_bins)
            print(" > Fitness:", the_worst_bins_fitness)
            print('\n')

        bin_selection_list = assignSelection(remaining_bins_w)
        crossoverBins(bin_selection_list, [1, 2])
        mutateBins(remaining_bins_w)

    # Tower Building
    elif puzzle_num == 2:
        pass

    # Bad Input
    else:
        print("Bad puzzle number input. Must be either a 1 for number allocation or a 2 for tower building")
