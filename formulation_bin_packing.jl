using JuMP
using HiGHS
using ArgParse
using Random

function parse_command_line()
    parser = ArgParseSettings()

    @add_arg_table! parser begin
        "--seed", "-s"
        help = "Random seed"
        arg_type = Int
        default = 0
        "--time_limit", "-t"
        help = "Program's time limit of execution in minutes"
        arg_type = Int
        default = 60
        "file_path"
        help = "Path of the txt file containing the instances"
        arg_type = String
        required = true
    end
    return parse_args(parser)
end

function get_instances(file_path)
    """
    Returns a 3-tuple that gets the following informations from the .txt file in file_path:
    First line - num_itens
    Second line - bins_capacity
    Other lines - itens
    """
    f = open(file_path, "r")

    num_itens = parse(Int64, readline(f))
    bins_capacity = parse(Int64, readline(f))

    itens = Vector{Integer}(undef, num_itens)

    for i in 1:num_itens
        weight = parse(Int64, readline(f))
        itens[i] = weight
    end

    close(f)

    return num_itens, bins_capacity, itens
end

function get_initial_num_bins(num_itens, bins_capacity, itens)
    """
    Returns the initial number of bins needed to store all the itens.
    """
    num_bins = 0
    total_sum = 0
    for i in 1:num_itens
        total_sum += itens[i]
        if (total_sum > bins_capacity)
            total_sum = itens[i]
            num_bins += 1
        end
    end


    return num_bins
end

function main()
    parsed_args = parse_command_line()
    num_itens, bins_capacity, itens = get_instances(parsed_args["file_path"])

    num_bins = get_initial_num_bins(num_itens, bins_capacity, itens)
    println("Starting num_bins: ", num_bins)

    model = Model(HiGHS.Optimizer)

    set_optimizer_attribute(model, "time_limit", 60.0 * parsed_args["time_limit"])
    set_optimizer_attribute(model, "log_to_console", false)

    # Variables:
    # A binary matrix with dimensions N x M
    # representing what bin is picked to store an item.
    # N is the number of itens. 
    # M is the number of starting bins that our heuristic found.
    # The rows represents a bin.
    # The columns represents an item.

    @variable(model, itens_storage[1:num_bins, 1:num_itens], Bin)

    # An auxiliar vector to represent which bins are being used
    @variable(model, bins_used[1:num_bins], Bin)

    # Constraints:
    # Each item must be store in exactly one bin
    for item in 1:num_itens
        @constraint(model, sum([itens_storage[bin, item] for bin in 1:num_bins]) == 1)
    end

    # The itens stored in a bin must not exceed its capacity
    for bin in 1:num_bins
        @constraint(model, sum([itens_storage[bin, item] * itens[item] for item in 1:num_itens]) <= bins_capacity * bins_used[bin])
    end

    # Populate the auxiliar vector
    for bin in 1:num_bins
        if (bin < num_bins)
            @constraint(model, bins_used[bin+1] <= bins_used[bin])
        end
        for item in 1:num_itens
            @constraint(model, bins_used[bin] >= itens_storage[bin, item])
        end
    end

    # Objective: Minimize the number of bins used
    @objective(model, Min, sum(bins_used))

    optimize!(model)

    if has_values(model)
        @show(objective_value(model))
        println(solution_summary(model))
    else
        println("The time limit was reached before finding a solution")
    end
end

main()