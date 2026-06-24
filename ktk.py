import random
import time

CARD_POOL = {
    "Slash": 30, "Dodge": 15, "Peach": 8, 
    "Ex Nihilo": 3, "Dismantle": 3, "Snatch": 3,
    "Bounty": 2, "Brotherhood": 2
}

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hp = 4
        self.max_hp = 4
        self.hand = []

    def is_alive(self):
        return self.hp > 0

    def show_status(self):
        if self.is_ai:
            return f"[{self.name}] HP: {self.hp}/{self.max_hp} | Hand: {len(self.hand)} cards"
        else:
            return f"[{self.name}] HP: {self.hp}/{self.max_hp} | Hand: {self.hand}"


class CardGame:
    def __init__(self):
        self.deck = self.init_deck()
        self.discard_pile = []
        self.player = Player("Player 1", is_ai=False)
        self.ai = Player("Computer (AI)", is_ai=True)
        self.round_count = 1

    def init_deck(self):
        deck = []
        for card, count in CARD_POOL.items():
            deck.extend([card] * count)
        random.shuffle(deck)
        return deck

    def draw_cards(self, character, num):
        for _ in range(num):
            if not self.deck:
                if not self.discard_pile:
                    break
                self.deck = self.discard_pile.copy()
                random.shuffle(self.deck)
                self.discard_pile.clear()
            
            if self.deck:
                card = self.deck.pop()
                character.hand.append(card)

    def print_board(self):
        print("\n" + "="*50)
        print(self.ai.show_status())
        print(self.player.show_status())
        print("="*50)

    def check_discard_phase(self, character):
        if len(character.hand) > character.hp:
            excess = len(character.hand) - character.hp
            print(f"\n--- Discard Phase for {character.name} ---")
            
            for _ in range(excess):
                if character.is_ai:
                    discarded = character.hand.pop(random.randint(0, len(character.hand) - 1))
                    self.discard_pile.append(discarded)
                else:
                    while True:
                        print(f"Your current hand: {character.hand}")
                        idx_input = input(f"Choose a card index to discard (1-{len(character.hand)}): ")
                        if idx_input.isdigit() and 1 <= int(idx_input) <= len(character.hand):
                            discarded = character.hand.pop(int(idx_input) - 1)
                            self.discard_pile.append(discarded)
                            break
            time.sleep(1)

    def play_card_logic(self, user, target, card_name):
        print(f"\n[ACTION] {user.name} plays: {card_name}")
        self.discard_pile.append(card_name)

        if card_name == "Slash":
            if "Dodge" in target.hand:
                target.hand.remove("Dodge")
                self.discard_pile.append("Dodge")
                print(f"-> {target.name} countered with Dodge!")
            else:
                target.hp -= 1
                print(f"-> {target.name} takes 1 Damage.")

        elif card_name == "Peach":
            user.hp = min(user.hp + 1, user.max_hp)
            print(f"-> {user.name} recovered 1 HP.")

        elif card_name == "Ex Nihilo":
            self.draw_cards(user, 2)

        elif card_name == "Dismantle":
            if target.hand:
                removed = target.hand.pop(random.randint(0, len(target.hand) - 1))
                self.discard_pile.append(removed)
                print(f"-> Dismantled 1 card from {target.name}'s hand.")

        elif card_name == "Snatch":
            if target.hand:
                stolen = target.hand.pop(random.randint(0, len(target.hand) - 1))
                user.hand.append(stolen)
                print(f"-> Snatched 1 card from {target.name}.")

        elif card_name == "Bounty":
            self.draw_cards(user, 1)
            self.draw_cards(target, 1)

        elif card_name == "Brotherhood":
            if user.hp < user.max_hp: user.hp += 1
            if target.hp < target.max_hp: target.hp += 1

    def start_game(self):
        print("Welcome to Three Kingdoms Kill!")
        self.draw_cards(self.player, 5)
        self.draw_cards(self.ai, 5)

        while self.player.is_alive() and self.ai.is_alive():
            print(f"\n>>>>>>> ROUND {self.round_count} <<<<<<<")
            
            print(f"\n--- [ {self.player.name}'s Turn ] ---")
            if self.round_count > 1:
                self.draw_cards(self.player, 2)
                
            has_slashed = False
            
            while True:
                self.print_board()
                print("Options:\n [0] End Turn")
                for idx, card in enumerate(self.player.hand):
                    print(f" [{idx + 1}] {card}")
                
                choice = input("Select a number to play: ")
                if choice == "0":
                    break
                
                if not choice.isdigit() or not (1 <= int(choice) <= len(self.player.hand)):
                    continue
                
                chosen_card = self.player.hand[int(choice) - 1]
                
                if chosen_card == "Dodge":
                    print("[INVALID] Cannot play Dodge on your turn.")
                    continue
                if chosen_card == "Slash" and has_slashed:
                    print("[INVALID] One Slash per turn.")
                    continue
                if chosen_card == "Peach" and self.player.hp == self.player.max_hp:
                    print("[INVALID] HP is full.")
                    continue

                self.player.hand.pop(int(choice) - 1)
                if chosen_card == "Slash":
                    has_slashed = True
                
                self.play_card_logic(self.player, self.ai, chosen_card)
                
                if not self.ai.is_alive():
                    break
                time.sleep(1)

            if not self.ai.is_alive(): break
            self.check_discard_phase(self.player)

            print(f"\n--- [ {self.ai.name}'s Turn ] ---")
            time.sleep(1)
            if self.round_count > 1:
                self.draw_cards(self.ai, 2)
            
            ai_has_slashed = False
            ai_acting = True
            
            while ai_acting and self.ai.is_alive():
                if "Peach" in self.ai.hand and self.ai.hp < self.ai.max_hp:
                    self.ai.hand.remove("Peach")
                    self.play_card_logic(self.ai, self.player, "Peach")
                elif "Ex Nihilo" in self.ai.hand:
                    self.ai.hand.remove("Ex Nihilo")
                    self.play_card_logic(self.ai, self.player, "Ex Nihilo")
                elif "Slash" in self.ai.hand and not ai_has_slashed:
                    self.ai.hand.remove("Slash")
                    ai_has_slashed = True
                    self.play_card_logic(self.ai, self.player, "Slash")
                elif "Dismantle" in self.ai.hand:
                    self.ai.hand.remove("Dismantle")
                    self.play_card_logic(self.ai, self.player, "Dismantle")
                elif "Snatch" in self.ai.hand:
                    self.ai.hand.remove("Snatch")
                    self.play_card_logic(self.ai, self.player, "Snatch")
                else:
                    ai_acting = False
                
                if not self.player.is_alive():
                    break
                time.sleep(1.5)

            if not self.player.is_alive(): break
            self.check_discard_phase(self.ai)

            self.round_count += 1

        print("\n=================== GAME OVER ===================")
        if self.player.is_alive():
            print("[SUCCESS] Victory!")
        else:
            print("[DEFEAT] Game Over.")

if __name__ == "__main__":
    game = CardGame()
    game.start_game()