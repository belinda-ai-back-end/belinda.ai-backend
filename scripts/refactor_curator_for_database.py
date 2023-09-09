import json

# Открываем файл curators.json для чтения
with open('curators.json', 'r') as file:
    input_json = json.load(file)

# Создаем новый JSON
output_json = {}
for key, value in input_json.items():
    new_value = {
        "name": value["name"],
        "desc": value["desc"],
        "email": None,
        "password": None,
        "socialLinks": {
            k: v for k, v in value.items() if k.endswith("_link") and v is not None
        }
    }
    output_json[key] = new_value

# Записываем преобразованный JSON в новый файл
with open('new_curators.json', 'w') as output_file:
    json.dump(output_json, output_file, indent=4)

print("Преобразование завершено. Результат сохранен в файл new_curators.json.")
