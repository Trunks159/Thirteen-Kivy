import kivy
from card_functions import order_cards, isSingle, isChain, isDuplicate, isChop
from random import shuffle
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from os import path	
faces = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
suits = ['S', 'C', 'D', 'H']		
Builder.load_file("thirteen_.kv")

class WindowManager(ScreenManager):
	pass
	
#basically a screen that asks how many players, and runs a game based on what was selected
class HowManyPlayers(Screen):
	humans = ObjectProperty(None) #how many humans selected
	shape_shifter_o = ObjectProperty(None) #button info that changes from btn to label depending on if an option was selected
	def on_shape_shifter_o(self, instance, value):#removes button or label and replaces it
		self.remove_widget(self.ids.shape_shifter)
		self.ids.shape_shifter = value
		self.add_widget(self.ids.shape_shifter)
		if isinstance(self.ids.shape_shifter, Button):
			self.ids.shape_shifter.bind(on_release = self.change_screen)
		
	def create_players(self, instance):
		players = []
		for i in range(int(self.humans)):
			players.append(Player("Player " + str(i)))
		return players
		
	def change_screen(self, instance):
		players = self.create_players(instance)
		sm.add_widget(Game(players))
		sm.current = "game"
		
class Human(ToggleButton):
	def on_state(self, instance, value):
		if value == "down":
			hmp.humans = self.text
			hmp.shape_shifter_o = Button(text = hmp.ids.shape_shifter.text,size_hint = hmp.ids.shape_shifter.size_hint,pos_hint = hmp.ids.shape_shifter.pos_hint)

		elif value == "normal":
			hmp.humans = ""
			hmp.shape_shifter_o = Label(text = hmp.ids.shape_shifter.text,size_hint = hmp.ids.shape_shifter.size_hint,pos_hint = hmp.ids.shape_shifter.pos_hint)

class Game(Screen):
	def __init__(self, players, **kwargs):
		super(Game, self).__init__(**kwargs)
		self.players = players
		self.players_dict = self.set_players_dict(self.players)
		self.deck = Deck()
		self.current_player = self.players[0]
		self.deal()
		self.current_player = self.find_lowest_card(self.players)
		for player in self.players:
			self.add_widget(player)
		self.hud = HUD()
		self.add_widget(self.hud)
		self.but = Button(text = "Order Hand")
		self.lab = Label(text = self.current_player.name)
		self.but.bind(on_press = self.players[0].order_hand)
		self.hud.add_widget(self.but)
		self.hud.add_widget(self.lab)

		
	def set_players_dict(self, players):	#works
		new_dict = {}
		for player in players:
			new_dict[player.name] = player
		return new_dict
		
	def start(self):
		self.deal()
		self.current_player = self.find_lowest_card(self.players)
		print("This is the current_player: " , self.current_player.name)
		
#pops cards from deck, adds to hands of players, supports 4 players actually		
	def deal(self):
		hands = []
		for i in range(4):
			hands.append(self.deck.deal(13))
		for player in self.players:
			player.hand = hands.pop()
	
	def find_lowest_card(self, players): #algorithm to find the lowest card in the players' hands
		values = []
		for player in players:
			for card in player.hand:
				values.append(card.value)
		lowest_card = min(values)
		for player in players:
			for card in player.hand:
				if card.value == lowest_card:
					return player

#called by field to change turns
	def next_turn(self):	#doesn't work yet
		i = 0
		for player in self.players:
			if player == self.current_player: break
			i+=1
		i += 1 #adds turn kinda
		
		if i == len(self.players): i = 0
		self.current_player = self.players[i]
		
class Grid(GridLayout):
	pass

class Card(ToggleButton):
	def __init__(self, face, suit, **kwargs):
		super(Card, self).__init__(**kwargs)
		self.face = face
		self.suit = suit
		self.value = self.get_value(self.face, self.suit)
		self.text = self.face + self.suit
		self.background_normal = "Pictures/JPEG/" + self.face + self.suit + ".jpg"
		
	def get_value(self, face, suit):
		return self.get_face_value()[face] + self.get_suit_value()[suit]
	
	def get_face_value(self):
		faces = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
		value = {}
		i = 0
		for item in faces:
			value[item] = i
			i+=1
		return value
			
	def get_suit_value(self):
		suits = ['S', 'C', 'D', 'H']
		value = {}
		k = 0
		for item in suits:
			value[item] = k
			k+=.1
		return value
		
class Deck():
	def __init__(self):
		self.cards = self.initialize_deck()
		
	def deal(self, number):	#takes a number and returns a list of number * cards
		hand = []
		for i in range(number):
			hand.append(self.cards.pop())
		return hand

#conjours deck and shuffles it
	def initialize_deck(self):
		cards = []
		faces = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
		suits = ['S', 'C', 'D', 'H']			
		for face in faces:
			for suit in suits:
				cards.append(Card(face, suit))		
		shuffle(cards)
		return cards
		
class Player(GridLayout):
	hand = ObjectProperty(None)
	def __init__(self, name, **kwargs):
		super(Player, self).__init__(**kwargs)
		self.name = name
		self.pos_hint = self.set_position(self.name)
		self.turn = False


#determined pos based on the player name
	def set_position(self, name):
		if name == "Player 0":
			return {"bottom": 1}
		else:
			return {"top":1}		
		
#when hand gets initialized, display the cards
	def on_hand(self, instance, value):
		print("on_hand was triggered...")
		self.display_cards(value)

#first method that initially shows hand
	def display_cards(self, hand):	
		if hand:	
			self.clear_widgets()
		for card in hand:
			self.add_widget(card)
			
#looks through hand and if a button is down it removed from and widget from Player, returns the widgets to add to Field
	def selected_cards(self, hand): 
		print("THIS IS HAND: ", hand)
		i = 0
		selected = []
		while i < len(hand):
			if hand[i].state == "down":
				print("APPARENTLY DOWN WAS FOUND")
				hand[i].state = "normal"	#untoggles button
				self.remove_widget(hand[i])
				selected.append(hand.pop(i))
				continue
			i+=1
		return selected
		


#returns Play(), where the cards played are the ones selected, called when Field is touched		
	def make_play(self):
		selected = self.selected_cards(self.hand)
		p = Play(self.name, selected)
		if p.combo == False:
			print("COMBO = FALSE...")
			hand = self.hand + p.cards
			self.hand = hand
		return p	
	
#makes a new list with the Play() cards and self.hand cards and updates player's hand, which triggers on_hand

		
#called by HUD, it orders P1's hand		
	def order_hand(self, instance):	
		self.hand = order_cards(self.hand)

#deals with the current gamestate most of the time
class Field(GridLayout):
	current_play = ObjectProperty(None)
	
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			current_player = self.parent.current_player			
			new_play = current_player.make_play()

			if self.current_play == None:
				self.current_play = new_play
				self.parent.next_turn()
			elif new_play == "skip":
				self.parent.next_turn()
			elif self.does_it_beat(new_play, self.current_play):
				self.current_play = new_play
			else:
				print("You cant do this play")
				current_player.hand = current_player.hand.append(current_play.cards)

				
	def on_current_play(self, instance, play):
		self.clear_widgets()
		for card in play.cards:
			self.add_widget(card)

	def make_play(self, *cards):
		return Play(self.name, cards)		

#if the new play isn't high enough, or is not the same combo as the on the field, return False
	def does_it_beat(self, new_play, current_play):
		print("does_it_beat ran")
		if new_play.value <= current_play.value:
			print("That card(s) value too low. Try again...")
			return False
		elif new_play.combo != current_play.combo:
			print("What you put was not a " + current_play.combo)
			return False
		else:
			return True

#each instance runs the value of a list of cards and finds the card combination
class Play():
	def __init__(self, player_name, cards):
		self.player_name = player_name
		self.cards = cards
		self.combo = self.run_tests(self.cards)
		self.value = self.get_value(self.cards)
		
#takes cards and returns the card combo
	def run_tests(self, cards):
		if cards == "skip":
			combo = "skip"
		elif isSingle(cards):
			combo = "single"
		elif isChop(cards):
			combo = "chop"
		elif isDuplicate(cards, 2):
			combo = "double"
		elif isDuplicate(cards, 3):
			combo = "triple"
		elif isDuplicate(cards, 4):
			combo = "bomb"
		elif isChain(cards):
			combo = "chain"
		else:
			combo = False
		return combo
				
#takes a bunch of cards and returns value of those cards added up
	def get_value(self, cards):
		if isSingle(cards):
			total = cards[0].value
		else:
			total = 0
			for card in cards:
				total += card.value
		return total
	


class HUD(GridLayout):
	pass
sm = WindowManager()
hmp = HowManyPlayers()
sm.add_widget(hmp)

class ThirteenApp(App):
	
	def build(self):
		Window.clearcolor = [1, 0, 0, 1]
		Window.size = (560,940)
		Window.left = 0
		Window.top = 25
		return sm


			
if __name__ == '__main__':
	app = ThirteenApp()
	app.run()
