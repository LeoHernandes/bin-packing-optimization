using JuMP
using GLPK
using ArgParse

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

    # println(parsed_args["time_limit"])
    # println(parsed_args["seed"])

    num_itens, bins_capacity, itens = get_instances(parsed_args["file_path"])

    println("Num itens: ", num_itens)
    println("Bins capacity: ", bins_capacity)
    println("First five itens weights: ", itens[1:5])
end

main()