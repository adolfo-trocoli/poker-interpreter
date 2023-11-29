import re

loose_header_regex = re.compile(r'^\d.*')
loose_player_regex = re.compile(r'^[a-zA-Z].*')

header_regex = re.compile(r'(\d{1,2})\/(\d{1,2})\/(\d{2})\s+(\d{2,3})\s*:\s+(\d{1,2})\s*€?\s*')
player_regex = re.compile(r'(\w+)\s+([+-]?\d+)\s*=\s*([+-]?\d+(.\d+)?)\s*€?\s*')

strict_header_regex = re.compile(r'(\d{1,2})\/(\d{1,2})\/(\d{2})\s(\d{2,3}):\s(\d{1,2})€')
strict_player_regex = re.compile(r'(\w+)\s([+-]\d+)\s=\s([+-]\d+(.\d+)?)€')

incomplete_player_regex = re.compile(r'(\w+)\s+([+-]?\d+)\s*=?\s*[+-]?\s*$')

def warning(message, line_number):
	print(f'WARN - Linea {str(line_number)}: {message}')

def alarm(message, line_number):
	print(f'ERROR - Linea {str(line_number)}: {message}')

def treat_header(line, line_number):
	if not re.search(header_regex, line):
		alarm('Error de encabezado.', line_number)
		return
	if not re.search(strict_header_regex, line):
		warning('No estricto')

def treat_player(line, line_number):
	if not re.search(player_regex, line) and not re.search(incomplete_player_regex, line):
		alarm ('Error de jugador.', line_number)
		return
	if not re.search(strict_player_regex, line):
		warning('No estricto', line_number)

def check_format(line, line_number):
	if re.search(loose_header_regex, line):
		treat_header(line, line_number)
	elif re.search(loose_player_regex, line):
		treat_player(line, line_number)
	else:
		print('NO MATCH: ' + str(line_number))

def format_checker(file):
	with open(file, 'r') as file:
		for line_number, line in enumerate(file, 1):
			if line.strip() == '':
				continue
			check_format(line.strip(), line_number)