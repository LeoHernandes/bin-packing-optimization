import argparse


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


def main():
    args = parse_command_line()
    num_itens, bins_capacity, itens = get_instances(args.file_path)
    print(args.time_limit, args.seed, args.file_path)
    print("Num itens:", num_itens)
    print("Bins capacity:", bins_capacity)
    print("First five itens:", itens[:5])
    num_bins = 0
    total_sum = 0
    for item in itens:
        total_sum += item
        if(total_sum > bins_capacity):
            total_sum = item
            num_bins +=1


main()
