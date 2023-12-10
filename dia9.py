
"""
Ok, this is __all_to_easy__ . What is the catch??
"""

def sequentiator(sequence, direction = "forward"):
    derivatives = []
    while not all(number == 0 for number in sequence):
        derivatives.append(sequence[:])
        sequence = [sequence[i + 1] - sequence[i] for i in range(0, len(sequence) - 1)]
    derivatives.append(sequence[:])
    derivatives[-1].append(0)
    for i in range(len(derivatives) - 2, -1, -1):
        if direction == "forward":
            derivatives[i].append(derivatives[i][-1] + derivatives[i + 1][-1])
        else:
            derivatives[i].insert(0, derivatives[i][0] - derivatives[i + 1][0])
    return derivatives[0]

aa = """0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45"""

def do_it(data, direction="forward"):
    bb = [[int(i) for i in line.split()] for line in data.split("\n")]
    cc = [sequentiator(seq, direction) for seq in bb]
    index = -1 if direction == "forward" else 0
    return sum(x[index] for x in cc)
