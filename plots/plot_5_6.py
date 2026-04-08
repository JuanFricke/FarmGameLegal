def sort_list(lst):
    nova_lista = lst[:]  # copia da lista original
    
    n = len(nova_lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            if nova_lista[j] > nova_lista[j + 1]:
                # troca
                nova_lista[j], nova_lista[j + 1] = nova_lista[j + 1], nova_lista[j]
    
    return nova_lista
