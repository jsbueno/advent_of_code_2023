
# pip install extradict # to get "MapGetter"
# (optional)

aa = """32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483"""

from enum import Enum
from functools import cached_property

from extradict import MapGetter

class Rank(int, Enum):
    five_of_a_kind = 6
    four_of_a_kind = 5
    full_house = 4
    three_of_a_kind = 3
    two_pairs = 2
    pair = 1
    highest = 0



with MapGetter(Rank):
    from Rank import five_of_a_kind, four_of_a_kind, full_house, three_of_a_kind, two_pairs, pair, highest

# Magetter does just this:
# five_of_a_kind = Rank.five_of_a_kind
# ...



class Hand:
    values = {L: V for V, L in enumerate("23456789TJQKA")}
    #part1
    def __init__(self, cards, bid=0):
        self.cards = cards
        self.bid = bid
        self.sorted_cards = sorted(cards, key=lambda k: self.values[k])

    def __getitem__(self, index):
        return self.cards[index]

    @cached_property
    def count(self):
        result = {}
        for card in self.cards:
            result[card] = result.get(card, 0) + 1
        result = sorted(((v, k) for k, v in result.items()), reverse=True)
        return result

    @cached_property
    def rank(self):
        count = self.count
        if count[0][0] == 5:
            rank = five_of_a_kind
        elif count[0][0] == 4:
            rank = four_of_a_kind
        elif count[0][0] == 3 and count[1][0] == 2:
            rank = full_house
        elif count[0][0] == 3:
            rank = three_of_a_kind
        elif count[0][0] == 2 and count[1][0] == 2:
            rank = two_pairs
        elif count[0][0] == 2:
            rank = pair
        else:
            rank = highest
        return rank

    def key(self):
        return (
            self.rank,
            *(self.values[k] for k in self.cards)
        )

    def __repr__(self):
        return self.cards

def create_hand_list(data, cls=Hand):
    hands = []
    for line in data.split("\n"):
        hand_txt, bid_txt = line.split()
        hands.append(cls(hand_txt, int(bid_txt)))
    return hands

hands = create_hand_list(aa)
hands[0].bid
h = hands[0]


def total_winnings(data, cls=Hand):
    hands = create_hand_list(data, cls)
    hands.sort(key=Hand.key)
    total = 0
    for i, hand in enumerate(hands, 1):
        total += i * hand.bid
    return total

total = total_winnings(aa)

# part2

class HandPart2(Hand):
    values = {L: V for V, L in enumerate("J23456789TQKA")}

    @cached_property
    def count(self):
        preliminar = super().count
        joker_count = 0
        joker_position = None
        for i, card in enumerate(preliminar):
            if card[1] == "J":
                joker_count = card[0]
                joker_position = i
                break
        if not joker_count or joker_count == 5:
            return preliminar
        cards = preliminar
        del cards[joker_position]
        cards[0] = cards[0][0] + joker_count, cards[0][1]
        return cards

hands2 = create_hand_list(aa, cls=HandPart2)
