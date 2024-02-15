import requests
import json
from datetime import datetime
from rdflib.namespace import OWL, RDF, RDFS, SKOS
from rdflib import Graph, Literal, Namespace, URIRef
from interfaces import InterfaceAI
from langcodes import *
from WikiPandas import WikiPandas
import jwt
import hashlib
import os
import pytz

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class GraphAI():
    def __init__(self, llmapi=None, llmramapi=None, url=None, q=None, rootgraph=None, debug=False):
        self.known = {}
        self.llmramapi = None
        self.llmapi = None
        self.NS = "https://id.now.museum/"
        #self.LMRAM = "http://192.168.1.113:8010"
        self.graph = None
        self.data = None
        self.dates = {} 
        self.wikipediapage = None
        if 'LLMAPI' in os.environ:
            self.llmapi = os.environ['LLMAPI']
        if 'LLMRAMAPI' in os.environ:
            self.llmramapi = os.environ['LLMRAMAPI']
        if llmapi:
            self.llmapi = llmapi
        if llmramapi:
            self.llmramapi = llmramapi
        if self.llmramapi:
            self.interface = InterfaceAI(self.llmapi, self.llmramapi)
        self.valuestats = {}

        if rootgraph:
            self.graph = rootgraph.graph
        else:
            self.graph = Graph()

    def cleanstats(self):
        self.valuestats = {}

    def check_values(self, obj, SEPARATOR='_', FORBIDDEN='/'):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    if value: #'value' in value:
#                        print("\t %s" % value)
                        if SEPARATOR in value:
                            if not FORBIDDEN in value:
                                if value in self.valuestats:
                                    self.valuestats[value] = self.valuestats[value] + 1
                                else:
                                    self.valuestats[value] = 1
                else:
                    self.check_values(value)
        elif isinstance(obj, list):
            for item in obj:
                self.check_values(item)
        return self.valuestats

    def current_date(self):
        current_utc_datetime = datetime.utcnow()

        # Specify the desired timezone (e.g., 'America/New_York')
        desired_timezone = 'Europe/Amsterdam'

        # Convert the UTC datetime to the desired timezone
        self.dates['current_datetime_with_timezone'] = current_utc_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(desired_timezone))
        self.dates['formatted_date'] = self.dates['current_datetime_with_timezone'].strftime('%a, %d %b %Y %H:%M:%S %Z')
        return datetime.now()

    def make_cache(self, q, data, url=None, type=None):
        if not type:
            type = 'resource'
        API_ENDPOINT = "%s/llmcache/" % self.llmramapi
        jsondata = json.loads(data)
        postdata = {'data': jsondata }
        postdata['type'] = type
        md5 = str(self.generate_md5(q))
        postdata['md5'] = md5
        if url:
            postdata['url'] = url
        postdata['jwt'] = jwt.encode({q: type}, "secret", algorithm="HS256")
        postdata['type'] = type
        postdata['name'] = q
        postdata['date'] = self.current_date()
        postdata['wiki_identitifers'] = self.check_values(jsondata)
        w = WikiPandas()
        self.wikipedia_page = w.get_wikipedia_page(self.valuestats)
        print(postdata) 
        print(self.wikipedia_page)
        #if self.wikipedia_page:
        #    postdata['url'] = self.wikipedia_page

        r = requests.post(API_ENDPOINT, data = json.dumps(postdata, cls=DateTimeEncoder))
        return r.text

    def ingest_document(self, url, q):
        if q:
            self.API_url = "%s/graph?prompt=graph.prompt&inputtext=%s" % (self.llmapi, q)
            self.data = json.loads(requests.get(self.API_url).text)
            print(self.API_url)
            print(self.data)
            API_ENDPOINT = "%s/llmcache/" % self.llmramapi
            for index in self.data:
                print("index %s" % index)
                postitem = self.data[str(index)] #['data']
                postitem['url'] = url
                if 'data' in postitem:
                    print("POST %s" % postitem['data'])
                    self.build_knowledge_graph(postitem['data'], url)
                    postitem['url'] = url
                    postitem['type'] = 'relationship'
                    r = requests.post(API_ENDPOINT, data = json.dumps(postitem))
                    print(r.text)
        return

    def build_knowledge_graph(self, data, url):
        print(data)
        ex = Namespace("http://knowledgegraph.ai/")
        rel = Namespace("http://knowledgerelationship.org/")

        for relationship in data['graph']:
            concept1 = URIRef(ex[relationship["concept1"].replace(' ','_')])
            concept2 = URIRef(ex[relationship["concept2"].replace(' ','_')])
            relationship_type = rel[relationship["relationship"].replace(' ','_')]
            importance = Literal(relationship["importance"])

            self.graph.add((concept1, relationship_type, concept2))
            self.graph.add((concept1, rel["hasImportance"], importance))
            c1 = relationship["concept1"]
            c2 = relationship["concept2"]
            if not c1 in self.known:
                self.interface.translate_in_context(c1, data['source'], url)
                self.known[c1] = data['source']
            if not c2 in self.known:
                self.interface.translate_in_context(c2, data['source'], url)
                self.known[c2] = data['source']
        return self.graph

    def serialize(self, filename=None, defaultformat='turtle'):
        if filename:
            self.graph.serialize(destination=filename, format=defaultformat)
        else:
            return self.graph.serialize(format=defaultformat)

    def generate_md5(self, text):
        # Create an MD5 hash object
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        # Get the hexadecimal representation of the digest
        md5_digest = md5_hash.hexdigest()
        return md5_digest
    
        if q:
            self.API_url = "http://0.0.0.0:8008/graph?prompt=graph.prompt&inputtext=%s" % q
            self.data = json.loads(requests.get(self.API_url).text)
            print(self.API_url)
            print(self.data)
            API_ENDPOINT = "http://10.147.18.160:8010/llmcache/"
            for index in self.data:
                print("index %s" % index)
                postitem = self.data[str(index)] #['data']
                postitem['url'] = url
                if 'data' in postitem:
                    print("POST %s" % postitem['data'])
                    self.build_knowledge_graph(postitem['data'], url)
                    postitem['url'] = url
                    postitem['type'] = 'relationship'
                    r = requests.post(API_ENDPOINT, data = json.dumps(postitem))
                    print(r.text)

    def data_loader(self, page):
        url = "%s/resolver?url=%s" % (self.LMRAM, page)
        #"https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FQueen_%28band%29"
        r = requests.get(url)
        self.data = json.loads(r.text)
        return self.data

    def create_graph(self, data):
        graph = Graph()
        graph.bind('purl', URIRef('http://purl.org/'))
        predicate_uri = URIRef("http://purl.org/dc/terms/identifier")
        skos = Namespace('http://www.w3.org/2004/02/skos/core#')
        id = Namespace(self.NS)
        graph.bind('id', URIRef(self.NS))
        graph.bind('skos', skos)
        i = 0
        known = {}
        for item in data:
            i = i + 1
            if i: # < 20:
                Q = URIRef("%s%s" % (self.NS, item['md5']))
                for possiblelang in item:
                    if 'description' in possiblelang:
                        graph.add((Q, SKOS.scopeNote, Literal(item[possiblelang])))
                        graph.add((Q, RDF['type'], skos['Concept']))
                        graph.add((Q, predicate_uri, Literal("DID")))
                    else:
                        try:
                            plang = find(possiblelang)
                            #print(plang.language)
                            #print(item[possiblelang])
                            label = item[possiblelang]
                            label = label.replace('\"', '')
                            graph.add((Q, SKOS.prefLabel, Literal(label, lang=plang.language)))
                        except:
                            #print(possiblelang)
                            continue
                        #graph.add((Q, SKOS.scopeNote, Literal(q['background'])))
                #graph.add((Q, SKOS.code, Literal(i)))
                graph.bind('skos', skos)
            if self.graph:
                self.graph = graph
            else:
                self.graph = self.graph + graph
        return graph

    def data_to_graph(self, data):
        for item in data:
            if 'data' in item:
                #print(item)
                self.graph = self.rebuild_knowledge_graph(self.graph, item['data'], '')
                try:
                    self.graph = self.rebuild_knowledge_graph(self.graph, item['data'], '')
                except:
                    continue
        return self.graph
            
    def rebuild_knowledge_graph(self, graph, dataitem, url):
        DEBUG = True
        if dataitem:
            if DEBUG:
                print(dataitem['graph'])
        # Define namespaces
            ex = Namespace("http://kg.ai/")
            rel = Namespace("http://kg.ai/")
    
            for relationship in dataitem['graph']:
                print("\t\%s" % relationship)
                md5_hash_c1 = str(self.generate_md5(relationship["concept1"]))
                md5_hash_c2 = str(self.generate_md5(relationship["concept2"]))
                concept1 = URIRef(ex[relationship["concept1"].replace(' ','_').replace('%','')])
                concept2 = URIRef(ex[relationship["concept2"].replace(' ','_').replace('%s','')])
                relationship_type = rel[relationship["relationship"].replace(' ','_')]
                importance = Literal(relationship["importance"])
                Q1 = URIRef("%s%s" % (self.NS, md5_hash_c1))
                Q2 = URIRef("%s%s" % (self.NS, md5_hash_c2))
                if DEBUG:    
                    print("%s %s %s" % (md5_hash_c1, relationship_type, Literal(relationship["concept2"])))
                    print("%s %s %s" % (md5_hash_c1, relationship_type, md5_hash_c2))
                    print(Q1)
    
                if 'relat' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.related, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.related, Q2))
                elif 'narrower' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.narrower, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.narrower, Q2))
                elif 'broader' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.broader, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.broader, Q2))
                elif 'closeMatch' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.closeMatch, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.closeMatch, Q2))      
                elif 'topConceptOf' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.topConceptOf, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.topConceptOf, Q2)) 
                elif 'inScheme' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.inScheme, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.inScheme, Q2)) 
                elif 'partOf' in relationship["relationship"].lower():
                    graph.add((Q1, SKOS.topConceptOf, Literal(relationship["concept2"])))
                    graph.add((Q1, SKOS.topConceptOf, Q2))
                #topConceptOf,narrower,broader,inScheme,closeMatch,
                else:
                    graph.add((Q1, URIRef("%s" % (relationship_type)), Literal(relationship["concept2"])))
                #self.graph.add((concept1, rel["hasImportance"], importance))
            return graph       
        return graph

    def getpairs(self, d, DEBUG=False):
        resultpairs = []
        known = {}
        for idx in range(0, len(d)):
            if DEBUG:
                print(d[idx])
            for intindex in range(0, len(d)):
                pairs = {}
                if not d[idx]==d[intindex]:
                    if DEBUG:
                        print("\t%s" % d[intindex])
                    pairstring1 = "%s%s" % (d[idx], d[intindex])
                    pairstring2 = "%s%s" % (d[intindex], d[idx])
                    if not pairstring1 in known:
                        if not pairstring2 in known:
                            pairs[d[idx]] = d[intindex]
                            known[pairstring1] = 1
                            known[pairstring2] = 1
                if pairs:
                    resultpairs.append(pairs)
        return resultpairs

    def serialize_graph(self, results, outfile='/tmp/maincmme.json'):
        if results:
            columns = ["locResource", "property", "viafResource", "label", "topic"]
            nodes = {}
            links = {}
            viaf = {}
            points = []
            topics = {}
            LIMIT = 3000000
            counter = 0
            print(len(results))
            for row in results:
                #print(row)
                if counter < LIMIT:
                    counter = counter + 1
                    datapoint = {}
                    for ix in range(0,len(row)):
                        if row[ix]:
                            datapoint[columns[ix]] = str(row[ix])
                    if 'locResource' in datapoint:
                        datapoint['id'] = datapoint['locResource'].replace('http://id.loc.gov/authorities/names/no', '')
                    if 'label' in datapoint:
                        viaf[datapoint['viafResource']] = datapoint['label']
                    if 'topic' in datapoint:
                        topics[datapoint['locResource']] = datapoint['topic']
                        if datapoint['topic'] in links:
                            ids = links[datapoint['topic']]
                            ids.append(datapoint['id'])
                        else:
                            ids = [datapoint['id']]
                            links[datapoint['topic']] = ids
                        #print(datapoint)
                    points.append(datapoint)
                #print(datapoint)
                #print(f"Node: {row['node']}")
            enrichedpoints = []
            knownpoints = {}
            for item in points:
                print(item)
                if 'viafResource' in item:
                    #print(item['viafResource'])
                    if item['viafResource'] in viaf:
                        #print(viaf[item['viafResource']])
                        item['description'] = viaf[item['viafResource']]
                        item['user'] = viaf[item['viafResource']]
                    if 'locResource' in item:
                        #print(item['locResource'])
                        if item['locResource'] in topics:
                            item['topic'] = topics[item['locResource']]
                            item['description'] = topics[item['locResource']]
                #print("Enrichment %s" % item)

                if 'description' in item:
                    if 'id' in item:
                        if not item['id'] in knownpoints:
                            #if 'user' in item:
                            if item:
                                #del item['description']
                                if 'topic' in item:
                                    del item['topic']
                                item['link'] = item['viafResource']
                                del item['locResource']
                                del item['property']
                                del item['viafResource']
                                enrichedpoints.append(item) 
                                knownpoints[item['id']] = 1
            data = {}
            print(enrichedpoints)
            data['nodes'] = enrichedpoints
            #data['links'] = links
            totallinks = []
            for topic in links:
                pairs = self.getpairs(links[topic])
                #print(pairs)
                pairpoint = {}
                for pair in pairs:
                    pairpoint = {}
                    #print(list(pair.keys())[0])
                    pairpoint['source'] = list(pair.keys())[0]
                    pairpoint['target'] = list(pair.values())[0]
                    if pairpoint['source'] in knownpoints:
                        if pairpoint['target'] in knownpoints:
                            totallinks.append(pairpoint)
            data['links'] = totallinks#[0:100]
            with open(outfile, 'w') as fp:
                json.dump(data, fp)
        return

    def cmme_query(self, g):
        sparql_query = """
        PREFIX viaf: <http://viaf.org/viaf/>
        PREFIX loc: <http://id.loc.gov/authorities/names/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?locResource ?property ?viafResource ?label ?topic
        WHERE {
          {
            ?viafResource ?property ?locResource .
            FILTER(STRSTARTS(STR(?viafResource), str(viaf:)) && STRSTARTS(STR(?locResource), str(loc:)))
          }
          UNION
          {
            ?locResource ?property ?viafResource .
            FILTER(STRSTARTS(STR(?viafResource), str(viaf:)) && STRSTARTS(STR(?locResource), str(loc:)))
          }
          UNION
          {
          ?viafResource rdfs:label ?label.
          FILTER(STRSTARTS(str(?viafResource), "http://viaf.org/"))
          }
          UNION
          {
          ?locResource xsd:issued ?topic.
          FILTER(STRSTARTS(str(?locResource), "http://id.loc.gov/"))
          }
        }
        """
        # Execute the SPARQL query and print results
        results = g.query(sparql_query)

        print("All Nodes:")
        c = 0
        for row in results:
            if c < 100: 
                print(row)
                c = c + 1
        return results
