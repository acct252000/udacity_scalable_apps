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
    ScoreForms, ScoreForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
PLAY_CARD_REQUEST = endpoints.ResourceContainer(
    PlayCardForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

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
        if request.versus_computer:
            user_two = User.query(User.name == 'computer').get()
        else:
            user_two = User.query(User.name == request.user_two_name).get()
        if not user_two:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist for user two!')
        try:
            game = Game.new_game(user_one.key, user_two.key)
        return game.to_form('Good luck playing CrazyEights!')

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
                game_message = 'Time for' + game.user_one.get().name+ ' to make a move!'
            else:
                game_message = 'Time for' + game.user_two.get().name+ ' to make a move!'
            return game.to_form(game_message)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=PLAY_CARD_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def play_card(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        valid_card = False
        if game.game_over:
            return game.to_form('Game already over!')
        # determine number of top card in discard pile
        top_card_number = DECKOFCARDS[int(game.discard_pile.split(',')[0])][1]
        # check if played card crazy eight
        if request.card_number == 8:
            if request.crazy_suit:
                game.current_suit = request.crazy_suit
            else:
                game.current_suit = request.card_suit
            valid_card = True
        # check if top card crazy eight
        elif top_card_number == 8:
            if game.current_suit == request.card_suit:
                valid_card = True
        elif top_card_number == request.card_number or game.current_suit == request.card_suit
            game.current_suit = request.current_suit
            valid_card = True
        if valid_card:
              game.discard_card(game.user_one_turn, request.card_number, request.card_suit)

            
        #to insert in top of list
        #list.insert(0,string)

        if game.attempts_remaining < 1:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
            game.put()
            return game.to_form(msg)

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
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([GuessANumberApi])