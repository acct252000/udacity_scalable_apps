"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


CARD_NUMBER_VALUES = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
CARD_SUITS = ['Hearts', 'Diamonds','Clubs','Spades']

DECKOFCARDS = []

for suit in CARD_SUITS:
    for value in CARD_NUMBER_VALUES:
        card = (suit, value)
        DECKOFCARDS.append(card)


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

   




class Game(ndb.Model):
    """Game object"""
    player_one_hand = ndb.TextProperty(required=True)
    player_two_hand = ndb.TextProperty(required=True)
    discard_pile = ndb.TextProperty(required=True)
    undrawn_cards = ndb.TextProperty(required=True)
    current_suit = ndb.StringProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user_one = ndb.KeyProperty(required=True, kind='User')
    user_two = ndb.KeyProperty(required=True, kind='User')
    user_one_turn = ndb.BooleanProperty(required=True)
    cancelled = ndb.BooleanProperty(required=True)
    move = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user_one, user_two):
        cards = range(0,52)
        cards = map(str,cards)
        random.shuffle(cards)
        game = Game(user_one=user_one,
                    user_two=user_two,
                    player_one_hand = ','.join(cards[0:7]),
                    player_two_hand = ','.join(cards[7:14]),
	                discard_pile = cards[14],
                    current_suit = DECKOFCARDS[int(cards[14])][0],
                    undrawn_cards = ','.join(cards[15:]),
                    user_one_turn = bool(random.getrandbits(1)),
                    cancelled = False,
                    game_over = False)
        game.put()
        return game

    def to_card_type(cls, card_string):
        # split string into integer list
        card_list = card_string.split(',')
        card_list = map(int,card_list)
        # add text cards to list
        card_values = []
        for card_number in card_list:
            card = DECKOFCARDS[card_number]
            card_string = '(' + card[0] + ',' + card[1] + ')'
            card_values.append(card_string)
            card_values_string = ','.join(card_values)
        return card_values_string

    def card_in_hand(self, card_number, card_suit):
        card_in_question = (card_suit,card_number)
        card_in_question_number = str(DECKOFCARDS.index(card_in_question))
        if self.user_one_turn:
            cards_held_list = self.player_one_hand.split(',')
        else:
            cards_held_list = self.player_two_hand.split(',')
        if card_in_question_number in cards_held_list:
            return True
        else:
            return False

    def discard_card(self,user_one_turn, play_card_number, play_card_suit):
        #update discard pile
        discarded_card = (play_card_suit,play_card_number)
        discarded_card_number = DECKOFCARDS.index(discarded_card)
        #add card to discarded pile
        discarded_pile_list = self.discard_pile.split(',')
        discarded_pile_list.insert(0,str(discarded_card_number))
        self.discard_pile = ','.join(discarded_pile_list)
        
        #update player hand and game history
        if user_one_turn:
            player_hand_list = self.player_one_hand.split(',')
            player_hand_list.remove(str(discarded_card_number))
            self.player_one_hand = ','.join(player_hand_list)
            self.user_one_turn = False
            user_name = self.user_one.get().name
        else:
            player_hand_list = self.player_two_hand.split(',')
            player_hand_list.remove(str(discarded_card_number))
            self.player_two_hand = ','.join(player_hand_list)
            self.user_one_turn = True
            user_name = self.user_two.get().name
        game_move = [user_name, 'play', play_card_suit, play_card_number]
        self.move.append(','.join(game_move))
        self.put()

    def draw_card(self,user_one_turn):

        # return string number of top undrawn card
        undrawn_card_list = self.undrawn_cards.split(',')
        # set reshuffle to true if drawing last card
        reshuffle = False
        if len(undrawn_card_list) == 1:
            reshuffle = True
        drawn_card = undrawn_card_list.pop(0)
        if user_one_turn == True:
            player_hand_list = self.player_one_hand.split(',')
            player_hand_list.append(drawn_card)
            self.player_one_hand = ','.join(player_hand_list)
            user_name = self.user_one.get().name
        else:
            player_hand_list = self.player_two_hand.split(',')
            player_hand_list.append(drawn_card)
            self.player_two_hand = ','.join(player_hand_list)
            user_name = self.user_two.get().name
        if reshuffle == True:
            discard_pile_list = self.discard_pile.split(',')
            last_discard_card = discarded_pile_list.pop(0)
            random.shuffle(discarded_pile_list)
            self.undrawn_cards = ','.join(discarded_pile_list)
            self.discard_pile = last_discard_card
        else:
            self.undrawn_cards = ','.join(undrawn_card_list)
        game_move = [user_name, 'draw', DECKOFCARDS[int(drawn_card)][0],DECKOFCARDS[int(drawn_card)][1]]
        self.move.append(','.join(game_move))
        self.put()

    def to_form(self, form_message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_one_name = self.user_one.get().name
        form.user_two_name = self.user_two.get().name
        form.player_one_hand = self.to_card_type(self.player_one_hand)
        form.player_two_hand = self.to_card_type(self.player_two_hand)
        form.discard_pile = self.to_card_type(self.discard_pile)
        form.current_suit = self.current_suit
        form.undrawn_cards = self.to_card_type(self.undrawn_cards)
        form.user_one_turn = self.user_one_turn
        form.game_over = self.game_over
        form.cancelled = self.cancelled
        form.message = form_message
        return form

    def to_history_form(self):
        form = GameHistoryForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_one_name = self.user_one.get().name
        form.user_two_name = self.user_two.get().name
        form.move = self.move
        return form


    def cancel_game(self):
        self.cancelled = True
        self.game_over = True
        self.put()

    def end_game(self, user_one_turn):
        self.game_over = True
        self.put()
        if user_one_turn:
            score = Score(winning_user=self.user_one, losing_user = self.user_two, date=date.today())
        else:
            score = Score(winning_user=self.user_two, losing_user = self.user_one, date=date.today())    
        # Add the game to the score 'board'
        score.put()

    
       


class Score(ndb.Model):
    """Score object"""
    winning_user = ndb.KeyProperty(required=True, kind='User')
    losing_user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)

    
    def to_form(self):
        return ScoreForm(winning_user_name=self.winning_user.get().name, losing_user_name=self.losing_user.get().name,
                         date=str(self.date))


class TestForm(messages.Message):
    user_one_name = messages.StringField(1,required=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_one_name = messages.StringField(2, required=True)
    user_two_name = messages.StringField(3, required=True)
    player_one_hand = messages.StringField(4, required=True)
    player_two_hand = messages.StringField(5, required=True)   
    discard_pile = messages.StringField(6, required=True)
    current_suit = messages.StringField(7,required=True)
    undrawn_cards = messages.StringField(8, required=True)
    user_one_turn = messages.BooleanField(9, required=True)
    game_over = messages.BooleanField(10, required=True)
    cancelled = messages.BooleanField(11, required=True)
    message = messages.StringField(12)
    

class GameHistoryForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    user_one_name = messages.StringField(2, required=True)
    user_two_name = messages.StringField(3, required = True)
    move = messages.StringField(4, repeated=True)
 
class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_one_name = messages.StringField(1, required=True)
    user_two_name = messages.StringField(2, required=True)

class PlayCardForm(messages.Message):
    """Used to make a move in an existing game"""
    card_number = messages.StringField(1, required=True)
    card_suit = messages.StringField(2, required=True)
    crazy_suit = messages.StringField(3)

class DrawCardForm(messages.Message):
    """Used to make a move in an existing game"""
    draw_card = messages.BooleanField(1, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    winning_user_name = messages.StringField(1, required=True)
    losing_user_name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)

class UserRankingForm(messages.Message):
     user_name = messages.StringField(1, required=True)
     wins = messages.IntegerField(2, required=True)
     losses = messages.IntegerField(3, required=True)
     games = messages.IntegerField(4, required=True)
     winning_percentage = messages.FloatField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class UserRankingForms(messages.Message):
    items = messages.MessageField(UserRankingForm, 1, repeated=True)

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)