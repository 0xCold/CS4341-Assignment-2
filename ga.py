import copy
import math
import random
import argparse
import time
from copy import deepcopy

NUM_BINS = 4
BIN_SIZE = 10
MUTATION_ODDS = 10  # Odds out of 100 for an individual bin to mutate
FINISH_BUILDING_PREMATURELY_ODDS = 10

INITIAL_POPULATION_SIZE = 10

USE_ELITISM = True
NUM_ELITISM = 1
USE_CULLING = True
NUM_CULLING = 5

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
def assignSelectionBins(bin_sets):
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
            # If mutation is true, swap a random number in this bin with a number from a different, random bin
            if random.randint(0, 100) <= MUTATION_ODDS:
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

    while True:
        counter_2 = 0
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

    # Define the 2 parents
    bin_set_a = bin_sets_to_crossover[0]
    bin_set_b = bin_sets_to_crossover[1]

    # Make 2 sets of copies
    bin_set_a_copy = deepcopy(bin_set_a)
    bin_set_b_copy = deepcopy(bin_set_b)
    bin_set_a_copy_2 = deepcopy(bin_set_a)
    bin_set_b_copy_2 = deepcopy(bin_set_b)

    # Swap the bins
    bin_set_a_copy[bins_to_swap[0]] = bin_set_b_copy_2[bins_to_swap[0]]
    bin_set_a_copy[bins_to_swap[1]] = bin_set_b_copy_2[bins_to_swap[1]]
    bin_set_b_copy[bins_to_swap[0]] = bin_set_a_copy_2[bins_to_swap[0]]
    bin_set_b_copy[bins_to_swap[1]] = bin_set_a_copy_2[bins_to_swap[1]]

    # Look for duplicates
    bin_dict_a = make_bin_dicts(bin_set_a_copy)
    bin_dict_b = make_bin_dicts(bin_set_b_copy)
    bin_a_duplicates = find_duplicate_keys(bin_dict_a)
    bin_b_duplicates = find_duplicate_keys(bin_dict_b)

    for duplicate_index in range(len(bin_a_duplicates)):
        duplicate_number_a = bin_a_duplicates[duplicate_index]
        duplicate_number_b = bin_b_duplicates[duplicate_index]
        bin_a_index = bin_dict_a.get(duplicate_number_a)[0]
        bin_b_index = bin_dict_b.get(duplicate_number_b)[0]
        bin_set_a_copy[bin_a_index[0]][bin_a_index[1]] = duplicate_number_b
        bin_set_b_copy[bin_b_index[0]][bin_b_index[1]] = duplicate_number_a

    return bin_set_a_copy, bin_set_b_copy


def make_bin_dicts(bin_set):
    bin_dict = {}
    for bin_num in range(NUM_BINS):
        for bin_index in range(BIN_SIZE):
            number = bin_set[bin_num][bin_index]
            if number in bin_dict.keys():
                bin_dict.update({number: [bin_dict.get(number)[0],
                                          bin_dict.get(number)[1] + 1]})
            else:
                bin_dict[number] = [[bin_num, bin_index], 1]

    return bin_dict


def find_duplicate_keys(bin_dict):
    keys = []
    for item in bin_dict.items():
        if item[1][1] > 1:
            keys.append(item[0])
    return keys


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
    pieces_copy = list.copy(pieces)
    constructed_tower = []
    do_end = False
    for piece in range(len(pieces_copy)):
        random.shuffle(pieces_copy)
        if not do_end:
            constructed_tower.append(pieces_copy.pop())
            do_end = random.randint(0, 100) <= FINISH_BUILDING_PREMATURELY_ODDS
    return constructed_tower


def mutateTowers(towers):
    for tower in towers:
        tower_copy = copy.deepcopy(tower)
        do_mutate = random.randint(0, 100) <= MUTATION_ODDS
        if do_mutate:
            tower_piece_a = random.choice(tower_copy)
            tower_piece_a_index = tower_copy.index(tower_piece_a)
            tower_piece_b = random.choice(tower_copy)
            tower_piece_b_index = tower_copy.index(tower_piece_b)
            tower[tower_piece_a_index] = tower_piece_b
            tower[tower_piece_b_index] = tower_piece_a
    return towers


# From a list of sets of bins, return the N best-scoring sets (by fitness), along with the remaining boards
def getBestNTowers(towers, n):
    copy_towers = deepcopy(towers)
    best_towers = []
    for _ in range(n):
        best_fitness = -1
        best_tower_index = 0
        for index, tower in enumerate(copy_towers):
            tower_fitness = calcTowerFitness(tower)
            if tower_fitness > best_fitness:
                best_fitness = tower_fitness
                best_tower_index = index
        best_towers.append(copy_towers[best_tower_index])
        del copy_towers[best_tower_index]
    return best_towers


# From a list of sets of bins, return the N worst-scoring sets (by fitness), along with the remaining boards
def getAndPopWorstNTowers(towers, n):
    copy_towers = deepcopy(towers)
    for _ in range(n):
        worst_fitness = 99999
        worst_tower_index = 0
        for index, tower in enumerate(copy_towers):
            tower_fitness = calcTowerFitness(tower)
            if tower_fitness < worst_fitness:
                worst_fitness = tower_fitness
                worst_tower_index = index
        del copy_towers[worst_tower_index]
    return copy_towers


def assignSelectionTowers(towers):
    tower_fitness = []

    for tower in towers:
        tower_fitness.append(calcTowerFitness(tower))

    min_tower_fitness = min(tower_fitness)
    if min_tower_fitness < 0:
        min_tower_fitness = abs(min_tower_fitness) + 10
        shifted_tower_fitness = []
        for tower_fit in tower_fitness:
            shifted_tower_fitness.append(tower_fit + min_tower_fitness)

        tower_fitness = shifted_tower_fitness

    # find sum of all fitness's
    sum_tower_fitness = max(sum(tower_fitness), 0.001)

    tower_selection = []
    total_percentage = 0
    for k in range(len(towers)):
        cumulative_percentage = (tower_fitness[k] / sum_tower_fitness) + total_percentage
        total_percentage = cumulative_percentage
        selection_tower = (cumulative_percentage, towers[k])
        tower_selection.append(selection_tower)

    return tower_selection  # List of tuple + list: [(probability, [bin_set])]


def crossoverTowers(towers, pieces_to_swap):
    parent_1 = random.uniform(0, 1)
    parent_2 = random.uniform(0, 1)

    # Find parent 1 and parent 2
    towers_to_crossover = []
    counter_1 = 0
    for tuple_set in towers:
        if parent_1 <= tuple_set[0]:
            towers_to_crossover.append(tuple_set[1])
            break
        counter_1 += 1

    counter_2 = 0
    while True:
        for tuple_set in towers:
            if parent_2 <= tuple_set[0]:
                if counter_1 == counter_2:
                    parent_2 = random.uniform(0, 1)
                else:
                    towers_to_crossover.append(tuple_set[1])
                break
            counter_2 += 1
        if counter_1 != counter_2:
            break

    if len(towers_to_crossover) == 0:
        towers_copy = list.copy(towers)
        random.shuffle(towers_copy)
        towers_to_crossover.append(towers_copy.pop()[1])
        random.shuffle(towers_copy)
        towers_to_crossover.append(towers_copy.pop()[1])

    _tower_a = towers_to_crossover[0]
    _tower_b = towers_to_crossover[1]

    tower_a_upper_half = _tower_a[0: math.floor(len(_tower_a) / 2)]
    tower_b_lower_half = _tower_b[math.floor(len(_tower_b) / 2): len(_tower_b)]

    new_tower_a = tower_a_upper_half + tower_b_lower_half

    return new_tower_a


def calcTowerFitness(tower):
    cost = 0
    if (tower[0][0] != "Door") or (tower[len(tower) - 1][0] != "Lookout"):
        return 0

    previous_piece_wideness = -1
    for index, piece in enumerate(tower):
        if (piece[0] == "Door" and index != 0) or (piece[0] == "Lookout" and index != (len(tower) - 1)):
            return 0

        if (int(piece[1]) > previous_piece_wideness) and (previous_piece_wideness != -1):
            return 0
        previous_piece_wideness = int(piece[1])

        num_pieces_above = len(tower) - index
        if num_pieces_above > int(piece[2]):
            return 0

        cost += int(piece[3])

    return 10 + (len(tower) ** 2) - cost


def printTower(tower):
    for piece in tower:
        for spec in piece:
            print(spec, end=" ")
        print('\n')


def printTowers(towers):
    index = 1
    for tower in towers:
        print("Tower " + str(index) + ":")
        printTower(tower)
        print("\n")
        index += 1


# Read the representation of a set of bins from a specified file path
def parseTowerPieces(pieces_file_path):
    parsed_pieces = []
    with open(pieces_file_path, "r") as f:
        pieces_text = f.readlines()
        for piece in pieces_text:
            parsed_pieces.append(piece[:-1].split(", "))
    return parsed_pieces


def assertTowerValid(tower, pieces):
    pieces_copy = list.copy(pieces)
    for piece in tower:
        if piece not in pieces_copy:
            return False
        del pieces_copy[pieces_copy.index(piece)]
    return True


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
            tuple_bins = assignSelectionBins(population)
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
        input_pieces = parseTowerPieces(info_file)

        population = []
        for i in range(INITIAL_POPULATION_SIZE):
            random_tower = genRandomTower(input_pieces)
            population.append(random_tower)

        best_tower = getBestNTowers(population, 1)[0]
        generation_num = 0
        best_tower_generation = generation_num
        ga_running = True
        start_time = time.time()

        while ga_running:
            generation_num += 1
            if USE_ELITISM:
                children_towers = getBestNTowers(population, NUM_ELITISM)
            else:
                children_towers = []
            if USE_CULLING:
                population = getAndPopWorstNTowers(population, NUM_CULLING)

            tuple_towers = assignSelectionTowers(population)

            children_len = len(children_towers)
            for _ in range(INITIAL_POPULATION_SIZE - children_len):
                new_child_tower = crossoverTowers(tuple_towers, CROSSOVER_BINS)
                if assertTowerValid(new_child_tower, input_pieces):
                    children_towers.append(new_child_tower)
                else:
                    children_towers.append(genRandomTower(input_pieces))

            # Mutation
            children_towers = mutateTowers(children_towers)

            # Check if a new best tower has been found
            best_child = getBestNTowers(children_towers, 1)[0]
            if calcTowerFitness(best_child) > calcTowerFitness(best_tower):
                best_tower = deepcopy(best_child)
                best_tower_generation = generation_num

            # Set up next generation
            population = children_towers
            ga_running = not timeRunOut(start_time, num_seconds)

            print(population)

        # Output
        print("****OUTPUT****")
        print("Best Tower")
        printTower(best_tower)
        print("Best Score", calcTowerFitness(best_tower))
        print("Total Generations Run", generation_num)
        print("Best Generation", best_tower_generation)

    # Bad Input
    else:
        print("Bad puzzle number input. Must be either a 1 for number allocation or a 2 for tower building")
