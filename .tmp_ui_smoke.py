import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt5.QtWidgets import QApplication, QMessageBox, QTabWidget

# Make message boxes non-blocking in smoke test
QMessageBox.information = staticmethod(lambda *args, **kwargs: QMessageBox.Ok)
QMessageBox.warning = staticmethod(lambda *args, **kwargs: QMessageBox.Ok)
QMessageBox.critical = staticmethod(lambda *args, **kwargs: QMessageBox.Ok)
QMessageBox.question = staticmethod(lambda *args, **kwargs: QMessageBox.Yes)

from src.simulator import RoutingSimulator
from src.ui.main_window import MainWindow

sim = RoutingSimulator('config/test_topology1.json')
assert sim.load_config(), 'load_config_failed'
assert sim.build_network(), 'build_network_failed'
assert sim.start_simulation(), 'start_simulation_failed'

app = QApplication([])
win = MainWindow(sim)

# Verify tabs
central = win.centralWidget()
assert isinstance(central, QTabWidget), 'central_widget_not_tabs'
assert central.count() == 4, f'tab_count_unexpected:{central.count()}'

# Topology view refresh
win.topology_widget.refresh_topology()

# Routing table refresh
win.routing_table_widget.update_router_list()
win.routing_table_widget.refresh_tables()

# Algorithm compare smoke: run one benchmark and feed UI update handler
router_id = win.algorithm_widget.router_combo.itemData(0)
router = sim.routers[router_id]
results = router.path_calculator.benchmark_algorithms(runs=1)
win.algorithm_widget._on_benchmark_finished(results, 1)

# Control actions: failure and recovery
cw = win.control_widget
cw.fail_router1.setValue(1)
cw.fail_router2.setValue(2)
cw.create_link_failure()

cw.recover_router1.setValue(1)
cw.recover_router2.setValue(2)
cw.cost_spinbox.setValue(7)
cw.create_link_recovery()

cw.update_statistics()
win.update_status()

print('UI_SMOKE_PASS')
print(f'TABS={central.count()}')
print(f'ROUTER_ITEMS={win.routing_table_widget.router_combo.count()}')
print(f'ROUTE_ROWS={win.routing_table_widget.table.rowCount()}')

win.close()
sim.stop_simulation()
app.quit()
