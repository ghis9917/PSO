import random
from typing import List

import numpy as np

from src.genetic import Crossover, Mutations
from src.genetic.Decoder import optimization_decoder
from src.genetic.Genome import Genome
from src.genetic.Population import Population
from src.optimization_function.Visualizer import Visualizer
from src.simulator.Simulator import Simulator
from src.utils.Constants import N_GENERATION, ELITISM_PERCENTAGE, SELECT_PERCENTAGE, N_INDIVIDUALS, DRAW, OPTI_FUNC, CROSSOVER_MUTATION_PERCENTAGE, VALUES_PER_AXIS, MUTATION_PROBABILITY
from src.utils.DataVisualizer import DataManager


class GeneticAlgorithm:
    """
    Author Frederic Abraham
    """

    def __init__(self, robot: bool = False):
        self.emergency_break = False
        self.display_data = dict(
            avg_fitness = dict(display_name = 'avg fitness',  value = 0, graph = True),
            best_fitness = dict(display_name = 'best fitness',  value = 0, graph = True),
            diversity = dict(display_name = 'diversity',  value = 0, graph = True),
            generation = dict(display_name = 'generation',  value = 0, graph = False),
        )

        self.data_manager: DataManager = DataManager(data_names = [
            display_name['display_name'] for display_name in list(filter(lambda ele: ele['graph'], self.display_data.values()))
        ], parallel = False, visualize=False)

        self.robot = robot
        if self.robot:
            self.sim = Simulator(display_data = self.display_data, simulation_time = 50, gui_enabled = DRAW, stop_callback = self.stop)

        self.populations: List[Population] = []
        self.history = {i: [] for i in range(0, N_GENERATION)}

        self.generation = 0
        self.avg_fitness = [-1]
        self.best_fitness = [-1]

        self.test_name = "sim"
        self.func_name = "Rosenbrock"
        self.crossover_str = "two_point_crossover"
        self.crossover_func = Crossover.two_point_crossover
        self.mutation_str = "gaussian"
        self.mutation = Mutations.gaussian
        self.title = f"Genetic Algorithm - crossover: {self.crossover_str} with {VALUES_PER_AXIS} Values per axis and {self.mutation_str} mutation with {MUTATION_PROBABILITY} probability - {self.func_name}"
        self.write_title = f"{self.test_name.replace(' ', '_')}_{self.func_name}_{self.crossover_str.replace(' ', '_')}"

    def run(self):

        population = Population()
        for generation in range(1, N_GENERATION + 1):
            if self.emergency_break:
                break

            self.generation = generation

            self.populations.append(population)

            self.evaluation(population)
            self.update_data(generation, population)

            next_population = self.selection()
            self.crossover_mutation(next_population)
            self.generate_new(next_population)

            # for i in range(5):
            #     print(next_population[-i].genes)

            population = Population(next_population)

        self.data_manager.stop()

        viz = Visualizer(OPTI_FUNC, self.history, self.title,
                      dict(
                        avg_fitness = np.log(self.data_manager.get_data("avg fitness")),
                        best_fitness = np.log(self.data_manager.get_data("best fitness")),
                        diversity = np.log(self.data_manager.get_data("diversity")),
                      ))
        print("Viz Done")
        viz.show_fig()
        viz.write_fig(self.write_title.lower())


    def evaluation(self, population: Population):
        if self.robot:
            self.robot_evaluation(population)
        else:
            self.optimisation_evaluation(population)

    def robot_evaluation(self, population):
        self.sim.set_population(population)
        self.sim.start()

    def optimisation_evaluation(self, population):
        individuals = population.individuals
        for i, individual in enumerate(individuals):
            coordinates = optimization_decoder(individual)
            altitude = OPTI_FUNC(coordinates)
            individual.set_fitness(0.00000001 if altitude == 0 else altitude)
            self.history.get(self.generation - 1).append(
                dict(
                    id=i,
                    alt=altitude,
                    best=False,
                    pos=coordinates,
                    vel=0,
                    swarm=1
                )
            )

    def selection(self) -> List[Genome]:
        next_population = []
        ordered_by_fitness = list(sorted(self.populations[-1].individuals, key=lambda genome: genome.fitness, reverse=True))
        fitness = [individual.fitness for individual in ordered_by_fitness]

        # Select first n as elite
        for i in range(1, int(N_INDIVIDUALS * ELITISM_PERCENTAGE) + 1):
            best_genome = ordered_by_fitness[-i]
            next_population.append(best_genome)

        weights = np.reciprocal(fitness)  # Invert all weights
        weights = weights / np.sum(weights)  # Normalize
        # Do roulette wheel selection
        for i in range(int(N_INDIVIDUALS * SELECT_PERCENTAGE)):
            choice = np.random.choice(ordered_by_fitness, p = weights)
            next_population.append(choice)  # Sample

        return next_population

    def crossover_mutation(self, next_population: List):
        for i in range(int(N_INDIVIDUALS * CROSSOVER_MUTATION_PERCENTAGE)):
            parent1 = random.sample(next_population, 1)[0]
            parent2 = random.sample(next_population, 1)[0]
            child = self.crossover_func(parent1, parent2)

            child = self.mutation(child)

            next_population.append(child)

    def generate_new(self, next_population):
        while len(next_population) < N_INDIVIDUALS:
            next_population.append(Genome())

    def stop(self):
        self.emergency_break = True
        self.data_manager.stop()

    def update_data(self, generation, population):
        individuals = population.individuals

        individual_fitness = [x.fitness for x in individuals]

        self.data_manager.update_time_step(generation)
        self.display_data['generation']['value'] = generation
        self.display_data['avg_fitness']['value'] = np.mean(individual_fitness)
        self.display_data['best_fitness']['value'] = np.min(individual_fitness)
        self.display_data['diversity']['value'] = np.mean(np.abs(np.diff(individual_fitness)))

        for data in self.display_data.values():
            if 'graph' in data and data['graph']:
                self.data_manager.update_value(data['display_name'], data['value'])

        self.data_manager.update()

