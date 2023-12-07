# Everything Data

Everything Data is FastAPI implementation for transformers, State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX.

This demonstrator works for various use cases:
- connect to Dataverse, read datasets and describe files on variables level
- create SQL table out of tabular datasets and fill with data points in the appropriate format
- link variables to Semantic Web concepts such as Wikidata or Skosmos hosted
- ask your data with natural language about anything, get back answers with explanation or SQL queries to do verification of results.

Usage:
```
cp env.sample .env
docker-compose up -d
curl http://0.0.0.0:8008/docs
```
Try it with Titanic Disaster Dataset:
```
wget https://raw.githubusercontent.com/amberkakkar01/Titanic-Survival-Prediction/master/test.csv -O ./data/titanic.csv

curl http://0.0.0.0:8008/tranformers?job=sql_generator&query=How+many+passengers+from+second+class+survived?
```
