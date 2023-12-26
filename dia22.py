class V3(tuple):
    def __new__(cls, x, y=None, z=None):
        if isinstance(x, str):
            x = [int(comp.strip()) for comp in x.split(",")]
        elif y != None:
            x = (x, y, z)
        return super().__new__(cls, x)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]

    def __add__(self, other):
        return type(self)((self.x + other[0], self.y + other[1], self.z + other[2]))

    __radd__ = __add__

    def __sub__(self, other):
        return type(self)(self.x - other[0], self.y - other[1], self.z - other[2])

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1] and self[2] == other[2]

    def __hash__(self):
        return hash(tuple(self))

    def __neg__(self):
        return type(self)(-self.x, -self.y, -self.z)

    def __mul__(self, other):
        return type(self)(self.x * other, self.y * other, self.z * other)

    __rmul__ = __mul__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x}, {self.y}, {self.z})"

    def manhattan(self, other):
        return abs(self[0] - other[0]) + abs(self[1] - other[1]) + abs(self[2] - other[2])

X, Y, Z = V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)

def sgn(num):  # this is missing from Python built-ins
    return 1 if num > 0 else -1 if num != 0 else 0

class Block:
    def __init__(self, well, line, nick=""):
        self.well = well
        self.nick = nick
        v1, v2 = map(V3, line.split("~"))
        self.shape = v2 - v1
        self.offset = min(v1, v2, key=lambda v: v.z)
        self.orientation = X if self.shape.x else Y if self.shape.y else Z
        self.length = 1 + self.shape[0 if self.shape.x else 1 if self.shape.y else 2]
        self.supporting = set()
        self.add_to()

    def __iter__(self):
        """yields all cubes ocuppied by this block in the owner"""
        for i in range(0, self.length, sgn(self.length)):
            yield self.offset + i * self.orientation

    def _update(self, mode: "Literal['add', 'remove']"):
        """adds or removes self's cubes to Well all-cube structure"""
        # TBD: maybe consider "de-refactoring" this method?
        collision = False
        for offset in self:
            if mode == "add":
                if other:=self.well.voxels.get(offset, None):
                    collision = other
                self.well.voxels[offset] = self
            else:
                self.well.voxels.pop(offset, None)
        return collision


    add_to = lambda self: self._update("add")
    remove_from = lambda self: self._update("remove")

    def update(self, to_pos):
        self.remove_from()
        self.offset = to_pos
        if other:=self.add_to():
            raise ValueError("Block Collision: {self} with {other}")

    def __del__(self):
        self.remove_from()

    def __repr__(self):
        return f"Block {self.shape} at {self.offset}" if not self.nick else self.nick

class Well:
    def __init__(self, data):
        self.voxels = dict()
        self.blocks = list()
        self.load(data)

    def load(self, data):
        for line in data.split("\n"):
            self.blocks.append(Block(self, line))

    def __getitem__(self, pos):
        return self.voxels.get(pos)

    def reset_blocks(self):
        self.blocks.sort(key=lambda block: block.offset.z)
        for block in self.blocks:
            block.supporting = set()
            block.supported_by = set()

    def process_fall(self):
        self.reset_blocks()
        heights = dict()
        for block in self.blocks:
            target_z = 1
            for voxel in block:
                target_z = max(target_z, heights.get((voxel.x, voxel.y), 0) + 1)
            block.update(V3(block.offset.x, block.offset.y, target_z))
            for voxel in block:
                resting_at = V3(voxel.x, voxel.y, target_z - 1)
                heights[voxel.x, voxel.y] = voxel.z
                if supporter:= self[resting_at]:
                    supporter.supporting.add(block)
                    block.supported_by.add(supporter)


    def doit(self):
        self.process_fall()
        desintegrable = {block for block in self.blocks for supported in block.supporting if len(supported.supported_by) > 1}
        desintegrable.update(block for block in self.blocks if not block.supporting)
        return desintegrable

    def __repr__(self):
        return f"Well <{self.voxels}>"

