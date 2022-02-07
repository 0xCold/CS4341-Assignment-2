import math
import random
import numpy as np


NUM_BINS = 4


def genRandomBins(nums):
    nums_copy = nums.copy()
    nums_per_bin = math.floor(len(nums_copy) / NUM_BINS)
    bins = []
    for bin_count in range(NUM_BINS):
        a_bin = []
        for bin_nums_count in range(nums_per_bin):
            random.shuffle(nums_copy)
            a_bin.append(nums_copy.pop())
        bins.append(a_bin)
    return bins


def calcBinsFitness(bins):
    bin_one_score = 1
    for num in bins[0]:
        bin_one_score *= num
    bin_two_score = 0
    for num in bins[1]:
        bin_two_score += num
    bin_three_score = max(bins[2]) - min(bins[2])
    return bin_one_score + bin_two_score + bin_three_score


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


def printBins(bins):
    for a_bin in bins:
        for num in a_bin:
            print(round(num, 3), end=" ")
        print('\n')


def genRandomTower():
    None


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
    test_bins_set = []
    for bins_set_count in range(10):
        print("Bins Set #" + str(bins_set_count) + ":")
        test_nums = np.random.uniform(-10, 10, 40)
        test_nums = test_nums.tolist()
        test_bins = genRandomBins(test_nums)
        printBins(test_bins)
        test_bins_fitness = calcBinsFitness(test_bins)
        print(" > Fitness:", test_bins_fitness)
        print('\n')
        test_bins_set.append(test_bins)

    best_bins, remaining_bins = getAndPopBestNBinSets(test_bins_set, 2)
    print("Top 2 Bins:")
    for the_best_bins in best_bins:
        printBins(the_best_bins)
        the_best_bins_fitness = calcBinsFitness(the_best_bins)
        print(" > Fitness:", the_best_bins_fitness)
        print('\n')
