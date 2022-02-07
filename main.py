import random


def genRandomBins(nums):
    bins = []
    for bin_count in range(4):
        a_bin = []
        for bin_nums_count in range(4):
            random.shuffle(nums)
            a_bin.append(nums.pop())
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

    bin_four_score = 0

    return bin_one_score + bin_two_score + bin_three_score + bin_four_score


def printBins(bins):
    for a_bin in bins:
        for num in a_bin:
            print(num, end=" ")
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
            print(spec, end=" ")
        print('\n')


if __name__ == "__main__":
    test_bins = [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]
    printBins(test_bins)
    test_bins_fitness = calcBinsFitness(test_bins)
    print(" > Fitness:", test_bins_fitness)
    print('\n')

    test_tower = [["Door", 1, 1, 1], ["Wall", 1, 1, 1], ["Lookout", 1, 1, 1]]
    printTower(test_tower)
    test_tower_fitness = calcTowerFitness(test_tower)
    print(" > Fitness:", test_tower_fitness)
    print('\n')

    test_tower = [["Lookout", 1, 1, 1], ["Wall", 1, 1, 1], ["Door", 1, 1, 1]]
    printTower(test_tower)
    test_tower_fitness = calcTowerFitness(test_tower)
    print(" > Fitness:", test_tower_fitness)
    print('\n')

    test_tower = [["Door", 1, 1, 1], ["Door", 1, 1, 1], ["Lookout", 1, 1, 1]]
    printTower(test_tower)
    test_tower_fitness = calcTowerFitness(test_tower)
    print(" > Fitness:", test_tower_fitness)
    print('\n')

