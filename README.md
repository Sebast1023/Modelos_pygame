# Modelos_pygame

Integrantes

- Yhoan Mauricio Bermudez Tique (20242020242)

- Sebastian David Trujillo Vargas (20242020217)

- David Felipe Batanero Molina (20241020092)

# Decorator Runner (pygame)

Este proyecto es un videojuego 2D desarrollado en **Python con pygame**, cuyo objetivo es aplicar el patrón de diseño **Decorator** dentro de un entorno interactivo.

El jugador controla un personaje que puede moverse, saltar y recoger potenciadores mientras evita obstáculos.

---

##  Concepto principal

El juego implementa el patrón **Decorator**, permitiendo modificar dinámicamente las habilidades del personaje sin alterar su estructura base.

Esto se logra envolviendo el personaje con clases decoradoras que añaden comportamientos como:

* Aumento de velocidad
* Salto mejorado
* Escudo temporal

---

## Características

* Sistema de movimiento (izquierda, derecha, salto)
* Animaciones del personaje (idle, run, jump, dead)
* Sistema de vidas (HP)
* Obstáculos (hazards)
* Power-ups:

  *  Speed Boost
  *  Jump Boost
  *  Shield
* Sistema de decoradores con duración
* Fondo personalizado
* Sprites animados (personaje y obstáculos)

---

##  Controles

| Tecla           | Acción          |
| --------------- | --------------- |
| A / ←           | Mover izquierda |
| D / →           | Mover derecha   |
| W / ↑ / Espacio | Saltar          |
| ESC             | Salir del juego |

---

##  Estructura del proyecto

```
Modelos_pygame/
│
├── Decorator.py
├── ninja/              # Sprites del personaje
├── extras/             # Imagénes (power-ups)
├── background/         # Fondo del juego
└── README.md
```

---

##  Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <[url-del-repo](https://github.com/Sebast1023/Modelos_pygame.git)>
cd Modelos_pygame
```

### 2. Instalar dependencias

```bash
pip install pygame
```

### 3. Ejecutar el juego

```bash
python Decorator.py
```

---

## 🔥 Implementación del patrón Decorator

El personaje base (`SimpleCharacter`) implementa la interfaz `ICharacter`.

Los decoradores extienden la funcionalidad:

* `SpeedBoost`
* `JumpBoost`
* `Shield`

Cada decorador:

* Envuelve al personaje
* Modifica atributos específicos
* Tiene duración limitada (`TimedDecorator`)

---

## Sprites y gráficos

* Personaje con animaciones por frames
* Power-ups con imágenes personalizadas
* Fondo escalado al tamaño de la ventana

Se separa:

* **Hitbox (colisión)** → lógica del juego
* **Sprite (visual)** → apariencia

---

## Problemas resueltos durante el desarrollo

* Error de rutas de imágenes (`FileNotFoundError`)
* Desfase entre sprite y colisión
* Animación infinita al morir
* Índices fuera de rango en animaciones
* Escalado incorrecto del fondo

---

## Posibles mejoras

* Sonidos (saltos, daño, power-ups)
* Menú principal
* Sistema de reinicio
* Enemigos móviles
* Parallax en el fondo
* Sistema de puntuación persistente

