import yaml
from notion_client import Client
from typing import List

from libraries.SharedUtilities import getFullTable

pages = {
    'tasks': '2863fbf082e94879a2dfedb8ab5a3e3e',
    'projects': '5c2922d29ffa4d65bf38c2ee6e98f6b5',
    'location': '215e4262ca804a47b237f7d631cbeec5',
    'routines': '893c600045fa4fc99c93a79bb3e3fcbe',
    'abilities': '69b882d0526441969dc0c9df226bdc84',
    'objectives': 'f2dd0ba8c5f24e198ae0e1e0b6c9a250',
    'notes': '076251a22f6c4c5ba58db453c75cef01',
    'results': '11c9a6e53a9745d1a268a11a4f23039d',
    'calendar': '5d278fb56d6c4384b49533a3fa9369c9'
}

class ObjectivesNode:
    @staticmethod
    def _generate_id_key(id_string):
        return 'id' + id_string.replace('-', '')

    def __init__(self, objective):
        self.name = objective['properties']['Name']['title'][0]['text']['content']
        self.id = ObjectivesNode._generate_id_key(objective['id'])
        if objective['icon'] and objective['icon']['type'] == 'emoji':
            self.icon = objective['icon']['emoji']
        else:
            self.icon = None
        if 'Link' in objective['properties']:
            self.link = objective['properties']['Link']['url']
        else:
            self.link = None

    def addChildren(self, children_list):
        self.children = children_list

    def addParents(self, parents_list):
        self.parents = parents_list


class mermaidDiagram:
    def __init__(self, nodes_list: List[ObjectivesNode]):
        self.nodes = []
        for node in nodes_list:
            classDef = ':::clickable' if node.link != None else ''
            self.nodes.append(f'{node.id}["{node.icon} {node.name}"]{classDef}')
            if node.link != None:
                self.nodes.append(f'click {node.id} "{node.link}"')
        self.edges = []
        for node in nodes_list:
            for child_node in node.children:
                self.edges.append(f'{node.id} ---> {child_node.id}')
        self.source = "\n\t".join(['graph LR','classDef clickable fill:#33A5FF;'] + self.nodes + self.edges)

def print_tree_diagram(page_id,parent_field_name,child_field_name,output_name):
    with open('../secrets/secrets.yml', 'r') as stream:
        config = yaml.safe_load(stream)
    notion = Client(auth=config['PersonalToken'])
    data = getFullTable(notion, page_id)
    objectives_diagram_dict = {}
    def evaluateNode(node):
        return objectives_diagram_dict[ObjectivesNode._generate_id_key(node['id'])]
    for objective in data: # Create all nodes and map them to an id
        objectives_diagram_dict[ObjectivesNode._generate_id_key(objective['id'])] = ObjectivesNode(objective)
    for objective in data: # Map Relations
        children = objective['properties'][child_field_name]['relation']
        parents = objective['properties'][parent_field_name]['relation']

        objectives_diagram_dict[ObjectivesNode._generate_id_key(objective['id'])].addChildren(map(evaluateNode, children))
        objectives_diagram_dict[ObjectivesNode._generate_id_key(objective['id'])].addParents(map(evaluateNode, parents))

    diagram = mermaidDiagram(list(objectives_diagram_dict.values()))
    with open(f'diagram/diagram{output_name}.txt', 'wt') as mermaidDiagramFile:
        mermaidDiagramFile.write(diagram.source)
    with open(f'diagram/diagramView{output_name}.html', 'wt') as mermaidDiagramFile:
        mermaidDiagramFile.write(f'<html><body>'
                                 f'<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
                                 f'<script>mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});</script><div class="mermaid">'
                                 f'{diagram.source}'
                                 f'</div></body></html>')

    print(diagram.source)

#config Vars
page_id = pages['projects']
parent_field_name = 'Parent Projects'
child_field_name = 'Subprojects'
output_name = 'projects'
print_tree_diagram(page_id, parent_field_name, child_field_name, output_name)