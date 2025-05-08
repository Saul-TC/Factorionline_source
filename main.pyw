from factorionline.factorionline import Factorionline
from factorionline.logger import Log

try:
    app = Factorionline(Log(debug=True))
    app.run()
except Exception as e:
    app.stop()
    raise e