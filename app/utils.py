import re
import os
from localconfig import mappings
import wikipediaapi
import requests
import re
import json
from rdflib import Graph, URIRef, Literal, Namespace, FOAF, RDF
import hashlib
from langdetect import detect
import json
from collections import defaultdict
import nltk

def getlanguage(text):
    return detect(text)

def json_to_graph(json_ld_data, format='turtle'):
    g = Graph()
    schema = Namespace("https://schema.org/")

    # Add triples to the graph
    subject_uri = URIRef(f"urn:uuid:{json_ld_data['md5']}")
    g.add((subject_uri, RDF.type, schema[json_ld_data['type']]))

    # Process the @context and @data
    for term, value in json_ld_data["@data"].items():
        if term in json_ld_data["@context"]:
            predicate_uri = URIRef(json_ld_data["@context"][term])
            if isinstance(value, list):
                for item in value:
                    g.add((subject_uri, predicate_uri, Literal(item)))
            else:
                g.add((subject_uri, predicate_uri, Literal(value)))
    return g.serialize(format=format)

#split_into_sentences, split_into_paragraphs
def split_into_sentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

def split_into_paragraphs(text):
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)

    # Combine consecutive sentences into paragraphs
    paragraphs = []
    current_paragraph = ""

    for sentence in sentences:
        if sentence.strip():  # Skip empty lines
            current_paragraph += sentence + " "
        else:
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""

    # Add the last paragraph if not empty
    if current_paragraph:
        paragraphs.append(current_paragraph.strip())

    return paragraphs

def get_entities(inputcontent):
    nlpurl = "%s/process" % os.environ['NERAPI']
    newentities = {}
    content = ''
    if not 'original_entities' in inputcontent:
        newdata = {"text": inputcontent }
        print(newdata)
        x = requests.post(nlpurl, json = newdata)
        newentities = json.loads(x.text)
        content = inputcontent
        print(x.text)
    else:
        newentities = inputcontent
        content = ''
        if 'title' in inputcontent:
            content = inputcontent['title']
        if 'text' in inputcontent:
            content = content + inputcontent['text']

    record = defaultdict(list)
    if 'lang' in newentities:
        record['lang'] = [newentities['lang']]

    if 'entities' in newentities:
        for newitem in newentities['original_entities']:
            value = newitem['label']
            witem = newitem['entity']
            #value = 'I-PER'
            if len(witem):
                record[value].append(witem)
        record['type'] = ['entities']
    context = {}
    metadata = { 'md5': generate_md5(content), 'type': 'entities' }
    mappings = {'ORG': 'https://schema.org/parentOrganization', 'PERSON': 'https://schema.org/person', 'PER': 'https://schema.org/person', 'GPE': 'https://schema.org/location', 'lang': 'https://schema.org/language', 'LOC': 'https://schema.org/location', 'MONEY': 'https://schema.org/MonetaryAmount', 'PRODUCT': 'https://schema.org/Product', 'WORK_OF_ART': 'https://schema.org/VisualArtwork', 'DATE': 'https://schema.org/date', 'CARDINAL': 'https://schema.org/value' }
    for field in record:
        if field in mappings:
            context[field] = mappings[field] 
    metadata['@context'] = context
    metadata['@data'] = record
    #print(context)
    return json.dumps(metadata, indent=4)

def infocleaner(response):
    response = response.replace('\n', '<br>')
    response = re.sub('^.+<\|assistant\|>','', response, re.M).split('<br>')
    data = {}
    for item in response:
        print(item)
        if item:
            info = re.search(r'(^.+?)\:\s*(.+)$', item)
            data[info.group(1)] = info.group(2)
    return data

def generate_md5(text):
    # Create an MD5 hash object
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode('utf-8'))
    # Get the hexadecimal representation of the digest
    md5_digest = md5_hash.hexdigest()
    return md5_digest

def graphreader(source, llminput):
    artefacts = {}
    facts = []    
    atoms = []
    for entities in llminput.split('}'):
        graphatom = {}
        chain = ""
        for entity in entities.split('\n'):
            print("# %s #" % entity)
            p = re.search(r"\"(\S+)\"\:\s+(.+)", entity)
            if p:
                graphatom[p.group(1)] = p.group(2).replace(',','')
                #print("* %s" % p.group(0))
                #print("* %s" % p.group(1))
        if graphatom:
            print(graphatom)
            atoms.append(graphatom)
            chain = "%s *%s* %s" % (graphatom['concept1'], graphatom['relationship'], graphatom['concept2'])
            facts.append(chain)
    artefacts['source'] = source
    artefacts['facts'] = facts
    artefacts['graph'] = atoms
    return artefacts

def old_get_wikipedia_article(title):
    UA = 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'
    wiki_wiki = wikipediaapi.Wikipedia(UA, 'en')  # 'en' for English Wikipedia, you can change it to the language you want

    page_py = wiki_wiki.page(title)

    if page_py.exists():
        if 'DEBUG' in os.environ:
            print(f"Title: {page_py.title}")
            print("Content:")
            print(page_py.text[:500])  # Display the first 500 characters of the content
        return page_py.text
    else:
        if os.environ['DEBUG']:
            print(f"The page '{title}' does not exist on Wikipedia.")
        return 

def get_wikidata_ids_from_wikipedia_page(page_title, language='eu'):
    print(type(page_title))
    if isinstance(page_title, list):
        page_titles = page_title 
    else:
        page_titles = [ page_title ]
    
    pageids = {}
    for page in page_titles:
        pageitems = {}
        if 'http' in page:
            if '//wikipedia' in page:
                langcheck = re.search(r'wikipedia.org\/wiki\/(\S+)', page)
                if langcheck:
                    pageitems['page'] = langcheck.group(1)
                    pageitems['lang'] = 'eu'               
            else:
                page = page.replace('www.','')
                langcheck = re.search(r'\/\/(\S+?)\.wikipedia.org\/wiki\/(\S+)', page)
                if langcheck:
                    pageitems['page'] = langcheck.group(2)
                    pageitems['lang'] = langcheck.group(1)
        if pageitems:
            # Construct the URL for the Wikidata API request
            api_url = "https://www.wikidata.org/w/api.php"
            params = {
                "action": "wbgetentities",
                "sites": f"{pageitems['lang']}wiki",
                "titles": pageitems['page'],
                "format": "json",
            }

            # Make the API request
            response = requests.get(api_url, params=params)
            data = response.json()
            # Extract the Wikidata identifier from the response
            entities = data.get("entities")
            if entities:
                entity_id = next(iter(entities))
                pageids[page] = entities[entity_id].get("id")
    return pageids
