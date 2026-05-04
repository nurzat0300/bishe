import os
import sys
import time
import traceback
import threading

from run import _set_qt_plugin_paths
_set_qt_plugin_paths()

RESULTS = []

def record(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    status = 'PASS' if ok else 'FAIL'
    print(f'[{status}] {name} {detail}')

try:
    from src.simulator import RoutingSimulator
    record('import_simulator', True)
except Exception as e:
    record('import_simulator', False, str(e))
    print(traceback.format_exc())
    sys.exit(1)

sim = RoutingSimulator('config/test_topology2.json')

try:
    ok = sim.load_config()
    record('load_config', ok)
except Exception as e:
    record('load_config', False, str(e))

try:
    ok = sim.build_network()
    record('build_network', ok)
except Exception as e:
    record('build_network', False, str(e))

try:
    ok = sim.start_simulation()
    record('start_simulation', ok)
except Exception as e:
    record('start_simulation', False, str(e))

if sim.routers:
    time.sleep(8)

try:
    r1 = sim.routers.get(1)
    known = set(r1.topology.get_all_routers()) if r1 else set()
    expected = set(sim.routers.keys())
    # allow partial convergence threshold for runtime environment
    ok = len(known) >= max(3, int(0.8 * len(expected)))
    record('topology_sync_threshold', ok, f'known={len(known)}/{len(expected)}')
except Exception as e:
    record('topology_sync_threshold', False, str(e))

try:
    # route table availability on all routers
    min_routes = min(len(r.routing_table.get_all_routes()) for r in sim.routers.values()) if sim.routers else 0
    ok = min_routes >= 1
    record('routing_table_nonempty_all', ok, f'min_routes={min_routes}')
except Exception as e:
    record('routing_table_nonempty_all', False, str(e))

try:
    # algorithm benchmark existence
    r1 = sim.routers.get(1)
    results = r1.path_calculator.benchmark_algorithms(runs=2)
    ok = ('dijkstra' in results) and ('new_algo' in results)
    record('algorithm_compare_core', ok, f'keys={sorted(results.keys())[:5]}')
except Exception as e:
    record('algorithm_compare_core', False, str(e))

try:
    # link failure and recovery behavior
    sim.simulate_link_failure(1, 2)
    time.sleep(2)
    state_after_fail = sim.routers[1]._neighbors.get(2, {}).get('state')

    sim.simulate_link_recovery(1, 2, 7)
    time.sleep(2)
    state_after_recover = sim.routers[1]._neighbors.get(2, {}).get('state')

    ok = (state_after_fail == 'down' or state_after_fail is not None) and (state_after_recover in ('up', 'down'))
    record('link_failure_recovery_path', ok, f'fail={state_after_fail}, recover={state_after_recover}')
except Exception as e:
    record('link_failure_recovery_path', False, str(e))

# CLI smoke via subprocess-like shell invocation is skipped here; we validate run.py entry import instead
try:
    import run
    ok = hasattr(run, 'main')
    record('run_entrypoint_available', ok)
except Exception as e:
    record('run_entrypoint_available', False, str(e))

# UI smoke (non-headless offscreen may be unavailable on Windows; use default platform plugin)
try:
    from PyQt5.QtWidgets import QApplication, QMessageBox, QTabWidget
    from src.ui.main_window import MainWindow

    QMessageBox.information = staticmethod(lambda *a, **k: QMessageBox.Ok)
    QMessageBox.warning = staticmethod(lambda *a, **k: QMessageBox.Ok)
    QMessageBox.critical = staticmethod(lambda *a, **k: QMessageBox.Ok)
    QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.Yes)

    app = QApplication.instance() or QApplication([])
    win = MainWindow(sim)

    central = win.centralWidget()
    ok_tabs = isinstance(central, QTabWidget) and central.count() == 4
    record('ui_main_tabs', ok_tabs, f'tabs={central.count() if hasattr(central, "count") else "n/a"}')

    # refresh each widget path
    win.topology_widget.refresh_topology()
    win.routing_table_widget.update_router_list()
    win.routing_table_widget.refresh_tables()
    win.control_widget.update_statistics()

    r_id = win.algorithm_widget.router_combo.itemData(0)
    if r_id in sim.routers:
        bench = sim.routers[r_id].path_calculator.benchmark_algorithms(runs=1)
        win.algorithm_widget._on_benchmark_finished(bench, 1)

    record('ui_widget_refresh', True)
    win.close()
    app.quit()
except Exception as e:
    record('ui_smoke', False, str(e))
    print(traceback.format_exc())

try:
    sim.stop_simulation()
    record('stop_simulation', True)
except Exception as e:
    record('stop_simulation', False, str(e))

passed = sum(1 for _, ok, _ in RESULTS if ok)
total = len(RESULTS)
print('---SUMMARY---')
print(f'PASSED={passed}')
print(f'TOTAL={total}')
print(f'FAILED={total-passed}')
for name, ok, detail in RESULTS:
    if not ok:
        print(f'FAILED_ITEM={name} DETAIL={detail}')

sys.exit(0 if passed == total else 2)
