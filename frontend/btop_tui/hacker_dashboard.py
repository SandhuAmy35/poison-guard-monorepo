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
    
    # CSS engineered to exactly match the btop screenshot aesthetic
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
    
    /* Specific overrides */
    #cpp-graph-box { width: 75%; border-right: none; }
    #cpp-stats-box { width: 25%; }
    
    /* Typography & Colors */
    .title { color: #ffffff; text-style: bold; }
    .label { color: #888888; }
    .value { color: #ffffff; }
    .highlight { color: #cccccc; }
    
    /* Sparkline monochrome tuning */
    Sparkline { height: 100%; margin-top: 1; }
    Sparkline > .sparkline--max-color { color: #ffffff; }
    Sparkline > .sparkline--min-color { color: #444444; }
    
    /* Progress bars for Memory/GPU */
    ProgressBar { width: 100%; height: 1; margin-bottom: 1; }
    ProgressBar > .progress--bar { color: #aaaaaa; background: #222222; }
    
    /* DataTable tuning */
    DataTable { background: #000000; color: #aaaaaa; }
    DataTable > .datatable--header { background: #111111; color: #ffffff; text-style: bold; }
    """

    BINDINGS = [("q", "quit", "Quit TUI")]

    def __init__(self):
        super().__init__()
        # Data History Windows
        self.cpp_history = deque([0]*100, maxlen=100)
        self.rl_history = deque([0.5]*30, maxlen=30)
        self.total_ingested = 0

    def compose(self) -> ComposeResult:
        # TOP ROW: Huge graph (left) + Overall Stats (right) - Mimicking CPU pane
        with Horizontal(id="top-pane"):
            with Vertical(classes="box", id="cpp-graph-box") as v1:
                v1.border_title = "mmap_core ▼ ingestion_speed"
                yield Sparkline(id="spark-cpp", summary_function=max)
            
            with Vertical(classes="box", id="cpp-stats-box") as v2:
                v2.border_title = "sys ▼ totals"
                yield Static("Status: [bold white]LINKED[/bold white]", id="txt-status")
                yield Static("\n[#888888]Rows/sec:[/] 0", id="txt-speed")
                yield Static("[#888888]Total:[/] 0", id="txt-total")
                yield Static("\n[#888888]ZeroMQ Latency:[/] 0ms", id="txt-zmq-lat")
                yield Static("[#888888]Payloads/sec:[/] 0", id="txt-zmq-speed")

        # BOTTOM LEFT: Hardware & RL Warden - Mimicking Mem/Disks pane
        with Vertical(id="bottom-left"):
            with Vertical(classes="box", id="gpu-box") as v3:
                v3.border_title = "hw ▼ rtx4070"
                yield Static("[#888888]CUDA Cores:[/] 0%", id="txt-cuda")
                yield ProgressBar(id="bar-cuda", total=100, show_percentage=False)
                yield Static("[#888888]VRAM Used:[/] 0 GiB / 12.0 GiB", id="txt-vram")
                yield ProgressBar(id="bar-vram", total=12288, show_percentage=False)
                yield Static("[#888888]Temp:[/] 0°C", id="txt-temp")

            with Vertical(classes="box", id="rl-box") as v4:
                v4.border_title = "net ▼ rl_warden"
                yield Static("[#888888]State:[/] SCANNING", id="txt-rl-state")
                yield Static("[#888888]Reward:[/] 0.000", id="txt-rl-reward")
                yield Static("[#888888]Threshold:[/] 0.000", id="txt-rl-thresh")
                yield Sparkline(id="spark-rl", summary_function=max)

        # BOTTOM RIGHT: Live Threat/Process Log - Mimicking the Process pane
        with Vertical(classes="box", id="bottom-right") as v5:
            v5.border_title = "proc ▼ layer3_scan_log"
            yield DataTable(id="table-procs", cursor_type="row")

    async def on_mount(self) -> None:
        self.title = "AI PoisonGuard"
        
        # Setup the process table
        table = self.query_one(DataTable)
        table.add_columns("Batch ID", "Status", "Risk", "Rows", "Z-Score", "Influence")
        
        # Pre-fill with some dummy process rows to make it look active immediately
        for i in range(25):
            self.add_table_row(table)

        # Start the telemetry loop
        asyncio.create_task(self.telemetry_loop())

    def add_table_row(self, table: DataTable):
        """Generates a row for the process list."""
        batch = f"b_{random.randint(10000, 99999)}"
        status = "clean" if random.random() > 0.05 else "[bold white]flagged[/]"
        risk = f"{random.uniform(0.01, 0.15):.2f}" if status == "clean" else f"[bold white]{random.uniform(0.75, 0.99):.2f}[/]"
        rows = str(random.randint(1024, 4096))
        z_score = f"{random.uniform(0.1, 1.5):.2f}" if status == "clean" else f"{random.uniform(3.5, 6.0):.2f}"
        influence = f"{random.uniform(0.001, 0.005):.4f}"
        
        # Keep table size manageable
        if table.row_count > 40:
            table.remove_row(table.coordinate_to_cell_key(0, 0).row_key)
            
        table.add_row(batch, status, risk, rows, z_score, influence)

    async def telemetry_loop(self) -> None:
        uri = "ws://localhost:8000/ws/telemetry"
        table = self.query_one(DataTable)
        
        while True:
            try:
                # Try to connect to FastAPI
                async with websockets.connect(uri) as ws:
                    self.query_one("#txt-status", Static).update("Status: [bold white]LINKED[/bold white]")
                    async for message in ws:
                        data = json.loads(message)
                        self.update_ui(data, table)
            except Exception:
                # FALLBACK MOCK MODE (Silently generate data to keep the UI looking alive)
                self.query_one("#txt-status", Static).update("Status: [bold #888888]MOCK MODE[/]")
                
                speed = random.randint(48000, 52000)
                mock_data = {
                    "cpp_speed": speed,
                    "cpp_total": self.total_ingested + speed,
                    "cuda_util": random.randint(78, 85),
                    "vram": random.randint(3500, 4100),
                    "temp": random.randint(62, 65),
                    "zmq_latency": random.randint(1, 4),
                    "zmq_payloads": random.randint(400, 450),
                    "rl_reward": random.uniform(0.85, 0.95),
                    "rl_threshold": 0.450
                }
                self.update_ui(mock_data, table)
                await asyncio.sleep(0.1) # Fast refresh for the btop feel

    def update_ui(self, data: dict, table: DataTable) -> None:
        """Parses data and updates DOM."""
        # Top Pane (C++)
        if "cpp_speed" in data:
            speed = data["cpp_speed"]
            self.total_ingested = data.get("cpp_total", self.total_ingested + speed)
            self.cpp_history.append(speed)
            
            self.query_one("#txt-speed", Static).update(f"[#888888]Rows/sec:[/] [bold white]{speed:,}[/]")
            self.query_one("#txt-total", Static).update(f"[#888888]Total:[/] {self.total_ingested:,}")
            self.query_one("#spark-cpp", Sparkline).data = list(self.cpp_history)

        # Top Pane (ZeroMQ)
        if "zmq_latency" in data:
            self.query_one("#txt-zmq-lat", Static).update(f"[#888888]ZeroMQ Latency:[/] {data['zmq_latency']}ms")
            self.query_one("#txt-zmq-speed", Static).update(f"[#888888]Payloads/sec:[/] {data['zmq_payloads']}")

        # Bottom Left (GPU)
        if "cuda_util" in data:
            vram_gb = data.get('vram', 0) / 1024
            self.query_one("#txt-cuda", Static).update(f"[#888888]CUDA Cores:[/] {data['cuda_util']}%")
            self.query_one("#bar-cuda", ProgressBar).update(progress=data['cuda_util'])
            
            self.query_one("#txt-vram", Static).update(f"[#888888]VRAM Used:[/] {vram_gb:.1f} GiB / 12.0 GiB")
            self.query_one("#bar-vram", ProgressBar).update(progress=data.get('vram', 0))
            
            self.query_one("#txt-temp", Static).update(f"[#888888]Temp:[/] {data.get('temp', 45)}°C")

        # Bottom Left (RL Warden)
        if "rl_reward" in data:
            self.rl_history.append(data["rl_reward"])
            self.query_one("#txt-rl-reward", Static).update(f"[#888888]Reward:[/] {data['rl_reward']:.4f}")
            self.query_one("#txt-rl-thresh", Static).update(f"[#888888]Threshold:[/] {data.get('rl_threshold', 0):.4f}")
            self.query_one("#spark-rl", Sparkline).data = list(self.rl_history)

        # Bottom Right (Process Log)
        # Add a new row every few ticks to simulate scanning
        if random.random() > 0.7:
            self.add_table_row(table)
            # Auto-scroll to the bottom
            table.scroll_end(animate=False)

if __name__ == "__main__":
    app = HackerTUI()
    app.run()