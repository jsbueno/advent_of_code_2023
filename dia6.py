from collections import namedtuple
import pygame

race = namedtuple("race", "time distance")
times, distances = data.split("\n")
times = times.removeprefix("Time:").strip()
distances = distances.removeprefix("Distance:").strip()
races = [race(int(time), int(distance))  for time, distance in zip(times.split(), distances.split())]

# brute force function:
def calc_race(race):
    wins = 0
    for x in range(race.time):
        distance = x * (race.time - x)
        if distance > race.distance:
            wins += 1
    return wins

# brute force could calculate part 2 in under 20seconds -
# so, still good.  :-p
"""
analytic solution would go like, given the above:
    x * (race_time - x) > race_distance
    -x**2 + race_time * x - race_distance > 0
    # then fundamental school formula
    # delta = race.time ** 2 - 4 * -1 * +race.distance =>
def analyze_race(race):
    delta = race.time ** 2 - 4 * race.distance
    delta_root = delta ** 0.5
    x1 = (-race.time - delta_root) / -2
    x2 = (-race.time + delta_root) / -2
    return math.ceil(x1) - math.ceil(x2)


"""

# historam drawing brute-force func:
def calc_race(race, screen: "pygame.Surface=None", h_scale=10):
    wins = 0
    width, height = tela.get_size()
    bucket_width = width // race.time
    for x in range(race.time):
        color = (255,0,0)
        distance = x * (race.time - x)
        if distance > race.distance:
            color = (0, 255, 0)
            wins += 1
        if tela:
            pygame.draw.rect(screen, color, (bucket_width * x, height - distance * h_scale, bucket_width, distance * h_scale))
        pygame.display.update()
        time.sleep(0.05)
    return wins
