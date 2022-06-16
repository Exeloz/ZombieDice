import copy
import neat
from neat.graphs import required_for_output

class PrunedGenome(neat.DefaultGenome):
    def get_pruned_copy(self, genome_config):
        used_node_genes, used_connection_genes = (
            PrunedGenome.get_pruned_genes(self.nodes, self.connections,
                                            genome_config.input_keys, genome_config.output_keys))
        new_genome = neat.DefaultGenome(None)
        new_genome.nodes = used_node_genes
        new_genome.connections = used_connection_genes
        return new_genome

    @staticmethod
    def get_pruned_genes(node_genes, connection_genes, input_keys, output_keys):
        used_nodes = required_for_output(input_keys, output_keys, connection_genes)
        used_pins = used_nodes.union(input_keys)

        # Copy used nodes into a new genome.
        used_node_genes = {}
        for n in used_nodes:
            used_node_genes[n] = copy.deepcopy(node_genes[n])

        # Copy enabled and used connections into the new genome.
        used_connection_genes = {}
        for key, cg in connection_genes.items():
            in_node_id, out_node_id = key
            if cg.enabled and in_node_id in used_pins and out_node_id in used_pins:
                used_connection_genes[key] = copy.deepcopy(cg)

        return used_node_genes, used_connection_genes