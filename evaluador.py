import re
import argparse
import comprobar_formato
from datetime import date as daydate
from matplotlib import pyplot as plt


# Argumentos

parser = argparse.ArgumentParser()

parser.add_argument('-t', '--total', help='total de beneficios de todos los jugadores', action = 'store_true')
parser.add_argument('-p', '--pumas', help='solo mostrar pumas, debe ser usado en combinación con -t', action='store_true')
parser.add_argument('-j', '--jugador', help='total de beneficios para el jugador indicado')
parser.add_argument('-g', '--grafico', help='grafico de historia de beneficios del jugador indicado')
parser.add_argument('-gt', '--graficototal', help='grafico de historia acumulada de beneficios del jugador indicado')
parser.add_argument('-cm', '--comprobar', help='muestra el si hay diferencia entre lo ganado por los jugadores y el total jugado', action = 'store_true')
parser.add_argument('-o', '--output', help='output to given file')
parser.add_argument('-l', '--list', help='list games', action='store_true')
parser.add_argument('-lg', '--game', help='show one game by id')
parser.add_argument('-r', '--resolve', help='resolver tricount')
parser.add_argument('-cf', '--check_format', help='comprobar el formato', action='store_true')

args = parser.parse_args()

# Definicion de objetos

class player:
	def __init__(self, name, cuantity, money = None):
		self.name = name
		self.cuantity_gained = cuantity
		self.money_gained = money
		self.complete = money is not None

class header:
	def __init__(self, date, cuantity, buyin):
		self.date = date
		self.cuantity = cuantity
		self.buyin = buyin

class game:
	def __init__(self, header, players, complete = True):
		self.date = header.date
		self.cuantity = header.cuantity
		self.buyin = header.buyin
		self.players = players
		self.complete = complete

# Metodos de parsing

def check_line(line):
	global inside_block
	global header_tmp
	global players
	global games
	global incomplete
	header_result = re.search(header_regex, line)
	player_result = re.search(player_regex, line)
	incomplete_player_result = re.search(incomplete_player_regex, line)
	if line == '':
		if not inside_block:
			return
		else:	
			inside_block = False
			if incomplete:
				incomplete = False
				games.append(create_incomplete_game(header_tmp, players))
			else:
				games.append(create_game(header_tmp, players))
			players = []
			header_tmp = None
	if header_result:
		header_tmp = create_header(header_result)
	if player_result:
		inside_block = True
		players.append(create_player(player_result))
	if incomplete_player_result:
		inside_block = True
		incomplete = True
		players.append(create_incomplete_player(incomplete_player_result))

def add_last_game():
	global inside_block
	global incomplete
	inside_block = False
	if incomplete:
		incomplete = False
		games.append(create_incomplete_game(header_tmp, players))
	else:
		games.append(create_game(header_tmp, players))
	
def create_header(header_result):
	groups = header_result.groups()
	date = daydate(int('20' + groups[2]),int(groups[1]),int(groups[0]))
	cuantity = float(groups[3])
	buyin = float(groups[4])
	return header(date, cuantity, buyin)

def create_player(player_result):
	groups = player_result.groups()
	name = groups[0].lower()
	cuantity = float(groups[1])
	money = float(groups[2])
	return player(name, cuantity, money)

def create_incomplete_player(incomplete_player_result):
	groups = incomplete_player_result.groups()
	name = groups[0].lower()
	cuantity = float(groups[1])
	return player(name, cuantity)

def create_game(header, players):
	return game(header, players)

def create_incomplete_game(header, players):
	return game(header, players, False)

def complete_game(game):
	for player in game.players:
		player.money_gained = player.cuantity_gained / game.cuantity * game.buyin
		player.complete = True
	game.complete = True

# Metodos de aplicacion

def total_benefit():
	players_total = dict()
	for game in games:
		for player in game.players:
			if player.name in players_total:
				players_total[player.name] += player.money_gained
			else:
				players_total[player.name] = player.money_gained
	return players_total

def player_benefit_history():
	history = []
	dates = []
	for game in games:
		for player in game.players:
			if player.name == args.grafico:
				if game.date not in dates:
					history.append(player.money_gained)
					dates.append(game.date)
				else:
					history[-1] += player.money_gained

	return (history, dates)

def player_total_benefit_history():
	total_history = []
	total = 0
	dates = []
	for game in games:
		for player in game.players:
			if player.name == args.graficototal:
				total += player.money_gained
				if game.date not in dates:
					total_history.append(total)
					dates.append(game.date)
				else:
					total_history[-1] = total
	return (total_history, dates)

def comprobar():
	results = []
	for game in games:
		results.append(comprobar_partida(game))
	return results

def comprobar_partida(game):
	total = 0
	error = False
	for player in game.players:
			total += player.money_gained
	if abs(total) >  game.buyin / 50:
		error = True
	return (total, game.date, error)

def resolve():
	game = games[int(args.resolve) - 1]
	winner_remain = 0
	looser_id = 0
	result_list = []
	rest = 0
	winners = [(player.name, player.money_gained) for player in game.players if player.money_gained > 0]
	loosers = [(player.name, -1 * player.money_gained) for player in game.players if player.money_gained < 0]
	for winner in winners:
		result_list.append(winner)
		winner_remain = winner[1]
		while looser_id < len(loosers):
			if rest == 0:
				rest = loosers[looser_id][1]
			if rest < winner_remain:
				result_list.append((loosers[looser_id][0], -1 * rest))
				winner_remain -= rest
				rest = 0
			else:
				result_list.append((loosers[looser_id][0], -1 * winner_remain))
				rest = rest - winner_remain
				break
			if rest == 0:
				looser_id += 1
		result_list.append((None, None))
	return result_list

# Metodos de vista

def show_total_benefit():
	output('------------------------\n')
	output('-- Beneficio total --\n')
	output('------------------------\n')
	for k,v in sorted(total_benefit().items(), key=lambda item: item[1], reverse=True):
		if args.pumas:
			if k in lista_pumas:
				output(f'  {k}: {number_string(v)}\n')
		else:
			output(f'  {k}: {number_string(v)}\n')
	output('------------------------\n')

def show_jugador_benefit():
	output('------------------------\n')
	output(f'-- Beneficio de {args.jugador} --\n')
	output('------------------------\n')
	output(f'  {total_benefit()[args.jugador]:.2f}\n')
	output('------------------------\n')

def show_player_benefit_history():
	(history, dates) = player_benefit_history()
	date_strings = [date_string(onedate) for onedate in dates]
	plt.bar(date_strings, history)
	plt.show()

def show_player_total_benefit_history():
	(history, dates) = player_total_benefit_history()
	date_strings = [date_string(onedate) for onedate in dates]
	plt.plot(date_strings, history)
	plt.show()

def show_comprobar():
	for (result, date, error) in comprobar():
		if error:
			output(color_text('red', f'{date}: {result:.2f}\n'))
		else:
			output(f'{date}: {result:.2f}\n')

def show_list_games():
	id = 1
	for game in games:
		output(f'{id}: {date_string(game.date)}\n')
		id += 1

def show_game():
	game = games[int(args.game) - 1]
	output('------------------------\n')
	output(f'-- Partida {int(args.game)} --\n')
	output(f'{date_string(game.date)} {str(int(game.cuantity))}: {str(int(game.buyin))}€\n')
	output('------------------------\n')
	for player in game.players:
		output(f'{player.name} {number_string(player.cuantity_gained)} = {number_string(player.money_gained)}€\n')
	output('------------------------\n')

def show_resolve():
	output('------------------------\n')
	output(f'-- Pagos Tricount --\n')
	output('------------------------\n')
	for (name, value) in resolve():
		if name is not None:
			output(f'{name} {number_string(value)}\n')
		else:
			output('------------------------\n')

def number_string(number):
	plus = '+' if number > 0 else ''
	noplus = str(int(number)) if int(number) == number else f'{number:.2f}'
	return plus + noplus

def date_string(date):
	return str(date.strftime('%d/%m/%Y'))

def color_text(color, text):
	if color == "red":
		return '\033[0;31m' + text + '\033[0m'

def output(message):
	global output_file
	if(args.output):
		output_file.write(message)
	else:
		print(message, end='')

# Definicion de expresiones regulares

header_regex = re.compile(r'(\d{1,2})\/(\d{1,2})\/(\d{2})\s+(\d{2,3})\s*:\s+(\d{1,2})\s*€?\s*')
player_regex = re.compile(r'(\w+)\s+([+-]?\d+)\s*=\s*([+-]?\d+(.\d+)?)\s*€?\s*')

incomplete_player_regex = re.compile(r'(\w+)\s+([+-]?\d+)\s*=?\s*[+-]?\s*$')

# Definicion de variables

file_output = False

incomplete = False
inside_block = False
header_tmp = None
players = []
games = []

lista_pumas = ['adolfo', 'marco', 'nico', 'mario']

# Lectura del archivo

if args.output:
	output_file = open(args.output, 'w')

if args.check_format:
	comprobar_formato.format_checker()

with open('nota.txt', 'r') as file:
	for line in file:
		check_line(line.strip())
	add_last_game()

for game in games:
	if not game.complete:
		complete_game(game)

if args.total:
	show_total_benefit()
if args.jugador:
	show_jugador_benefit()
if args.grafico:
	show_player_benefit_history()
if args.graficototal:
	show_player_total_benefit_history()
if args.comprobar:
	show_comprobar()
if args.list:
	show_list_games()
if args.game:
	show_game()
if args.resolve:
	show_resolve()

if args.output:
	output_file.close()