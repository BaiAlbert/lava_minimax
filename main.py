# Importación de librerías
import pygame
import sys
import math
import copy
from pathlib import Path

# Configuración de constantes
ANCHO_VENTANA = 1100
ALTO_VENTANA = 760
TAMAÑO_TABLERO = 6
TAM_CELDA = 82
MARGEN_X = 67
MARGEN_Y = 198

# Colores
COLOR_FONDO = (30, 30, 46)
COLOR_PANEL = (49, 50, 68)
COLOR_CELDA = (69, 71, 90)
COLOR_CELDA_BORDE = (88, 91, 112)
COLOR_LAVA = (243, 139, 168)  # Casilla destruida
COLOR_HUMANO = (137, 180, 250)  # Azul (Humano - Minimizador)
COLOR_IA = (250, 179, 135)  # Naranja (IA - Maximizador)
COLOR_AYUDA = (166, 227, 161)  # Verde para movimientos válidos
COLOR_TEXTO = (205, 214, 244)
COLOR_AMARILLO = (249, 226, 175)

# Estados de cada casilla en la matriz
VACIA = 0
HUMANO = 1
IA = 2
DESTRUIDA = -1


# =====================================================================
# 1. LÓGICA DEL JUEGO
# =====================================================================

# Lógica de creación del tablero
def crear_tablero():
    """
    Inicializa el tablero del juego creando una matriz de 6x6 vacía
    y colocando al Humano y a la IA en sus posiciones de salida.

    :return: Matriz 6x6 (lista de listas) con el estado inicial.
    """
    # Creamos la matriz de 6x6 vacía y ponemos a cada jugador en las posiciones iniciales
    tablero = [[VACIA for i in range(TAMAÑO_TABLERO)] for i in range(TAMAÑO_TABLERO)]
    tablero[5][2] = HUMANO  # Humano empieza abajo
    tablero[0][3] = IA  # IA empieza arriba
    return tablero


# Lógica para la busqueda de un jugador en el tablero
def buscar_jugador(tablero, jugador):
    """
    Busca las coordenadas actuales de un jugador dentro del tablero.

    :param tablero: Matriz actual del juego.
    :param jugador: Constante del jugador a buscar (HUMANO o IA).
    :return: Tupla (fila, columna) con la posición, o None si no se encuentra.
    """
    # Recorremos la matriz y devolvemos la fila y columna donde está el jugador que busquemos
    for fila in range(TAMAÑO_TABLERO):
        for columna in range(TAMAÑO_TABLERO):
            if tablero[fila][columna] == jugador:
                return (fila, columna)
    return None


# Lógica para obtener los movimientos posibles de un jugador
def obtener_movimientos_ficha(tablero, jugador):
    """
    Mira las 8 casillas vecinas alrededor del jugador (arriba, abajo, lados y diagonales)
    y devuelve una lista con las coordenadas que están dentro del tablero y VACÍAS.

    :param tablero: Matriz actual del juego.
    :param jugador: Jugador que quiere moverse (HUMANO o IA).
    :return: Lista de tuplas (fila, columna) con las casillas libres a las que puede saltar.
    """
    pos = buscar_jugador(tablero, jugador)

    # Si no encontramos al jugador devolvemos nada
    if not pos:
        return []

    # Creamos las variables con la posición del jugador
    fila, columna = pos
    movimientos = []

    for desplazamiento_fila in [-1, 0, 1]:
        for desplazamiento_columna in [-1, 0, 1]:

            # Comprobamos si estamos en la fila y columna 0 que seria el jugador
            if desplazamiento_fila == 0 and desplazamiento_columna == 0:
                continue # Saltamos si estamos en la casilla del jugador, porque no nos interesa

            # Calculamos la fila y columna a comprobar, es decir fila actual (5 por ejemplo) más la fila de desplazamiento (-1 por ejemplo) por lo que acaba siendo la fila 4 del tablero
            # En resumen estamos calculando la fila y columna real en el tablero de nuestra matriz alrededor del jugador
            nueva_fila, nueva_columna = fila + desplazamiento_fila, columna + desplazamiento_columna

            # Aquí descartamos casillas posibles que se salgan del tablero
            # Es decir, que si nueva_fila acaba siendo -1, pues lo ignoramos porque no es posible moverse a una casilla fuera del tablero
            if 0 <= nueva_fila < TAMAÑO_TABLERO and 0 <= nueva_columna < TAMAÑO_TABLERO:
                # Si la casilla está vacía
                if tablero[nueva_fila][nueva_columna] == VACIA:
                    movimientos.append((nueva_fila, nueva_columna)) # Añadimos el movimiento a la lista de movimientos posibles

    # Devolvemos la lista de casillas disponibles para moverse
    return movimientos


# Lógica para generar todas las jugadas posibles en un turno de un jugador (jugada = movimiento + casilla a quemar)
def jugadas_posibles(tablero, maximizador):
    """
    Genera todas las jugadas completas posibles en un turno para el jugador actual.
    Cada jugada es una combinación de 2 acciones: (casilla_destino, casilla_a_quemar).
    Solo considera quemar casillas a una distancia de 2 o menos del rival para optimizar el árbol.

    :param tablero: Matriz con el estado del tablero a evaluar.
    :param maximizador: True si es el turno de la IA, False si es el turno del Humano.
    :return: Lista de tuplas con formato ((fila_mover, col_mover), (fila_quemar, col_quemar)).
    """
    jugador = IA if maximizador else HUMANO
    rival = HUMANO if maximizador else IA

    # Buscamos los posibles movimientos de nuestro jugador
    movs_ficha = obtener_movimientos_ficha(tablero, jugador)
    # Buscamos la posicion del rival
    pos_rival = buscar_jugador(tablero, rival)
    jugadas = []

    # Iteramos sobre todos los movimientos posibles
    for destino in movs_ficha:
        # Recorremos el tablero
        for fila in range(TAMAÑO_TABLERO):
            for columna in range(TAMAÑO_TABLERO):
                # Si la casilla actual está vacía y no es el destino (si lo fuera nos suicidaríamos)
                if tablero[fila][columna] == VACIA and (fila, columna) != destino:
                    # Buscamos la distancia absoluta entre la fila y columna actual y la posición del rival
                    distancia_al_rival = max(abs(fila - pos_rival[0]), abs(columna - pos_rival[1]))
                    # Solo nos merece la pena si está a 2 o menos de distancia del rival
                    if distancia_al_rival <= 2:
                        # Por lo que metemos en "jugadas" el movimiento posible con la casilla a quemar
                        jugadas.append((destino, (fila, columna)))

    # Devolvemos las jugadas posibles (movimiento + casilla a quemar)
    return jugadas


# Lógica para aplicar una jugada, es decir que la IA por ejemplo mueva su ficha y queme una casilla
def aplicar(jugada, tablero, maximizador):
    """
    Ejecuta una jugada sobre el tablero: mueve la ficha del jugador a la nueva
    casilla, libera su casilla anterior y destruye (convierte en lava) la casilla elegida.

    :param jugada: Tupla con ((fila_destino, col_destino), (fila_destruir, col_destruir)).
    :param tablero: Matriz del tablero donde se aplicarán los cambios.
    :param maximizador: True si mueve la IA, False si mueve el Humano.
    """
    jugador = IA if maximizador else HUMANO
    pos_anterior = buscar_jugador(tablero, jugador)
    destino, destruir = jugada

    tablero[pos_anterior[0]][pos_anterior[1]] = VACIA  # Deja libre donde estaba
    tablero[destino[0]][destino[1]] = jugador  # Coloca la ficha en el destino
    tablero[destruir[0]][destruir[1]] = DESTRUIDA  # Quema la casilla elegida


# =====================================================================
# 2. LÓGICA DEL MINIMAX Y LA PUNTUACIÓN (HEURÍSTICA)
# =====================================================================

nodos_explorados = 0
podas_alfa_beta = 0


def puntuacion(tablero):
    """
    FUNCIÓN HEURÍSTICA h(x): Evalúa quién tiene ventaja en el tablero actual.
    Resta las casillas libres alrededor de la IA menos las casillas libres del Humano.
    - Valor positivo (+): Ventaja para la IA (+1000 si gana la IA).
    - Valor negativo (-): Ventaja para el Humano (-1000 si gana el Humano).

    :param tablero: Matriz del tablero a evaluar.
    :return: Nota numérica (int) del estado del tablero.
    """
    salidas_ia = len(obtener_movimientos_ficha(tablero, IA))
    salidas_humano = len(obtener_movimientos_ficha(tablero, HUMANO))

    # Estados terminales (victoria o derrota)
    # Si el humano ya no tiene movimientos posibles gana la IA
    if salidas_humano == 0:
        return 1000
    # Pero si la IA no tiene movimientos posibles gana el humano
    if salidas_ia == 0:
        return -1000

    # Cuantas más salidas tenga la IA y menos el humano, mejor
    # Cuanto mayor sea la heurística más posibilidades de ganar tiene la IA por lo que es mejor,
    # es decir, cuantos más movimientos posibles tenga la IA mejor
    return salidas_ia - salidas_humano


def minimax(profundidad, tablero, maximizador, profundidadMaxima, alpha, beta):
    """
    Algoritmo recursivo Minimax con poda Alfa-Beta (Esquema del temario).
    Explora el árbol de jugadas futuras alternando entre el turno de la IA (Maximizador)
    y el turno simulado del Humano (Minimizador), cortando ramas inútiles cuando alpha >= beta.

    :param profundidad: Nivel actual del árbol en el que estamos buscando (empieza en 0).
    :param tablero: Matriz con el estado del tablero en este nodo.
    :param maximizador: True si simula el turno de la IA (busca nota máxima), False si es el Humano (busca nota mínima).
    :param profundidadMaxima: Límite de niveles a explorar hacia el futuro.
    :param alpha: Mejor nota máxima que la IA ya tiene garantizada en el camino actual.
    :param beta: Peor nota mínima a la que el Humano ya sabe que puede forzar a la IA.
    :return: Tupla (mejor_jugada, nota_heuristica).
    """
    global nodos_explorados, podas_alfa_beta
    # Por cada vez que se ejecute la función sumamos 1 a los nodos explorados
    nodos_explorados += 1

    # Calculamos los movimientos posibles de la IA y del humano
    salidas_ia = len(obtener_movimientos_ficha(tablero, IA))
    salidas_humano = len(obtener_movimientos_ficha(tablero, HUMANO))

    # CASO BASE: Si llegamos a la profundidad límite o alguien pierde, devolvemos la nota
    if profundidad == profundidadMaxima or salidas_ia == 0 or salidas_humano == 0:
        # De normal devolvemos (mejor_jugada, nota), pero como aquí ya no movemos más,
        # devolvemos None en la jugada y la nota actual del tablero
        return None, puntuacion(tablero)

    # Calculamos todas las jugadas posibles del jugador actual
    posibles = jugadas_posibles(tablero, maximizador)

    # Turno de la IA (Maximizador: busca la nota más alta)a
    if maximizador:
        # Empezamos con la peor puntuación posible para la IA
        maximo = -math.inf
        # Cogemos la primera jugada en caso de que haya jugadas
        mejor_jugada = posibles[0] if posibles else None

        # Recorremos todas las jugadas posibles de la IA
        for jugada in posibles:
            # Copiamos el tablero
            copia_tablero = copy.deepcopy(tablero)
            # Aplicamos la jugada actual en el tablero de copia
            aplicar(jugada, copia_tablero, True)

            # Bajamos un nivel (profundidad + 1) cambiando el turno al humano (False)
            # Ponemos [1] al final porque solo queremos recoger la 'nota' que nos devuelva
            nota = minimax(profundidad + 1, copia_tablero, False, profundidadMaxima, alpha, beta)[1]

            # Si la nota calculada es mayor que el maximo actual, guardamos esta nota como el maximo y esta jugada como la mejor
            if nota > maximo:
                maximo = nota
                mejor_jugada = jugada

            # Alpha guarda la mejor nota que la IA ya tiene asegurada en este camino (osea lo peor que nos pueda dar el humano)
            alpha = max(alpha, nota)
            # Si lo que la IA tiene asegurado (alpha) es mayor o igual que lo que el humano
            # va a permitir en otra rama (beta), dejamos de buscar porque el humano no dejará llegar aquí
            if alpha >= beta:
                podas_alfa_beta += 1
                break  # Poda Beta: cortamos el bucle para ahorrar tiempo

        return mejor_jugada, maximo

    # Turno del Humano (Minimizador: busca el valor más bajo para fastidiar a la IA)
    else:
        # Empezamos con la peor puntuación posible para el humano (+infinito, que sería que gane la IA)
        minimo = math.inf
        # Cogemos la primera jugada en caso de que haya jugadas
        mejor_jugada = posibles[0] if posibles else None

        # Recorremos todas las jugadas posibles del humano
        for jugada in posibles:
            # Copiamos el tablero
            copia_tablero = copy.deepcopy(tablero)
            # Aplicamos la jugada actual en el tablero de copia (False porque mueve el humano)
            aplicar(jugada, copia_tablero, False)

            # Bajamos un nivel (profundidad + 1) cambiando el turno a la IA (True)
            # Ponemos [1] al final porque solo queremos recoger la 'nota' que nos devuelva
            nota = minimax(profundidad + 1, copia_tablero, True, profundidadMaxima, alpha, beta)[1]

            # Si la nota calculada es menor que el minimo actual, guardamos esta nota como el minimo y esta jugada como la mejor
            if nota < minimo:
                minimo = nota
                mejor_jugada = jugada

            # Beta guarda la nota más baja a la que el humano ya se ha asegurado poder forzar a la IA en este camino
            beta = min(beta, nota)
            # Si lo que la IA tiene asegurado (alpha) es mayor o igual que lo que el humano
            # va a permitir en otra rama (beta), dejamos de buscar porque el humano no dejará llegar aquí
            if alpha >= beta:
                podas_alfa_beta += 1
                break  # Poda Alfa: dejamos de mirar más jugadas en esta rama

        return mejor_jugada, minimo


# =====================================================================
# 3. INTERFAZ GRÁFICA EN PYGAME (GENERADA POR IA)
# =====================================================================

class JuegoIsolaPygame:
    """Interfaz volcánica con sprites. Las reglas y Minimax se mantienen."""

    OSCURO = (18, 12, 17)
    PANEL = (32, 20, 22)
    TEXTO = (255, 234, 211)
    MUTED = (190, 165, 151)
    AZUL = (51, 167, 255)
    NARANJA = (255, 121, 28)
    FUEGO = (255, 183, 63)

    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("EL SUELO ES LAVA | Minimax con poda alfa-beta")
        self.reloj = pygame.time.Clock()
        self.fuente_titulo = pygame.font.SysFont("dejavusans", 22, bold=True)
        self.fuente_texto = pygame.font.SysFont("dejavusans", 15)
        self.fuente_fuerte = pygame.font.SysFont("dejavusans", 15, bold=True)
        self.fuente_chica = pygame.font.SysFont("dejavusans", 12)
        self.fuente_numero = pygame.font.SysFont("dejavusans", 25, bold=True)
        self.profundidad_maxima = 3
        self.btn_reiniciar = pygame.Rect(638, 633, 202, 62)
        self.btn_dificultad = pygame.Rect(855, 633, 202, 62)
        self.imagenes = {}
        self.cargar_sprites()
        self.reiniciar_juego()

    def cargar_sprites(self):
        ruta = Path(__file__).resolve().parent / "assets"
        tamanos = {
            "tile_empty": (78, 78), "tile_human_blocked": (78, 78),
            "tile_ai_blocked": (78, 78), "tile_lava": (78, 78),
            "highlight_human": (78, 78), "highlight_ai": (78, 78),
            "player_blue": (63, 83), "player_orange": (63, 83),
            "button_idle": (202, 62), "button_hover": (202, 62),
            "button_pressed": (202, 62), "button_disabled": (202, 62),
            "logo": (377, 154), "scene": (1100, 760), "torch": (80, 145),
        }
        for nombre, tam in tamanos.items():
            archivo = ruta / (nombre + ".png")
            try:
                imagen = pygame.image.load(str(archivo)).convert_alpha()
                self.imagenes[nombre] = pygame.transform.smoothscale(imagen, tam)
            except (FileNotFoundError, pygame.error):
                self.imagenes[nombre] = None

    def imagen(self, nombre, rect):
        recurso = self.imagenes.get(nombre)
        if recurso is None:
            return False
        if isinstance(rect, pygame.Rect):
            pos = rect.topleft
        else:
            pos = rect
        self.pantalla.blit(recurso, pos)
        return True

    def texto(self, mensaje, x, y, fuente=None, color=None):
        imagen = (fuente or self.fuente_texto).render(str(mensaje), True, color or self.TEXTO)
        self.pantalla.blit(imagen, (x, y))

    def texto_centrado(self, mensaje, rect, fuente=None, color=None):
        img = (fuente or self.fuente_fuerte).render(str(mensaje), True, color or self.TEXTO)
        self.pantalla.blit(img, img.get_rect(center=rect.center))

    def caja(self, rect, radio=15, alpha=228):
        capa = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(capa, (*self.PANEL, alpha), capa.get_rect(), border_radius=radio)
        pygame.draw.rect(capa, (147, 73, 36, 200), capa.get_rect(), 2, border_radius=radio)
        self.pantalla.blit(capa, rect.topleft)

    def boton(self, rect, texto):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        sprite = "button_hover" if hover else "button_idle"
        if not self.imagen(sprite, rect):
            pygame.draw.rect(self.pantalla, (137, 60, 26) if hover else (81, 42, 29), rect, border_radius=13)
            pygame.draw.rect(self.pantalla, self.FUEGO, rect, width=2, border_radius=13)
        self.texto_centrado(texto, rect, self.fuente_fuerte)

    def reiniciar_juego(self):
        global nodos_explorados, podas_alfa_beta
        self.tablero = crear_tablero()
        self.fase = "HUMANO_MOVER"
        self.ganador = None
        self.ultimo_score_ia = 0
        # Este diccionario es solo visual: las reglas siguen usando DESTRUIDA = -1.
        self.bloqueadas_por = {}
        self.ultima_bloqueada = None
        self.turnos_ia = 0
        self.turnos_humano = 0
        nodos_explorados = 0
        podas_alfa_beta = 0

    def obtener_celda_raton(self, pos_raton):
        x, y = pos_raton
        if (MARGEN_X <= x < MARGEN_X + TAMAÑO_TABLERO * TAM_CELDA and
                MARGEN_Y <= y < MARGEN_Y + TAMAÑO_TABLERO * TAM_CELDA):
            return ((y - MARGEN_Y) // TAM_CELDA, (x - MARGEN_X) // TAM_CELDA)
        return None

    def comprobar_fin_partida(self):
        if len(obtener_movimientos_ficha(self.tablero, HUMANO)) == 0:
            self.fase = "FIN"
            self.ganador = "IA (CPU)"
            return True
        if len(obtener_movimientos_ficha(self.tablero, IA)) == 0:
            self.fase = "FIN"
            self.ganador = "HUMANO"
            return True
        return False

    def dibujar_fondo(self):
        self.pantalla.fill(self.OSCURO)
        if self.imagenes.get("scene"):
            self.imagen("scene", (0, 0))
            capa = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
            capa.fill((12, 8, 15, 186))
            self.pantalla.blit(capa, (0, 0))
        pygame.draw.line(self.pantalla, (239, 83, 21), (42, 174), (1060, 174), 2)
        self.imagen("logo", (40, 9))
        self.texto("JUEGO DE ESTRATEGIA  /  MINIMAX + ALFA-BETA", 602, 94, self.fuente_fuerte, self.FUEGO)
        self.texto("Muévete, destruye una plataforma y deja atrapado al rival.", 604, 126, self.fuente_chica)

    def dibujar_tablero(self):
        self.caja(pygame.Rect(48, 181, 531, 523), alpha=244)
        validas = set(obtener_movimientos_ficha(self.tablero, HUMANO)) if self.fase == "HUMANO_MOVER" else set()
        hover = self.obtener_celda_raton(pygame.mouse.get_pos())
        for f in range(TAMAÑO_TABLERO):
            for c in range(TAMAÑO_TABLERO):
                pos = (f, c)
                r = pygame.Rect(MARGEN_X + c * TAM_CELDA + 2, MARGEN_Y + f * TAM_CELDA + 2, 78, 78)
                estado = self.tablero[f][c]
                if estado == DESTRUIDA:
                    autor = self.bloqueadas_por.get(pos)
                    clave = "tile_human_blocked" if autor == HUMANO else "tile_ai_blocked" if autor == IA else "tile_lava"
                else:
                    clave = "tile_empty"
                if not self.imagen(clave, r):
                    color = (25, 76, 137) if estado == DESTRUIDA and self.bloqueadas_por.get(pos) == HUMANO else (149, 63, 29) if estado == DESTRUIDA else (70, 62, 63)
                    pygame.draw.rect(self.pantalla, color, r, border_radius=12)
                if pos == hover and ((pos in validas) or (self.fase == "HUMANO_DESTRUIR" and estado == VACIA)):
                    res = pygame.Surface(r.size, pygame.SRCALPHA)
                    pygame.draw.rect(res, (253, 195, 63, 75), res.get_rect(), 5, border_radius=12)
                    self.pantalla.blit(res, r.topleft)
                if pos in validas:
                    pygame.draw.circle(self.pantalla, self.FUEGO, r.center, 6)
                    pygame.draw.circle(self.pantalla, (255, 245, 200), r.center, 3)
                if estado in (HUMANO, IA):
                    recurso = "player_blue" if estado == HUMANO else "player_orange"
                    if not self.imagen(recurso, (r.centerx - 31, r.y - 7)):
                        pygame.draw.circle(self.pantalla, self.AZUL if estado == HUMANO else self.NARANJA, r.center, 27)
                if estado == DESTRUIDA and pos == self.ultima_bloqueada:
                    pygame.draw.circle(self.pantalla, (255, 250, 235), (r.right - 10, r.top + 11), 5)
                    pygame.draw.circle(self.pantalla, self.OSCURO, (r.right - 10, r.top + 11), 2)

    def dibujar_panel(self):
        self.caja(pygame.Rect(609, 181, 451, 523), alpha=238)
        self.texto("ESTADO DE LA PARTIDA", 635, 199, self.fuente_fuerte, self.FUEGO)
        if self.fase == "HUMANO_MOVER":
            titulo, ayuda, col = "TU TURNO · MOVER", "Haz clic en una plataforma cercana.", self.AZUL
        elif self.fase == "HUMANO_DESTRUIR":
            titulo, ayuda, col = "TU TURNO · BLOQUEAR", "Destruye cualquier casilla libre.", self.AZUL
        elif self.fase == "TURNO_IA":
            titulo, ayuda, col = "LA IA ESTÁ JUGANDO", "Evaluando sus posibles movimientos...", self.NARANJA
        else:
            titulo, ayuda, col = "PARTIDA TERMINADA", "Ganador: " + str(self.ganador), self.FUEGO
        pygame.draw.circle(self.pantalla, col, (646, 248), 6)
        self.texto(titulo, 665, 237, self.fuente_titulo)
        self.texto(ayuda, 638, 276, self.fuente_chica, self.MUTED)
        pygame.draw.line(self.pantalla, (128, 77, 55), (632, 304), (1034, 304), 1)

        self.texto("PLATAFORMAS DESTRUIDAS", 635, 320, self.fuente_fuerte, self.FUEGO)
        self.imagen("tile_human_blocked", (640, 353))
        self.imagen("tile_ai_blocked", (839, 353))
        # Los indicadores del panel tienen tamaño fijo aunque el sprite nativo sea grande.
        self.texto("TÚ", 719, 368, self.fuente_fuerte, self.AZUL)
        self.texto("IA", 919, 368, self.fuente_fuerte, self.NARANJA)
        humano = sum(v == HUMANO for v in self.bloqueadas_por.values())
        ia = sum(v == IA for v in self.bloqueadas_por.values())
        self.texto(str(humano) + " bloqueadas", 719, 389, self.fuente_chica)
        self.texto(str(ia) + " bloqueadas", 919, 389, self.fuente_chica)
        pygame.draw.line(self.pantalla, (128, 77, 55), (632, 453), (1034, 453), 1)
        self.texto("TELEMETRÍA DE MINIMAX", 635, 471, self.fuente_fuerte, self.FUEGO)
        estadisticas = [
            ("Profundidad", str(self.profundidad_maxima)),
            ("Valor heurístico h(x)", f"{self.ultimo_score_ia:.1f}"),
            ("Nodos explorados", str(nodos_explorados)),
            ("Podas alfa-beta", str(podas_alfa_beta)),
            ("Movimientos (tú / IA)", f"{len(obtener_movimientos_ficha(self.tablero, HUMANO))} / {len(obtener_movimientos_ficha(self.tablero, IA))}"),
        ]
        for i, (etiqueta, dato) in enumerate(estadisticas):
            y = 500 + i * 24
            self.texto(etiqueta, 638, y, self.fuente_chica, self.MUTED)
            numero = self.fuente_fuerte.render(dato, True, self.TEXTO)
            self.pantalla.blit(numero, (1034 - numero.get_width(), y - 2))
        self.boton(self.btn_reiniciar, "NUEVA PARTIDA")
        self.boton(self.btn_dificultad, f"PROFUNDIDAD {self.profundidad_maxima}")

    def dibujar(self):
        self.dibujar_fondo()
        self.dibujar_tablero()
        self.dibujar_panel()
        self.texto("AZUL: tus bloqueos", 68, 721, self.fuente_chica, self.AZUL)
        self.texto("NARANJA: bloqueos IA", 272, 721, self.fuente_chica, self.NARANJA)
        self.texto("El punto blanco señala el último bloqueo.", 633, 721, self.fuente_chica, self.MUTED)
        pygame.display.flip()

    def ejecutar(self):
        global nodos_explorados, podas_alfa_beta
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    pos = evento.pos
                    if self.btn_reiniciar.collidepoint(pos):
                        self.reiniciar_juego()
                        continue
                    if self.btn_dificultad.collidepoint(pos) and self.fase != "TURNO_IA":
                        self.profundidad_maxima = 2 if self.profundidad_maxima == 4 else self.profundidad_maxima + 1
                        continue
                    celda = self.obtener_celda_raton(pos)
                    if celda:
                        f, c = celda
                        if self.fase == "HUMANO_MOVER":
                            if (f, c) in obtener_movimientos_ficha(self.tablero, HUMANO):
                                pos_ant = buscar_jugador(self.tablero, HUMANO)
                                self.tablero[pos_ant[0]][pos_ant[1]] = VACIA
                                self.tablero[f][c] = HUMANO
                                self.fase = "HUMANO_DESTRUIR"
                        elif self.fase == "HUMANO_DESTRUIR":
                            if self.tablero[f][c] == VACIA:
                                self.tablero[f][c] = DESTRUIDA
                                self.bloqueadas_por[(f, c)] = HUMANO
                                self.ultima_bloqueada = (f, c)
                                self.turnos_humano += 1
                                if not self.comprobar_fin_partida():
                                    self.fase = "TURNO_IA"
            self.dibujar()
            if self.fase == "TURNO_IA":
                pygame.time.delay(250)
                nodos_explorados = 0
                podas_alfa_beta = 0
                mejor_jugada, valor_minimax = minimax(
                    0, self.tablero, True, self.profundidad_maxima, -math.inf, math.inf
                )
                if mejor_jugada:
                    aplicar(mejor_jugada, self.tablero, True)
                    destruir = mejor_jugada[1]
                    self.bloqueadas_por[destruir] = IA
                    self.ultima_bloqueada = destruir
                    self.turnos_ia += 1
                    self.ultimo_score_ia = valor_minimax
                if not self.comprobar_fin_partida():
                    self.fase = "HUMANO_MOVER"
            self.reloj.tick(30)


if __name__ == "__main__":
    juego = JuegoIsolaPygame()
    juego.ejecutar()