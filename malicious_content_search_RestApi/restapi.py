import asyncio
import json
import os
import sys

import asyncpg
from flask_cors import CORS
import flask
from flask import request, jsonify, Response
from backend import uclookup, get_file_from_db, isApiKeyAuthorized, getStatistics
import urllib3

app = flask.Flask(__name__)
CORS(app, supports_credentials=True)
app.config["DEBUG"] = True
app.debug = True
app.config['JSON_SORT_KEYS'] = False
# loop = asyncio.get_event_loop()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
name = os.path.splitext(os.path.basename(__file__))[0]


@app.route('/iocs/api/v1/', methods=['GET'])
def getMalwareInfo():

    readme = """<pre>   
    Method: POST
    Api Key is required.
    -----------------------------
    Request Value for IOCs Query:
                Authorization: {
                    'username': Not required but any value must be set.
                    'password': apikey required
                    }
                data: {
                    "query":"c6d6f7a40112f4639357830955b149a6e39765b4ab9852ee749291cd68ce75bc",
                    # Note for query: query must be MD5,SHA1,SHA256,IP,URL or DOMAIN
                    "sources": ['VirusTotal', 'AlienVault', 'MISP', 'MalwareBazaar', 'VirusShare', 'MalShare', 'AbuseIPDB', 'THREATfox', 'VXVault', 'URLhaus', 'FEODOtracker', 'firehol']
                    # Note for sources: At least one of them must be set
                    }
    Response Value for IOCs Query:
            Success:
                    {
                        'VirusTotal': {'url': '', 'url1': '', 'data': {},
                        'AlienVault': {'url': '', 'url1': '', 'data': {},
                        'AbuseIPDB': {'url': '', 'url1': '', 'data': {},
                        'URLhaus': {'url': '', 'url1': '', 'data': {}
                    }
            Error:
                    {
                        "query_status": "Illegal_query",
                        "data": "Illegal data for query (must be MD5,SHA1,SHA256,IP,URL or DOMAIN)"
                    }
    ---------------------------------
    Request Value for IOCs Statistics:
                Authorization: {
                    'username': Not required but any value must be set.
                    'password': apikey required
                    }
                data: {
                    "interval":"1"
                    # Note for interval: For daily set 1, for weekly set 7 and for monthly set 30, default value is 1
                    }
    Response Value for IOCs Statistics:
            Success:
                    {
                        'data': {'malwares': 3366276, 'malips': 3805474, 'maldomains': 178, 'malurls': 66925, 'MalShare': 953487, 'MalwareBazaar': 410306, 'VirusShare': 1998578, 'VXVault': 3905, 'AbuseIPDB': 19066, 'FEODOtracker': 127, 'firehol': 3786281, 'THREATfox': 12225, 'URLhaus': 64607},
                        # Note for data:  First 4 values for numbers of IOCs by Types, others for numbers of IOCs by Sources
                        'types': {'url': 37, 'ipport': 9, 'ioc': 108, 'domain': 11, 'malware': 104, 'ip': 372},
                        # Note for types: Numbers of Searches by IOCs Types
                        'searches': {'125.63.101.62': 222, '167.248.133.60': 117, 'http://42.224.100.181:49573/Mozi.m': 12, 'd0ffa4c79219727d07f52377ba0a309de4f0db3a6196aa6721d02fc549a2cbe8': 3, 'https://nypu.us/canister.php': 3, 'http://112.248.1.82:46865/Mozi.m': 2, '427988b7f16152b0961e20d710f0509d': 2, 'http://34.64.139.63:8080/ga.js': 2, '1a700f845849e573ab3148daef1a3b0b': 1, '82f3607f81e018e695d15afb4038142910bbab917f90b0362b6e4a9f367734f4': 1}}
                        # Note for searches: Numbers of Most Searched IOCs
                    }
            Error:
                    {
                        "query_status": "Unexpected api error",
                        "data": "Unexpected api error"}
                    }     
                </pre>"""
    return readme


@app.route('/iocs/api/v1/', methods=['POST'])
async def getIOCsInfo():
    if request.authorization is not None:
        try:
            apikey = request.authorization.get('password')
            username = request.authorization.get('username')
            interval = 0
            query = ''
            sources = ''
            if apikey != '' and await isApiKeyAuthorized(apikey):
                data = request.json
                if data is not None:
                    try:
                        query = data['query']
                    except KeyError as ke:
                        pass
                    try:
                        sources = data['sources']
                    except KeyError as ke:
                        pass
                    try:
                        interval = data['interval']
                    except KeyError as ke:
                        pass
                    if interval is not None and int(interval) > 0:
                        if not isinstance(int(interval), int):
                            interval = 1
                        context = await getStatistics(int(interval))
                        context = json.loads(context)
                        if (type(context) == str):
                            context = json.loads(context)
                        return Response(json.dumps(context, indent=4),
                                        status=200,
                                        mimetype='application/json')
                    elif query is not None and query != '':
                        results = await uclookup(query, sources, username, apikey, flask.request.remote_addr)
                        if not results:
                            return Response('{"query_status": "Illegal_query","data": "Illegal data for query (must be '
                                            'MD5,SHA1,SHA256,IP,URL or DOMAIN)"}',
                                            status=404,
                                            mimetype='application/json')
                        else:
                            return Response(json.dumps(results, indent=4),
                                            status=200,
                                            mimetype='application/json')
                    else:
                        return Response('{"query_status": "Illegal_query",'
                                        '"data": "Illegal data for query (query must be MD5,SHA1,SHA256,IP,URL or DOMAIN)"}',
                                        status=500,
                                        mimetype='application/json')
                else:
                    return Response('{"query_status": "Illegal_query","data": "Illegal query (query must be '
                                    'MD5,SHA1,SHA256,IP,URL or DOMAIN)"}',
                                    status=500,
                                    mimetype='application/json')
            else:
                return Response('{"query_status": "Illegal_apikey", "data": "API_KEY is wrong."}', status=500,
                                mimetype='application/json')
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error = "ERROR:%s:%s:%s:" % (str(exc_type).split('\'')[1], exc_value, name) + ".py:%s" % str(
                exc_traceback.tb_lineno)
            data = '{"query_status": "Unexpected api error","data": "' + error + '"}'
            return Response(data, status=500, mimetype='application/json')
    else:
        return Response('{"query_status": "Illegal_apikey", "data": "API_KEY is required."}',
                        status=500,
                        mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)