#!/usr/bin/env python

"""main.py - This file contains handlers that are called by cronjobs."""
import logging
import webapp2
from google.appengine.api import mail, app_identity
from api import CrazyEightsApi
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        games = Game.query(Game.game_over == false)
        users = User.query()

        user_keys = []
        for game in games:
            if game.user_one not in user_keys:
                user_keys.append(game.user_one)
            if game.user_two not in user_keys:
                user_keys.append(game.user_two)

        for user in users:
            if user.key in user_keys:
                subject = 'This is a reminder!'
                body = ('Hello {}, you still have an'
                        ' active Crazy Eights Game!').format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail)
], debug=False)
