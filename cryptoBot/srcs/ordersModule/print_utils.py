def print_usage():
    print('\033[94m {}\033[00m' .format("Usage: python3 binanceScript.py [BUY/SELL] [ammount]"))
    exit(84)

def print_error(text):
    print('\033[91m {}\033[00m' .format("Error: " + text))
    exit(84)

def print_warning(text):
    print('\033[93m {}\033[00m' .format("Warning: " + text))

def print_success(text):
    print('\033[92m {}\033[00m' .format("Success: " + text))