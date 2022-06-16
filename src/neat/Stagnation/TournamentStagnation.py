class TournamentStagnation(object):
    """
    This class is used as a drop-in replacement for the default species stagnation scheme.

    A species is only marked as stagnant if the user has not selected one of its output images
    within the last `max_stagnation` generations.
    """

    def __init__(self, config, reporters):
        self.max_stagnation = int(config.get('max_stagnation'))
        self.reporters = reporters

    @classmethod
    def parse_config(cls, param_dict):
        config = {'max_stagnation': 15}
        config.update(param_dict)

        return config

    @classmethod
    def write_config(cls, f, config):
        f.write('max_stagnation       = {}\n'.format(config['max_stagnation']))

    def update(self, species_set, generation):
        result = []
        for s in species_set.species.values():
            # If any member of the species is selected (i.e., has a fitness above zero),
            # mark the species as improved.
            for m in s.members.values():
                if m.fitness > 0:
                    s.last_improved = generation
                    break

            stagnant_time = generation - s.last_improved
            is_stagnant = stagnant_time >= self.max_stagnation
            result.append((s.key, s, is_stagnant))

        return result

