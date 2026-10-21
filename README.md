# El Suelo es Lava — IA con Minimax y Poda Alfa-Beta

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green?style=for-the-badge&logo=python&logoColor=white)
![Algoritmo](https://img.shields.io/badge/IA-Minimax%20%2B%20Poda%20%CE%B1--%CE%B2-orange?style=for-the-badge)
![Curso](https://img.shields.io/badge/Especializaci%C3%B3n-IA%20y%20Big%20Data-purple?style=for-the-badge)

Implementación en Python y Pygame del juego de estrategia abstracta **Isola** (*"El Suelo es Lava"*), desarrollado para el módulo de **Programación de Inteligencia Artificial (PIA)** del Curso de Especialización en Inteligencia Artificial y Big Data.

El proyecto enfrenta a un jugador humano contra un agente inteligente capaz de tomar decisiones óptimas en tiempo real explorando el árbol de juegos mediante el algoritmo **Minimax con Poda Alfa-Beta ($\alpha-\beta$)**.

---

## ¿En qué consiste el juego?

Se juega en un tablero cuadriculado de **6x6** donde el **Humano (Azul)** y la **IA (Naranja)** comienzan en extremos opuestos. 

En cada turno, el jugador activo debe realizar **dos acciones obligatorias y consecutivas**:
1. **Mover su ficha** una casilla en cualquier dirección (horizontal, vertical o diagonal, como el Rey en el ajedrez) hacia una casilla vacía.
2. **Destruir (quemar) una casilla vacía** del tablero, convirtiéndola en lava para que ningún jugador pueda volver a pisarla en el resto de la partida.

**Condición de victoria:** Pierde el primer jugador que se quede completamente rodeado (por lava o bordes del tablero) y no tenga movimientos válidos al inicio de su turno.

---

## Fundamentación Teórica e Inteligencia Artificial

### 1. Clasificación del entorno (Teoría de Juegos)
* **Secuencial:** Los jugadores actúan por turnos alternos.
* **Información perfecta:** Ambos jugadores conocen el estado completo del tablero en todo momento, sin elementos ocultos ni azar.
* **Suma cero:** La ganancia de un jugador equivale exactamente a la pérdida de opciones del rival ($+1000$ vs $-1000$).
* **Simétrico:** Ambos jugadores disponen de las mismas reglas y condiciones de victoria.

### 2. Representación de Estados y Poda de Dominio
* **Matriz de estado (`6x6`):** Cada celda toma valores enteros: `0` (Vacía), `1` (Humano), `2` (IA) y `-1` (Destruida/Lava).
* **Optimización del factor de ramificación:** En lugar de evaluar quemar cualquiera de las casillas vacías lejanas (que no aportan ventaja táctica), la función `jugadas_posibles()` filtra las casillas destruibles a un radio de **distancia $\le 2$ respecto al rival**, reduciendo drásticamente el ancho del árbol y acelerando la respuesta de la IA.

### 3. Función Heurística $h(x)$
Cuando el algoritmo alcanza el límite de profundidad (`profundidadMaxima`), evalúa la calidad del tablero mediante una heurística de movilidad:

$$h(x) = \text{Movimientos Libres}_{\text{IA}} - \text{Movimientos Libres}_{\text{Humano}}$$

* **Estados terminales:**
  * Si $\text{Movimientos}_{\text{Humano}} = 0 \implies h(x) = +1000$ *(Victoria de la IA)*.
  * Si $\text{Movimientos}_{\text{IA}} = 0 \implies h(x) = -1000$ *(Victoria del Humano)*.
* **Estados intermedios:** Premia las configuraciones donde la IA conserva muchas salidas alrededor mientras asfixia el espacio disponible del jugador humano.

### 4. Algoritmo Minimax con Poda Alfa-Beta ($\alpha-\beta$)
El motor de decisión construye un árbol recursivo mediante copias profundas del estado (`copy.deepcopy`):
* **Nivel MAX (`maximizador = True`):** Turno de la IA. Busca maximizar la nota del tablero. Actualiza el valor de $\alpha$ (mejor puntuación mínima garantizada para la IA).
* **Nivel MIN (`maximizador = False`):** Turno simulado del Humano. Asume que el rival jugará de forma óptima buscando minimizar la puntuación de la IA. Actualiza el valor de $\beta$ (peor castigo garantizado por el humano).
* **Condición de poda (`alpha >= beta`):** Si en cualquier nodo se cumple que $\alpha \ge \beta$, se interrumpe la exploración de los hermanos restantes (`break`), ahorrando miles de evaluaciones innecesarias.

---

## Interfaz Gráfica y Telemetría en Vivo

La interfaz construida en **Pygame** incluye un panel lateral que muestra en tiempo real el trabajo interno del algoritmo en cada turno:
* **Indicador de fase:** Guía paso a paso al jugador (Paso 1: Mover ficha / Paso 2: Quemar casilla) e ilumina en verde las casillas válidas.
* **Profundidad máxima configurable:** Permite alternar la profundidad del árbol en caliente (niveles 2, 3 y 4) para observar la diferencia de dificultad y coste computacional.
* **Contador de nodos y podas:** Muestra cuántos nodos (`nodos_explorados`) ha visitado la IA en su último turno y cuántas ramas ha descartado gracias a la poda $\alpha-\beta$ (`podas_alfa_beta`).

---
