import parse_ghosts
import parse_ghost_general

parser_a = parse_ghosts.Parser()
data = parser_a.extract_to_json()

parser_b = parse_ghost_general.Parser()
data = parser_b.extract_to_json()