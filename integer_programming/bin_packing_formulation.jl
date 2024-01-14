using JuMP
using GLPK
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

function main()
    parsed_args = parse_command_line()

    num_items, bins_capacity, items = get_instances(parsed_args["file_path"])
    small = 0
    for i in 1:num_items
        if(items[i] <= bins_capacity/2)
            small += 1
        end
    end
    # arredonda small/2 para baixo
    small = floor(Int64, small/2)


    #num_bins = num_items
    num_bins = num_items - small
    println("num_bins: ", num_bins)
    model = Model(GLPK.Optimizer)

   # set_optimizer_attribute(model, "TimeLimitSec", parsed_args["time_limit"] * 60)
   # Random.seed!(parsed_args["seed"])
   # set_optimizer_attribute(m, "msg_lev", GLPK.GLP_MSG_ALL)

    # Variables:
    # A binary matrix with dimensions N x N
    # representing what bin is picked to store an item.
    # N is the number of items. 
    # The rows represents a bin.
    # The columns represents an item.
    # 
    # The worst case is that we need one bin for each item, 
    # so we allocate space for a N x N matrix.
    @variable(model, items_storage[1:num_bins, 1:num_items], Bin)

    # An auxiliar vector to represent which bins are being used
    @variable(model, bins_used[1:num_bins], Bin)

    # Constraints:
    # Each item must be store in exactly one bin
    for item in 1:num_items
        @constraint(model, sum([items_storage[bin, item] for bin in 1:num_bins]) == 1)
    end

    # The items stored in a bin must not exceed its capacity
    for bin in 1:num_bins
        @constraint(model, sum([items_storage[bin, item] * items[item] for item in 1:num_items]) <= bins_capacity * bins_used[bin])
    end

    # Populate the auxiliar vector
    for bin in 1:num_bins
        #@constraint(model, bins_used[bin] <= sum([items_storage[bin, item] for item in 1:num_items]))
        if(bin < num_bins)
            @constraint(model, bins_used[bin+1] <= bins_used[bin]) 
        end
        for item in 1:num_items
            @constraint(model, bins_used[bin] >= items_storage[bin, item])
        end
    end

    # Objective: Minimize the number of bins used
    @objective(model, Min, sum(bins_used))

    optimize!(model)
    @show objective_value(model)
end

main()