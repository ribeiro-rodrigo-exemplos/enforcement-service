import urllib3

from injector import Injector

from di.argo_module import ArgoModule
from app.watcher import EnforcementWatcher

urllib3.disable_warnings()

injector = Injector([
    ArgoModule()
])

if __name__ == "__main__":
    watcher = injector.get(EnforcementWatcher)
    watcher.run()
