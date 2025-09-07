from core.side_sniffer_radix_tree import RadixTreeProtocolFilter
from configuration.side_sniffer_configuration import BASE_DIR_RULES, RULES_FILE


protocol_tree = RadixTreeProtocolFilter()
protocol_tree.load_from_json(f"{BASE_DIR_RULES}/{RULES_FILE}")
