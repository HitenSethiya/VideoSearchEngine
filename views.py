from flask import Flask, request, render_template
from pymongo import MongoClient
from py2neo import Graph
#from flask.ext.mysql import MySQL
import MySQLdb
app = Flask(__name__)
url = 'http://localhost:7474'
username = 'neo4j'
password = 'hello'
graph = Graph(url + '/db/data/', username=username, password=password)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'mysqlpass'
# app.config['MYSQL_DATABASE_DB'] = 'logs'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)
def get_matching_tags_videos(video_id):
    query = '''
    match p=(n1)-[r:`Matching Description`]->(n2)<-[s:`Matching Tags`]-(n1) where n1.name='{video_id}' return  n2.name Order by r.weightage limit(3)

    '''

    return list(graph.run(query,{'video_id':video_id}))


def get_matching_desc_videos(video_id):
    query = '''
    match p=(n1)-[r:`Matching Description`]->(n2)<-[s:`Matching Tags`]-(n1) where n1.name='{video_id}' return  n2.name Order by s.weightage limit(3)
    '''

    return list(graph.run(query,{'video_id':video_id}))


def get_matching_channel_videos(video_id):
    query = '''
    match p=(n1)-[r:`Same Channel`]->(n2) where n1.name='{video_id}' return n2.name Order by n2.viewCount limit(4)
    '''

    return list(graph.run(query,{'video_id':video_id}))




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():

    query = request.form['search_query']
    data_client = MongoClient()
    database = data_client.Hojabc
    videos = database.videos
    search_results = list(videos.find({"videoInfo.snippet.description": {'$regex': str(query)}}).limit(5))
    titles = []
    thumbnails = []
    for result in search_results:
        thumbnails.append(result['videoInfo']['snippet']['thumbnails']['default']['url'])

    for result in search_results:
        titles.append([result['videoInfo']['id'], result['videoInfo']['snippet']['localized']['title']])

    return render_template('search.html', data=titles, thumb=thumbnails)


@app.route('/<video_id>')
def video(video_id):
    data_client = MongoClient()
    database = data_client.Hojabc
    videos = database.videos
    active_video = list(videos.find({"videoInfo.id": {'$regex': str(video_id)}}))
    titl = ''
    thum = ''
    for vid in active_video:
        titl = vid['videoInfo']['snippet']['localized']['title']
        thum = vid['videoInfo']['snippet']['thumbnails']['default']['url']
    print(titl)
    rel_videos_a = list(get_matching_channel_videos(video_id))
    rel_videos_b = list(get_matching_desc_videos(video_id))
    rel_videos_c = list(get_matching_tags_videos(video_id))
    titles1 = []
    for result in rel_videos_a:
        titles1.append([result['videoInfo']['id'], result['videoInfo']['snippet']['localized']['title']])
    for result in rel_videos_a:
        titles1.append([result['videoInfo']['id'], result['videoInfo']['snippet']['localized']['title']])
    for result in rel_videos_a:
        titles1.append([result['videoInfo']['id'], result['videoInfo']['snippet']['localized']['title']])

    print(titles1)
    return render_template('play_video.html', video_thumb=thum,
                           video=video_id, video_title=titl, related_channel=rel_videos_a,
                           related_desc=rel_videos_b, related_tags=rel_videos_c)


if __name__ == '__main__':
    app.run(debug=True)
