
from runtime import security_context
from external_policy import read_file, delete_file
print("Identity :", security_context.identity)
print("Attributes :", security_context.attributes)

print("=== TEST 1 : READ autorisé ===")

content = read_file("/tmp/agent-data/test.txt")

print("Contenu :", content)


print("\n=== TEST 2 : READ interdit ===")

try:
    read_file("/etc/passwd")
    print("ERREUR : lecture autorisée alors qu'elle devrait être refusée")

except PermissionError as e:
    print("DENY OK :", e)


print("\n=== TEST 3 : DELETE interdit pour file-reader ===")

try:
    delete_file("/tmp/agent-data/test.txt")
    print("ERREUR : suppression autorisée alors qu'elle devrait être refusée")

except PermissionError as e:
    print("DENY OK :", e)
