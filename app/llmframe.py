import pandas as pd
import duckdb
import time
from config import Config
from utils import generate_md5
from localconfig import mappings
from langchain.llms import Ollama
from localconfig import SYS_PROMPT, R_SYS_PROMPT
from nltk import tokenize, sent_tokenize
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import accelerate
import bitsandbytes
import re

def keywords_cleaner(content):
    response = str(content).replace('<br>','\n')
    response = "%s }" % response
    data = {}
    keywords_list = []
    keywords = re.findall(r'\"(.+?)\"', response)
    for keyword in keywords:
        if keyword != 'keywords':
            keywords_list.append(keyword)
    data['keywords'] = keywords_list
    return data

class LLMFrame():
    def __init__(self, config=False, job=False, customprompt=False, debug=False):
        self.DEBUG = debug
        self.pipe = False
        self.df = False
        self.data = False
        self.SYS_PROMPT = False
        self.config = False
        if job:
            self.config = config
        if customprompt:
            with open("%s/%s" % (os.environ['GRAPHDIR'], customprompt), 'r') as file:
                self.SYS_PROMPT = file.read()            
        #print("PROMPT %s" % self.SYS_PROMPT)
        print(self.config)
        
    def graphtuning(self, source, llminput):
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
                    graphatom[p.group(1)] = p.group(2).replace(',','').replace('"','')
            if graphatom:
                print(graphatom)
                atoms.append(graphatom)
                if 'relationship' in graphatom:
                    if graphatom['relationship'] in mappings:
                        graphatom['relationship'] = mappings[graphatom['relationship']]
                    if not 'is part of' in graphatom['relationship']:
                        chain = "%s %s(%s) %s" % (graphatom['concept1'], graphatom['entity'], graphatom['relationship'], graphatom['concept2'])
                    else:
                        chain = "%s %s (%s) %s" % (graphatom['concept2'], graphatom['entity'], graphatom['relationship'], graphatom['concept1'])
                    facts.append(chain)
        artefacts['source'] = source
        artefacts['facts'] = facts
        artefacts['graph'] = atoms
        return artefacts

    def graph_decompression(self, inputdata):
        inputtext = ''
        for field in inputdata:
            inputtext = "%s. %s" % (inputtext, inputdata[field])

        customquery = f"context: ```{inputtext}``` \n\n output: "
        model = os.environ['LLAMAMODEL']
        ollama = Ollama(base_url="%s" % os.environ['OLLAMA_API'], model=model, system=R_SYS_PROMPT)
        s = sent_tokenize(inputtext)
        data = {}
        for ix in range(0,len(s)):
            sent = s[ix]
            record = { 'uid': ix }
            if len(sent) > int(os.environ['MIN_SENTENCE_SIZE']):
                item = ollama(sent)
                item = item.replace('<|im_end|>','')
                if len(item) > int(os.environ['MIN_SENTENCE_SIZE']):
                    record['data'] = self.graphtuning(sent, item)
                    record['md5'] = generate_md5(sent)
            data[ix] = record
        return data

    def loader(self, path="../data"):
        csvfiles =[]
        xlsfiles = []
        csvfiles = [x for x in os.listdir(path = path) if ".csv" in x]
        xlsfiles = [x for x in os.listdir(path = path) if ".xls" in x]
        if csvfiles:
            self.df = pd.concat((pd.read_csv(path +"/" + f) for f in csvfiles), ignore_index=True)
            self.data = True
        if xlsfiles:
            self.df = pd.concat((pd.read_excel(path +"/" + f) for f in xlsfiles), ignore_index=False)
            self.data = True
        return self.df
        
    def create_message(self, table_name = None, query = None, customquery = None, direct=None, context=None):
        class table_message:
            def __init__(message, system, user, column_names, column_attr):
                message.system = system
                message.user = user
                message.column_names = column_names
                message.column_attr = column_attr

   
        if self.SYS_PROMPT:
            system_template = self.SYS_PROMPT
            user_template = customquery
        else:
            self.data = True
        
        if self.data:
            system_template = self.config['instruction']
            user_template = self.config['template']

        if direct:
            system_template = customquery
            user_template = "%s %s" % (user_template, customquery)
            user_template = customquery

        if table_name:
            tbl_describe = duckdb.sql("DESCRIBE SELECT * FROM " + table_name +  ";")
            col_attr = tbl_describe.df()[["column_name", "column_type"]]
            col_attr["column_joint"] = col_attr["column_name"] + " " +  col_attr["column_type"]
            col_names = str(list(col_attr["column_joint"].values)).replace('[', '').replace(']', '').replace('\'', '')

            system = system_template.format(table_name, col_names)
            user = user_template.format(query)
            print("SYSTEM")
            print(system)
            print(user)

            m = table_message(system = system, user = user, column_names = col_attr["column_name"], column_attr = col_attr["column_type"])
            return m
        else:
#  instruction: 'Given the following text, your job is to link user's request to the same context: {}.\n'
#  template: 'then translate user's query in {}'
# English, French and Spanish'

            if self.SYS_PROMPT:
                system = system_template
                user = user_template
            else:
                print(system_template)
                print(customquery)
                system = system_template.format(context, customquery)
                user = user_template.format(query)
            m = table_message(system = system, user = user, column_names = None, column_attr = None)
            return m
        return 
    
    def add_quotes(self, query, col_names):
        for i in col_names:
            if i in query:
                query = str(query).replace(i, '"' + i + '"')
        return(query)
    
    def prepare_message(self, m):
        messages = [
        {
          "role": "system",
          "content": m.system
        },
        {
          "role": "user",
          "content": m.user
        }
        ]
        return messages

    def debug_messages(self, msg):
        print(msg.system)
        print(msg.user)
        print(msg.column_names)
        print(msg.column_attr)
        return

    def run_pipeline(self, messages):
        if not self.pipe:
            print("LOAD pipeline")
            self.pipe = pipeline("text-generation",
                model=os.environ['MODEL'],
                torch_dtype=torch.bfloat16,
                device_map="auto")

        prompt = self.pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = self.pipe(prompt,
               max_new_tokens=256,
               do_sample=True,
               temperature=0.1,
               top_k=1,
               top_p=0.95)
        print(outputs[0]["generated_text"])
        return outputs


