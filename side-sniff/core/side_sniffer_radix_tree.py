import logging
import json


class RadixTreeNode:
    def __init__(self):
        self.children = {}
        self.rules = []


class RadixTreeProtocolFilter:
    """
    Radix Tree per filtrare pacchetti in base al protocollo
    (es. Modbus TCP -> TCP port 502).
    """

    def __init__(self):
        self.root = RadixTreeNode()

    def insert(self, key: str, protocol_info: dict):
        current = self.root
        for char in key:
            if char not in current.children:
                current.children[char] = RadixTreeNode()
            current = current.children[char]
        current.rules.append(protocol_info)
        logging.debug(f"Regola inserita: {key} -> {protocol_info}")

    def search(self, key: str):
        current = self.root
        for char in key:
            if char not in current.children:
                return []  # Nessuna corrispondenza
            current = current.children[char]
        return current.rules

    def display(self, node=None, prefix=""):
        if node is None:
            node = self.root
        if node.rules:
            print(f"Prefisso: {prefix}, Protocol Info: {node.rules}")
        for char, child in node.children.items():
            self.display(child, prefix + char)

    def load_from_json(self, filepath: str):
        """
        Carica regole dal file JSON e le inserisce nel Radix Tree.
        JSON: lista di dict { "layer": "TCP", "port": 502, "protocol": "modbus" }
        """
        with open(filepath, "r") as f:
            rules = json.load(f)

        for r in rules:
            key = f"{r['layer']}-{r['port']}"
            self.insert(key, {"protocol": r["protocol"]})
        logging.info(f"{len(rules)} regole caricate dal file JSON.")
