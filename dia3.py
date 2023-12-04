class Mapa:
    def __init__(self, dados):
        self.dados = dados.split("\n") if isinstance(dados, str) else dados
        self.larg = len(self.dados[0])
        self.alt = len(self.dados)

    def _getitem (self, pos):
        return self.dados[pos[1]][pos[0]]

    def __getitem__(self, pos):
        x, y = pos
        if x < 0 or y < 0 or x >= self.larg or y >= self.alt:
            return (None, False)
        elemento = self._getitem(pos)
        adjacente = False
        if elemento == ".":
            elemento = None
        elif elemento.isdigit():
            numero = ""
            while x >= 0 and self._getitem((x, y)).isdigit():
                x -= 1
            x += 1
            while x < self.larg and (digito := self._getitem((x,y))).isdigit():
                numero += digito
                x += 1
            elemento = int(numero)
            x_final = x; x_inicial = x - len(numero) -1
            for linha in (y-1, y, y + 1):
                for col in range(x_inicial, x_final + 1):
                    if linha < 0 or linha >= self.alt or col < 0 or col >= self.larg:
                        continue
                    if linha == y and not(col <= x_inicial or col >= x_final):
                        continue
                    if self._getitem((col, linha)) not in ".0123456789":
                        adjacente = True
                        break
        return (elemento, adjacente)
    def __iter__(self):
        for y in range(0, self.alt):
            x_inicio = -100
            ultimo_numero = -1
            for x in range(0, self.larg):
                elemento, conectado = self[x, y]
                if isinstance(elemento, int) and conectado:
                    if elemento != ultimo_numero or x - x_inicio > len(str(elemento)):
                        yield elemento
                        ultimo_numero = elemento
                        x_inicio = x

    def __repr__(self):
        return "\n".join(self.dados)

class MapaParte2(Mapa):
    def __iter__(self):
        for y in range(0, self.alt):
            for x in range(0, self.larg):
                if self._getitem((x, y)) != "*":
                    continue
                numeros = list()
                for desl_y in (-1, 0, 1):
                    for desl_x in (-1, 0, 1):
                        if desl_x == 0 and desl_y == 0:
                            continue
                        pos = x + desl_x, y + desl_y
                        numero, _ = self[pos]
                        if isinstance(numero, int):
                            if numero not in numeros:
                                numeros.append(numero)
                                pos_inicio = pos
                            elif pos[1] != pos_inicio[1] or pos[0] - pos_inicio[0] > len(str(numero)):
                                numeros.append(numero)
                                pos_inicio = pos

                if len(numeros) == 2:
                    yield numeros[0] * numeros[1]

