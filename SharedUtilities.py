import pickle
from os.path import exists

from neo4j import GraphDatabase


def getFullTable(client, tableID, filter=None):
    page = 0
    all_results = []
    if filter is not None:
        current_result = client.databases.query(tableID, filter=filter)
    else:
        current_result = client.databases.query(tableID)
    while current_result['has_more']: # Get and add all pages
        page = page + 1
        print(f"Loading page {page}")
        all_results.extend(current_result['results'])
        if filter:
            current_result = client.databases.query(tableID, filter=filter, start_cursor=current_result['next_cursor'])
        else:
            current_result = client.databases.query(tableID, start_cursor=current_result['next_cursor'])
    all_results.extend(current_result['results']) # Add final page
    print('Done Loading!')
    return all_results


def loadCachedData(client, tableID, filter=None):
    cache_file_path = f"data/{tableID}"
    if not exists(cache_file_path):
        data = getFullTable(client, cache_file_path, filter)
        with open(cache_file_path, 'wb') as file:
            pickle.dump(data, file)
    else:
        with open(cache_file_path, 'rb') as file:
            data = pickle.load(file)
    return data


# class Neo4JDatabase:
#     def __init__(self, uri, user, password):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))
#
#     def close(self):
#         self.driver.close()
#
#     def print_greeting(self, message):
#         with self.driver.session() as session:
#             greeting = session.write_transaction(self._create_and_return_greeting, message)
#             return greeting
#
#
#     @staticmethod
#     def _create_and_return_greeting(tx, message):
#         result = tx.run("CREATE (a:Greeting) "
#                         "SET a.message = $message "
#                         "RETURN a.message + ', from node ' + id(a)", message=message)
#         return result.single()[0]


# class PersonalNotionClient:
#     def __init__(self, token):
#         self.client = 0