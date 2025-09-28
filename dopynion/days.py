from dopynion.cards import Card, CardName

day1: set[CardName] = {
    CardName.COPPER,
    CardName.GOLD,
    CardName.SILVER,
    CardName.ESTATE,
    CardName.DUCHY,
    CardName.PROVINCE,
    CardName.FESTIVAL,
    CardName.LABORATORY,
    CardName.MARKET,
    CardName.SMITHY,
    CardName.VILLAGE,
    CardName.WOODCUTTER,
}

day2: set[CardName] = set()

day3: set[CardName] = {
    CardName.COUNCILROOM,
    CardName.CURSE,
    CardName.DISTANTSHORE,
    CardName.FARMINGVILLAGE,
    CardName.HIRELING,
    CardName.WITCH,
}

# begin hooks
day4: set[CardName] = {
    CardName.BANDIT,
    CardName.BUREAUCRAT,
    CardName.CHANCELLOR,
    CardName.GARDENS,
    CardName.MILITIA,
}

day5: set[CardName] = {
    CardName.ADVENTURER,
    CardName.CELLAR,
    CardName.FEAST,
    CardName.FORTUNETELLER,
    CardName.LIBRARY,
    CardName.MAGNATE,
    CardName.WORKSHOP,
}

day6: set[CardName] = {
    CardName.CHAPEL,
    CardName.MINE,
    CardName.MONEYLENDER,
    CardName.REMODEL,
    CardName.SWAP,
}

day7: set[CardName] = {
    CardName.ARTIFICER,
    CardName.COLONY,
    CardName.MARQUIS,
    CardName.POACHER,
    CardName.REMAKE,
}

day8: set[CardName] = {
    CardName.CURSEDGOLD,
    CardName.HARVEST,
    CardName.MAGPIE,
    CardName.PORT,
}

day9: set[CardName] = {
    CardName.FAIRGROUNDS,
    CardName.PLATINUM,
}


def init_day() -> None:
    allowed_cards = day1
    for card_name in list(Card.types):
        if card_name not in allowed_cards:
            Card.types.pop(card_name)
