import wikipediaapi
import re
import json
import requests
import os

# Download the punkt tokenizer if you haven't already
#YOUR_ACCESS_TOKEN = "default"
YOUR_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': "Bearer %s" % YOUR_ACCESS_TOKEN
}

# Example: 
# interface = InterfaceAI()
# interface.translate_in_context(concept, context)
class InterfaceAI():
    def __init__(self, llmapi=None, llmramapi=None, url=None, q=None, debug=False):
        self.known = {}
        self.DEBUG = debug
        if 'LLMAPI' in os.environ:
            self.llmapi = os.environ['LLMAPI']
        if 'LLMRAMAPI' in os.environ:
            self.llmramapi = os.environ['LLMRAMAPI'] 
        if llmapi:
            self.llmapi = llmapi
        if llmramapi:
            self.llmramapi = llmramapi

    def get_llmapi(self):
        return self.llmapi

    def get_llmramapi(self):
        return self.llmramapi

    def translate_in_context(self, concept, context, url=None):
        llmapi = "http://10.147.18.193:8008"
    #    llmramapi = "http://10.147.18.160:8010"
        if concept:
            print("TRANS")
            tdata = { 'concept': concept, 'context': context }
            print(tdata)
            r = requests.post("%s/translate/" % self.llmapi, data = json.dumps(tdata), headers=headers, timeout=200)
            print(r.text)
            try:
                aidata = json.loads(r.text)
                aidata['type'] = 'concept'
                aidata['name'] = concept
                if url:
                    aidata['url'] = url
                print("Translations: %s " % aidata)
                r = requests.post("%s/llmcache/" % self.llmramapi, data = json.dumps(aidata))
            except:
                print("ERROR: no translation for %s" % concept)
        return

def get_wikipedia_article(title):
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

def analyze_page(url):
    if not 'http' in url:
        content = get_wikipedia_article(url)
    else:
        if "dataset.xhtml?persistentId=" in url:
            m = re.search(r"Id=(\S+)", url)
            if m:
                jsonurl = "https://portal.devstack.odissei.nl/api/datasets/export?exporter=OAI_ORE&persistentId=%s" % m.group(1)
                print(jsonurl)
                r = requests.get(jsonurl)
                content = json.loads(r.text)
                print(content['ore:describes']['citation:dsDescription']['citation:dsDescriptionValue'])
                content = "%s. %s" % (content['ore:describes']['title'], content['ore:describes']['citation:dsDescription']['citation:dsDescriptionValue'])
        else:
            reader = "%s/process_url?url=%s" % (os.environ['NERAPI'], url)
            print(reader)
            r = requests.get(reader)
            content = json.loads(r.text)
    return content
