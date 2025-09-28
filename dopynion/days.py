from dopynion.cards import Card, CardName

day1 = {
    CardName.VILLAGE,
}

unused_cards = [
    CardName.ADVENTURER,
    CardName.ARTIFICER,
    CardName.BANDIT,
    CardName.BUREAUCRAT,
    CardName.CELLAR,
    CardName.CHANCELLOR,
    CardName.CHAPEL,
    CardName.COLONY,
    CardName.COPPER,
    CardName.COUNCILROOM,
    CardName.CURSE,
    CardName.CURSEDGOLD,
    CardName.DISTANTSHORE,
    CardName.DUCHY,
    CardName.ESTATE,
    CardName.FAIRGROUNDS,
    CardName.FARMINGVILLAGE,
    CardName.FEAST,
    CardName.FESTIVAL,
    CardName.FORTUNETELLER,
    CardName.GARDENS,
    CardName.GOLD,
    CardName.HARVEST,
    CardName.HIRELING,
    CardName.LABORATORY,
    CardName.LIBRARY,
    CardName.MAGNATE,
    CardName.MAGPIE,
    CardName.MARKET,
    CardName.MARQUIS,
    CardName.MILITIA,
    CardName.MINE,
    CardName.MONEYLENDER,
    CardName.PLATINUM,
    CardName.POACHER,
    CardName.PORT,
    CardName.PROVINCE,
    CardName.REMAKE,
    CardName.REMODEL,
    CardName.SILVER,
    CardName.SMITHY,
    CardName.SWAP,
    CardName.WITCH,
    CardName.WOODCUTTER,
    CardName.WORKSHOP,
]


def init_day() -> None:
    allowed_cards = day1
    for card_name in list(Card.types):
        if card_name not in allowed_cards:
            Card.types.pop(card_name)
