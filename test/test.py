import json as js

asd = ["aaa", 'bbb']
json = js.dumps(asd)
print(json)
print(js.loads(json))