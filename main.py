def calcTowerFitness(tower):
    return 0


def assertTowerValid(tower):
    if tower[0][0] != "Door":
        print("Invalid tower: Does not start with door.")
        return False

    if tower[len(tower) - 1][0] != "Lookout":
        print("Invalid tower: Does not end with lookout.")
        return False

    previous_piece_wideness = 0
    for index, piece in enumerate(tower):
        if piece[0] == "Door" and index != 0:
            print("Invalid tower: Door found in invalid position.")
            return False

        if piece[0] == "Lookout" and index != (len(tower) - 1):
            print("Invalid tower: Lookout found in invalid position.")
            return False

        if piece[1] > previous_piece_wideness:
            print("Invalid tower: Wider piece stacked on top of a narrower piece.")
            return False
        previous_piece_wideness = piece[1]

    return True


if __name__ == "__main__":
    test_tower = [["Door", 1, 1, 1], ["Wall", 1, 1, 1], ["Lookout", 1, 1, 1]]
    tower_is_valid = assertTowerValid(test_tower)
    print(tower_is_valid)

    test_tower = [["Lookout", 1, 1, 1], ["Wall", 1, 1, 1], ["Door", 1, 1, 1]]
    tower_is_valid = assertTowerValid(test_tower)
    print(tower_is_valid)

    test_tower = [["Door", 1, 1, 1], ["Door", 1, 1, 1], ["Lookout", 1, 1, 1]]
    tower_is_valid = assertTowerValid(test_tower)
    print(tower_is_valid)
