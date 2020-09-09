import pinject

from service.rancher import RancherService
from helper.config import Config
from app.enforcement_watcher import EnforcementWatcher


container = pinject.new_object_graph()
watcher = container.provide(EnforcementWatcher)
