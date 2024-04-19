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

        # Create questions stack
        self.questions_stack = list(Game.trivia_questions.keys())

        # Shuffle the keys randomly
        random.shuffle(self.questions_stack)

        self.__finish = False

        self.current_question = None
        self.current_question_answer = None

        # TODO: change this
        self.server_name = "Smelly Cat Squad"

        self.__game()

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
        """
        param message: message from game's server
        Handle messages that is relevant for both server and clients-prints the message in all the consoles
        """
        self.__send_message_to_players(message)
        print(message)

    def starting_game_messages(self):
        # starting the game
        self.handle_message(self.get_welcome_message())
        self.new_question_message()

    def new_question_message(self):
        self.generate_question()
        self.handle_message(self.get_question_message())

    def handling_players_answer_threads(self) -> list[queue]:
        """
        This method creates thread for each player to handle the player's response and handle all players responses.
        :return: list of queues, each one contains player's answer and response time for this round of game.
        """
        # initialize queue for each player's thread
        players_response = [queue.Queue() for _ in range(len(self.__players))]

        # initialize array of thread, one for each player to handle player's response
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

        return players_response

    def find_winner(self, players_response: list[queue]) -> int:
        """
        :param players_response:  List of queues, each one contains player's answer and response time for this round of game.
        :return: The winner's index if there is a winner, None if there is no winner
        """
        # initialize variables to track the shortest time and index of the correct answer
        shortest_time = float('inf')
        correct_answer_index = None

        # iterate over each player's response queue
        for index, response_queue in enumerate(players_response):
            # get the response tuple from the queue
            response_tuple = response_queue.get()
            # unpack the tuple
            curr_answer, curr_time = response_tuple
            # TODO: remove printing
            print(f'index: {index}, answer: {curr_answer}, time: {curr_time}')
            # check if the answer is correct and time is shorter than the current shortest time
            if curr_answer == self.current_question_answer and curr_time < shortest_time:
                shortest_time = curr_time
                correct_answer_index = index
        return correct_answer_index

    def __game(self):
        # TODO: handle disqualified

        # TODO: check with Gil
        self.starting_game_messages()
        players_response = self.handling_players_answer_threads()
        correct_answer_index = self.find_winner(players_response)

        # In case there is no winner-continue the game
        while correct_answer_index is None:
            self.new_question_message()
            players_response = self.handling_players_answer_threads()
            correct_answer_index = self.find_winner(players_response)
            print(f'correct answer index: {correct_answer_index}')

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
        # TODO: need the set socket timeout?
        player.get_socket().settimeout(10)
        start = time.time()
        try:
            ans = player.get_socket().recv(1024)
            ans = ans.decode()
            player_answer = self.convert_answer(ans)
            # TODO: remove printing
            print(f'Player {player.get_name()} answered {player_answer}')
        except Exception:
            # TODO: timeout exception?
            player_answer = None
        end = time.time()
        # tuple of the answer according to player and response time
        answer_time_tuple = (player_answer, end - start)
        # TODO remove
        print(answer_time_tuple)
        response.put(answer_time_tuple)
        # return

    def __finish_game(self):
        self.__finish = True
        # TODO: for some reason this message is printed twice only at LOSING client's console
        # self.__send_message_to_players("Server disconnected, listening for offer requests...3")
        # TODO: i dont think we need to kill player's threads
        for player in self.__players:
            player.kill()
        print("Game over, sending out offer requests...")
