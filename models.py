from py2neo import Graph, Node, Relationship
import os

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('neo4j')
password = os.environ.get('hello')
graph = Graph(url + '/db/data/', username=username, password=password)


def get_matching_desc_videos(video_id):
    query = '''
    match p=(n1)-[r:`Matching Description`]->(n2)<-[s:`Matching Tags`]-(n1) where n1.name={video_id} return  n2.name Order by s.weightage limit(3)
    '''

    return graph.run(query)

def get_matching_tags_videos(video_id):
    query = '''
    match p=(n1)-[r:`Same Channel`]->(n2) where n1.name={video_id} return n2.name Order by n2.viewCount limit(4)
    '''
    return graph.run(query)
