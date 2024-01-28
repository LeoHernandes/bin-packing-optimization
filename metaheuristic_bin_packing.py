import argparse
import random
from timeit import default_timer as timer
from datetime import timedelta
from typing import List, Tuple, Dict


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "-i",
        "--max_iterations",
        default=0,
        type=int,
        help="Program's max iterations without improvement on solution",
    )
    parser.add_argument(
        "-t",
        "--taboo_tenure",
        default=0,
        type=int,
        help="Program's taboo list size",
    )
    parser.add_argument(
        "file_path", help="Path of the txt file containing the instances"
    )

    return parser.parse_args()


def get_instances(file_path):
    """
    Returns a 3-tuple that gets the following informations from the .txt file in file_path:
    First line - num_itens
    Second line - bins_capacity
    Other lines - itens
    """
    with open(file_path, "r") as f:
        num_itens = int(f.readline())
        bins_capacity = int(f.readline())
        itens = [int(weight) for weight in f]

    return num_itens, bins_capacity, itens


def get_starting_solution(itens: List[int], bins_capacity: int) -> List[int]:
    total_sum = 0

    current_bin = 0
    bins = []
    for item in itens:
        total_sum += item
        if total_sum > bins_capacity:
            total_sum = item
            current_bin += 1
        bins.append(current_bin)
    return bins


class TabooList:
    def __init__(self, num_items: int, taboo_tenure: int):
        self.list = [0] * num_items
        self.tenure = taboo_tenure

    def ban_item(self, item_index: int, current_iteration: int):
        self.list[item_index] = current_iteration

    def is_taboo(self, item_index: int, current_iteration: int) -> bool:
        return current_iteration - self.list[item_index] < self.tenure


class TabooBins:
    def __init__(self, bins: List[int], weights: List[int], bins_capacity: int):
        self.bins = bins
        self.weights = weights
        self.bins_capacity = bins_capacity
        self.num_bins = max(bins) + 1
        self.bins_weight = [0] * self.num_bins
        self.init_bins_weights()

    def get_num_bins(self):
        return self.num_bins

    def get_bins(self):
        return self.bins

    def move(self, movement: Tuple[int, int]):
        item_idx, destination_bin = movement
        source_bin = self.bins[item_idx]

        # Change bin and total weights
        self.bins_weight[source_bin] -= self.weights[item_idx]
        self.bins[item_idx] = destination_bin

        # If the movement created a new bin
        if destination_bin == self.num_bins:
            self.bins_weight.append(self.weights[item_idx])
            self.num_bins += 1
        else:
            self.bins_weight[destination_bin] += self.weights[item_idx]

        # If the item was the only one in the bin
        if self.bins_weight[source_bin] == 0:
            self.pop_bin(source_bin)

    def init_bins_weights(self):
        for i in range(len(self.bins)):
            self.bins_weight[self.bins[i]] += self.weights[i]

    def will_overflow(self, movement: Tuple[int, int]):
        item_idx, destination_bin = movement
        return (
            self.bins_weight[destination_bin] + self.weights[item_idx]
            > self.bins_capacity
        )

    def pop_bin(self, bin):
        for item_idx, bin_index in enumerate(self.bins):
            if bin_index > bin:
                self.bins[item_idx] -= 1
        self.bins_weight.pop(bin)
        self.num_bins -= 1

    def find_movements(self) -> Dict[Tuple[int, int], int]:
        """
        Returns a dict of movements that can be made without overflowing the bins
        The entries are in the format of (item_index, destination_bin) : movement_value
        """
        movements = {}
        for item_idx, item_bin in enumerate(self.get_bins()):
            for current_bin in range(self.get_num_bins()):
                movement = (item_idx, current_bin)
                if item_bin != current_bin and not self.will_overflow(movement):
                    movements[movement] = self.get_movement_value(movement)

            # If the current item is not the only one in the bin
            if self.weights[item_idx] != self.bins_weight[item_bin]:
                # Make possible to move to a new empty bin
                movement = (item_idx, self.num_bins)
                movements[movement] = self.get_movement_value(movement)

        return movements

    def get_movement_value(self, movement: Tuple[int, int]) -> int:
        # If is adding a new bin
        item_index, destination_bin = movement
        if destination_bin > self.num_bins - 1:
            return self.num_bins + 1

        # If is Is leaving the bin empty
        source_bin = self.bins[item_index]
        source_bin_weight = self.bins_weight[source_bin]
        if source_bin_weight - self.weights[item_index] == 0:
            return self.num_bins - 1

        # Else, it remains the same number of bins
        return self.num_bins


class TabooSearch:
    def __init__(
        self,
        bins: TabooBins,
        bins_capacity: int,
        weights: List[int],
        taboo_tenure: int,
        num_iters_no_improve: int,
        iterations: int = 0,
    ):
        self.bins = bins
        self.bins_capacity = bins_capacity
        self.best_solution = bins.get_num_bins()
        self.weights = weights
        self.num_iters_no_improve = num_iters_no_improve
        self.taboo_tenure = taboo_tenure
        self.taboo_list = TabooList(len(weights), taboo_tenure)
        self.iterations = iterations

    def get_best_movement(self) -> Tuple[Tuple[int, int], int]:
        movements = self.bins.find_movements()
        # If there is no movements
        if len(movements) == 0:
            return None, None

        # If the best solution found in this iteration is the best we've seen so far
        min_value = min(movements.values())
        if min_value < self.best_solution:
            # Ignore if it's taboo and return it
            movements_of_best_value = [
                key for key, value in movements.items() if value == min_value
            ]
            random_index = random.randint(0, len(movements_of_best_value) - 1)
            return movements_of_best_value[random_index], min_value

        # Remove taboo movements:
        def filter_taboo(dict_row: Tuple[Tuple[int, int]]):
            ((item_idx, _), _) = dict_row
            return self.taboo_list.is_taboo(item_idx, self.iterations)

        no_taboo_moves = dict(filter(filter_taboo, movements.items()))

        # If all movements are taboo
        if len(no_taboo_moves) == 0:
            return None, None

        # Return the best solution from movements that aren't taboo
        min_value = min(no_taboo_moves.values())
        movements_of_best_value = [
            key for key, value in no_taboo_moves.items() if value == min_value
        ]
        random_index = random.randint(0, len(movements_of_best_value) - 1)
        return movements_of_best_value[random_index], min_value

    def run(self):
        iters_no_improve = 0
        while iters_no_improve < self.num_iters_no_improve:
            movement, value = self.get_best_movement()
            if movement is None:
                break

            self.bins.move(movement)
            self.taboo_list.ban_item(movement[0], self.iterations)
            if value < self.best_solution:
                self.best_solution = value
                iters_no_improve = 0
            else:
                iters_no_improve += 1

            self.iterations += 1
        return self.best_solution


def main():
    args = parse_command_line()
    num_items, bins_capacity, items = get_instances(args.file_path)

    # Initialize random
    random.seed(args.seed)

    # Start benchmark:
    start_time = timer()
    bins = get_starting_solution(items, bins_capacity)
    if args.max_iterations == 0:
        args.max_iterations = num_items * 2
    if args.taboo_tenure == 0:
        args.taboo_tenure = num_items // 2
    taboo_bins = TabooBins(bins, items, bins_capacity)
    taboo_search = TabooSearch(
        taboo_bins, bins_capacity, items, args.taboo_tenure, args.max_iterations
    )

    initial_solution = taboo_search.best_solution

    number_of_bins = taboo_search.run()
    end_time = timer()

    print(
        "Solving problem for "
        + str(num_items)
        + " items and bins with capacity of "
        + str(bins_capacity)
        + ":"
    )
    print(
        "#################################################################################\n"
    )
    print("The initial solution was:" + str(initial_solution) + " bins!")
    print("The best solution found was using " + str(number_of_bins) + " bins!")
    print("Time elapsed: " + str(timedelta(seconds=end_time - start_time)))


if __name__ == "__main__":
    main()
