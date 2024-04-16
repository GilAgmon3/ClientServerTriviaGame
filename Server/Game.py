import queue
import random
import threading
import time
import socket
from Player import Player


class Game:
    trivia_questions = {
        "Ross Geller has been married three times throughout the series.": True,
        "Monica Geller is allergic to shellfish.": True,
        "Joey Tribbiani's catchphrase is 'How you doin'?": True,
        "Phoebe Buffay's twin sister's name is Ursula.": True,
        "Chandler Bing's job title is 'Transponster'.": False,
        "Rachel Green's favorite movie is 'Jurassic Park'.": False,
        "Monica and Ross are twins.": False,
        "Phoebe's mother's name is Lily Buffay.": True,
        "Joey doesn't share food.": True,
        "Rachel was originally supposed to marry Barry.": True,
        "Gunther's last name is Central Perk.": False,
        "Ross and Rachel got married in Las Vegas.": True,
        "Phoebe's favorite holiday is Thanksgiving.": False,
        "Chandler's middle name is Muriel.": True,
        "Monica's biggest pet peeve is animals dressed as humans.": True,
        "Rachel worked at Ralph Lauren.": True,
        "Phoebe was once homeless.": True,
        "Joey's stuffed penguin is called Hugsy.": True,
        "Ross and Monica's parents' names are Jack and Judy.": True,
        "Chandler's father is a famous novelist.": False
    }

    def __init__(self, players: list[Player]):
        # Get the players of the game
        self.__players = players

        # Create an empty stack
        self.questions_stack = list(Game.trivia_questions.keys())

        # Shuffle the keys randomly
        random.shuffle(self.questions_stack)

        self.__finish = False

        # TODO: why do we need this in our init?
        # random_question = self.generate_question()
        # self.__question = random_question[0]
        # self.__answer = random_question[1]
        self.current_question = None
        self.current_question_answer = None

        # TODO: change this
        self.server_name = "Smelly Cat Squad"

    def generate_question(self) -> bool:
        '''
        Generate the next random question from question stack.
        :return: True if there is question that wasn't asked already to generate, False else
        '''
        if self.questions_stack:
            self.current_question = self.questions_stack.pop()
            self.current_question_answer = Game.trivia_questions[self.current_question]
            return True
        else:
            return False

    def get_welcome_message(self) -> str:
        welcome_message = f"Welcome to the {self.server_name} server, where we are answering trivia questions about 'Friends' TV show!\n"

        players_info = ""
        for i, player in enumerate(self.__players):
            players_info += f"Player {i + 1}: {player.get_name()}\n"

        return welcome_message + players_info

    def get_question_message(self) -> str:
        question_message = "==\n"
        question_message += f"True or False: {self.current_question}\n"
        return question_message

    def get_winner_message(self, winner_index: int) -> str:
        player = self.__players[winner_index]
        winner_message = f"{player.get_name()} is correct! {player.get_name()} wins!"
        return winner_message

    def get_summary_message(self, winner_index: int) -> str:
        player = self.__players[winner_index]
        summary_message = f"Game over! \n Congratulations to the winner: {player.get_name()}"
        return summary_message

    def handle_message(self, message: str):
        self.__send_message_to_players(message)
        print(message)

    def starting_game_messages(self):
        # starting the game
        self.handle_message(self.get_welcome_message())
        print("checkpoint 1")
        self.generate_question()
        print("checkpoint 2")

        self.handle_message(self.get_question_message())
        print("checkpoint 3")

    def __game(self):
        # starting the game
        self.handle_message(self.get_welcome_message())

        self.generate_question()

        self.handle_message(self.get_question_message())

        # initilize queue for each player's thread
        players_response = [queue.Queue() for _ in range(len(self.__players))]

        # initilize array of thread, one for each player to handle player's response
        threads_arr = [threading.Thread(target=Game.__handle_player_question_answer,
                                        args=[self, player, response])
                       for player, response in zip(self.__players, players_response)]

        # starting all players threads
        for thread in threads_arr:
            thread.start()
        # TODO: hande 10 sec timer for all players
        # TODO: remove join?
        # joining response threads for all players
        for thread in threads_arr:
            thread.join()

        for response in players_response:
            response.get()

        # TODO: handle disqualified

        # initialize variables to track the shortest time and index of the correct answer
        shortest_time = float('inf')
        correct_answer_index = None

        # iterate over each player's response queue
        for index, response_queue in enumerate(players_response):
            # get the response tuple from the queue
            response_tuple = response_queue.get()
            # unpack the tuple
            curr_answer, curr_time = response_tuple
            # check if the answer is correct and time is shorter than the current shortest time
            if curr_answer == self.current_question_answer and curr_time < shortest_time:
                shortest_time = curr_time
                correct_answer_index = index
        # send to clients and print at server the message of the win
        self.handle_message(self.get_winner_message(correct_answer_index))

        # finishing the game
        self.__finish_game()

    def __send_message_to_players(self, message: str):
        for player in self.__players:
            player.get_socket().send(message.encode())

    def convert_answer(self, answer: str):
        '''
        :param answer: answer from player
        :return: True if the player answer any of True valid version, False else
        '''

        return answer in ('T', 'Y', '1')

    def __handle_player_question_answer(self, player: Player, response: queue):
        # TODO set socket timeout?

        start = time.time()
        try:
            ans = player.get_socket().recv(1024)
            ans = ans.decode()
            player_answer = self.convert_answer(ans)
        except Exception:
            # TODO: timeout exception?
            player_answer = None
        end = time.time()
        # tuple of the answer according to player and response time
        answer_time_tuple = (player_answer, end - start)
        response.put(answer_time_tuple)
        # return

    def __finish_game(self):
        self.__finish = True
        self.__send_message_to_players("Server disconnected, listening for offer requests...")
        for player in self.__players:
            player.kill()
        print("Game over, sending out offer requests...")
