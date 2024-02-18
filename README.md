# Everything Data

Everything Data is a FastAPI framework implementation for transformers, State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX. Knowledge graph extraction is built on Ollama as a service, which enables the execution of Open-Source Large Language Models (LLMs), such as Llama 2 and Mistral. The interface enriches the capabilities of Large Language Models (LLMs) by seamlessly integrating RAM memory and persistent memory (ROM) while natively supporting Decentralized Identifiers (DID). This ensures the persistence of available resources, including prompts, questions, and answers.

Created by [Slava Tykhonov](https://www.linkedin.com/in/vyacheslavtikhonov/), [DANS-KNAW](https://dans.knaw.nl/en) R&D. Development is supported by [BioSTM](https://rozen.perso.math.cnrs.fr/YR/HOME.html), Paris Cité University, France, and [ODISSEI](https://odissei-data.nl/en/), Open Data Infrastructure for Social Science and Economic Innovations.

This demonstrator will be working for various use cases:
- create SQL table out of tabular datasets and fill with data points in the appropriate format
- ask your data with natural language about anything, get back answers with explanation or SQL queries to do verification of results.
- create multilingual vocabularies from scratch or extend existent vocabularies with properties translated in the context
- connect to Dataverse, read datasets and describe files on variables level
- link variables to Semantic Web concepts such as Wikidata or Skosmos hosted

<!--- Indent entire section -->
<div style="margin-left: 1.5em;">

Prerequisites: [git](https://git-scm.com/downloads), [cURL](https://curl.haxx.se/download.html), [Docker](https://docs.docker.com/get-docker/), [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

```shell
sudo apt-get install git curl docker-compose -y

# Make sure the Docker daemon is running.
sudo systemctl start docker

# Add your user to the Docker group.
sudo usermod -a -G docker <username>

# Check version numbers  
docker --version
docker-compose --version

curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu22.04/nvidia-docker.list > /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update
sudo apt-get update     && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
This should get GPU unit supported inside of Docker container. You can test by running separate commands for cuda11 and cuda12 to check if NVIDIA-compatible GPU unit is recognized (tested with A100 and A6000):
```
docker run --rm --runtime=nvidia --gpus all dansknaw/everythingdata:devel-cuda11 nvidia-smi
or
docker run --rm --runtime=nvidia --gpus all dansknaw/everythingdata:devel-cuda12 nvidia-smi
```

Install Everythingdata and Ollama Docker:
```
git clone https://github.com/Dans-labs/everythingdata
cd everythingdata
git clone https://github.com/valiantlynx/ollama-docker/
```

If you see NVIDIA screen then start Everythingdata as a service:
```
cp env.sample .env
docker-compose up -d
curl http://0.0.0.0:8008/docs
docker exec ollama /usr/bin/ollama pull llama2
```
Try it with Titanic Disaster Dataset:
```
wget https://raw.githubusercontent.com/amberkakkar01/Titanic-Survival-Prediction/master/test.csv -O ./data/titanic.csv
```

## Example 1: Survived passengers of the Titanic from the second class

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

## Example 3. Getting the list of questions your data can answer

Now we want AI to analyze dataset and give us the list of possible questions related to the data:
```
<|system|>
Given the following SQL table, your job is to write queries given a user’s request. CREATE TABLE df (PassengerId BIGINT, Pclass BIGINT, Name VARCHAR, Sex VARCHAR, Age DOUBLE, SibSp BIGINT, Parch BIGINT, Ticket VARCHAR, Fare DOUBLE, Cabin VARCHAR, Embarked VARCHAR)

<|user|>
Write a SQL query that returns - Give me back possible questions to be answered with table df
<|assistant|>
I do not have the context of your specific use case or requirements. however, based on the given table, here are some possible questions that can be answered using sql queries:

1. what is the average fare for passengers in the first class (pclass = 1)?
2. how many female passengers (sex = 'female') were traveling with at least one sibling (sibsp > 0)?
3. what is the most common embarkation port for passengers in the third class (pclass = 3)?
4. how many passengers embarked from southampton (embarked ='s') and what is the average fare for them?
5. what is the highest fare paid by a passenger in the second class (pclass = 2)?
6. how many passengers were traveling alone (sibsp = parch = 0)?
7. what is the total number of passengers who embarked from quebec (embarked = 'q')?
8. what is the average age for passengers in the second class (pclass = 2) who embarked from southampton (embarked ='s')?
```
