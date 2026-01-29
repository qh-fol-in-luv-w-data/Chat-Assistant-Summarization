import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(messages):
    total = 0
    for m in messages:
        total += len(enc.encode(m["content"]))
    return total
