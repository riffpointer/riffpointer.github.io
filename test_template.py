import sys

with open("tools/posts_manager/main.py", "r") as f:
    content = f.read()

# Extract PREVIEW_HTML_TEMPLATE
start = content.find('PREVIEW_HTML_TEMPLATE = """')
end = content.find('"""', start + 30)

template = content[start+28:end]
print(template)
