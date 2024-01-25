import argparse
from timeit import default_timer as timer
from datetime import timedelta
from typing import List, Tuple, Dict


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "-t",
        "--time_limit",
        default=60,
        type=int,
        help="Program's time limit of execution in minutes",
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

    current_bin = 1
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
        self.num_bins = self.bins[-1]  # Bins indexes are in order at init
        self.bins_weight = [0] * self.num_bins
        self.init_bins_weights()

    def get_num_bins(self):
        return self.num_bins

    def get_bins(self):
        return self.bins

    def move(self, movement: Tuple[int, int]):
        ## TODO: pop bin if it is empty after movement `pop_bin(bin)`
        item_idx, destination_bin = movement
        self.bins[item_idx] = destination_bin
        self.bins_weight[self.bins[item_idx]] = -self.weights[item_idx]

        if destination_bin > self.num_bins:
            self.bins_weight.append(self.weights[item_idx])

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
        for item_index, bin_index in self.bins:
            if bin_index > bin:
                self.bins[item_index] -= 1
        self.bins_weight.pop(bin)
        self.num_bins -= 1

    def find_movements(self) -> Dict[Tuple[int, int], int]:
        """
        Returns a dict of movements that can be made without overflowing the bins
        The entries are in the format of (item_index, destination_bin) : movement_value
        """
        # TODO: consider moving item to a new empty bin
        movements = {}
        for item_idx, item_bin in enumerate(self.get_bins()):
            for current_bin in range(1, self.get_num_bins() + 1):
                movement = (item_idx, current_bin)
                if item_bin != current_bin and not self.bins.will_overflow(movement):
                    movements[movement] = self.get_movement_value(movement)

        return movements

    def get_movement_value(self, movement: Tuple[int, int]) -> int:
        # If is adding a new bin
        item_index, destination_bin = movement
        if destination_bin > self.num_bins:
            return destination_bin

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
    ):
        self.bins = bins
        self.bins_capacity = bins_capacity
        self.best_solution = bins.get_num_bins()
        self.weights = weights
        self.num_iters_no_improve = num_iters_no_improve
        self.taboo_tenure = taboo_tenure
        self.taboo_list = TabooList(len(weights), taboo_tenure)

    def get_best_movement(self) -> Tuple[Tuple[int, int], int]:
        movements = self.bins.find_movements()
        ## TOOD: Se o melhor valor da vizinhança for melhor que self.best_solution -> return movement

        ## TOOD: Senão, tira todos os movementos taboos, self.taboo_list.is_taboo()
        ## se não sobrou nada, retorna nadan
        if len(movements) == 0:
            return None
        ## TODO: senão retorna o melhor dentre os que sobraram
        pass

    def run(self):
        iters_no_improve = 0
        iterations = 0
        while iters_no_improve < self.num_iters_no_improve:
            movement, value = self.bins.get_best_movement()
            if movement is None:
                break

            self.bins.move(movement)
            self.taboo_list.ban_item(movement.item, iterations)
            if value > self.best_solution:
                self.best_solution = value
                iters_no_improve = 0
            else:
                iters_no_improve += 1

            iterations += 1


"""
TODO: 
- [x] Fazer a taboo list é um vetor em que cada posição diz a iteração que o item foi mexido, e comparar com o taboo tenure (len = num_itens)
- [x] Ao invés de utilizar a matriz binária, ser um vetor em que cada posição é a bin que o item está (len = num_itens)
- [x] Vetor com as capacidades de cada bin (len = num_bins)
- [ ] Todos os itens podem mover para uma bin vazia que sempre existirá, a não ser que ele seja o único item na bin
- [ ] Somente checamos o critério de aspiração por objetivo quando ele for o único item na bin 
"""


def main():
    args = parse_command_line()
    num_items, bins_capacity, items = get_instances(args.file_path)

    # Start benchmark:
    start_time = timer()
    bins = get_starting_solution(items, bins_capacity)

    taboo_bins = TabooBins(bins, items)
    taboo_search = TabooSearch(taboo_bins, bins_capacity, items, num_items // 2)
    number_of_bins = taboo_search.run()
    end_time = timer()

    print("The best solution found was using " + number_of_bins + " bins!")
    print("Time elapsed: " + timedelta(seconds=end_time - start_time))


main()
