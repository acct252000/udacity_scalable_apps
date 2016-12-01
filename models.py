"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


CARD_VALUES = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
CARD_SUITS = ['Hearts', 'Diamonds','Clubs','Spades']

DECKOFCARDS = []

for suit in CARD_SUITS:
    for value in CARD_VALUES:
        card = (suit, value)
        DECKOFCARDS.append(card)


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    player_one_hand = ndb.StringProperty(required=True)
    player_two_hand = ndb.StringProperty(required=True)
    discard_pile = ndb.StringProperty(required=True)
    undrawn_cards = ndb.StringProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user_one = ndb.KeyProperty(required=True, kind='User')
    user_two = ndb.KeyProperty(required=True, kind='User')
    user_one_turn = ndb.BooleanProperty(required=True)
    versus_computer = ndb.BooleanProperty(required=True)

    @classmethod
    def new_game(cls, versus_computer, user_one, user_two):
        """Creates and returns a new game"""
	cards = range(0,52)
    cards = map(str,cards)
	random.shuffle(cards)
        game = Game(user_one=user_one,
                    user_two=user_two,
                    player_one_hand = ','.join(cards[0:7]),
                    player_two_hand = ','.join(cards[7:14]),
	                discard_pile = cards[14],
                    undrawn_cards = ','.join(cards[15:]),
                    user_one_turn = bool(random.getrandbits(1)),
                    versus_computer = versus_computer,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_one_name = self.user_one.get().name
        form.user_two_name = self.user_two.get().name
        form.player_one_hand = self.player_one_hand
	    form.player_two_hand = self.player_two_hand
        form.discard_pile = self.discard_pile
        form.undrawn_cards = self.undrawn_cards
        form.user_one_turn = self.user_one_turn
        form.versus_computer = self.versus_computer
        form.game_over = self.game_over
        form.message = message
        return form

    def end_game(self, won=False, winning_user):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
	if self.user_one.get().name == winning_user:
            score = Score(winning_user=self.user_one, losing_user = self.user_two, date=date.today())
        else:
            score = Score(winning_user=self.user_two, losing_user = self.user_one, date=date.today())    
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score.put()


class Score(ndb.Model):
    """Score object"""
    winning_user = ndb.KeyProperty(required=True, kind='User')
    losing_user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    
    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_one_name = messages.StringField(2, required=True)
    user_two_name = messages.StringField(3, required=True)
    player_one_hand = messages.StringField(4, required=True)
    player_two_hand = messages.StringField(5, required=True)   
    discard_pile = messages.StringField(6, required=True)
    undrawn_cards = messages.StringField(7, required=True)
    user_one_turn = messages.BooleanField(8, required=True)
    versus_computer = messages.BooleanField(9, required=True)
    game_over = messages.BooleanField(10, required=True)
 
class NewGameForm(messages.Message):
    """Used to create a new game"""
    versus_computer = messages.BooleanField(1, required=True)
    user_one_name = messages.StringField(2, required=True)
    user_two_name = messages.StringField(3)

class PlayCardForm(messages.Message):
    """Used to make a move in an existing game"""
    play_card = messages.BooleanField(1, required=True)
    card_number = messages.IntegerField(2, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    opponent = messages.BooleanField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)