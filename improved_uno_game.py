from random import shuffle

"""
Rules from: https://www.unorules.org/how-many-cards-in-uno/ 
"""

COLOURS = ("RED", "GREEN", "BLUE", "YELLOW")
RANKS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "Draw2")
WILD_RANKS = ("Wild", "Draw4")


class Card:
  def __init__(self, colour: str | None, rank: str) -> None:
    self.rank: str = rank
    self.colour: str = colour if (rank not in WILD_RANKS) else "BLACK"

  def __repr__(self) -> str:
    return f"{self.colour} {self.rank}" 

  def __str__(self) -> str:
    return f"{self.colour} {self.rank}"

  def can_play_on(self, other_card: 'Card') -> bool:
    return (self.colour == other_card.colour or
            self.rank == other_card.rank or
            self.rank in WILD_RANKS)

  def is_wild(self) -> bool:
    return self.rank in WILD_RANKS

  def is_action(self) -> bool:
    return self.rank in RANKS[10:] or self.rank in WILD_RANKS

  def is_number(self) -> bool:
    return self.rank in RANKS[:10]

  def reset_wild_colour(self) -> None:
    if self.is_wild():
      self.colour = "BLACK"


class Deck:
  def __init__(self) -> None:
    self.cards: list[Card] = self._create_deck()
    self.shuffle()

  def _create_deck(self) -> list[Card]:
    cards: list[Card] = []
    
    # Add numbered and action cards for each color
    for colour in COLOURS:
      # One zero card per color
      cards.append(Card(colour, "0"))
      # Two of each numbered card (1-9) and action card per color
      for rank in RANKS[1:]:
        cards.extend([Card(colour, rank), Card(colour, rank)])

    # Add wild cards (4 of each type)
    for rank in WILD_RANKS:
      cards.extend([Card(None, rank) for _ in range(4)])
        
    return cards

  def shuffle(self) -> None:
    shuffle(self.cards)

  def deal(self) -> Card | None:
    return self.cards.pop() if self.cards else None

  def is_empty(self) -> bool:
    return not self.cards

  def add_cards(self, cards: list[Card]) -> None:
    for card in cards:
      card.reset_wild_colour()
    self.cards.extend(cards)

  def __len__(self) -> int:
    return len(self.cards)


class Player:
  """
  Derive HumanPlayer and ComputerPlayer from this class
  """
  def __init__(self, name: str) -> None:
    self.name: str = name
    self.cards: list[Card] = []

  def add_card(self, card: Card | None) -> None:
    if card:
      self.cards.append(card)

  def add_cards(self, cards: list[Card]) -> None:
    self.cards.extend(cards)

  def get_playable_cards(self, top_card: Card) -> list[Card]:
    return [card for card in self.cards if card.can_play_on(top_card)]

  def play_card(self, card: Card) -> Card | None:
    if card in self.cards:
      self.cards.remove(card)
      return card
    return None

  def has_uno(self) -> bool:
    return len(self.cards) == 1

  def has_won(self) -> bool:
    return len(self.cards) == 0

  def __len__(self) -> int:
    return len(self.cards)


class HumanPlayer(Player):
  def choose_card_to_play(self, playable_cards: list[Card], top_card: Card) -> Card | None:
    self._display_hand()
    self._display_playable_cards(playable_cards)
    
    while True:
      try:
        choice_str = input("Choose a card to play (by index), or 'd' to draw: ").strip().lower()
        if choice_str == 'd':
          return None

        choice = int(choice_str) - 1
        if 0 <= choice < len(self.cards):
          card_to_play = self.cards[choice]
          if card_to_play.can_play_on(top_card):
            return card_to_play
          else:
            print("Invalid play. That card cannot be played on the current top card.")
        else:
          print("Invalid index. Please choose an index from your hand.")
      except ValueError:
        print("Invalid input. Please enter a number or 'd'.")

  def _display_hand(self) -> None:
    print(f"\nYour hand ({len(self.cards)} cards):")
    for i, card in enumerate(self.cards, start=1):
      print(f"  {i}: {card}")

  def _display_playable_cards(self, playable_cards: list[Card]) -> None:
    if playable_cards:
      playable_indices = [str(self.cards.index(card) + 1) for card in playable_cards]
      print(f"Playable cards: {', '.join(playable_indices)}")

  def choose_wild_colour(self) -> str:
    print("\nChoose a new colour:")
    for i, colour in enumerate(COLOURS, start=1):
      print(f"  {i}: {colour}")
    
    while True:
      try:
        choice = input("Enter colour number or name: ").strip()
        
        if choice.isdigit():
          choice_num = int(choice)
          if 1 <= choice_num <= len(COLOURS):
            return COLOURS[choice_num - 1]
        
        choice_upper = choice.upper()
        if choice_upper in COLOURS:
          return choice_upper
            
        print("Invalid colour. Please try again.")
      except ValueError:
        print("Invalid input. Please try again.")

  def should_play_drawn_card(self, card: Card, top_card: Card) -> bool:
    if card.can_play_on(top_card):
      print(f"You drew: {card}")
      print("You can play the card you just drew.")
      while True:
        choice = input("Play it? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
          return True
        elif choice in ['n', 'no']:
          return False
        print("Please enter 'y' or 'n'.")
    return False


class ComputerPlayer(Player):
  def choose_card_to_play(self, playable_cards: list[Card], top_card: Card) -> Card | None:
    if not playable_cards:
      return None

    # Strategy: prefer same color, then numbers, then actions, then wild cards
    same_colour_cards = [c for c in playable_cards if c.colour == top_card.colour and not c.is_wild()]
    number_cards = [c for c in playable_cards if c.is_number()]
    action_cards = [c for c in playable_cards if c.is_action() and not c.is_wild()]
    wild_cards = [c for c in playable_cards if c.is_wild()]

    if same_colour_cards:
      same_colour_numbers = [c for c in same_colour_cards if c.is_number()]
      if same_colour_numbers:
        return same_colour_numbers[0]
      return same_colour_cards[0]
    elif number_cards:
      return number_cards[0]
    elif action_cards:
      return action_cards[0]
    else:
      return wild_cards[0] if wild_cards else None

  def choose_wild_colour(self) -> str:
    colour_counts: dict[str, int] = {colour: 0 for colour in COLOURS}
    
    for card in self.cards:
      if card.colour in colour_counts:
        colour_counts[card.colour] += 1
    
    if all(count == 0 for count in colour_counts.values()):
      return COLOURS[0]
        
    return max(colour_counts, key=colour_counts.get)

  def should_play_drawn_card(self, card: Card, top_card: Card) -> bool:
    return card.can_play_on(top_card)


class UnoGame:
  def __init__(self, player_names=None) -> None:
    if player_names is None:
      player_names = ["Player", "Computer"]
    
    self.players: list[Player] = [
      HumanPlayer(player_names[0]),
      ComputerPlayer(player_names[1])
    ]
    self.deck: Deck = Deck()
    self.discard_pile: list[Card] = []
    self.current_player_index: int = 0
    self.game_over: bool = False
    self.turn_direction: int = 1

    self._setup_game()

  def _setup_game(self) -> None:
    # Deal 7 cards to each player
    for _ in range(7):
      for player in self.players:
        card = self.deck.deal()
        if card:
          player.add_card(card)

    self._setup_initial_discard()

    print("""
    ██╗   ██╗███╗   ██╗ ██████╗ 
    ██║   ██║████╗  ██║██╔═══██╗
    ██║   ██║██╔██╗ ██║██║   ██║
    ██║   ██║██║╚██╗██║██║   ██║
    ╚██████╔╝██║ ╚████║╚██████╔╝
     ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
    """)
    print(f"Starting card: {self.get_top_card()}")
    print("=" * 40)

  def _setup_initial_discard(self) -> None:
    # Keep drawing until we get a number card for the starting card
    first_card = self.deck.deal()
    
    while first_card and (first_card.is_wild() or first_card.is_action()):
      self.deck.cards.insert(0, first_card)
      self.deck.shuffle()
      first_card = self.deck.deal()
    
    if first_card:
      self.discard_pile.append(first_card) 

  def get_top_card(self) -> Card | None:
    return self.discard_pile[-1] if self.discard_pile else None

  def get_current_player(self) -> Player:
    return self.players[self.current_player_index]

  def _next_player(self) -> None:
    self.current_player_index = (self.current_player_index + self.turn_direction) % len(self.players)

  def _reshuffle_deck(self) -> bool:
    if len(self.discard_pile) <= 1:
      print("Cannot reshuffle - not enough cards in discard pile!")
      return False
        
    print("Deck is empty. Reshuffling discard pile...")
    top_card = self.discard_pile.pop()
    self.deck.add_cards(self.discard_pile)
    self.deck.shuffle()
    self.discard_pile = [top_card]
    print(f"Deck reshuffled with {len(self.deck)} cards")
    return True

  def _draw_cards(self, player: Player, num_cards: int) -> int:
    cards_drawn = 0
    for _ in range(num_cards):
      if self.deck.is_empty():
        if not self._reshuffle_deck():
          break
      
      card = self.deck.deal()
      if card:
        player.add_card(card)
        cards_drawn += 1
            
    if cards_drawn > 0:
      print(f"{player.name} draws {cards_drawn} card{'s' if cards_drawn != 1 else ''}.")
    return cards_drawn

  def _handle_action_card(self, card: Card) -> None:
    if card.rank == "Skip":
      next_player = self._get_next_player()
      print(f"Skipping {next_player.name}'s turn!")
      self._next_player()
        
    elif card.rank == "Reverse":
      print("Turn order reversed!")
      self.turn_direction *= -1
      if len(self.players) == 2:
        self._next_player()
      
    elif card.rank == "Draw2":
      next_player = self._get_next_player()
      print(f"{next_player.name} must draw 2 cards and is skipped!")
      self._draw_cards(next_player, 2)
      self._next_player()
        
    elif card.is_wild():
      self._handle_wild_card(card)

  def _get_next_player(self) -> Player:
    next_index = (self.current_player_index + self.turn_direction) % len(self.players)
    return self.players[next_index]

  def _handle_wild_card(self, card: Card) -> None:
    current_player = self.get_current_player()
    new_colour = current_player.choose_wild_colour()
    
    print(f"{current_player.name} changes the colour to {new_colour}.")
    
    # Create a new card with the chosen color for the discard pile
    top_card = self.get_top_card()
    if top_card:
      top_card.colour = new_colour

    if card.rank == "Draw4":
      next_player = self._get_next_player()
      print(f"{next_player.name} must draw 4 cards and is skipped!")
      self._draw_cards(next_player, 4)
      self._next_player()

  def play_turn(self) -> None:
    player = self.get_current_player()
    print(f"\n--- {player.name}'s Turn ---")
    
    top_card = self.get_top_card()
    if not top_card:
      print("Error: No top card available!")
      return
        
    print(f"Top card: {top_card}")

    playable_cards = player.get_playable_cards(top_card)
    
    if playable_cards:
      card_to_play = player.choose_card_to_play(playable_cards, top_card)
      if card_to_play:
        self._play_card(player, card_to_play)
      else:
        self._handle_draw(player)
    else:
      print(f"{player.name} has no playable cards and must draw.")
      self._handle_draw(player)

    # Check win condition
    if player.has_won():
      print(f"\n🎉 {player.name} wins! 🎉")
      print("Game Over!")
      self.game_over = True
    elif player.has_uno():
      print(f"🔥 {player.name} has UNO! 🔥")

    if not self.game_over:
      self._next_player()
      print("=" * 40)

  def _handle_draw(self, player: Player) -> None:
    if self._draw_cards(player, 1) > 0:
      drawn_card = player.cards[-1]
      top_card = self.get_top_card()
      if top_card and player.should_play_drawn_card(drawn_card, top_card):
        self._play_card(player, drawn_card)

  def _play_card(self, player: Player, card: Card) -> None:
    played_card = player.play_card(card)
    if played_card:
      self.discard_pile.append(played_card)
      print(f"{player.name} plays: {played_card}")
      
      if played_card.is_action() or played_card.is_wild():
        self._handle_action_card(played_card)

  def is_game_over(self) -> bool:
    return self.game_over


def main():
  print("Welcome to UNO!")
  print("=" * 40)
  
  while True:
    try:
      game = UnoGame()
      
      while not game.is_game_over():
        game.play_turn()

      print("\nFinal Card Count:")
      for player in game.players:
        print(f"   {player.name}: {len(player)} cards")

      print("\n" + "=" * 40)
      while True:
        play_again = input("Play again? (y/n): ").lower().strip()
        if play_again in ("y", "yes"):
          print("\nStarting new game...\n")
          break
        elif play_again in ("n", "no"):
          print("Thanks for playing UNO!")
          return
        else:
          print("Invalid input. Please enter 'y' or 'n'.")
            
    except KeyboardInterrupt:
      print("\nThanks for playing UNO!")
      break
    except Exception as e:
      print(f"An error occurred: {e}")
      print("Starting a new game...")


if __name__ == "__main__":
  main()