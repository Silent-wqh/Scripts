import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-4")
with open(r".\resources\prompt.txt","r", encoding="utf8") as f:
    prompt = f.read()
    print("token: ",len(encoding.encode(prompt)))
    print("word: ",len(prompt))
