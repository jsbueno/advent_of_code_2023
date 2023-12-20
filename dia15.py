def hash_(text):
    v = 0
    for char in text:
        v += ord(char)
        v *= 17
        v %= 0x100
    return v

def doit(data):
    data = data.replace("\n", "")
    return sum(hash_(com) for com in data.split(","))


def setup(steps):
    boxes = {}
    for step in steps:
        label = step[:-1] if step[-1] == "-" else step.split("=")[0]
        box = hash_(label)
        if step[-1] == "-":
            boxes.get(box, {}).pop(label, None)
        else: # "="
            lens_power = int(step.split("=")[1])
            boxes.setdefault(box, {})[label] = lens_power
    return boxes

def focus(index, boxes):
    total = 0
    for lens_index, (label, power) in enumerate(boxes.items(), 1):
        lens = (index + 1) * lens_index * power
        total += lens
        print (index, lens)
    return total

def doit_part2(data):
    steps = data.split(",")

    boxes = setup(steps)
    return sum(focus(index, box) for index, box in  boxes.items())
