import re
import json

def parse_receipt(text):
    # Date and time
    dt_match = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})", text)
    date_time = dt_match.group(1) if dt_match else "Не найдено"
    
    # Payment method
    payment_match = re.search(r"Банковская карта:\s*([\d\s,]+)", text)
    payment_method = "Банковская карта" if payment_match else "Наличные"

    # Product names and prices
    items = []
    item_pattern = re.compile(r"^\d+\.\n(.*?)\n(?:\d+[/.,]\d+\sx\s[\d\s,]+\n)?([\d\s,]+)\nСтоимость", re.MULTILINE | re.DOTALL)
    matches = item_pattern.findall(text)

    # Calculate total amount
    total_calculated = 0.0
    for name, price_str in matches:
        clean_price = float(price_str.replace(" ", "").replace(",", "."))
        items.append({"product": name, "price": clean_price})
        total_calculated += clean_price

    total_match = re.search(r"ИТОГО:\s*([\d\s,]+)", text)
    total_receipt = float(total_match.group(1).replace(" ", "").replace(",", ".")) if total_match else total_calculated

    return {
        "date_time": date_time,
        "payment_method": payment_method,
        "items": items,
        "total_amount": total_receipt
    }


with open("raw.txt", "r", encoding="utf-8") as file:
    receipt_text = file.read()
    
result = parse_receipt(receipt_text)
print(json.dumps(result, indent=4, ensure_ascii=False))