from __future__ import annotations

import inspect
import logging
import random
import sys
from collections import defaultdict
from typing import TYPE_CHECKING, ClassVar, Final

from dopynion.data_model import (
    CardName,
    CardNameAndHand,
    Cards,
    Hand,
    MoneyCardsInHand,
    PossibleCards,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import TracebackType

    from dopynion.player import Player

logger = logging.getLogger(__name__)


# TODO ajout robustesse sur action invalide
# TODO afficher dans les logs les résultats de hook
# TODO vérifier que l'on répond avec une carte dans possible_cards


class ErrorManager:
    def __init__(self, player: Player) -> None:
        self.player = player

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is not None:
            self.player.game.record.add_error(
                f"Error: {exc_type!r} {exc_val!r}",
                self.player,
            )
            self.player.eliminate()
            self.player.game.save()
        return True


class ClassNameRepr(type):
    def __repr__(cls) -> str:
        return cls.__name__


class Card(metaclass=ClassNameRepr):
    types: ClassVar[dict[CardName, type[Card]]] = {}
    card_set = "baseset"
    name = "Unknown"
    cost = 10_000
    money = 0
    is_action = False
    is_kingdom = True
    is_treasure = False
    is_victory = False
    more_cards_from_deck = 0
    more_purchases = 0
    more_actions = 0
    more_money = 0
    victory_points = 0

    @classmethod
    def card_name(cls) -> CardName:
        return CardName[cls.__name__.upper()]

    @staticmethod
    def class_(card_name: str) -> type[Card]:
        return Card.types.get(CardName[card_name.upper()], Card)

    def __init_subclass__(cls) -> None:
        Card.types[cls.card_name()] = cls

    def __eq__(self, other: object) -> bool:
        return isinstance(self, type(other)) or self.__class__ is other

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def action(cls, player: Player) -> None:
        for _ in range(cls.more_cards_from_deck):
            card_name = player.take_one_card_from_deck()
            if card_name is not None:
                player.hand.append(card_name)
        player.purchases_left += cls.more_purchases
        player.actions_left += cls.more_actions
        player.money += cls.more_money

        with ErrorManager(player):
            cls._action(player)

    @classmethod
    def _action(cls, player: Player) -> None:
        pass

    @classmethod
    def buy(cls, player: Player) -> None:
        with ErrorManager(player):
            cls._buy(player)

    @classmethod
    def _buy(cls, player: Player) -> None:
        pass


class Adventurer(Card):
    name = "Aventurier"
    cost = 6
    is_action = True
    nb_treasure_cards = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_kept_cards = 0
        while nb_kept_cards < cls.nb_treasure_cards:
            card_name = player.take_one_card_from_deck()
            if card_name is None:
                break
            if Card.class_(card_name).is_treasure:
                nb_kept_cards += 1
                player.hand.append(card_name)
            else:
                player.discard.append(card_name)


class Artificer(Card):
    name = "Maître artisan"
    card_set = "adventures"
    cost = 5
    is_action = True
    more_actions = 1
    more_cards_from_deck = 1
    more_money = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_discarded_cards = 0
        for card_name in player.hand.copy():
            if player.use_hook(
                player.hooks.confirm_discard_card_from_hand,
                CardNameAndHand(card_name=card_name, hand=list(player.hand)),
            ):
                player.hand.remove(card_name)
                player.discard.append(card_name)
                nb_discarded_cards += 1

        possible_cards: list[CardName] = list({
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.class_(card_name).cost == nb_discarded_cards
        })
        if possible_cards:
            chosen_card_name = player.use_hook(
                player.hooks.choose_card_to_receive_in_deck,
                PossibleCards(possible_cards=possible_cards),
            )
            card_name = CardName[chosen_card_name.upper()]
            player.game.stock.remove(card_name)
            player.deck.prepend(card_name)


class Bandit(Card):
    name = "Bandit"
    card_set = "baseset2add"
    cost = 5
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        if CardName.GOLD in player.game.stock:
            player.game.stock.remove(CardName.GOLD)
            player.discard.append(CardName.GOLD)
        for other_player in player.other_players():
            with ErrorManager(other_player):
                drawn_cards = [
                    card_name
                    for _ in range(2)
                    if (card_name := other_player.take_one_card_from_deck()) is not None
                ]
                trashable_money_cards = [
                    card_name
                    for card_name in drawn_cards
                    if card_name in (treasure_card_name - {CardName.COPPER})
                ]
                trashable_money_cards.sort(key=lambda c: Card.class_(c).money)
                if trashable_money_cards:
                    # TODO afficher dans le log
                    drawn_cards.remove(trashable_money_cards[0])
                for card_name in drawn_cards:
                    other_player.discard.append(card_name)


class Bureaucrat(Card):
    name = "Bureaucrate"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        silver = Silver.card_name()
        if silver in player.game.stock:
            player.deck.prepend(silver)
            player.game.stock.remove(silver)
        for other_player in player.other_players():
            with ErrorManager(other_player):
                victory_cards = other_player.hand.victory_cards
                if victory_cards:
                    other_player.deck.prepend(victory_cards[0])
                    other_player.hand.remove(victory_cards[0])


class Cellar(Card):
    name = "Cave"
    cost = 2
    is_action = True
    more_actions = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_discarded_cards = 0
        for card_name in player.hand.copy():
            if player.use_hook(
                player.hooks.confirm_discard_card_from_hand,
                CardNameAndHand(card_name=card_name, hand=list(player.hand)),
            ):
                player.hand.remove(card_name)
                player.discard.append(card_name)
                nb_discarded_cards += 1
        for _ in range(nb_discarded_cards):
            discarded_card_name = player.take_one_card_from_deck()
            if discarded_card_name is not None:
                player.hand.append(discarded_card_name)


class Chancellor(Card):
    name = "Chancelier"
    cost = 3
    is_action = True
    more_money = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        if player.use_hook(player.hooks.confirm_discard_deck):
            player.deck.empty_to(player.discard)


class Chapel(Card):
    name = "Chapelle"
    cost = 2
    is_action = True
    max_trashed_cards: Final[int] = 4

    @classmethod
    def _action(cls, player: Player) -> None:
        nb_trashed_cards = 0
        for card_name in player.hand.copy():
            if player.use_hook(
                player.hooks.confirm_trash_card_from_hand,
                CardNameAndHand(card_name=card_name, hand=list(player.hand)),
            ):
                player.hand.remove(card_name)
                nb_trashed_cards += 1
            if nb_trashed_cards >= cls.max_trashed_cards:
                break


class Colony(Card):
    name = "Colonie"
    card_set = "prosperity"
    cost = 11
    is_kingdom = False
    is_victory = True
    victory_points = 10


class Copper(Card):
    name = "Cuivre"
    cost = 0
    money = 1
    is_kingdom = False
    is_treasure = True


class CouncilRoom(Card):
    name = "Chambre du conseil"
    cost = 5
    is_action = True
    more_cards_from_deck = 4
    more_purchases = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            with ErrorManager(other_player):
                card_name = other_player.take_one_card_from_deck()
                if card_name is not None:
                    other_player.hand.append(card_name)


class Curse(Card):
    name = "Malédiction"
    cost = 0
    is_kingdom = False
    is_victory = True
    victory_points = -1


class CursedGold(Card):
    name = "Or maudit"
    card_set = "nocturne"
    cost = 4
    money = 3
    is_kingdom = False
    is_treasure = True

    @classmethod
    def _buy(cls, player: Player) -> None:
        if CardName.CURSE in player.game.stock:
            player.game.stock.remove(CardName.CURSE)
            player.discard.append(CardName.CURSE)


class DistantShore(Card):
    name = "Rivage lointain"
    card_set = "allies"
    cost = 6
    is_action = True
    is_victory = True
    more_actions = 1
    more_cards_from_deck = 2
    victory_points = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        if CardName.ESTATE in player.game.stock:
            player.game.stock.remove(CardName.ESTATE)
            player.discard.append(CardName.ESTATE)


class Duchy(Card):
    name = "Duché"
    cost = 5
    is_kingdom = False
    is_victory = True
    victory_points = 3


class Estate(Card):
    name = "Domaine"
    cost = 2
    is_kingdom = False
    is_victory = True
    victory_points = 1


class FairGrounds(Card):
    name = "Champ de foire"
    card_set = "cornucopia"
    cost = 6
    is_victory = True


class FarmingVillage(Card):
    name = "Village agricole"
    card_set = "cornucopia"
    cost = 4
    is_action = True
    more_actions = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        drawn_cards = CardContainer()
        while (card_name := player.take_one_card_from_deck()) is not None:
            class_ = Card.class_(card_name)
            if class_.is_treasure or class_.is_action:
                player.hand.append(card_name)
                break
            drawn_cards.append(card_name)
        drawn_cards.empty_to(player.discard)


class Feast(Card):
    name = "Festin"
    cost = 4
    is_action = True
    max_new_card_cost: Final[int] = 5

    @classmethod
    def _action(cls, player: Player) -> None:
        player.played_cards.pop()
        possible_cards: list[CardName] = list({
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.class_(card_name).cost <= cls.max_new_card_cost
        })
        if possible_cards:
            chosen_card_name = player.use_hook(
                player.hooks.choose_card_to_receive_in_discard,
                PossibleCards(possible_cards=possible_cards),
            )
            card_name = CardName[chosen_card_name.upper()]
            player.game.stock.remove(card_name)
            player.discard.append(card_name)


class Festival(Card):
    name = "Festival"
    cost = 5
    is_action = True
    more_purchases = 1
    more_actions = 2
    more_money = 2


class FortuneTeller(Card):
    name = "Diseuse de bonne aventure"
    card_set = "cornucopia"
    cost = 3
    is_action = True
    more_money = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            with ErrorManager(other_player):
                drawn_cards = CardContainer()
                while (card_name := other_player.take_one_card_from_deck()) is not None:
                    if Card.class_(card_name).is_victory:
                        other_player.deck.prepend(card_name)
                        break
                    drawn_cards.append(card_name)
                drawn_cards.empty_to(other_player.discard)


class Gardens(Card):
    name = "Jardins"
    cost = 4
    is_victory = True


class Gold(Card):
    name = "Or"
    cost = 6
    money = 3
    is_kingdom = False
    is_treasure = True


class Harvest(Card):
    name = "Récolte"
    card_set = "cornucopia"
    cost = 5
    is_action = True
    nb_drawn_cards: Final[int] = 4

    @classmethod
    def _action(cls, player: Player) -> None:
        drawn_cards = CardContainer()
        while (card_name := player.take_one_card_from_deck()) is not None:
            drawn_cards.append(card_name)
            if len(drawn_cards) == cls.nb_drawn_cards:
                break
        nb_different_cards = len(set(drawn_cards))
        drawn_cards.empty_to(player.discard)
        for _ in range(nb_different_cards):
            card_name = player.take_one_card_from_deck()
            if card_name is None:
                break
            player.hand.append(card_name)


class Hireling(Card):
    name = "Recrue"
    card_set = "adventures"
    cost = 6
    is_action = True
    more_cards_from_deck = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        player.played_cards.pop()
        player.nb_hireling += 1


class Laboratory(Card):
    name = "Laboratoire"
    cost = 5
    is_action = True
    more_cards_from_deck = 2
    more_actions = 1


class Library(Card):
    name = "Bibliothèque"
    cost = 5
    is_action = True
    target_hand_size: Final[int] = 7

    @classmethod
    def _action(cls, player: Player) -> None:
        skipped_cards = CardContainer()
        while len(player.hand) < cls.target_hand_size:
            card_name = player.take_one_card_from_deck()
            if card_name is None:
                break
            if not Card.class_(card_name).is_action:
                player.hand.append(card_name)
            elif player.use_hook(
                player.hooks.skip_card_reception_in_hand,
                CardNameAndHand(card_name=card_name, hand=list(player.hand)),
            ):
                skipped_cards.append(card_name)
            else:
                player.hand.append(card_name)
        skipped_cards.empty_to(player.discard)


class Magnate(Card):
    name = "Magnat"
    card_set = "prosperity2add"
    cost = 5
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        for _ in list(player.hand.money_cards):
            card_name = player.take_one_card_from_deck()
            if card_name is not None:
                player.hand.append(card_name)


class Magpie(Card):
    name = "Pie voleuse"
    card_set = "adventures"
    cost = 4
    is_action = True
    more_actions = 1
    more_cards_from_deck = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        card_name = player.take_one_card_from_deck()
        if card_name is not None:
            if card_name in treasure_card_name:
                player.hand.append(card_name)
            else:
                player.deck.prepend(card_name)
                if CardName.MAGPIE in player.game.stock:
                    player.game.stock.remove(CardName.MAGPIE)
                    player.discard.append(CardName.MAGPIE)


class Market(Card):
    name = "Marché"
    cost = 5
    is_action = True
    more_cards_from_deck = 1
    more_purchases = 1
    more_actions = 1
    more_money = 1


class Marquis(Card):
    name = "Marquis"
    card_set = "allies"
    cost = 6
    is_action = True
    more_purchases = 1
    hand_size_left: Final[int] = 10

    @classmethod
    def _action(cls, player: Player) -> None:
        for _ in list(player.hand):
            card_name = player.take_one_card_from_deck()
            if card_name is not None:
                player.hand.append(card_name)
        while len(player.hand) > cls.hand_size_left:
            removed_card = player.use_hook(
                player.hooks.discard_card_from_hand,
                Hand(hand=list(player.hand)),
            )
            player.hand.remove(CardName[removed_card.upper()])
            player.discard.append(CardName[removed_card.upper()])


class Militia(Card):
    name = "Milice"
    cost = 4
    is_action = True
    more_money = 2
    enemy_hand_size_left: Final[int] = 3

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            with ErrorManager(other_player):
                while len(other_player.hand) > cls.enemy_hand_size_left:
                    removed_card = other_player.use_hook(
                        other_player.hooks.discard_card_from_hand,
                        Hand(hand=list(other_player.hand)),
                    )
                    other_player.hand.remove(CardName[removed_card.upper()])
                    other_player.discard.append(CardName[removed_card.upper()])


class Mine(Card):
    name = "Mine"
    cost = 5
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        money_cards: list[str] = list(set(player.hand.money_cards))
        if money_cards:
            trashed_card = player.use_hook(
                player.hooks.trash_money_card_for_better_money_card,
                MoneyCardsInHand(money_in_hand=money_cards),
            )
            if trashed_card is not None:
                trashed_card_name = CardName[trashed_card.upper()]
                player.hand.remove(trashed_card_name)
                possible_money_cards = [
                    card_name
                    for card_name in player.game.stock
                    if (class_ := Card.class_(card_name)).is_treasure
                    and class_.cost <= Card.class_(trashed_card_name).cost + 3
                    and player.game.stock.quantity(card_name)
                ]
                if possible_money_cards:
                    best_money = max(
                        possible_money_cards,
                        key=lambda card_name: Card.class_(card_name).money,
                    )
                    player.hand.append(best_money)


class MoneyLender(Card):
    name = "Prêteur sur gages"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        if player.hand.copper_qty >= 1 and player.use_hook(
            player.hooks.confirm_trash_card_from_hand,
            CardNameAndHand(card_name=CardName.COPPER, hand=list(player.hand)),
        ):
            player.hand.remove(CardName.COPPER)
            player.money += 3


class Platinum(Card):
    name = "Platine"
    card_set = "prosperity"
    cost = 9
    money = 5
    is_kingdom = False
    is_treasure = True


class Poacher(Card):
    name = "Braconnier"
    card_set = "baseset2add"
    cost = 4
    is_action = True
    more_cards_from_deck = 1
    more_actions = 1
    more_money = 1

    @classmethod
    def _action(cls, player: Player) -> None:
        for _ in range(player.game.stock.nb_empty_piles):
            if not player.hand:
                break
            removed_card = player.use_hook(
                player.hooks.discard_card_from_hand,
                Hand(hand=list(player.hand)),
            )
            player.hand.remove(CardName[removed_card.upper()])
            player.discard.append(CardName[removed_card.upper()])


class Port(Card):
    name = "Ville portuaire"
    card_set = "adventures"
    cost = 4
    is_action = True
    more_cards_from_deck = 1
    more_actions = 2


class Province(Card):
    name = "Province"
    cost = 8
    is_kingdom = False
    is_victory = True
    victory_points = 6


class Remake(Card):
    name = "Renouvellement"
    card_set = "cornucopia"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        for _ in range(2):
            if not player.hand:
                return
            trashed_card = player.use_hook(
                player.hooks.trash_card_from_hand,
                Hand(hand=list(player.hand)),
            )
            trashed_card_name = CardName[trashed_card.upper()]
            player.hand.remove(trashed_card_name)
            possible_cards: list[CardName] = list({
                card_name
                for card_name in player.game.stock
                if player.game.stock.quantity(card_name)
                and Card.class_(card_name).cost
                == Card.class_(trashed_card_name).cost + 1
            })
            if possible_cards:
                chosen_card = player.use_hook(
                    player.hooks.choose_card_to_receive_in_discard,
                    PossibleCards(possible_cards=possible_cards),
                )
                chosen_card_name = CardName[chosen_card.upper()]
                player.game.stock.remove(chosen_card_name)
                player.discard.append(chosen_card_name)


class Remodel(Card):
    name = "Rénovation"
    cost = 4
    is_action = True

    @classmethod
    def _action(cls, player: Player) -> None:
        if not player.hand:
            return
        trashed_card = player.use_hook(
            player.hooks.trash_card_from_hand,
            Hand(hand=list(player.hand)),
        )
        trashed_card_name = CardName[trashed_card.upper()]
        player.hand.remove(trashed_card_name)
        possible_cards: list[CardName] = list({
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.class_(card_name).cost <= Card.class_(trashed_card_name).cost + 2
        })
        if possible_cards:
            chosen_card = player.use_hook(
                player.hooks.choose_card_to_receive_in_discard,
                # TODO partout où il y a des possible_cards, vérifier que la réponse est
                # dans la liste
                PossibleCards(possible_cards=possible_cards),
            )
            chosen_card_name = CardName[chosen_card.upper()]
            player.game.stock.remove(chosen_card_name)
            player.discard.append(chosen_card_name)


class Silver(Card):
    name = "Argent"
    cost = 3
    money = 2
    is_kingdom = False
    is_treasure = True


class Smithy(Card):
    name = "Forgeron"
    cost = 4
    is_action = True
    more_cards_from_deck = 3


class Swap(Card):
    name = "Troc"
    card_set = "allies"
    cost = 5
    is_action = True
    more_cards_from_deck = 1
    more_actions = 1
    max_cost_swap = 5

    @classmethod
    def _action(cls, player: Player) -> None:
        for trashed_card_name in list(player.hand):
            if not Card.class_(trashed_card_name).is_action:
                continue
            # TODO c'est pas vraiment un trash, il faudrait utiliser un nouveau hook
            if player.use_hook(
                player.hooks.confirm_trash_card_from_hand,
                CardNameAndHand(card_name=trashed_card_name, hand=list(player.hand)),
            ):
                player.hand.remove(trashed_card_name)
                player.game.stock.append(trashed_card_name)

                possible_cards: list[CardName] = list({
                    card_name
                    for card_name in player.game.stock
                    if player.game.stock.quantity(card_name)
                    and Card.class_(card_name).cost <= cls.max_cost_swap
                    and Card.class_(card_name).is_action
                    and card_name != trashed_card_name
                })
                if possible_cards:
                    # TODO normalement ça ne va pas en discard, mais dans la main,
                    # nouveau hook à prévoir
                    chosen_card = player.use_hook(
                        player.hooks.choose_card_to_receive_in_discard,
                        # TODO partout où il y a des possible_cards, vérifier que la
                        # réponse est dans la liste
                        PossibleCards(possible_cards=possible_cards),
                    )
                    chosen_card_name = CardName[chosen_card.upper()]
                    player.game.stock.remove(chosen_card_name)
                    player.discard.append(chosen_card_name)

                break


class Village(Card):
    name = "Village"
    cost = 3
    is_action = True
    more_cards_from_deck = 1
    more_actions = 2


class Witch(Card):
    name = "Sorcière"
    cost = 5
    is_action = True
    more_cards_from_deck = 2

    @classmethod
    def _action(cls, player: Player) -> None:
        for other_player in player.other_players():
            with ErrorManager(other_player):
                if player.game.stock.curse_qty:
                    other_player.discard.append(CardName.CURSE)
                    player.game.stock.remove(CardName.CURSE)


class Woodcutter(Card):
    name = "Bucheron"
    cost = 3
    is_action = True
    more_purchases = 1
    more_money = 2


class Workshop(Card):
    name = "Atelier"
    cost = 3
    is_action = True
    max_cost_of_received_card: Final[int] = 4

    @classmethod
    def _action(cls, player: Player) -> None:
        possible_cards: list[str] = list({
            card_name
            for card_name in player.game.stock
            if player.game.stock.quantity(card_name)
            and Card.class_(card_name).cost <= cls.max_cost_of_received_card
        })
        possible_cards = list(set(possible_cards))
        logger.debug(possible_cards)
        if possible_cards:
            chosen_card = player.use_hook(
                player.hooks.choose_card_to_receive_in_discard,
                PossibleCards(possible_cards=possible_cards),
            )
            chosen_card_name = CardName[chosen_card.upper()]
            player.game.stock.remove(chosen_card_name)
            player.discard.append(chosen_card_name)


actions_card_name: set[CardName] = {
    CardName[name.upper()]
    for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_action
}

treasure_card_name: set[CardName] = {
    CardName[name.upper()]
    for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_treasure
}

victory_card_name: set[CardName] = {
    CardName[name.upper()]
    for name, class_ in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(class_, Card) and class_.name != "Unknown" and class_.is_victory
}


class CardContainer:
    """Storage for card."""

    def __init__(self) -> None:
        self._quantities: dict[CardName, int] = defaultdict(int)
        self._cards: list[CardName] = []

    def __getattr__(self, attribute: str) -> int:
        if attribute.endswith("_qty"):
            card_name = attribute[:-4]
            return self._quantities.get(CardName[card_name.upper()], 0)
        raise AttributeError

    def __repr__(self) -> str:
        return str(self._cards)

    def __add__(self, other: CardContainer) -> CardContainer:
        ret = CardContainer()
        for card_name in self:
            ret.append(card_name)
        for card_name in other:
            ret.append(card_name)
        return ret

    def __contains__(self, card_name: CardName) -> bool:
        return self._quantities.get(card_name, 0) > 0

    def __len__(self) -> int:
        return len(self._cards)

    def __getitem__(self, index: int) -> CardName:
        return self._cards[index]

    def __iter__(self) -> Iterator[CardName]:
        return iter(self._cards)

    def clear(self) -> None:
        self._quantities.clear()
        self._cards.clear()

    def copy(self) -> CardContainer:
        new = CardContainer()
        new._quantities = self._quantities.copy()
        new._cards = self._cards.copy()
        return new

    def prepend(self, card_name: CardName) -> None:
        """
        Insert next card to be played.

        Raises:
            KeyError: If unknown card_name.

        """
        if card_name not in Card.types:
            raise KeyError(card_name)
        self._cards.insert(0, card_name)
        self._quantities[card_name] += 1

    def append(self, card_name: CardName) -> None:
        if card_name not in Card.types:
            raise KeyError(card_name)
        self._cards.append(card_name)
        self._quantities[card_name] += 1

    def append_several(self, qty: int, card_name: CardName) -> None:
        for _ in range(qty):
            self.append(card_name)

    def remove(self, card_name: CardName) -> None:
        self._cards.remove(card_name)
        self._quantities[card_name] -= 1

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def contains_action(self) -> bool:
        return any(
            card_name in actions_card_name
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

    @property
    def victory_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if card_name in victory_card_name:
                ret.append_several(qty, card_name)
        return ret

    @property
    def action_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if card_name in actions_card_name:
                ret.append_several(qty, card_name)
        return ret

    def contains_money(self) -> bool:
        return any(
            card_name in treasure_card_name
            for card_name, qty in self._quantities.items()
            if qty > 0
        )

    @property
    def money_cards(self) -> CardContainer:
        ret = CardContainer()
        for card_name, qty in self._quantities.items():
            if card_name in treasure_card_name:
                ret.append_several(qty, card_name)
        return ret

    @property
    def money(self) -> int:
        return sum(
            Card.class_(card_name).money * quantity
            for card_name, quantity in self._quantities.items()
        )

    def pop(self, index: int = -1) -> CardName:
        card_name = self._cards.pop(index)
        self._quantities[card_name] -= 1
        return card_name

    def quantity(self, card_name: CardName) -> int:
        return self._quantities.get(card_name, 0)

    def sort(self, key: Callable, *, reverse: bool = False) -> None:
        self._cards.sort(key=key, reverse=reverse)

    def empty_to(self, other: CardContainer) -> None:
        while self:
            card_name = self.pop(0)
            other.append(card_name)
        self._quantities.clear()
        self._cards.clear()

    @property
    def nb_empty_piles(self) -> int:
        return sum(1 for qty in self._quantities.values() if qty == 0)

    @property
    def three_empty_piles(self) -> bool:
        nb_piles = 3
        return self.nb_empty_piles >= nb_piles

    @property
    def state(self) -> Cards:
        return Cards(
            quantities={
                card_name: quantity
                for card_name, quantity in self._quantities.items()
                if quantity > 0
            },
        )
