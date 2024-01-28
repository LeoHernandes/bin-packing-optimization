import pandas as pd
from glob import glob
from metaheuristic_bin_packing import *
from os import path

files = glob("selected_bpp_instances/*.txt")
NUM_SEEDS = 10

output_df = pd.DataFrame(
    columns=[
        "file",
        "seed",
        "num_items",
        "bins_capacity",
        "initial_solution",
        "best_solution",
        "time",
        "max_iterations",
        "taboo_tenure",
    ]
)
try:
    for file in files:
        print("Processing file: " + path.basename(file))
        for seed in range(NUM_SEEDS):
            print("Seed: " + str(seed))
            num_items, bins_capacity, items = get_instances(file)

            # Initialize random
            random.seed(seed)

            # Start benchmark:
            start_time = timer()
            bins = get_starting_solution(items, bins_capacity)

            max_iterations = num_items
            taboo_tenure = num_items // 2

            taboo_bins = TabooBins(bins, items, bins_capacity)
            taboo_search = TabooSearch(
                taboo_bins, bins_capacity, items, taboo_tenure, max_iterations
            )

            initial_solution = taboo_search.best_solution

            number_of_bins = taboo_search.run()
            end_time = timer()

            df = pd.DataFrame(
                [
                    [
                        path.basename(file),
                        seed,
                        num_items,
                        bins_capacity,
                        initial_solution,
                        number_of_bins,
                        end_time - start_time,
                        max_iterations,
                        taboo_tenure,
                    ]
                ],
                columns=[
                    "file",
                    "seed",
                    "num_items",
                    "bins_capacity",
                    "initial_solution",
                    "best_solution",
                    "time",
                    "max_iterations",
                    "taboo_tenure",
                ],
            )
            output_df = pd.concat([output_df, df], ignore_index=True)
except KeyboardInterrupt:
    print("Interrupting processing")
finally:
    output_df.to_csv("output/output.csv", index=False)
