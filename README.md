# Problema do empacotamento resolvido com heurística Busca Tabu

## Formulação inteira

A formulação inteira do problema, utilizando o solver `HiGHS`, foi implementada na linguagem Julia.

Utilizamos uma matriz binária `M` para representar a presença de um item (coluna) num pacote (linha):

Para todo item `x_ij` pertencente à matriz `M`
- x_ij = 0: item `j` **não** está no pacote `i`
- x_ij = 1: item `j` está no pacote `i`

Com essa estrutura precisamos garantir que:
- Toda coluna possua apenas um elemento com valor `1`. Um item está em exatamente 1 caixa sempre.
- A soma dos valores das linhas cruzados com os pesos dos itens não pode ultrapassar a capacidade dum pacote.

O número de pacotes considerados como utilizáveis é obtido através de uma heurística simples inicial, a qual armazena os items ordenados em ordem decrescente pelo seus pesos em pacotes até que eles estejam cheios. 

Precisamos minimizar a quantidade de pacotes utilizados. Para facilitar esse cálculo, utilizamos um vetor `V` binário de tamanho igual ao número de pacotes considerados inicialmente e que determina se um pacote está sendo usado.

Para todo elemento `p_i` pertencente ao vetor `V`:
- p_i = 0: pacote `ì` **não** está sendo usado.
- p_i = 1: pacote `ì` está sendo usado.

## Execução do código

Para executar a formulação inteira, execute os comandos em Julia:

```julia
Import Pgk;
Pkg.add("HiGHS");
Pkg.add("JuMP");
Pkg.add("ArgParse");
```

E então execute o programa:

```shell
julia formualtion_bin_packing.jl -s 0 -t 60 "selected_bpp_instaces/${file_name}"
```

Em que:
- `-s` é o parâmetro para determinar a seed utilizada.
- `-t` é o tempo máximo de duração da execução em minutos.
- `file_name` é o nome de algum arquivo de instância do problema contido na pasta `./selected_bpp_instaces`.

Caso queira uma forma automatizada de executar a formulação para várias instâncias com parâmetros recomendados, edite no script em shell `run_formulation.sh` a lista de arquivos de instâncias que deseja usar e então use o comando:

```shell
./run_formulation.sh
```

## Meta-heurística

Representação do problema:
- Optamos por trabalhar com um vetor b[] de tamanho igual ao número de itens da instância do problema, em que b[i] = k, i representa o índice de um item e k o índice do pacote no qual esse item está armazenado.

Construção da solução inicial:
- O algoritmo usado para termos uma solução inicial é o mesmo descrito para a formulação inteira em Julia, com a única diferença sendo a estrutura de dados que é construída como saída desse algoritmo: em vez de uma matriz binária, temos um vetor de números inteiros.

Principais estruturas de dados:
- Construímos classes que representam a lista de movimentos tabu e o vetor de indexação dos itens com seus respectivos métodos de transformação, sendo elas englobadas pela classe que executa a busca em si.

## Execução do código

A meta-heurística foi implementada na linguagem Python apenas com bibliotecas nativas. 

Em que:
- `-s` é o parâmetro para determinar a seed utilizada..
- `-i` é o número máximo de iterações que não melhoram a melhor solução.
- `-t` é o valor do tabu tenure: o número de iterações que um item fica na lista tabu.
- `file_name` é o nome de algum arquivo de instância do problema contido na pasta `./selected_bpp_instaces`.

Para tanto a formulação inteira quanto a meta-heurística, somente file_name é um parâmetro obrigatório, os outros possuem valores defaults e não precisam ser passados na execução do programa
