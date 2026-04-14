import random
import string

def generate_complex_key():
    # Format: SB-XXXX-500-XXXX (X - harf yoki raqam)
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SB-{part1}-500-{part2}"

keys = [generate_complex_key() for _ in range(500)]

with open("keys.txt", "w") as f:
    for key in keys:
        f.write(key + "\n")

print(f"500 ta murakkab kalit keys.txt fayliga yozildi.")
