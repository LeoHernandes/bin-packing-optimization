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

function get_initial_num_bins(num_itens, bins_capacity, itens)
    """
    Returns the initial number of bins needed to store all the itens.
    """

    small = 0
    for i in 1:num_itens
        if (itens[i] <= bins_capacity / 2)
            small += 1
        end
    end

    small = floor(Int64, small / 2)
    num_bins = num_itens - small

    return num_bins
end

function main()
    parsed_args = parse_command_line()
    num_itens, bins_capacity, itens = get_instances(parsed_args["file_path"])

    num_bins = get_initial_num_bins(num_itens, bins_capacity, itens)
    println("Starting num_bins: ", num_bins)

    # tm_lim is in milliseconds
    model = Model(optimizer_with_attributes(GLPK.Optimizer, "tm_lim" => (60000 * parsed_args["time_limit"])))

    # set_optimizer_attribute(model, "msg_lev", GLPK.GLP_MSG_ALL)
    Random.seed!(parsed_args["seed"])

    # Variables:
    # A binary matrix with dimensions N x N
    # representing what bin is picked to store an item.
    # N is the number of itens. 
    # The rows represents a bin.
    # The columns represents an item.
    # 
    # The worst case is that we need one bin for each item, 
    # so we allocate space for a N x N matrix.
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
        @constraint(model, sum([itens_storage[bin, item] * itens[item] for item in 1:num_itens]) <= bins_capacity)
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
    println(solution_summary(model))

    if termination_status(model) == OPTIMAL
        println("Solution is optimal")
        @show(objective_value(model))
    elseif termination_status(model) == TIME_LIMIT
        if has_values(model)
            println("Solution is suboptimal due to a time limit, but a primal solution is available")
            @show(objective_value(model))
        else
            println("The time limit was reached before finding a solution")
        end
    else
        error("The model was not solved correctly.")
    end
end

main()