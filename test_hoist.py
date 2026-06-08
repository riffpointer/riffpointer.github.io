import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

app = QApplication(sys.argv)
view = QWebEngineView()

html = """
<html>
<body>
<script>
  throw new Error("test error");
  function myFunc() { console.log("myFunc called"); }
</script>
</body>
</html>
"""

view.setHtml(html)

def check_func():
    print("Checking myFunc...")
    view.page().runJavaScript("myFunc();", lambda res: print("Result:", res))

view.loadFinished.connect(lambda ok: check_func())

# We don't need to show it, just let it process
import threading
threading.Timer(2.0, app.quit).start()
app.exec()
