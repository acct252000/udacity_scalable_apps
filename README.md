###Crazy Eights Google App Engine Endpoint Game

##Set-Up Instructions:

APIs can be accessed at (https://udacity-scalable-game.appspot.com/_ah/api/explorer)[https://udacity-scalable-game.appspot.com/_ah/api/explorer]

##Game Description:

Crazy Eights is a card game.  This implementation is for two players, or one player vs. the computer.  In order to create a game played vs. the computer, enter "Computer" as
the user two name when creating a new game.

Each player is dealt seven cards, and one card is discarded.  Player one has the first turn, and must discard a card that matches either the top discarded card's suit or number.
Eights are "crazy", and can be played at any time to change the suit to the desired suit of the player playing the card.  If the player does not have a match, he must
draw cards until a card can be played.  If the deck runs out, the discarded cards are reshuffled and cards are continued to be drawn until a card can be played.

The first player to discard all his cards wins.

##Web interface:

This implementation is for two players using google+ sign-in, or one player using google+ sign-in versus the computer.  Create a new game on the Games page, access existing games, game histories, and cancel games on the Games
page.  View user scores on the Scores page and update profile information on the Profile page.

Known issue - Google App Engine is extremely slow; 

##Files Included:
api.py: Contains endpoints and game playing logic.
app.yaml: App configuration.
cron.yaml: Cronjob configuration.
main.py: Handler for taskqueue handler.
models.py: Entity and message definitions including helper methods.
utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
static and template files for web interface

note settings.py not included as holds sensitive information

##Endpoints Included:

- **create_user** 
- Path: 'user'
- Method: POST
- Parameters: user_name, email
- Returns: Message confirming creation of the User.
- Description: Creates a new User. user_name and email provided must be unique. Will raise a ConflictException if a User with that user_name or email already exists.

- **getProfile**
- Path: 'profile'
- Method: GET
- Parameters: none
- Returns: UserForm of current user
- Description: Returns user information from google+ sign-in.   Will raise an Authorization Exception if not signed in, and add signed in user if signed in and not in datastore

- **saveProfile**
- Path: 'user'
- Method: POST
- Parameters: user_name, email
- Returns: UserForm of current user
- Description: Allows current signed in user to change their user name. Returns UserForm of current user.

- **new_game**
- Path: 'games'
- Method: POST
- Parameters: NewGameForm
- Returns: GameForm with initial game state.
- Description: Creates a new Game. user_names provided must correspond to an existing user - will raise a NotFoundException if not. 

- **get_game**
- Path: 'game/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: GameForm with current game state.
- Description: Returns the current state of a game.

- **play_card**
- Path: 'game/play/{urlsafe_game_key}'
- Method: PUT
- Parameters: PlayCardForm, urlsafe_game_key
- Returns: GameForm with current game state.
- Description: Plays a card in the game.  When playing versus the computer, also plays the computer's card.  Does not play card and returns messages if card played is not in a player's hand, is not playable, or if the game is already over.
When the last card is played, ends game and reports winner.

- **draw_card**
- Path: 'game/draw/{urlsafe_game_key}'
- Method: PUT
- Parameters: DrawCardForm, urlsafe_game_key
- Returns: GameForm with new game state.
- Description: Allows player to draw a card.  Reshufflse discard pile when undrawn cards are empty.

- **get_scores**
- Path: 'scores'
- Method: GET
- Parameters: None
- Returns: ScoreForms.
- Description: Returns all Scores in the database (unordered).

- **get_user_scores**
- Path: 'scores/user/{user_name}'
- Method: GET
- Parameters: user_name and email
- Returns: ScoreForms.
- Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.

- **get_user_games**
- Path: 'profile/user_games'
- Method: GET
- Parameters: user_name
- Returns: GameForms
- Description: Returns all of a user's active games.

- **get_all_rankings**
- Path: 'rankings'
- Method: GET
- Parameters: None
- Returns: UserRankingForms
- Description: Returns user rankings sorted by winning percentage

- **get_game_history**
- Path: 'game/history/{urlsafe_game_key}'
- Method: GET
- Parameters: urlsafe_game_key
- Returns: GameHistoryForm
- Description: Returns history of plays in the game.

- **cancel_game**
- Path: 'game/cancel/{urlsafe_game_key}'
- Method: PUT
- Parameters: urlsafe_game_key
- Returns: GameForm
- Description: Cancels game without assigning winner.


##Models Included:

- **User**
- Stores unique user_name and email address.

- **Game**
-Stores unique game states. Associated with User model via KeyProperty.
- Attributes:
  -      player_one_hand: text property holding comma sepearated 
                          cardnumbers (0-51) of hand
   -     player_two_hand: text property holding comma separated
                          cardnumbers (0-51) of hand
    -    discard_pile: text property holding comma separated
                      cardnumbers(0-51) of discarded cards
     -   undrawn_cards: text property holding comma separated
                       cardnumbers(0-51) of discarded cards
    -    current_suit: text property holding lower case current suit of game
     -   game_over: boolean property indicating if game is over
    -    user_one: key property referencing User class
    -    user_two: key property referencing User class
    -    user_one_turn: boolean property indicating if user one turn
    -    cancelled: boolean property indicating if game is cancelled
    -    move: repeated field holding string tracking game history in format
              user, action, card suit, card number
     -   date: date property holding date created
      -  computer_card: string property used for computer games, the string
                       number of the card selected by the computer to play
      -  computer_crazy_suit: string property used for computer games, the 
                             suit the computer has selected when playing an 8
       - game_message: string message used for messages from computer play

- **Score**
- Records winning user, losing user, and date. Associated with Users model via KeyProperty.

##Forms Included:

- **UserForm**
- Holds user_name and email.

- **GameForm**
-Representation of a Game's state.  Includes fields from Game model, except for move field which tracks history, computer_card, computer_crazy_suit, and game_message fields used to play vs computer, along with a text message field for game messages.
User one and user two fields in Game model are representd by user_one_name and user_two_name in form.  Also holds urlsafe_key.

- **GameForms**
- Multiple GameForm container

- **GameHistoryForm**
-Representation of a Game's history.  Holds game's urlsafe_key, user_one_name, user_two_name, date, and move fields.

- **NewGameForm**
- Used to create a new game (user_one_name, user_two_name)

- **PlayCardForm**
- Form holding card_number, card_suit, and crazy_suit(if eight played) to play a card.

- **ScoreForm**
- Representation of a completed game's score, defined as winner_user_name, losing_user_name, and date.

- **ScoreForms**
Multiple ScoreForm container.

- **UserRankingForm**
- Representation of current user rankings by user_name, wins, losses, games, winning_- percentage

- **UserRankingForms**
- Multiple UserRankingForm container

- **StringMessage**
- General purpose String container.