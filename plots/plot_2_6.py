def decode_hash(text, key):
    resultado = ""
    
    for i in range(len(text)):
        k = key[i % len(key)]  # chave cíclica
        resultado += chr(ord(text[i]) - ord(k))
    
    return resultado
