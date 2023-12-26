
class V2(tuple):
    def __new__(cls, x, y=None):
        if y != None:
            x = (x, y)
        return super().__new__(cls, x)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def __add__(self, other):
        return type(self)((self.x + other[0], self.y + other[1]))

    def __radd__(self, other):
        return type(self)((self.x + other[0], self.y + other[1]))

    def __sub__(self, other):
        return type(self)(self.x - other[0], self.y - other[1])

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]

    def __hash__(self):
        return hash(tuple(self))

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def manhattan(self, other):
        return abs(self[0] - other[0]) + abs(self[1] - other[1])
UP = V2(0,-1)
DOWN = V2(0, 1)
LEFT = V2(-1, 0)
RIGHT = V2(1, 0)


DIRECTIONS = {
    "U": UP,
    "R": RIGHT,
    "D": DOWN,
    "L": LEFT,
}

STARTING = "S"
ROCK = "#"
SPACE = "."
REACHABLE = "O"


class Map:  # basics brought from dia14.py
    def __init__(self, data:str):
        self.load(data)
    def load(self, data):
        S = data.index("S")
        self.data = [list(line) for line in data.split("\n")]
        self.width = len(self.data[0])
        self.height = len(self.data)
        self.starting_pos = S % (self.width + 1), S // (self.width + 1)
        self[self.starting_pos] = REACHABLE

    def reset(self, place_start=True):
        for pos in self.iter_positions():
            if self[pos] == REACHABLE:
                self[pos] = SPACE
        if place_start:
            self[self.starting_pos] = REACHABLE


    def __getitem__(self, pos):
        if not 0 <= pos[0] < self.width or not 0 <= pos[1] < self.height:
            return ROCK
        return self.data[pos[1]][pos[0]]
    def __setitem__(self, pos, val):
        self.data[pos[1]][pos[0]] = val

    def check_neigbours(self, pos, watch_for=REACHABLE):
        return any(self[pos + delta] == watch_for for delta in DIRECTIONS.values())

    def iter_positions(self):
        for y in range(self.height):
            for x in range(self.width):
                yield V2(x,y)

    def step(self):
        next_gen = set()
        for pos in self.iter_positions():
            if self[pos] in (SPACE, REACHABLE) and self.check_neigbours(pos):
                next_gen.add(pos)
        for pos in self.iter_positions():
            if pos in next_gen:
                self[pos] = REACHABLE
            elif self[pos] == REACHABLE:
                self[pos] = SPACE

    def count(self):
        return sum(self[pos] == REACHABLE for pos in self.iter_positions())

    def __repr__(self):
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += self[x,y]
            lines.append(line)
        return "\n".join(lines)

"""
Sugestão para a parte 2 (adiada  -resolvi fazer a parte 1 dos puzzles primeiro)
criar um mapa sem pedras: o número de posições alcançavel em
cada ladrilho de mapa é fixo. Subtraindo-se as pedras,
o número de um ladrilho sempre vai variar entre dois números.

Para interaçoes pares, sempre é um xadrez que exclui a posiçao inicial,
e para interações impares, é um xadrez que inclui a posiçao inicial.
O alcance sempre vai ser um "diamante" com "raio manhattan distance"
igual ao número de passos.

Calcular para os tiles no limite do numero de passos (26501365) o que está dentro
e o que está fora do tile
(são 26_500_000 X 4 passos no perímetro // tamanho do tile 131: ~820.000 tiles
para calcular os pontos de interseção e contar a área ocupada).


, e somar só as opções alcançáveis nesse limite
e somar um número fixo para cada tile incluso. (o mapa tem 131 x 131 então
se repete exatamente, entre vizinhos, e não se alternando como
num tabuleiro de xadrez 8x8
" "
