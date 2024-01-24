#!/bin/bash

# List of filenames for the problems instances
file_path="selected_bpp_instances"
file_list=("402_10000_DI_18.txt" "1002_80000_NR_27.txt" "BPP_100_150_0.1_0.7_0.txt" "BPP_500_300_0.2_0.8_6.txt" "Falkenauer_t60_00.txt" "Falkenauer_u1000_00.txt" "Hard28_BPP645.txt" "N1W1B1R0.txt")

# Path to the foobar script
formulation_path="./formulation_bin_packing.jl"

# Output directory
output_dir="./output"

# Iterate over the file list and run the formulation with each instance
for file_name in "${file_list[@]}"; do
    # Check if the file exists before running
    if [ -e "${file_path}/${file_name}" ]; then
        echo "Running formulation with $file_name and seed 0"
        output_file="${output_dir}/${file_name}_seed0.txt"
        julia $formulation_path -s 0 -t 60 "${file_path}/${file_name}" > $output_file 2>&1
        
        echo "Running formulation with $file_name and seed 1"
        output_file="${output_dir}/${file_name}_seed1.txt"
        julia $formulation_path -s 1 -t 60 "${file_path}/${file_name}" > $output_file 2>&1
    else
        echo "File $file_name not found."
    fi
done
