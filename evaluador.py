import re
import argparse
from datetime import date as daydate
from matplotlib import pyplot as plt

# Argumentos

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help='file name', default='nota.txt')
	parser.add_argument('-t', '--total', help='total de beneficios de todos los jugadores', action = 'store_true')
	parser.add_argument('-p', '--pumas', help='solo mostrar pumas, debe ser usado en combinación con -t', action='store_true')
	parser.add_argument('-j', '--jugador', help='total de beneficios para el jugador indicado')
	parser.add_argument('-g', '--grafico', help='grafico de historia de beneficios del jugador indicado')
	parser.add_argument('-gt', '--graficototal', help='grafico de historia acumulada de beneficios del jugador indicado')
	parser.add_argument('-cm', '--comprobar', help='muestra el si hay diferencia entre lo ganado por los jugadores y el total jugado', action = 'store_true')
	parser.add_argument('-o', '--output', help='output to given file')
	parser.add_argument('-l', '--list', help='list games', action='store_true')
	parser.add_argument('-lg', '--game', help='show one game by id')
	parser.add_argument('-r', '--resolve', nargs='+', help='resolver tricount')
	parser.add_argument('-cf', '--check_format', help='comprobar el formato', action='store_true')
	parser.add_argument('-i', '--igualar', help='ajustar el resultado de una partida para que la suma sea 0')
	return parser.parse_args()

# Definicion de objetos

class Player:
	def __init__(self, name, cuantity, money = None):
		self.name = name
		self.cuantity_gained = cuantity
		self.money_gained = money
		self.complete = money is not None

class Header:
	def __init__(self, date, cuantity, buyin):
		self.date = date
		self.cuantity = cuantity
		self.buyin = buyin

class Game:
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
	if inside_block and not line:
		inside_block = False
		games.append(create_game(header_tmp, players, not incomplete))
		players = []
		header_tmp = None
		if incomplete:
			incomplete = False
		return
	header_result = re.search(header_regex, line)
	player_result = re.search(player_regex, line)
	if header_result:
		header_tmp = create_header(header_result)
	elif player_result:
		inside_block = True
		players.append(create_player(player_result))

def add_last_game():
	global inside_block
	global incomplete
	if inside_block:
		inside_block = False
		games.append(create_game(header_tmp, players, not incomplete))
		if incomplete:
			incomplete = False
	
def create_header(header_result):
	groups = header_result.groups()
	date = daydate(int('20' + groups[2]),int(groups[1]),int(groups[0])) # 20 is to create 2023, 2024 (groups[2] is the year)
	cuantity = float(groups[4])
	buyin = float(groups[5])
	return Header(date, cuantity, buyin)

def create_player(player_result):
	global incomplete
	groups = player_result.groups()
	name = groups[0].lower()
	cuantity = float(groups[1])
	if len(groups) > 2: # si hay atributo money lo meto, si no no 
		money = float(groups[2])
		return Player(name, cuantity, money)
	else:
		incomplete = True
		return Player(name, cuantity)

def create_game(header, players, complete):
	return Game(header, players, complete)

def complete_game(game):
	for player in game.players:
		player.money_gained = player.cuantity_gained / game.cuantity * game.buyin
		player.complete = True
	game.complete = True

# Metodos de aplicacion

def total_benefit(game_list):
	players_total = dict()
	for game in game_list:
		for player in game.players:
			if player.name in players_total:
				players_total[player.name] += player.money_gained
			else:
				players_total[player.name] = player.money_gained
	return players_total # diccionario formado por parejas {nombre, ganancia en euros}

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

def count_resolve(player_list):
	winner_remain = 0
	looser_id = 0
	result_list = []
	rest = 0
	winners = [(player.name, player.money_gained) for player in player_list if player.money_gained > 0]
	loosers = [(player.name, -1 * player.money_gained) for player in player_list if player.money_gained < 0]
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

def resolve():
	game_list = []
	for id in args.resolve:
		game_list.append(games[int(id) - 1]) # lista de partidas pedidas como argumento
	players_total = total_benefit(game_list) # dict con nombre y cantidad ganada en dinero
	player_list = [Player(name, 0, money) for (name, money) in players_total.items()] # lista de players con nombre y money_gained
	result_list = count_resolve(player_list) # lista de tuplas (nombre, valor) con lo que ha ganado o perdido separado por tuplas (None, None)
	return result_list

def igualar():
	new_players = []
	total_game_benefit = 0
	game = games[int(args.igualar) - 1]
	benefit_dict = total_benefit([game]) # dict con jugadores y ganancias
	result = comprobar_partida(game)[0] # diferencia de dinero
	if result > 0:
		player_diff_list = [(name, value) for (name, value) in benefit_dict.items() if float(value) > 0]
	elif result < 0:
		player_diff_list = [(name, value) for (name, value) in benefit_dict.items() if float(value) < 0]
	else:
		return
	for player_diff in player_diff_list: # calculamos el beneficio total que ha habido en la partida
		total_game_benefit += player_diff[1]
	for player_diff in player_diff_list: # añadimos a los jugadores que tienen que cambiar el beneficio
		calculo = player_diff[1] - result*player_diff[1]/total_game_benefit
		new_players.append(Player(player_diff[0], int(calculo*game.cuantity/game.buyin), calculo))
	for player in game.players: # añadimos a los jugadores que faltan
		if result > 0 and player.money_gained < 0:
			new_players.append(player)
		if result < 0 and player.money_gained >= 0:
			new_players.append(player)
	new_header = Header(game.date, game.cuantity, game.buyin)
	new_game = Game(new_header, new_players)
	return new_game

# Metodos de vista

def show_total_benefit():
	output('------------------------\n')
	output('-- Beneficio total --\n')
	output('------------------------\n')
	for k,v in sorted(total_benefit(games).items(), key=lambda item: item[1], reverse=True):
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
	output(f'  {total_benefit(games)[args.jugador]:.2f}\n')
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
	id = 1
	for (result, date, error) in comprobar():
		if error:
			output(color_text('red', f'{id} - {date_string(date)}: {result:.2f}\n'))
		else:
			output(f'{id} - {date_string(date)}: {result:.2f}\n')
		id += 1

def show_list_games():
	id = 1
	for game in games:
		output(f'{id}: {date_string(game.date)}\n')
		id += 1

def show_game(game):
	buyin = str(int(game.buyin)) if int(game.buyin) == game.buyin else f'{game.buyin:.2f}'
	output('------------------------\n')
	output(f' -- Partida {date_string(game.date)} --\n')
	output('------------------------\n')
	output(f'{date_string(game.date)} {str(int(game.cuantity))}: {buyin}€\n')
	for player in game.players:
		output(f'{player.name} {number_string(player.cuantity_gained)} = {number_string(player.money_gained)}€\n')
	output('------------------------\n')

def show_game_command():
	show_game(games[int(args.game) - 1])

def show_igualar():
	game = igualar()
	output('------------------------\n')
	output('    Partida igualada\n')
	show_game(game)


def show_resolve():
	result_list = resolve()
	output('--------------------\n')
	output('-- Pagos Tricount --\n')
	output('--------------------\n')
	for (name, value) in result_list:
		if name is not None:
			output(f'{name} {number_string(value)}\n')
		else:
			output('--------------------\n')

def number_string(number):
	plus = '+' if number >= 0 else ''
	noplus = str(int(number)) if int(number) == number else f'{number:.2f}'
	return plus + noplus

def date_string(date):
	return str(date.strftime('%d/%m/%y'))

def color_text(color, text):
	if color == "red":
		return '\033[0;31m' + text + '\033[0m'

def output(message):
	global output_file
	if(args.output):
		output_file.write(message)
	else:
		print(message, end='')

def try_check_line(line, line_num = 0):
	try:
		check_line(line.strip())
	except Exception as e:
			print(f"Error de lectura en línea {line_num}, abortando.")
			print(e)

# Definicion de expresiones regulares

header_regex = re.compile(r'(\d{1,2})\/(\d{1,2})\/(\d{1,2})\s+(-torneo-)?\s*(\d{2,3})\s*:\s+(\d{1,2}(.\d+)?)\s*€?\s*')
player_regex = re.compile(r'(\w+)\s+([+-]?\d+).*$')

# Definicion de variables

file_output = False
incomplete = False
inside_block = False
header_tmp = None
players = []
games = []
args = []
lista_pumas = ['adolfo', 'marco', 'nico', 'mario']

# Main

def main():
	global args

	args = parse_arguments()

	if args.output:
		output_file = open(args.output, 'w')

	if args.check_format:
		comprobar_formato.format_checker(args.file)

	with open(args.file, 'r') as file:
		for line_num, line in enumerate(file, 1):
			try_check_line(line, line_num)
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
		show_game_command()
	if args.resolve:
		show_resolve()
	if args.igualar:
		show_igualar()

	if args.output:
		output_file.close()

if __name__ == "__main__":
	main()