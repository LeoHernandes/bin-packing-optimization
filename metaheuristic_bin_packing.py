import argparse
from time import time
from typing import List, Tuple


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


def get_bin(num_itens):
    return [0] * num_itens


# TODO: mudar essa função para retornar um vetor ao invés de uma matriz
def get_starting_solution(itens, num_itens, bins_capacity):
    total_sum = 0

    bins = []
    bins.append(get_bin(num_itens))

    for i, item in enumerate(itens):
        total_sum += item
        if total_sum > bins_capacity:
            total_sum = item
            bins.append(get_bin(num_itens))
        bins[-1][i] = 1

    return bins


class TabooMovement:
    def __init__(self, current_bin, destination_bin, item_idx):
        self.current_bin = current_bin
        self.destination_bin = destination_bin
        self.item_idx = item_idx

    def __str__(self):
        return f"[{self.item_idx}]: {self.current_bin} -> {self.destination_bin}"


class TabooState:
    pass


def find_movements(bins: TabooState, bins_capacity: int) -> List[TabooMovement]:
    pass


"""
TODO: 
- Fazer a taboo list é um vetor em que cada posição diz a iteração que o item foi mexido, e comparar com o taboo tenure (len = num_itens)
- Ao invés de utilizar a matriz binária, ser um vetor em que cada posição é a bin que o item está (len = num_itens)
- Vetor com as capacidades de cada bin (len = num_bins)
- Todos os itens podem mover para uma bin vazia que sempre existirá, a não ser que ele seja o único item na bin
- Somente checamos o critério de aspiração por objetivo quando ele for o único item na bin 
"""


def taboo_search(bins: TabooState, bins_capacity: int) -> int:
    TABOO_TENURE = len(bins) // 2
    taboo_list = []

    best_solution = len(bins)


def main():
    args = parse_command_line()
    num_itens, bins_capacity, itens = get_instances(args.file_path)

    bins = get_starting_solution(itens, num_itens, bins_capacity)

    best_solution = taboo_search(bins, bins_capacity)


main()
