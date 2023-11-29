
# Poker Interpreter

Intérprete para leer la lista de partidas de poker.

## Descripción

Script capaz de leer archivos compatibles con el formato descrito más abajo, incluso si no se incluye la cantidad de dinero ganado. También puede detectar fallos en la sintaxis, generar gráficos de historial, calcular totales, y alguna cosa más.

## Opciones

	-h, --help: muestra el menú de ayuda
	-t, --total: muestra el total de beneficios de todos los jugadores
	-p, --pumas: muestra solo el total de los pumas, debe ser usado en combinación con -t
	-j, --jugador: muestra el total de beneficios para el jugador indicado
	-g, --grafico: muestra el grafico de beneficios por partida para un el jugador indicado
	-gt, --graficototal: muestra el gráfico acumulado de beneficios para un jugador indicado
	-cm, --comprobar: muestra si las partidas son de suma 0. Si el total sumado dista más de un 2% del buy-in de la partida, aparece en rojo
	-o, --output: saca el resultado a un fichero indicado en vez de a la salida estándar
	-l, --list: lista las partidas mostrando id y fecha
	-lg, --game: muestra el resultado de la partida con el id indicado
	-r, --resolve: resuelve el tricount para la partida dada
	-cf, --check-format: Comprueba que el formato del fichero es correcto. Si hay errores pero es capaz de interpretarlos, muestra un warning. Si hay un error que no permite leer la línea, muestra el tipo de error y la línea donde se encuentra

## Formato del archivo

El archivo debe llevar un formato concreto igual al del ejemplo.
El programa es capaz de entender el archivo aunque tenga el formato mínimo, pero es más legible para humanos el formato estricto.

### Formato estricto

fecha cantidad_fichas: cantidad_euros€\
nombre_jugador [+-]cantidad_fichas = [+-]cantidad_euros\

-- Ejemplo --

20/10/23 90: 2€\
federico +98 = +2.18€\
anastasia -78 = -1.7€\
emmanuel -20 = -0.44€\

### Formato mínimo

fecha cantidad_fichas: cantidad_euros€\
nombre_jugador [-]cantidad_fichas

-- Ejemplo --

20/10/23 90: 2€\
federico +98\
anastasia -78\
emmanuel -20

## Autor

Adolfo Trocolí Naranjo

## Licencia

Este proyecto es de código libre. Cualquiera puede usarlo o colaborar si quiere.

## Agradecimientos

A los pumas por hacer esto posible.
