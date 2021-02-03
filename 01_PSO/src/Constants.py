# ---PARTICLE consts
MAX_POS = 10             # Maximum value of the position for both X and Y throughout the whole simulation
MIN_POS = -10            # Minimum value of the position for both X and Y throughout the whole simulation
MAX_VEL = 1             # Maximum value of the velocity for both X and Y for the initialization
MIN_VEL = -1            # Minimum value of the velocity for both X and Y for the initialization
SPEED = 0.1
W = 0.4                 # Factor for the current velocity (> means exploitation, < means exploration)
C1 = 2                  # Factor for the cognitive velocity (>C2 means exploitation, <C2 means exploration)
C2 = 2                  # Factor for the cognitive velocity (>C1 means exploration, <C1 means exploitation)

# ---PSO consts
N_SWARMS = 4            # Number of swarms used in the simulation
N_PARTICLES = 5        # Number of particles used for the simulation
N_ITERATIONS = 150      # Number of iterations used for the PSO
DIMENSION = 2           # Number of dimensions used for the benchmark function

# -- Viz
grid_granularity = 100
precision = 4


