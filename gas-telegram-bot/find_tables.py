import os
def search_dir(d):
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                with open(path, 'r') as fp:
                    try:
                        content = fp.readlines()
                        for i, line in enumerate(content):
                            if '.table(' in line or '.from_(' in line:
                                print(f"{path}:{i+1} {line.strip()}")
                    except: pass
search_dir('../gas-auth-service/src')
search_dir('../gas-user-service/src')
search_dir('../gas-gateway-api/src')
