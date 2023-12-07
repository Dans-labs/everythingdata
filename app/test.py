from llmframe import LLMFrame

llm = LLMFrame()
df = llm.loader()
print(llm.df.columns)
query = "Give me female penguins?"
msg = llm.create_message(table_name = "df", query = query)
query = "Give me the amount of people from 75 to 80 years old living on address with postcode 1031"

m = llm.create_message(table_name = "df", query = query)
llm.debug_messages(m)
#messages = llm.prepare_message(m)
#o = llm.run_pipeline(messages)
#print(o)

