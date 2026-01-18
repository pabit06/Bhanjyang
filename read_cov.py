
try:
    with open('contact_coverage.txt', 'r', encoding='utf-16') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading utf-16: {e}")
    try:
        with open('contact_coverage.txt', 'r', encoding='utf-8') as f2:
            print(f2.read())
    except Exception as e2:
        print(f"Error reading utf-8: {e2}")
