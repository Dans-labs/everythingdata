# Everything Data use cases

Everything Data is FastAPI implementation for transformers, State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.
Created by Slava Tykhonov, DANS-KNAW R&D.

## Translations in various languages for SKOS concept
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
