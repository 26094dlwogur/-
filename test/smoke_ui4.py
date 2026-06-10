"""ui 4.py 스모크 테스트: 3초간 실행 후 자동 종료."""
import importlib.util
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

spec = importlib.util.spec_from_file_location("ui4", root / "gui" / "ui 4.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.MangroveSimulation()
app.root.after(3000, app.root.destroy)
app.run()
print("smoke test OK")
