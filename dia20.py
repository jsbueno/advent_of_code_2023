from collections import deque
from textwrap import dedent as D

class BaseModule:
    type_id = ""

    type_registry = {}
    tick = 0

    def __init_subclass__(cls, *args, **kw):
        cls.type_registry[cls.type_id] = cls

    @classmethod
    def new_from_descr(cls, container, descr):
        return cls.type_registry[descr[0]](container, descr)

    def __init__(self, container, descr):
        #descr = descr.strip()
        self.container = container
        name, outputs = descr.split(" -> ")
        if name == "broadcaster": name = " broadcaster"
        self.name = name[1:]
        self.outputs = outputs.split(", ")
        self.pulse_queue = deque()
        self.container.modules[self.name] = self
        self.reset()

    def reset(self):
        self.state = 0

    def send(self, type_: "Literal['high', 'low']"):
        outputs = []
        for output_str in self.outputs:
            self.container.pulse_counter(type_)
            output = self.container.modules.get(output_str, None)
            if output:
                outputs.append(output)
                output.receive((self, self.tick, type_))
        __class__.tick += 1

        # processing all pulses a separate loop ensures execution order
        for output in outputs:
            output.process()

    def receive(self, pulse):
        self.pulse_queue.append(pulse)

    def process(self):
        pass

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"{type(self).__name__} module {self.type_id}{self.name} -> {', '.join(self.outputs)}. State: {self.state}"

class Output(BaseModule):
    type_id = "O"

class Button(BaseModule):
    type_id = "X"

    def press(self):
        self.send("low")

class Broadcaster(BaseModule):
    type_id = "b"

    def process(self):
        # if there was a way to have more than one pulse
        # sent here in a single "tick", a mechanism
        # for checking the tick number here would keep the order.

        # as it is, though, as a module can only be in the outputs
        # of a conneced module a single time, that is not needed.
        origin, tick, pulse = self.pulse_queue.popleft()
        self.send(pulse)

class FlipFlop(BaseModule):
    type_id = "%"

    def process(self):
        origin, tick, type_ = self.pulse_queue.popleft()
        if type_ == "low":
            self.state ^= 1
            self.send("high" if self.state else "low")

class Conjunction(BaseModule):
    type_id = "&"

    def reset(self):
        # super().reset()
        self.memory = {input: "low" for input in self.container.modules.values() if self.name in input.outputs}

    @property
    def state(self):
        return int(all(last=="high" for last in self.memory.values()))

    def process(self):
        origin, tick, type_ = self.pulse_queue.popleft()
        self.memory[origin] = type_
        self.send("low" if self.state else "high")


class WireUp:
    baseconf = D("""\
        Xbutton -> broadcaster
        Ooutput -> output\n""")

    def __init__(self, conf):
        conf = self.baseconf + conf
        self.modules = dict()
        self.load(conf)
        self.reset()

    def reset(self):
        self.counter = {"high": 0, "low": 0}
        for module in self.modules.values():
            module.reset()

    def load(self, conf):
        for module_descr in conf.split("\n"):
            BaseModule.new_from_descr(self, module_descr)

    def pulse_counter(self, type_):
        self.counter[type_] += 1

    def doit(self, times=1000):
        for i in range(times):
            self.modules["button"].press()
        return repr(self)

    def doit_part2(self):
        self.reset()
        self.load("Orx -> output")
        rx = self.modules["rx"]
        def process():
            origin, tick, type_ = rx.pulse_queue.popleft()
            if type_ == "low":
                raise RuntimeError()
        rx.process = process
        i = 0
        while True:
            i += 1
            try:
                self.modules["button"].press()
            except RuntimeError:
                break
            if not i%1000:
                print(i)
        return i

    def __repr__(self):
        return f"{self.__class__.__name__} with ({len(self.modules)}) and {self.counter} pulses sent. ({self.counter['high'] * self.counter['low']})"
