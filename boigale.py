import csv

# Passo 1: Ler os dados do boigale.csv
boigale_data = {}
with open('boigale.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        name = row['name'].strip()
        boigale_data[name] = int(row['qtd'])

# Passo 2: Processar o participants.csv
updated_rows = []
not_found_names = []

with open('participants.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    
    for row in reader:
        full_name = row['full_name'].strip()
        
        if full_name in boigale_data:
            # Atualiza o campo participants
            row['participants'] = boigale_data[full_name]
        else:
            # Mantém o valor original se não encontrado
            not_found_names.append(full_name)
        
        updated_rows.append(row)

# Passo 3: Mostrar nomes não encontrados
if not_found_names:
    print("Erro: Os seguintes nomes não foram encontrados:")
    for name in not_found_names:
        print(f" - {name}")
else:
    print("Todos os nomes foram encontrados e atualizados com sucesso!")

# Passo 4: Salvar o arquivo atualizado
with open('updated_participants.csv', mode='w', encoding='utf-8', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)

print("Arquivo atualizado salvo como: updated_participants.csv")