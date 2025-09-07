from core.side_sniffer_radix_tree import RadixTree


class RuleEngine:
    """
    Gestisce le regole per più protocolli usando una Radix Tree per ogni protocollo.
    """

    def __init__(self):
        self.trees = {}  # {protocol_name: RadixTree()}

    def register_protocol(self, protocol_name):
        if protocol_name not in self.trees:
            self.trees[protocol_name] = RadixTree()

    def add_rule(self, protocol_name, key, rule):
        if protocol_name not in self.trees:
            self.register_protocol(protocol_name)
        self.trees[protocol_name].insert(key, rule)

    def check_packet(self, protocol_name, key):
        if protocol_name not in self.trees:
            return []
        return self.trees[protocol_name].search(key)

    def display_rules(self, protocol_name):
        if protocol_name in self.trees:
            self.trees[protocol_name].display()
