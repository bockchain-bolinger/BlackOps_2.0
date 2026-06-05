import ast
import random
import string

class PolymorphicEngine:
    """Mutiert Python-Code durch AST-Manipulation."""
    
    def __init__(self):
        self.name_map = {}

    @staticmethod
    def _random_name(length=8):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def mutate(self, source_code):
        tree = ast.parse(source_code)
        
        # Sammle alle Funktionsnamen
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name != 'connect':
                new_name = self._random_name()
                self.name_map[node.name] = new_name
        
        # Wende Umbenennung an
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in self.name_map:
                node.name = self.name_map[node.name]
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in self.name_map:
                    node.func.id = self.name_map[node.func.id]
        
        # Mutation: Einfügen von Dummy-Variablen
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                dummy_name = self._random_name()
                dummy_value = ast.Constant(value=random.randint(1, 100))
                assign = ast.Assign(
                    targets=[ast.Name(id=dummy_name, ctx=ast.Store())],
                    value=dummy_value,
                    lineno=0  # Add lineno to avoid AttributeError in unparse
                )
                # Ensure the new node has correct context
                ast.fix_missing_locations(assign)
                node.body.insert(0, assign)
        
        return ast.unparse(tree)

if __name__ == "__main__":
    engine = PolymorphicEngine()
    original_code = """
def connect():
    print("Connecting...")
"""
    mutated = engine.mutate(original_code)
    print("--- Original ---")
    print(original_code)
    print("--- Mutated ---")
    print(mutated)
