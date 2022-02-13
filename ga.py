import math
import random
import argparse
import time
from copy import deepcopy


NUM_BINS = 4
MUTATION_ODDS = 10  # Odds out of 100 for an individual bin to mutate
FINISH_BUILDING_PREMATURELY_ODDS = 10

INITIAL_POPULATION_SIZE = 10

USE_ELITISM = True
NUM_ELITISM = 2
USE_CULLING = True
NUM_CULLING = 2

CROSSOVER_BINS = [1, 2]


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
    nums_copy = deepcopy(nums)
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
    return float(bin_one_score + bin_two_score + bin_three_score)


# From a list of sets of bins, return the N best-scoring sets (by fitness), along with the remaining boards
def getBestNBinSets(bin_sets, n):
    copy_bin_sets = deepcopy(bin_sets)
    best_bin_sets = []
    for _ in range(n):
        best_fitness = -1
        best_bin_set_index = 0
        for index, bins in enumerate(copy_bin_sets):
            bin_set_fitness = calcBinsFitness(bins)
            if bin_set_fitness > best_fitness:
                best_fitness = bin_set_fitness
                best_bin_set_index = index
        best_bin_sets.append(copy_bin_sets[best_bin_set_index])
        del copy_bin_sets[best_bin_set_index]
    return best_bin_sets


# From a list of sets of bins, return the N worst-scoring sets (by fitness), along with the remaining boards
def getAndPopWorstNBinSets(bin_sets, n):
    copy_bin_sets = deepcopy(bin_sets)
    for _ in range(n):
        worst_fitness = -1
        worst_bin_set_index = 0
        for index, bins in enumerate(copy_bin_sets):
            bin_set_fitness = calcBinsFitness(bins)
            if bin_set_fitness < worst_fitness:
                worst_fitness = bin_set_fitness
                worst_bin_set_index = index
        del copy_bin_sets[worst_bin_set_index]
    return copy_bin_sets


# pass in culled list of bin sets
def assignSelection(bin_sets):
    bin_fitness = []

    # calculate bin fitness of 4 bins
    for bin_set in bin_sets:
        bin_fitness.append(calcBinsFitness(bin_set))

    min_bin_fitness = min(bin_fitness)
    if min_bin_fitness < 0:
        min_bin_fitness = abs(min_bin_fitness) + 10
        shifted_bin_fitness = []
        for bin_fit in bin_fitness:
            shifted_bin_fitness.append(bin_fit + min_bin_fitness)

        bin_fitness = shifted_bin_fitness

    # find sum of all fitness's
    sum_bin_fitness = sum(bin_fitness)

    bin_selection = []
    total_percentage = 0
    for k in range(len(bin_sets)):
        cumulative_percentage = (bin_fitness[k] / sum_bin_fitness) + total_percentage
        total_percentage = cumulative_percentage
        selection_bin = (cumulative_percentage, bin_sets[k])
        bin_selection.append(selection_bin)

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

    return bin_sets


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

    return bin_set_a_copy, bin_set_b_copy


# Print out the beautified set of bins to the console
def printBins(bins):
    for a_bin in bins:
        for num in a_bin:
            print(round(num, 1), end=" ")
        print('\n')


# Write the representation of a set of bins to a file
def exportBins(nums, file_name_suffix):
    with open("puzzles/bins/bins-" + str(file_name_suffix) + ".txt", "w+") as f:
        for num in nums:
            f.write(str(num) + "\n")


# Read the representation of a set of bins from a specified file path
def parseBins(bins_file_path):
    parsed_nums = []
    with open(bins_file_path, "r") as f:
        bins_text = f.readlines()
        for num in bins_text:
            parsed_nums.append(float(num))
    return parsed_nums


def genRandomTower(pieces):
    constructed_tower = []
    do_end = False
    for piece in range(len(pieces)):
        pieces.shuffle()
        if not do_end:
            constructed_tower.append(pieces.pop())
            do_end = random.randint(0, 100) <= FINISH_BUILDING_PREMATURELY_ODDS
    return constructed_tower


def mutateTowers(towers):
    for tower in towers:
        tower_copy = list.copy(tower)
        do_mutate = random.randint(0, 100) <= MUTATION_ODDS
        if do_mutate:
            tower_copy.shuffle()
            tower_piece_a = tower_copy.pop()
            tower_copy.shuffle()
            tower_piece_b = tower_copy.pop()


def calcTowerFitness(tower):
    cost = 0
    if (tower[0][0] != "Door") or (tower[len(tower) - 1][0] != "Lookout"):
        return 0

    previous_piece_wideness = 0
    for index, piece in enumerate(tower):
        if (piece[0] == "Door" and index != 0) or (piece[0] == "Lookout" and index != (len(tower) - 1)):
            return 0

        if (piece[1] > previous_piece_wideness) and (previous_piece_wideness > 0):
            return 0

        previous_piece_wideness = piece[1]
        cost += piece[2]

    return 10 + (len(tower) ** 2) - cost


def printTower(tower):
    for piece in tower:
        for spec in piece:
            print(spec, " ")
        print('\n')


# Read the representation of a set of bins from a specified file path
def parseTowerPieces(pieces_file_path):
    parsed_pieces = []
    with open(pieces_file_path, "r") as f:
        pieces_text = f.readlines()
        for piece in pieces_text:
            parsed_pieces.append(piece.split())
    return parsed_pieces


if __name__ == "__main__":
    # Get user input
    puzzle_num, info_file, num_seconds = parse_args()

    # Number Allocation
    if puzzle_num == 1:
        input_nums = parseBins(info_file)

        population = []
        for i in range(INITIAL_POPULATION_SIZE):
            random_bin = genRandomBins(input_nums)
            population.append(random_bin)

        best_bin = getBestNBinSets(population, 1)[0]
        generation_num = 0
        best_bin_generation = generation_num
        ga_running = True
        start_time = time.time()

        while ga_running:
            generation_num += 1
            # Elitism
            if USE_ELITISM:
                children_bins = getBestNBinSets(population, NUM_ELITISM)
            else:
                children_bins = []
            # Culling
            if USE_CULLING:
                population = getAndPopWorstNBinSets(population, NUM_CULLING)

            # Crossover
            tuple_bins = assignSelection(population)
            children_len = len(children_bins)
            for _ in range(int((INITIAL_POPULATION_SIZE - children_len) / 2)):
                bin_a, bin_b = crossoverBins(tuple_bins, CROSSOVER_BINS)
                children_bins.append(bin_a)
                children_bins.append(bin_b)

            # Mutation
            children_bins = mutateBins(children_bins)

            # Check if a new best bin set has been found
            best_child = getBestNBinSets(children_bins, 1)[0]
            if calcBinsFitness(best_child) > calcBinsFitness(best_bin):
                best_bin = deepcopy(best_child)
                best_bin_generation = generation_num

            # Set up next generation
            population = children_bins
            ga_running = not timeRunOut(start_time, num_seconds)

        # Output
        print("****OUTPUT****")
        print("Best Bin Set")
        printBins(best_bin)
        print("Best Score", calcBinsFitness(best_bin))
        print("Total Generations Run", generation_num)
        print("Best Generation", best_bin_generation)
    # Tower Building
    elif puzzle_num == 2:
        pass
    # Bad Input
    else:
        print("Bad puzzle number input. Must be either a 1 for number allocation or a 2 for tower building")
