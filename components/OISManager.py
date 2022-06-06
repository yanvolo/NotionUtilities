import yaml
from neo4j import GraphDatabase
from notion_client import Client

from libraries.SharedUtilities import loadCachedData

pages = {
    'notes': 'de64f103da6b4cdfb1ea155a5d6b9ed7',
    'references': '4bc3c2e0d9ef42038c52787f3e909c46'
}

with open('../secrets/secrets.yml', 'r') as stream:
    config = yaml.safe_load(stream)
notion = Client(auth=config['token'])
note_data = loadCachedData(notion, pages['notes'])
references_data = loadCachedData(notion, pages['references'])

neo4jDriver = GraphDatabase.driver('bolt://localhost:7687',auth=('neo4j', config['neo4jPassword']))
# First Pass, Create Nodes
node_count = 0

with neo4jDriver.session() as session:
    # for note in note_data:
    #     note_properties = note['properties']
    #     session.run(f"CREATE (n:Note:{note_properties['Note Type']['select']['name']} {{title:\"{note_properties['Name']['title'][0]['text']['content']}\",created: datetime(\"{note_properties['Created']['created_time']}\"), id: \"{note['id']}\"}})")
    #     node_count = node_count + 1
    #     print(f"Creating node #{node_count}")
    # for reference in references_data:
    #     reference_properties = reference['properties']
    #     session.run(f"CREATE (n:Reference {{url:\"{reference_properties['Link']['url']}\", id:\"{reference['id']}\"}})")
    #     node_count = node_count + 1
    #     print(f"Creating node #{node_count}")
    # # Second Pass, Create Relationships
    relation_count = 0
    for note in note_data:
        note_properties = note['properties']
        for child in note_properties['Child']['relation']:
            session.run(f"MATCH (a:Note), (b:Note)  WHERE a.id='{note['id']}' AND b.id='{child['id']}' CREATE (a)-[r:PARENT_TOPIC]->(b)")
            relation_count = relation_count + 1
            print(f"Creating Relation #{relation_count}")
    # for reference in references_data:
    #     pass
neo4jDriver.close()