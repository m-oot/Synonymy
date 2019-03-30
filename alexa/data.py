# -*- coding: utf-8 -*-

SKILL_TITLE = "Synonymy"

WELCOME_MESSAGE = ("Welcome to synonymy, a game where I will tell you a "
                    "word and you try to tell me a synonym of that word. Say start a quiz if you are ready.")

START_QUIZ_MESSAGE = "OK, Let's begin."

EXIT_SKILL_MESSAGE = ("Thank you for playing synonymy. "
                      "Let's play again soon!")

HELP_MESSAGE = "I know lots of words and that's all i'm good for. Dont ask me for anything else but a quiz."

CORRECT_SPEECHCONS = ['Booya', 'All righty', 'Bam', 'Bazinga', 'Bingo',
                      'Boom', 'Bravo', 'Cha Ching', 'Cheers', 'Dynomite',
                      'Hip hip hooray', 'Hurrah', 'Hurray', 'Huzzah',
                      'Oh dear.  Just kidding.  Hurray', 'Kaboom', 'Kaching',
                      'Oh snap', 'Phew', 'Righto', 'Way to go', 'Well done',
                      'Whee', 'Woo hoo', 'Yay', 'Wowza', 'Yowsa']

WRONG_SPEECHCONS = ['Argh', 'Aw man', 'Blarg', 'Blast', 'Boo', 'Bummer',
                    'Darn', "D'oh", 'Dun dun dun', 'Eek', 'Honk', 'Le sigh',
                    'Mamma mia', 'Oh boy', 'Oh dear', 'Oof', 'Ouch', 'Ruh roh',
                    'Shucks', 'Uh oh', 'Wah wah', 'Whoops a daisy', 'Yikes']

USE_CARDS_FLAG = True

MAX_QUESTIONS = 10

BAD_ANSWER = (
    "I'm sorry. {} is not something I know very much about in this skill.")

FALLBACK_ANSWER = (
    "Sorry. I can't help you with that. {}".format(HELP_MESSAGE))

SCORE = "Your {} score is {} out of {}. "
