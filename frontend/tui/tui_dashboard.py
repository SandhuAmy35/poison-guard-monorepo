import asyncio
import json
import time
from collections import deque
import websockets
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Sparkline, DataTable, ProgressBar, Label, RichLog

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_GPU = True
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
except:
    HAS_GPU = False

class BtopTUI(App):
    CSS = """
    Screen { background: transparent; layout: grid; grid-size: 2 3; grid-columns: 2fr 3fr; grid-rows: 4fr 3fr 3fr; padding: 0; }
    #box-cpu { row-span: 1; column-span: 1; border: round #E06C75; border-title-color: #E06C75; }
    #box-mem { row-span: 1; column-span: 1; border: round #98C379; border-title-color: #98C379; }
    #box-net { row-span: 1; column-span: 1; border: round #61AFEF; border-title-color: #61AFEF; }
    
    /* We split the right side into a Table (span 2) and a Log (span 1) */
    #box-proc { row-span: 2; column-span: 1; border: round #C678DD; border-title-color: #C678DD; }
    #box-log { row-span: 1; column-span: 1; border: round #56B6C2; border-title-color: #56B6C2; }
    
    .stat-row-header { height: 3; }
    .box { background: transparent; padding: 0 1; height: 100%; }
    Label { width: 100%; }
    Sparkline { margin-top: 1; height: 100%; }
    #spark-cpp > .sparkline--max-color { color: #E06C75; }
    #spark-rl > .sparkline--max-color { color: #61AFEF; }
    ProgressBar { width: 100%; height: 1; margin-bottom: 1; }
    DataTable { background: transparent; border: none; height: 100%; }
    DataTable > .datatable--header { background: #282C34; color: #C678DD; text-style: bold; }
    RichLog { background: transparent; height: 100%; color: #ABB2BF; }
    """

    def __init__(self):
        super().__init__()
        self.cpp_history, self.rl_history = deque([0]*60, maxlen=60), deque([0]*60, maxlen=60)
        self.total_ingested, self.batch_count, self.last_tick = 0, 0, time.time()
        self.table_row_keys = [] 

    def compose(self) -> ComposeResult:
        with Vertical(classes="box", id="box-cpu"):
            yield Label("mmap_core (cpu)", classes="border-title")
            with Horizontal(classes="stat-row-header"):
                with Vertical():
                    yield Label("Status: [b green]CONNECTED[/]", id="txt-status")
                    yield Label("Rate  : [b white]0[/] rows/s", id="txt-speed")
                with Vertical():
                    yield Label("Total : [b white]0[/]", id="txt-total")
                    yield Label("ZMQLat: [b white]1[/] ms", id="txt-lat")
            yield Sparkline(id="spark-cpp", summary_function=max)

        with Vertical(classes="box", id="box-mem"):
            yield Label("hw_rtx4070 (mem)", classes="border-title")
            yield Label("CUDA Cores [b green]0%[/]", id="txt-cuda")
            yield ProgressBar(id="bar-cuda", total=100, show_percentage=False)
            yield Label("VRAM Used  [b yellow]0.0GiB[/] / 12.0GiB", id="txt-vram")
            yield ProgressBar(id="bar-vram", total=12.0, show_percentage=False)

        # --- NEW: ADDED ACCURACY & FPR TO THE TUI ---
        with Vertical(classes="box", id="box-net"):
            yield Label("rl_warden (policy metrics)", classes="border-title")
            with Horizontal(classes="stat-row-header"):
                with Vertical():
                    yield Label("Reward: [b cyan]0.000[/]", id="txt-reward")
                    yield Label("FPR   : [b red]0.00%[/]", id="txt-fpr")
                with Vertical():
                    yield Label("Epsilon: [b cyan]0.150[/]", id="txt-eps")
                    yield Label("Accuracy:[b green]0.00%[/]", id="txt-acc")
            yield Sparkline(id="spark-rl", summary_function=max)

        with Vertical(classes="box", id="box-proc"):
            yield Label("layer3_scan_log (proc)", classes="border-title")
            yield DataTable(id="table-procs", cursor_type="row")

        with Vertical(classes="box", id="box-log"):
            yield Label("rag_sidecar (logs)", classes="border-title")
            yield RichLog(id="sys-log", markup=True, wrap=True)

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("BATCH_ID", "DOMAIN", "MSE", "REWARD", "STATUS")
        self.query_one("#sys-log", RichLog).write("[b green][SYSTEM][/] RL Warden & RAG Sidecar Initialized. Awaiting telemetry...")
        self.run_worker(self.gpu_telemetry_loop(), exclusive=True)
        self.run_worker(self.ml_telemetry_loop(), exclusive=True)

    async def gpu_telemetry_loop(self) -> None:
        while True:
            if HAS_GPU:
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle)
                    mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
                    vram_gb = mem.used / (1024**3)
                    self.query_one("#txt-cuda", Label).update(f"CUDA Cores [b green]{util.gpu}%[/]")
                    self.query_one("#bar-cuda", ProgressBar).update(progress=util.gpu)
                    self.query_one("#txt-vram", Label).update(f"VRAM Used  [b yellow]{vram_gb:.1f}GiB[/] / 12.0GiB")
                    self.query_one("#bar-vram", ProgressBar).update(progress=vram_gb)
                except: pass
            await asyncio.sleep(1)

    async def ml_telemetry_loop(self) -> None:
        uri = "ws://127.0.0.1:8000/ws/dashboard"
        table = self.query_one(DataTable)
        sys_log = self.query_one("#sys-log", RichLog)
        
        while True:
            try:
                async with websockets.connect(uri, ping_interval=None) as ws:
                    self.query_one("#txt-status", Label).update("Status: [b green]CONNECTED[/]")
                    async for message in ws:
                        data = json.loads(message)
                        if data.get("type") == "TELEMETRY_UPDATE":
                            payload = data["data"]
                            now = time.time(); elapsed = now - self.last_tick
                            self.batch_count += 1; self.total_ingested += 1
                            
                            if elapsed > 0.5:
                                speed = int(self.batch_count / elapsed)
                                self.cpp_history.append(speed)
                                self.query_one("#spark-cpp", Sparkline).data = list(self.cpp_history)
                                self.query_one("#txt-speed", Label).update(f"Rate  : [b white]{speed}[/] rows/s")
                                self.query_one("#txt-total", Label).update(f"Total : [b white]{self.total_ingested}[/]")
                                self.batch_count = 0; self.last_tick = now
                            
                            rwd = payload.get("rl_reward", 0.0); eps = payload.get("rl_new_eps", 0.15)
                            self.rl_history.append(eps * 100)
                            self.query_one("#txt-reward", Label).update(f"Reward: [b cyan]{rwd:.2f}[/]")
                            self.query_one("#txt-eps", Label).update(f"Epsilon: [b cyan]{eps:.3f}[/]")
                            self.query_one("#spark-rl", Sparkline).data = list(self.rl_history)
                            
                            # --- NEW: CALCULATE AND DISPLAY LIVE ACCURACY ---
                            metrics = payload.get("metrics", {})
                            if metrics:
                                tp, tn, fp, fn = metrics.get("TP",0), metrics.get("TN",0), metrics.get("FP",0), metrics.get("FN",0)
                                total = tp + tn + fp + fn
                                fpr = (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0.0
                                acc = ((tp + tn) / total * 100) if total > 0 else 0.0
                                self.query_one("#txt-fpr", Label).update(f"FPR   : [b {'red' if fpr > 5.0 else 'green'}]{fpr:.2f}%[/]")
                                self.query_one("#txt-acc", Label).update(f"Accuracy:[b {'green' if acc > 90.0 else 'yellow'}]{acc:.2f}%[/]")

                            is_threat = payload.get("active_threats", 0) > 0
                            status = "[b red]ISOLATING[/]" if is_threat else "[green]CLEAN[/]"
                            
                            delta = payload.get("cluster_delta", [0])
                            delta_val = delta[0] if isinstance(delta, list) and len(delta) > 0 else 0.0
                            
                            batch_id_str = payload.get("batch_id", "UNK")
                            detected_domain = batch_id_str.split('_')[0] if "_" in batch_id_str else "UNK"
                            
                            row_key = table.add_row(batch_id_str, detected_domain, f"{delta_val:.4f}", f"{rwd:.2f}", status)
                            self.table_row_keys.append(row_key)
                            
                            if len(self.table_row_keys) > 50:
                                oldest_key = self.table_row_keys.pop(0)
                                table.remove_row(oldest_key)
                            table.scroll_end(animate=False)
                            
                            if is_threat:
                                log_msg = f"[b red]>> {payload.get('batch_id')}[/] {payload.get('rag_explanation', 'Neural deviation detected.')}"
                                sys_log.write(log_msg)
                            
            except Exception as e:
                error_msg = repr(e)[:30] if e else "Connection Dropped"
                self.query_one("#txt-status", Label).update(f"Status: [b red]ERR: {error_msg}[/]")
                await asyncio.sleep(1)

if __name__ == "__main__":
    BtopTUI().run()
