'use strict';

/**
 * @ngdoc object
 * @name crazyeightsApp
 * @requires $routeProvider
 * @requires conferenceControllers
 * @requires ui.bootstrap
 *
 * @description
 * Root app, which routes and specifies the partial html and controller depending on the url requested.
 *
 */
var app = angular.module('crazyeightsApp', ['conferenceControllers', 'ngRoute', 'ui.bootstrap']).
config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
        when('/game/history/:urlsafe_key', {
            templateUrl: '/partials/game_history.html',
            controller: 'GameHistoryCtrl'
        }).
        when('/game/cancel/:urlsafe_key', {
            templateUrl: '/partials/game_cancel.html',
            controller: 'CancelGameCtrl'
        }).
        when('/game/:urlsafe_key', {
            templateUrl: '/partials/game.html',
            controller: 'PlayGameCtrl'
        }).
        when('/scores', {
            templateUrl: '/partials/scores.html',
            controller: 'ScoreCtrl'
        }).
        when('/games', {
            templateUrl: '/partials/games.html',
            controller: 'GamesCtrl'
        }).
        when('/profile', {
            templateUrl: '/partials/profile.html',
            controller: 'MyProfileCtrl'
        }).
        when('/', {
            templateUrl: '/partials/home.html'
        }).
        otherwise({
            redirectTo: '/'
        });
    }
]);

/**
 * @ngdoc filter
 * @name startFrom
 *
 * @description
 * A filter that extracts an array from the specific index.
 *
 */
app.filter('startFrom', function() {
    /**
     * Extracts an array from the specific index.
     *
     * @param {Array} data
     * @param {Integer} start
     * @returns {Array|*}
     */
    var filter = function(data, start) {
        return data.slice(start);
    };
    return filter;
});


/**
 * @ngdoc constant
 * @name HTTP_ERRORS
 *
 * @description
 * Holds the constants that represent HTTP error codes.
 *
 */
app.constant('HTTP_ERRORS', {
    'UNAUTHORIZED': 401
});
/**
 * @ngdoc service
 * @name current_user_name
 *
 * @description
 * Service that holds the current user name information shared across all the pages.
 *
 */

app.factory('current_user_name', function($modal) {
    var current_user_name = {
        name: ''
    };


    current_user_name.update = function() {
        gapi.client.crazyeights.getProfile().
        execute(function(resp) {
            if (resp.error) {
                // Failed to get a user profile.
            } else {
                // Succeeded to get the user profile.
                current_user_name.name = resp.result.user_name;
            }
        });
    };


    return current_user_name;
});
/**
 * @ngdoc service
 * @name oauth2Provider
 *
 * @description
 * Service that holds the OAuth2 information shared across all the pages.
 *
 */
app.factory('oauth2Provider', function($modal) {
    var oauth2Provider = {
        CLIENT_ID: '91242573256-uv9bn5fgnu3fegagbehuji4br5ut5ckf.apps.googleusercontent.com',
        SCOPES: 'email profile',
        signedIn: false,
        email: 'test@test.com'
    };

    /**
     * Calls the OAuth2 authentication method.
     */
    oauth2Provider.signIn = function(callback) {
        gapi.auth.signIn({
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'accesstype': 'online',
            'approveprompt': 'auto',
            'scope': oauth2Provider.SCOPES,
            'callback': callback
        });
    };

    /**
     * Logs out the user.
     */
    oauth2Provider.signOut = function() {
        gapi.auth.signOut();
        // Explicitly set the invalid access token in order to make the API calls fail.
        gapi.auth.setToken({
            access_token: ''
        });
        oauth2Provider.signedIn = false;
    };

    /**
     * Shows the modal with Google+ sign in button.
     *
     * @returns {*|Window}
     */
    oauth2Provider.showLoginModal = function() {
        var modalInstance = $modal.open({
            templateUrl: '/partials/login.modal.html',
            controller: 'OAuth2LoginModalCtrl'
        });
        return modalInstance;
    };

    return oauth2Provider;
});