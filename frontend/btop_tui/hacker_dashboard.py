import asyncio
import json
import random
from collections import deque
import websockets

from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Static, Sparkline, DataTable, ProgressBar

class HackerTUI(App):
    """AI PoisonGuard - Monochrome btop-style Terminal UI."""
    
    CSS = """
    Screen {
        background: #000000;
        layout: grid;
        grid-size: 10 10;
        grid-gutter: 0;
        padding: 0;
        color: #aaaaaa;
    }
    
    /* Layout Mapping */
    #top-pane { column-span: 10; row-span: 4; layout: horizontal; }
    #bottom-left { column-span: 3; row-span: 6; layout: vertical; }
    #bottom-right { column-span: 7; row-span: 6; }
    
    /* Universal Box Styling */
    .box {
        border: solid #444444;
        background: #000000;
        padding: 0 1;
        height: 100%;
    }
    
    #cpp-graph-box { width: 75%; border-right: none; }
    #cpp-stats-box { width: 25%; }
    
    /* Sparkline monochrome tuning */
    Sparkline { height: 100%; margin-top: 1; }
    Sparkline > .sparkline--max-color { color: #ffffff; }
    Sparkline > .sparkline--min-color { color: #444444; }
    
    /* Progress bars for Hardware */
    ProgressBar { width: 100%; height: 1; margin-bottom: 1; }
    ProgressBar > .progress--bar { color: #aaaaaa; background: #222222; }
    
    /* DataTable tuning */
    DataTable { background: #000000; color: #aaaaaa; }
    DataTable > .datatable--header { background: #111111; color: #ffffff; text-style: bold; }
    """

    BINDINGS = [("q", "quit", "Quit TUI")]

    def __init__(self):
        super().__init__()
        self.cpp_history = deque([0]*100, maxlen=100)
        self.rl_history = deque([0]*30, maxlen=30)

    def compose(self) -> ComposeResult:
        # TOP ROW: Ingestion Engine
        with Horizontal(id="top-pane"):
            with Vertical(classes="box", id="cpp-graph-box") as v1:
                v1.border_title = "mmap_core ▼ ingestion_speed"
                yield Sparkline(id="spark-cpp", summary_function=max)
            
            with Vertical(classes="box", id="cpp-stats-box") as v2:
                v2.border_title = "sys ▼ totals"
                yield Static("Status: [bold white]LINKED[/bold white]", id="txt-status")
                yield Static("\n[#888888]Rate:[/] 0 GB/s", id="txt-speed")

        # BOTTOM LEFT: Hardware, Blockchain & RL Warden
        with Vertical(id="bottom-left"):
            with Vertical(classes="box", id="gpu-box") as v3:
                v3.border_title = "hw ▼ gpu_&_ledger"
                yield Static("[#888888]CUDA Cores:[/] 0%", id="txt-cuda")
                yield ProgressBar(id="bar-cuda", total=100, show_percentage=False)
                yield Static("\n[#888888]Polygon Ledger:[/] AWAITING", id="txt-ledger")

            with Vertical(classes="box", id="rl-box") as v4:
                v4.border_title = "net ▼ rl_warden"
                yield Static("[#888888]State:[/] SCANNING", id="txt-rl-state")
                yield Static("[#888888]Active Threats:[/] 0", id="txt-rl-threats")
                yield Sparkline(id="spark-rl", summary_function=max)

        # BOTTOM RIGHT: Live Process Log
        with Vertical(classes="box", id="bottom-right") as v5:
            v5.border_title = "proc ▼ layer3_scan_log"
            yield DataTable(id="table-procs", cursor_type="row")

    async def on_mount(self) -> None:
        self.title = "AI PoisonGuard"
        
        table = self.query_one(DataTable)
        table.add_columns("Batch ID", "Status", "Risk", "Rows", "Z-Score", "Influence")
        
        for i in range(25):
            self.add_table_row(table)

        asyncio.create_task(self.telemetry_loop())

    def add_table_row(self, table: DataTable):
        batch = f"b_{random.randint(10000, 99999)}"
        status = "clean" if random.random() > 0.05 else "[bold white]flagged[/]"
        risk = f"{random.uniform(0.01, 0.15):.2f}" if status == "clean" else f"[bold white]{random.uniform(0.75, 0.99):.2f}[/]"
        rows = str(random.randint(1024, 4096))
        z_score = f"{random.uniform(0.1, 1.5):.2f}" if status == "clean" else f"{random.uniform(3.5, 6.0):.2f}"
        influence = f"{random.uniform(0.001, 0.005):.4f}"
        
        if table.row_count > 40:
            table.remove_row(table.coordinate_to_cell_key(0, 0).row_key)
            
        table.add_row(batch, status, risk, rows, z_score, influence)

    async def telemetry_loop(self) -> None:
        uri = "ws://localhost:8000/ws/telemetry"
        table = self.query_one(DataTable)
        
        while True:
            try:
                async with websockets.connect(uri) as ws:
                    self.query_one("#txt-status", Static).update("Status: [bold green]LINKED TO FASTAPI[/]")
                    async for message in ws:
                        payload = json.loads(message)
                        # Match Dev 2's exact contract
                        if payload.get("type") == "TELEMETRY_UPDATE":
                            self.update_ui(payload.get("data", {}), table)
            except Exception:
                # FALLBACK MOCK MODE
                self.query_one("#txt-status", Static).update("Status: [bold #888888]MOCK MODE[/]")
                
                mock_data = {
                    "ingestion_rate": f"{random.uniform(1.0, 1.5):.1f}GB/s",
                    "cuda_utilization": f"{random.randint(40, 95)}%",
                    "active_threats": random.choice([0, 0, 1, 3]),
                    "blockchain_status": "VERIFIED",
                    "cluster_delta": [random.uniform(0.1, 0.9) for _ in range(3)]
                }
                self.update_ui(mock_data, table)
                await asyncio.sleep(0.5)

    def update_ui(self, data: dict, table: DataTable) -> None:
        # 1. Ingestion Rate (Parse "1.2GB/s" to 1.2)
        if "ingestion_rate" in data:
            rate_str = data["ingestion_rate"]
            self.query_one("#txt-speed", Static).update(f"[#888888]Rate:[/] [bold white]{rate_str}[/]")
            try:
                rate_val = float(''.join(c for c in rate_str if c.isdigit() or c == '.'))
                self.cpp_history.append(rate_val)
                self.query_one("#spark-cpp", Sparkline).data = list(self.cpp_history)
            except ValueError:
                pass

        # 2. CUDA & Blockchain (Parse "42%" to 42)
        if "cuda_utilization" in data:
            cuda_str = data["cuda_utilization"]
            self.query_one("#txt-cuda", Static).update(f"[#888888]CUDA Cores:[/] {cuda_str}")
            cuda_val = int(cuda_str.replace('%', '')) if '%' in cuda_str else 0
            self.query_one("#bar-cuda", ProgressBar).update(progress=cuda_val)

        if "blockchain_status" in data:
            b_status = data["blockchain_status"]
            color = "green" if b_status == "VERIFIED" else "red"
            self.query_one("#txt-ledger", Static).update(f"[#888888]Polygon Ledger:[/] [bold {color}]{b_status}[/]")

        # 3. RL Warden Threats
        if "active_threats" in data:
            threats = data["active_threats"]
            state_color = "red" if threats > 0 else "green"
            state_text = "ISOLATING" if threats > 0 else "SCANNING"
            
            self.query_one("#txt-rl-state", Static).update(f"[#888888]State:[/] [bold {state_color}]{state_text}[/]")
            self.query_one("#txt-rl-threats", Static).update(f"[#888888]Active Threats:[/] {threats}")
            
            if "cluster_delta" in data and data["cluster_delta"]:
                delta = data["cluster_delta"][0] 
                self.rl_history.append(delta)
                self.query_one("#spark-rl", Sparkline).data = list(self.rl_history)

        # 4. Process Log
        if data.get("active_threats", 0) > 0 or random.random() > 0.8:
            self.add_table_row(table)
            table.scroll_end(animate=False)

if __name__ == "__main__":
    app = HackerTUI()
    app.run()