from dopynion.cards import Card, CardName

day1 = {
    CardName.COPPER,
    CardName.GOLD,
    CardName.SILVER,
    CardName.ESTATE,
    CardName.DUCHY,
    CardName.PROVINCE,
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
    CardName.COUNCILROOM,
    CardName.CURSE,
    CardName.CURSEDGOLD,
    CardName.DISTANTSHORE,
    CardName.FAIRGROUNDS,
    CardName.FARMINGVILLAGE,
    CardName.FEAST,
    CardName.FESTIVAL,
    CardName.FORTUNETELLER,
    CardName.GARDENS,
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
    CardName.REMAKE,
    CardName.REMODEL,
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
