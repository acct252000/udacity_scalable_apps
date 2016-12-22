'use strict';

/**
 * The root crazyeightsApp module.
 *
 * @type {crazyeightsApp|*|{}}
 */
var crazyeightsApp = crazyeightsApp || {};

/**
 * @ngdoc module
 * @name conferenceControllers
 *
 * @description
 * Angular module for controllers.
 *
 */
crazyeightsApp.controllers = angular.module('conferenceControllers', ['ui.bootstrap']);

/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
crazyeightsApp.controllers.controller('MyProfileCtrl',
    function($scope, $log, oauth2Provider, current_user_name, HTTP_ERRORS) {
        /**
        * Holds the status if the query is being executed.
        * @type {boolean}
        */
        $scope.submitted = false;
        $scope.loading = false;

        /**
         * The initial profile retrieved from the server to know the dirty state.
         * @type {{}}
         */
        $scope.initialProfile = {};

        /**
         * Initializes the My profile page.
         * Update the profile if the user's profile has been stored.
         */
        $scope.init = function() {
            var retrieveProfileCallback = function() {
                $scope.profile = {};
                $scope.loading = true;
                gapi.client.crazyeights.getProfile().
                execute(function(resp) {
                    $scope.$apply(function() {
                        $scope.loading = false;
                        if (resp.error) {
                            // Failed to get a user profile.
                        } else {
                            // Succeeded to get the user profile.
                            $scope.profile.user_name = resp.result.user_name;
                            $scope.profile.email = resp.result.email;
                            $scope.initialProfile = resp.result;
                        }
                    });
                });


            };
            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveProfileCallback);
            } else {
                retrieveProfileCallback();
            }
        };

        /**
         * Invokes the crazyeights.saveProfile API.
         *
         */
        $scope.saveProfile = function() {
            $scope.submitted = true;
            $scope.loading = true;
            gapi.client.crazyeights.saveProfile($scope.profile).
            execute(function(resp) {
                $scope.$apply(function() {
                    $scope.loading = false;
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to update a profile : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.messages = 'The profile has been updated';
                        $scope.alertStatus = 'success';
                        $scope.submitted = false;
                        $scope.initialProfile = {
                            user_name: $scope.profile.user_name,
                            email: $scope.profile.email
                        };

                        $log.info($scope.messages + JSON.stringify(resp.result));
                    }
                });
            });
        };
    });

/**
 * @ngdoc controller
 * @name GameseCtrl
 *
 * @description
 * A controller used for the Games page, listing user games and allowing for new game creation
 */

crazyeightsApp.controllers.controller('GamesCtrl',
    function($scope, $log, oauth2Provider, current_user_name, HTTP_ERRORS) {
        /**
        * Holds the status if the query is being executed.
        * @type {boolean}
        */
        $scope.submitted = false;
        $scope.loading = false;

        $scope.user_one_name = '';
        $scope.user_two_name = '';
        $scope.user_games = [];

        /**
         * Invokes the get_user_games API.  Outside
         * of init function so can be called after game creation.
         */

        $scope.retrieveGamesCallback = function() {

            $scope.loading = true;
            gapi.client.crazyeights.get_user_games({
                    user_name: 'Larry'
                })
                .execute(function(resp) {
                    $scope.$apply(function() {
                        $scope.loading = false;
                        if (resp.error) {
                            // The request has failed.
                            var errorMessage = resp.error.message || '';
                            $scope.messages = 'Failed to get the games : ' +
                                ' ' + errorMessage;
                            $scope.alertStatus = 'warning';
                            $log.error($scope.messages);
                        } else {
                            // The request has succeeded.
                            $scope.alertStatus = 'success';
                            $scope.user_games = [];
                            angular.forEach(resp.items, function(game) {
                                $scope.user_games.push(game);
                            });
                        }
                    });
                });
        };
        /**
         * Initializes the Games page.
         * Update the profile if the user's profile has been stored.
         */
        $scope.init = function() {

            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then($scope.retrieveGamesCallback);
            } else {
                $scope.retrieveGamesCallback();
            }
        };

        /**
         * Invokes the crazyeights.new_game API.
         *
         */
        $scope.newGame = function() {
            $scope.submitted = true;
            $scope.loading = true;
            gapi.client.crazyeights.new_game({
                'user_one_name': $scope.user_one_name,
                'user_two_name': $scope.user_two_name
            }).
            execute(function(resp) {
                $scope.$apply(function() {
                    $scope.loading = false;
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to update a profile : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.messages = resp.result.message;
                        $scope.alertStatus = 'success';
                        $scope.submitted = false;
                        $scope.user_one_name = '';
                        $scope.user_two_name = '';
                        $scope.retrieveGamesCallback();
                        $log.info($scope.messages + JSON.stringify(resp.result));
                    }
                });
            });
        };
    });


/**
 * @ngdoc controller
 * @name PlayGameCtrl
 *
 * @description
 * A controller used for the main gaim playing page.
 */
crazyeightsApp.controllers.controller('PlayGameCtrl', function($scope, $log, $routeParams, oauth2Provider, current_user_name, HTTP_ERRORS) {

    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
    $scope.loading = false;
    $scope.submitted = false;
    $scope.current_user = current_user_name.name;

    /**
     * Holds the game currently displayed in the page.
     */
    $scope.game = [];
    $scope.is_user_one = false;
    $scope.is_player_turn = false;
    $scope.player_one_hand = [];
    $scope.player_one_hand_cards = [];
    $scope.player_two_hand = [];
    $scope.player_two_hand_cards = [];
    $scope.discard_pile = [];
    $scope.discard_pile_top_card = [];
    $scope.eight_played = false;
    $scope.crazy_suit = "hearts";
    $scope.eight_suit = 'hearts';
    $scope.show_suit = false;
    $scope.game_over = false;
    $scope.other_card_count = 0;
    /**
     * Resets user hands after a play
     */

    $scope.resetHands = function() {

        $scope.game.length = 0;
        $scope.player_one_hand.length = 0;
        $scope.player_one_hand_cards.length = 0;
        $scope.player_two_hand.length = 0;
        $scope.player_two_hand_cards.length = 0;
        $scope.discard_pile.length = 0;
        $scope.discard_pile_top_card.length = 0;
    };

    /**
     * Determines which player's turn it is
     */


    $scope.checkUserTurn = function() {

        if ($scope.is_user_one && $scope.game.user_one_turn) {
            $scope.is_player_turn = true;
        } else if ($scope.is_user_one && !$scope.game.user_one_turn) {
            $scope.is_player_turn = false;
        } else if (!$scope.is_user_one && $scope.game.user_one_turn) {
            $scope.is_player_turn = false;
        } else if (!$scope.is_user_one && !$scope.game.user_one_turn) {
            $scope.is_player_turn = true;
        }

    };

    /**
     * Converts card information into image ref with card number and suit.
     */

    $scope.getCardFromString = function(card_string) {
        var card_and_suit = card_string.slice(1, -1);
        var suit = card_and_suit.slice(0, card_and_suit.indexOf(",")).toLowerCase();
        var card_number = card_and_suit.slice(card_and_suit.indexOf(",") + 1);
        var img_ref = card_number.concat("_", suit, ".png");
        var card_object = {
            img: img_ref,
            card_number: card_number,
            card_suit: suit
        };
        return card_object;

    };

    /**
     * Invokes the play_card crazy eights API
     */


    $scope.playCard = function(card_suit, card_number, crazy_suit) {
        $scope.loading = true;
        gapi.client.crazyeights.play_card({
            'card_number': card_number,
            'card_suit': card_suit,
            'crazy_suit': crazy_suit,
            urlsafe_game_key: $routeParams.urlsafe_key
        }).
        execute(function(resp) {
            $scope.$apply(function() {
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to obtain the game : ' + errorMessage;
                    $scope.alertStatus = 'warning';
                    $log.error($scope.messages);

                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.game = resp.result;
                    $scope.resetHands();
                    $scope.player_one_hand = resp.result.player_one_hand.split('*');
                    $scope.player_one_hand.forEach(function(card) {
                        $scope.player_one_hand_cards.push($scope.getCardFromString(card));
                    });
                    $scope.player_two_hand = resp.result.player_two_hand.split('*');
                    $scope.player_two_hand.forEach(function(card) {
                        $scope.player_two_hand_cards.push($scope.getCardFromString(card));
                    });
                    $scope.discard_pile = resp.result.discard_pile.split('*');
                    $scope.discard_pile_top_card = $scope.getCardFromString($scope.discard_pile[0]);
                    if ($scope.discard_pile_top_card.card_number == '8') {
                        $scope.show_suit = true;
                    } else {
                        $scope.show_suit = false;
                    }
                    $scope.game_over = resp.result.game_over;
                    $scope.checkUserTurn();
                    if ($scope.is_user_one)
                    {
                        $scope.other_card_count = $scope.player_two_hand.length;
                    } else {
                        $scope.other_card_count = $scope.player_one_hand.length;
                    }
                    $scope.loading = false;

                }
                $scope.submitted = true;
            });
        });

    };


    /**
     * Allows for form to capture crazy eight suit if eight is played
     */


    $scope.takeTurn = function(card_suit, card_number, crazy_suit) {
        if (card_number == '8') {
            $scope.eight_played = true;
            $scope.card_suit = card_suit;
            return;
        } else {
            $scope.playCard(card_suit, card_number, crazy_suit);
        }
    };

    
    /**
     * Allows for form submittal to play crazy eight suit if eight is played
     */


    $scope.playCrazyEight = function(crazy_suit) {
        $scope.playCard($scope.card_suit, '8', crazy_suit);
        $scope.eight_played = false;
    };

     /**
     * Invokes draw_card API from crazy eights API
     */


    $scope.drawCard = function() {
            $scope.loading = true;
            gapi.client.crazyeights.draw_card({
                'draw_card': true,
                urlsafe_game_key: $routeParams.urlsafe_key
            }).
            execute(function(resp) {
                $scope.$apply(function() {
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to obtain the game : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages);

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.game = resp.result;
                        $scope.resetHands();
                        $scope.player_one_hand = resp.result.player_one_hand.split('*');
                        $scope.player_one_hand.forEach(function(card) {
                            $scope.player_one_hand_cards.push($scope.getCardFromString(card));
                        });
                        $scope.player_two_hand = resp.result.player_two_hand.split('*');
                        $scope.player_two_hand.forEach(function(card) {
                            $scope.player_two_hand_cards.push($scope.getCardFromString(card));
                        });
                        $scope.discard_pile = resp.result.discard_pile.split('*');
                        $scope.discard_pile_top_card = $scope.getCardFromString($scope.discard_pile[0]);
                        $scope.checkUserTurn();
                        if ($scope.is_user_one)
                        {
                        $scope.other_card_count = $scope.player_two_hand.length;
                        } else {
                        $scope.other_card_count = $scope.player_one_hand.length;
                        }
                        $scope.loading = false;

                    }
                    $scope.submitted = true;
                });
            });

        };

        /**
         * Retrieves the game to attend by calling the crazyeights.get_game method
         */
    $scope.init = function() {
        var retrieveGameCallback = function() {
            $scope.loading = true;
            $scope.current_user = current_user_name.name;
            gapi.client.crazyeights.get_game({
                urlsafe_game_key: $routeParams.urlsafe_key
            }).
            execute(function(resp) {
                $scope.$apply(function() {
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to obtain the game : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages);

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.game = resp.result;
                        $scope.game_over = resp.result.game_over;
                        $scope.player_one_hand = resp.result.player_one_hand.split('*');
                        $scope.player_one_hand.forEach(function(card) {
                            $scope.player_one_hand_cards.push($scope.getCardFromString(card));
                        });
                        $scope.player_two_hand = resp.result.player_two_hand.split('*');
                        $scope.player_two_hand.forEach(function(card) {
                            $scope.player_two_hand_cards.push($scope.getCardFromString(card));
                        });
                        $scope.discard_pile = resp.result.discard_pile.split('*');
                        $scope.discard_pile_top_card = $scope.getCardFromString($scope.discard_pile[0]);
                        if (resp.result.user_one_name == current_user_name.name || resp.result.user_two_name == "Computer") {
                            $scope.is_user_one = true;
                        }
                        $scope.checkUserTurn();
                        if ($scope.is_user_one)
                        {
                        $scope.other_card_count = $scope.player_two_hand.length;
                        } else {
                        $scope.other_card_count = $scope.player_one_hand.length;
                        }
                        $scope.loading = false;

                    }
                    $scope.submitted = true;
                });
            });
        };
        if (!oauth2Provider.signedIn) {
            var modalInstance = oauth2Provider.showLoginModal();
            modalInstance.result.then(retrieveGameCallback);
        } else {
            retrieveGameCallback();
        }
    };
});

/**
 * @ngdoc controller
 * @name CancelGameCtrl
 *
 * @description
 * A controller used to cancel games
 */
crazyeightsApp.controllers.controller('CancelGameCtrl', function($scope, $log, $routeParams, oauth2Provider, current_user_name, HTTP_ERRORS) {

    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
    $scope.submitted = false;
    $scope.current_user = current_user_name.name;


    /**
     * Holds the game currently displayed in the page.
     * @type {Array}
     */
    $scope.game = [];

     /**
     * Invokes the cancel_game crazyeights API
     * @type {Array}
     */

    $scope.cancelGame = function() {
        $scope.submitted = true;
        $scope.loading = true;
        gapi.client.crazyeights.cancel_game({
            urlsafe_game_key: $routeParams.urlsafe_key
        }).
        execute(function(resp) {
            $scope.$apply(function() {
                $scope.loading = false;
                if (resp.error) {
                    // The request has failed.
                    var errorMessage = resp.error.message || '';
                    $scope.messages = 'Failed to cancel a game : ' + errorMessage;
                    $scope.alertStatus = 'warning';


                    if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                        oauth2Provider.showLoginModal();
                        return;
                    }
                } else {
                    // The request has succeeded.
                    $scope.messages = 'The game has been cancelled';
                    $scope.alertStatus = 'success';
                    $scope.submitted = false;


                    $log.info($scope.messages + JSON.stringify(resp.result));
                }
            });
        });
    };
    /**
     * Retrieves the game subject to cancellation by invoking the get_game crazy eights API
     */
    $scope.init = function() {
        var retrieveGameCancelCallback = function() {
            $scope.loading = true;
            $scope.current_user = current_user_name.name;
            gapi.client.crazyeights.get_game({
                urlsafe_game_key: $routeParams.urlsafe_key
            }).
            execute(function(resp) {
                $scope.$apply(function() {
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to obtain the game : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages);

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.game = resp.result;
                        $scope.user_one_name = resp.result.user_one_name;
                        $scope.user_two_name = resp.result.user_two_name;
                        $scope.date = resp.result.date;
                        $scope.loading = false;

                    }
                    $scope.submitted = true;
                });
            });
        };
        if (!oauth2Provider.signedIn) {
            var modalInstance = oauth2Provider.showLoginModal();
            modalInstance.result.then(retrieveGameCancelCallback);
        } else {
            retrieveGameCancelCallback();
        }
    };
});
/**
 * @ngdoc controller
 * @name GameHistoryCtrl
 *
 * @description
 * A controller used to display game history
 */


crazyeightsApp.controllers.controller('GameHistoryCtrl', function($scope, $log, $routeParams, oauth2Provider, current_user_name, HTTP_ERRORS) {

    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
    $scope.submitted = false;
    $scope.current_user = current_user_name.name;

    /**
     * Holds the game currently displayed in the page.
     * @type {Array}
     */
    $scope.game_history = [];
    $scope.game_moves = [];


    /**
     * converts API feedback into information for display in template
     */


    $scope.getMoveFromList = function(history_list) {
        var move_list = [];
        move_list.push(history_list[0]);
        move_list.push(history_list[1]);
        var img_ref = history_list[3].concat("_", history_list[2], ".png");
        move_list.push(img_ref);
        return move_list;

    };

    /**
     * invokes get_game_history method of crazyeights API
     */



    $scope.init = function() {
        var retrieveGameHistoryCallback = function() {
            $scope.loading = true;
            $scope.current_user = current_user_name.name;
            gapi.client.crazyeights.get_game_history({
                urlsafe_game_key: $routeParams.urlsafe_key
            }).
            execute(function(resp) {
                $scope.$apply(function() {
                    if (resp.error) {
                        // The request has failed.
                        var errorMessage = resp.error.message || '';
                        $scope.messages = 'Failed to obtain the game : ' + errorMessage;
                        $scope.alertStatus = 'warning';
                        $log.error($scope.messages);

                        if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                            oauth2Provider.showLoginModal();
                            return;
                        }
                    } else {
                        // The request has succeeded.
                        $scope.game_history = resp.result;
                        $scope.game_moves = [];
                        angular.forEach(resp.move, function(move) {

                            $scope.game_moves.push($scope.getMoveFromList(move.split(',')));

                        });

                        $scope.loading = false;

                    }
                    $scope.submitted = true;
                });
            });
        };
        if (!oauth2Provider.signedIn) {
            var modalInstance = oauth2Provider.showLoginModal();
            modalInstance.result.then(retrieveGameHistoryCallback);
        } else {
            retrieveGameHistoryCallback();
        }
    };
});

/**
 * @ngdoc controller
 * @name ScoreCtrl
 *
 * @description
 * A controller used to display scores and user rankings
 */


crazyeightsApp.controllers.controller('ScoreCtrl',
    function($scope, $log, oauth2Provider, HTTP_ERRORS) {

    /**
     * Holds the status if the query is being executed.
     * @type {boolean}
     */
        $scope.submitted = false;
        $scope.loading = false;

       
        $scope.scores = [];
        $scope.user_scores = [];
        $scope.rankings = [];


        /**
         * invokes the get_scores method of the crazy eights API
         */
        $scope.init = function() {
            var retrieveScoresCallback = function() {
                $scope.scores = [];
                $scope.user_scores = [];
                $scope.loading = true;
                gapi.client.crazyeights.get_scores().
                execute(function(resp) {
                    $scope.$apply(function() {
                        $scope.loading = false;
                        if (resp.error) {
                            // Failed to get a user profile.
                        } else {
                            // Succeeded to get the user profile.
                            $scope.scores = [];
                            angular.forEach(resp.items, function(score) {
                                $scope.scores.push(score);
                            });
                        }
                    });
                });
         /**
         * invokes the get_user_scores method of the crazy eights API
         */

                gapi.client.crazyeights.get_user_scores({
                        user_name: 'Larry'
                    })
                    .execute(function(resp) {
                        $scope.$apply(function() {
                            $scope.loading = false;
                            if (resp.error) {
                                // The request has failed.
                                var errorMessage = resp.error.message || '';
                                $scope.messages = 'Failed to get the games : ' +
                                    ' ' + errorMessage;
                                $scope.alertStatus = 'warning';
                                $log.error($scope.messages);
                            } else {
                                // The request has succeeded.
                                $scope.alertStatus = 'success';
                                $scope.user_scores = [];
                                angular.forEach(resp.items, function(score) {
                                    $scope.user_scores.push(score);
                                });
                            }
                        });
                    });

        /**
         * invokes the get_rankings method of the crazy eights API
         */

                gapi.client.crazyeights.get_all_rankings({
                        'get_rankings': true
                    })
                    .execute(function(resp) {
                        $scope.$apply(function() {
                            $scope.loading = false;
                            if (resp.error) {
                                // The request has failed.
                                var errorMessage = resp.error.message || '';
                                $scope.messages = 'Failed to get the games : ' +
                                    ' ' + errorMessage;
                                $scope.alertStatus = 'warning';
                                $log.error($scope.messages);
                            } else {
                                // The request has succeeded.
                                $scope.alertStatus = 'success';
                                $scope.rankings = [];
                                angular.forEach(resp.items, function(ranking) {
                                    $scope.rankings.push(ranking);
                                });

                            }
                        });
                    });
            };
            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveScoresCallback);
            } else {
                retrieveScoresCallback();
            }
        };

    });
/**
 * @ngdoc controller
 * @name RootCtrl
 *
 * @description
 * The root controller having a scope of the body element and methods used in the application wide
 * such as user authentications.
 *
 */
crazyeightsApp.controllers.controller('RootCtrl', function($scope, $location, oauth2Provider, current_user_name) {
    /**
     * Returns if the viewLocation is the currently viewed page.
     *
     * @param viewLocation
     * @returns {boolean} true if viewLocation is the currently viewed page. Returns false otherwise.
     */
    $scope.isActive = function(viewLocation) {
        return viewLocation === $location.path();
    };

    /**
     * Returns the OAuth2 signedIn state.
     *
     * @returns {oauth2Provider.signedIn|*} true if siendIn, false otherwise.
     */
    $scope.getSignedInState = function() {
        return oauth2Provider.signedIn;
    };

    /**
     * Calls the OAuth2 authentication method.
     */
    $scope.signIn = function() {
        oauth2Provider.signIn(function() {
            gapi.client.oauth2.userinfo.get().execute(function(resp) {
                $scope.$apply(function() {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        oauth2Provider.email = resp.email;
                        $scope.alertStatus = 'success';
                        $scope.rootMessages = 'Logged in with ' + resp.email;
                    }
                });
                current_user_name.update();
            });
        });
    };

    /**
     * Render the signInButton and restore the credential if it's stored in the cookie.
     * (Just calling this to restore the credential from the stored cookie. So hiding the signInButton immediately
     *  after the rendering)
     */
    $scope.initSignInButton = function() {
        gapi.signin.render('signInButton', {
            'callback': function() {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function() {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });
    };

    /**
     * Logs out the user.
     */
    $scope.signOut = function() {
        oauth2Provider.signOut();
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
    };

    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function() {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };

});


/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */
crazyeightsApp.controllers.controller('OAuth2LoginModalCtrl',
    function($scope, $modalInstance, $rootScope, oauth2Provider, current_user_name) {
        $scope.singInViaModal = function() {
            oauth2Provider.signIn(function() {
                gapi.client.oauth2.userinfo.get().execute(function(resp) {
                    $scope.$root.$apply(function() {
                        oauth2Provider.signedIn = true;
                        $scope.$root.alertStatus = 'success';
                        $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                    });

                    $modalInstance.close();
                    current_user_name.update();
                });
            });
        };
    });

