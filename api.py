# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import DECKOFCARDS
from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, PlayCardForm,\
    DrawCardForm, ScoreForms, ScoreForm, GameForms, UserRankingForm, UserRankingForms, TestForm, GameHistoryForm
from utils import get_by_urlsafe
from google.appengine.ext import ndb

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
PLAY_CARD_REQUEST = endpoints.ResourceContainer(
    PlayCardForm,
    urlsafe_game_key=messages.StringField(1),)
DRAW_CARD_REQUEST = endpoints.ResourceContainer(
    DrawCardForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1))
TEST_REQUEST = endpoints.ResourceContainer(get_rankings=messages.BooleanField(1))
GET_RANKINGS_REQUEST = endpoints.ResourceContainer(get_rankings=messages.BooleanField(1))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

def ranking_to_form(self):
    uf = UserRankingForm()
    uf.user_name = self[0]
    uf.wins = self[1]
    uf.losses = self[2]
    uf.games = self[3]
    uf.winning_percentage = self[4]
    return uf

@endpoints.api(name='crazyeights', version='v1')
class CrazyEightsApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user_one = User.query(User.name == request.user_one_name).get()
        if not user_one:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist for user one!')
        user_two = User.query(User.name == request.user_two_name).get()
        if not user_two:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist for user two!')
        try:
            game = Game.new_game(user_one.key, user_two.key)
        except ValueError:
           raise endpoints.InternalServerErrorException(
                    'Game was not created!')

        return game.to_form("New game created!")



    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.user_one_turn:
                game_message = 'Time for ' + game.user_one.get().name+ ' to make a move!'
            else:
                game_message = 'Time for ' + game.user_two.get().name+ ' to make a move!'
            return game.to_form(game_message)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=PLAY_CARD_REQUEST,
                      response_message=GameForm,
                      path='game/play/{urlsafe_game_key}',
                      name='play_card',
                      http_method='PUT')
    def play_card(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        valid_card = False
        if game.game_over == True:
            return game.to_form('Game already over!')
        #Check if card played is in player's hand
        if game.card_in_hand(request.card_number, request.card_suit) == False:
            return game.to_form('That card is not in your hand!')

        
        # determine number of top card in discard pile
        top_card_number = DECKOFCARDS[int(game.discard_pile.split(',')[0])][1]
        # check if played card crazy eight
        if request.card_number == '8':
            if request.crazy_suit:
                game.current_suit = request.crazy_suit
            else:
                game.current_suit = request.card_suit
            valid_card = True
        # check if top card crazy eight
        elif top_card_number == '8':
            if game.current_suit == request.card_suit:
                valid_card = True
        elif top_card_number == request.card_number or game.current_suit == request.card_suit:
            game.current_suit = request.card_suit
            valid_card = True
        else:
            valid_card = False

        if valid_card == True:
        #End game if last card played
            if game.user_one_turn == True:
                if len(game.player_one_hand.split(',')) == 1:
                    game.discard_card(game.user_one_turn, request.card_number, request.card_suit)
                    game.end_game(game.user_one_turn)
                    return game.to_form('Game over! ' + game.user_one.get().name + ' wins!')
            else:
                if len(game.player_two_hand.split(',')) == 1:
                    game.discard_card(game.user_one_turn, request.card_number, request.card_suit)
                    game.end_game(game.user_one_turn)
                    return game.to_form('Game over! ' + game.user_two.get().name + ' wins!')
            game.discard_card(game.user_one_turn, request.card_number, request.card_suit)
            return game.to_form('Card played!')
        else:
              return game.to_form('Card not valid!')
        return game.to_form('This should not be returned')
   
    @endpoints.method(request_message=DRAW_CARD_REQUEST,
                      response_message=GameForm,
                      path='game/draw/{urlsafe_game_key}',
                      name='draw_card',
                      http_method='PUT')
    def draw_card(self, request):
        """Allows the player to draw a card"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        game.draw_card(game.user_one_turn)
        return game.to_form('Card drawn!')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.winning_user == user.key,Score.losing_user==user.key))
        return ScoreForms(items=[score.to_form() for score in scores])
  
    @endpoints.method(request_message=GET_USER_GAMES_REQUEST,
                    response_message=GameForms,
                    path='game/usergames/{user_name}',
                    name='get_user_games',
                    http_method='GET')
    def get_user_games(self, request):
         """Returns all of a user's active games"""
         user = User.query(User.name == request.user_name).get()
         if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
         user_games = Game.query(ndb.AND(ndb.OR(Game.user_one == user.key,Game.user_two==user.key),Game.game_over == False))
         return GameForms(items=[game.to_form("") for game in user_games])
  
    @endpoints.method(request_message=GET_RANKINGS_REQUEST,
                      response_message = UserRankingForms,
                      path='rankings',
                      name = 'get_all_rankings',
                      http_method = 'GET'
                      )
    def get_all_rankings(self, request):
        scores = Score.query()
        users = User.query()

        user_keys = []
        for score in scores:
            if score.winning_user not in user_keys:
                user_keys.append(score.winning_user)
            if score.losing_user not in user_keys:
                user_keys.append(score.losing_user)

        user_results = []
        for user in user_keys:
            wins = 0
            losses = 0
            current_user_name = ''
            for ind_user in users:
                if user == ind_user.key:
                    current_user_name = ind_user.name
            for score in scores:
                if score.winning_user == user:
                    wins = wins + 1
                if score.losing_user == user:
                   losses = losses +1
            games = wins + losses
            winning_percentage = float(wins)/float(games)
            user_result = (current_user_name,wins,losses, games, winning_percentage)
            user_results.append(user_result)
            user_results.sort(key = lambda x: x[4], reverse = True)

        return UserRankingForms(items=[ranking_to_form(result) for result in user_results])
     

    @endpoints.method(request_message=GET_GAME_HISTORY_REQUEST,
                       response_message=GameHistoryForm,
                       path='game/history/{urlsafe_game_key}',
                       name='get_game_history',
                       http_method='GET')
    def get_game_history(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_history_form()
        else:
            raise endpoints.NotFoundException('Game not found!')     

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                     response_message=GameForm,
                     path='game/cancel/{urlsafe_game_key}',
                     name='cancel_game',
                     http_method='PUT')
    def cancel_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over == True:
            return game.to_form('Game already over and cannot be cancelled!')
        game.cancel_game()
        return game.to_form('Game is cancelled!  Scores are not recorded.')



   
        

           



api = endpoints.api_server([CrazyEightsApi])