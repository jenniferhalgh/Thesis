import json
from pprint import pprint
from scalpel.call_graph.pycg import CallGraphGenerator, formats

cg_generator = CallGraphGenerator(["repomanager/file1.py"], "repomanager")
cg_generator.analyze()
cg = cg_generator.output()
print(cg)

edges = cg_generator.output_edges()
edges