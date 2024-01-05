# Everything Data use cases

Everything Data is a FastAPI implementation for transformers, State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.
Created by Slava Tykhonov, DANS-KNAW R&D.

## Use Case #1 - Translator: Translations in various languages for SKOS concept
```
curl "http://10.147.18.193:8008/translate?job=translate&customquery=Aanbod%20vaste%20uren%20werken?"
```
Expected output:
```
<|system|>
Aanbod vaste uren werken?
<|user|>
Translate user’s request in English, German, French and Spanish, Ukrainian and Russian, Italian, Portuguese, Polish, Czech, Slovak, Greek, Swedish, Norwegian, Danish. Provide short description in English up to 50 words. None
<|assistant|>
English: Fixed hours work?

German: Festen Arbeitszeiten?

French: Heures fixes de travail?

Spanish: Horas fijas de trabajo?

Ukrainian: Стандартні години роботи?

Russian: Стандартные часы работы?

Italian: Ore fisse di lavoro?

Portuguese: Horas fixas de trabalho?

Polish: Stałe godziny pracy?

Czech: Stálé hodiny práce?

Slovak: Stálé hodiny práce?

Greek: Σταθερές ώρες εργασίας;

Swedish: Fasta arbetstider?

Norwegian: Fast arbeids timer?

Danish: Fast arbejds timer?

Description: This phrase is commonly used to inquire about the set or fixed hours of operation for a business or organization. It is often used in job interviews or when discussing work sched
```

## Use case #2 - SKOS ontology creator: Filter out related concepts and create SKOS hierarchy for the list of keywords:
```
curl http://10.147.18.193:8008/tranformers?job=declassification2
```
Expected output:
```
<|system|>
I have keywords list: startup ecosystem , venture capital , artificial intelligence , silicon valley , funding round , raised $ , tech startups , generative ai , new york , south africa , united states , middle east , tech startup , north america , startup founders , market research , supply chain , $1 , san francisco , seed funding , social media , digital economy , global market , climate change , saudi arabia , african startups , growth rate , managing director , machine learning , market share , market size , nigerian startups , key players , forecast period , angel investors , vice president , chief executive , stage startups , economic growth , product development , venture capitalists , 1 billion , business model , digital transformation , financial services , $2 , ai startup , industry leaders , market report , southeast asia , tech companies , sam altman , seed round , accelerator program , innovative solutions , startup funding , renewable energy , indian startup , market dynamics , pivotal role , executive officer , latin america , vc funding , 1 million , business development , global startup , looking statements , market growth , small businesses , fintech startup , series b , startup act , pgt innovations , startup support
<|user|>
produce RDF for keyword "startup founders", add related keywords from this keywords list and create description and define possible relationships by using SKOS ontology and skos:broader, skos:narrower
<|assistant|>
@prefix rdf: .
@prefix skos: .

<#startupFounders>
a skos:Concept ;
skos:prefLabel "Startup Founders" ;
skos:definition "Individuals who initiate and lead the creation and development of new startups, typically in the technology sector." ;
skos:broader "Entrepreneurs" ;
skos:narrower "Tech Startup Founders" ;
skos:relatedMatch "Startup Ecosystem", "Venture"
```

## Use case #3 - Facts extraction: Get triples with SKOS relationships for the specified text, and export to JSON:
```
curl -X 'GET' \
  'http://10.147.18.193:8008/graph?prompt=graph.prompt&inputtext=Albert%20Einstein%20%28Ulm%2C%2014%20maart%201879%20%E2%80%93%20Princeton%20%28New%20Jersey%29%2C%2018%20april%201955%29%20was%20een%20Duits-Zwitsers-Amerikaanse%20theoretisch%20natuurkundige%20van%20Joodse%20afkomst.%20Hij%20wordt%20algemeen%20gezien%20als%20een%20van%20de%20belangrijkste%20natuurkundigen%20uit%20de%20geschiedenis%2C%20naast%20Isaac%20Newton%20en%20James%20Clerk%20Maxwell.%20Zelf%20noemde%20hij%20altijd%20Newton%20als%20een%20veel%20belangrijker%20natuurkundige%20dan%20zichzelf%20omdat%20Newton%2C%20anders%20dan%20Einstein%2C%20behalve%20theoretische%20ook%20grote%20experimentele%20ontdekkingen%20deed.%20In%20het%20dagelijks%20leven%20is%20de%20naam%20Einstein%20synoniem%20geworden%20met%20grote%20intelligentie.%5B1%5D' \
  -H 'accept: application/json'
```
Expected output:
```
{
  "0": {
    "source": "Albert Einstein (Ulm, 14 maart 1879 – Princeton (New Jersey), 18 april 1955) was een Duits-Zwitsers-Amerikaanse theoretisch natuurkundige van Joodse afkomst.",
    "facts": [
      "Albert Einstein is a(skos:narrower) theoretisch natuurkundige",
      "Albert Einstein is a(skos:narrower) Duits-Zwitsers-Amerikaanse",
      "Albert Einstein is a(skos:broader) Duits-Zwitsers-Amerikaanse theoretisch natuurkundige",
      "Albert Einstein is a(skos:narrower) theoretisch natuurkundige van Joodse afkomst"
    ],
    "graph": [
      {
        "concept1": "Albert Einstein",
        "concept2": "theoretisch natuurkundige",
        "entity": "is a",
        "relationship": "skos:narrower",
        "importance": "4"
      },
      {
        "concept1": "Albert Einstein",
        "concept2": "Duits-Zwitsers-Amerikaanse",
        "entity": "is a",
        "relationship": "skos:narrower",
        "importance": "4"
      },
      {
        "concept1": "Albert Einstein",
        "concept2": "Duits-Zwitsers-Amerikaanse theoretisch natuurkundige",
        "entity": "is a",
        "relationship": "skos:broader",
        "importance": "5"
      },
      {
        "concept1": "Albert Einstein",
        "concept2": "theoretisch natuurkundige van Joodse afkomst",
        "entity": "is a",
        "relationship": "skos:narrower",
        "importance": "4"
      }
    ]
  },
  "1": {
    "source": "Hij wordt algemeen gezien als een van de belangrijkste natuurkundigen uit de geschiedenis, naast Isaac Newton en James Clerk Maxwell.",
    "facts": [
      "Albert Einstein important scientists in history(skos:related) Isaac Newton",
      "James Clerk Maxwell important scientists in history(skos:related) Albert Einstein"
    ],
    "graph": [
      {
        "concept1": "Albert Einstein",
        "concept2": "Isaac Newton",
        "entity": "important scientists in history",
        "relationship": "skos:related",
        "importance": "5"
      },
      {
        "concept1": "James Clerk Maxwell",
        "concept2": "Albert Einstein",
        "entity": "important scientists in history",
        "relationship": "skos:related",
        "importance": "5"
      }
    ]
  },
  "2": {
    "source": "Zelf noemde hij altijd Newton als een veel belangrijker natuurkundige dan zichzelf omdat Newton, anders dan Einstein, behalve theoretische ook grote experimentele ontdekkingen deed.",
    "facts": [
      "Newton Natuurkundige(Broader) Einstein",
      "Theoretische ontdekkingen Natuurkundige(Broader) Experimentele ontdekkingen"
    ],
    "graph": [
      {
        "concept1": "Newton",
        "concept2": "Einstein",
        "entity": "Natuurkundige",
        "relationship": "Broader",
        "importance": "3"
      },
      {
        "concept1": "Theoretische ontdekkingen",
        "concept2": "Experimentele ontdekkingen",
        "entity": "Natuurkundige",
        "relationship": "Broader",
        "importance": "3"
      }
    ]
  },
  "3": {
    "source": "In het dagelijks leven is de naam Einstein synoniem geworden met grote intelligentie.",
    "facts": [
      "Einstein het dagelijks leven(owl:partOf) grote intelligentie"
    ],
    "graph": [
      {
        "concept1": "Einstein",
        "concept2": "grote intelligentie",
        "entity": "het dagelijks leven",
        "relationship": "owl:partOf",
        "importance": "5"
      }
    ]
  }
}
```
