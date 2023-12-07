# Everything Data

Everything Data is FastAPI implementation for transformers, State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX. Created by Slava Tykhonov, DANS-KNAW R&D.

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
```

## Example 1: Survived from the second class

Task 1. You are interested in how many Titanic passangers survived from the second class, just add this prompt "titanic_answer' to the configuration file in config/prompts.ini:

```
titanic_answer:
{
  action: 'text-generation'
  instruction: 'Given the following SQL table, your job is to write queries given a user’s request. CREATE TABLE {} ({}) \n'
  template: 'Write a SQL query that returns - {}'
  query: 'How many people survived from the second class?'
  device_map: 'auto'
}
```
Run this job to answer the question:
```
curl http://0.0.0.0:8008/tranformers?job=titanic_answer
```
Framework will generate SQL table to keep the structure of the dataset and give you back resulting SQL to query it:
```
<|system|>
Given the following SQL table, your job is to write queries given a user’s request. CREATE TABLE df (PassengerId BIGINT, Pclass BIGINT, Name VARCHAR, Sex VARCHAR, Age DOUBLE, SibSp BIGINT, Parch BIGINT, Ticket VARCHAR, Fare DOUBLE, Cabin VARCHAR, Embarked VARCHAR)

<|user|>
Write a SQL query that returns - How many people survived from the second class?
<|assistant|>
To answer this question, we need to filter the data to only include passengers from the second class (Pclass = 2) and then count the number of passengers who survived (Survived = 1).

Here's the SQL query:

SELECT COUNT(*)

FROM df

WHERE Pclass = 2 AND Survived = 1;

This query will return the total number of passengers who survived from the second class.
```

## Example 2: Looking for survived passengers by name
We want AI to help us to generate SQL query to find all survived passengers with surname Johnson.
New job describing prompt:
```
titanic_johnson:
{
  action: 'text-generation'
  instruction: 'Given the following SQL table, your job is to write queries given a user’s request. CREATE TABLE {} ({}) \n'
  template: 'Write a SQL query that returns - {}'
  query: 'Give me back all survived passangers with surname Johnson'
  device_map: 'auto'
}
```
Run this job from API:
```
curl http://0.0.0.0:8008/tranformers?job=titanic_johnson
```


Result will be like:
```
<|system|>
Given the following SQL table, your job is to write queries given a user’s request. CREATE TABLE df (PassengerId BIGINT, Pclass BIGINT, Name VARCHAR, Sex VARCHAR, Age DOUBLE, SibSp BIGINT, Parch BIGINT, Ticket VARCHAR, Fare DOUBLE, Cabin VARCHAR, Embarked VARCHAR)

<|user|>
Write a SQL query that returns - Give me back all survived passangers with surname Johnson
<|assistant|>
SELECT *
FROM df
WHERE survived = 1
AND SUBSTRING(Name, CHARINDEX(' ', Name) + 1) = 'Johnson';

-- Alternative syntax for SUBSTRING function:
-- SUBSTRING(Name, CHARINDEX(' ', Name) + 1, CHARINDEX(' ', Name, CHARINDEX(' ', Name) + 1) - (CHARINDEX(' ', Name) + 1))

-- Explanation:
-- We first filter the results to only include rows where the survived column is 1.
-- Then, we use the SUBSTRING function to extract the surname from the Name column.
-- The SUBSTRING function takes three arguments: the starting position, the length of the substring, and the ending position (optional).
-- In this case, we're using the CHARINDEX function to find the index of the first space character in the Name column.
-- We add 1 to this index to get the starting position of the surname.
-- We then use the CHARINDEX function again to find the index of the second space character in the Name column, starting from the first space character.
-- We subtract the starting
```
