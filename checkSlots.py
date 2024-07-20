def checkSlotsFirstFit(n, l):
    l = sorted(l)
    for i in range(len(l)):
        sublist = l[i:n+i]
        if len(sublist) < n:
            return []
        consecutive = sorted(sublist) == list(range(min(sublist), max(sublist)+1))
        if consecutive:
            return sublist
    return []

def checkSlotsBestGap(n, l):
    l = sorted(l)
    best_gap = None
    for i in range(len(l)):
        sublist = l[i:n+i]
        if len(sublist) < n:
            break
        consecutive = sorted(sublist) == list(range(min(sublist), max(sublist)+1))
        if consecutive:
            if best_gap is None or (max(sublist) - min(sublist) < max(best_gap) - min(best_gap)):
                best_gap = sublist
    return best_gap if best_gap else []

# Dados fornecidos
lista = [0, 2, 3, 4, 5, 7, 8, 9, 12, 20, 21, 22]
num_slots = 3

# Resultados dos algoritmos
first_fit_result = checkSlotsFirstFit(num_slots, lista)
best_gap_result = checkSlotsBestGap(num_slots, lista)

# Exibição dos resultados
print(f"lista >> {lista}")
print(f"num_slots >> {num_slots}")
print("-" * 30)
print(f"checkSlotsFirstFit: {first_fit_result}")
print(f"checkSlotsBestGap: {best_gap_result}")
