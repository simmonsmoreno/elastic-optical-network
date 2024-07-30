import tkinter as tk
from tkinter import ttk

class NetworkSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EON Simulator")
        self.geometry("1200x700")
        self.selected_device = None
        self.nodes = []
        self.create_widgets()

    def create_widgets(self):
        # Menu Principal
        self.create_menu()

        # Layout Principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Paleta de Dispositivos
        self.create_device_palette()

        # Área de Trabalho Principal
        self.create_main_workspace()

        # Painel de Propriedades
        self.create_properties_panel()

        # Painel de Logs
        self.create_logs_panel()

        # Painel de Controle
        self.create_control_panel()

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About")

    def create_device_palette(self):
        palette_frame = ttk.Frame(self.main_frame)
        palette_frame.grid(row=0, column=0, sticky="ns")

        palette_label = ttk.Label(palette_frame, text="Devices")
        palette_label.pack(pady=10)

        devices = ["Node", "Fiber"]
        for device in devices:
            device_button = ttk.Button(palette_frame, text=device, command=lambda d=device: self.select_device(d))
            device_button.pack(fill=tk.X, pady=5)

    def select_device(self, device):
        self.selected_device = device
        print(f"Selected device: {self.selected_device}")

    def create_main_workspace(self):
        workspace_frame = ttk.Frame(self.main_frame)
        workspace_frame.grid(row=1, column=1, sticky="nsew")

        self.canvas = tk.Canvas(workspace_frame, bg="lightgrey")
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Binding para adicionar dispositivos
        self.canvas.bind("<Button-1>", self.add_device)

    def add_device(self, event):
        if self.selected_device == "Node":
            self.add_node(event.x, event.y)
        elif self.selected_device == "Fiber" and len(self.nodes) >= 2:
            self.add_fiber()

    def add_node(self, x, y):
        node_radius = 10
        node = self.canvas.create_oval(x - node_radius, y - node_radius,
                                       x + node_radius, y + node_radius, fill="blue")
        self.nodes.append((node, x, y))
        print(f"Node added at ({x}, {y})")

    def add_fiber(self):
        if len(self.nodes) < 2:
            return

        node1 = self.nodes[-2]
        node2 = self.nodes[-1]
        self.canvas.create_line(node1[1], node1[2], node2[1], node2[2], fill="black", width=2)
        print(f"Fiber added between ({node1[1]}, {node1[2]}) and ({node2[1]}, {node2[2]})")

    def create_properties_panel(self):
        properties_frame = ttk.Frame(self.main_frame)
        properties_frame.grid(row=0, column=2, rowspan=2, sticky="ns")

        properties_label = ttk.Label(properties_frame, text="Properties")
        properties_label.pack(pady=10)

        properties_text = tk.Text(properties_frame, height=20, width=30)
        properties_text.pack()

    def create_control_panel(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        start_button = tk.Button(control_frame, text="Start", bg="green", fg="white", font=("Arial", 12, "bold"))
        start_button.pack(side=tk.LEFT, padx=10, pady=10)

        pause_button = tk.Button(control_frame, text="Pause", bg="yellow", fg="black", font=("Arial", 12, "bold"))
        pause_button.pack(side=tk.LEFT, padx=10, pady=10)

        stop_button = tk.Button(control_frame, text="Stop", bg="red", fg="white", font=("Arial", 12, "bold"))
        stop_button.pack(side=tk.LEFT, padx=10, pady=10)

    def create_logs_panel(self):
        logs_frame = ttk.Frame(self.main_frame)
        logs_frame.grid(row=2, column=1, sticky="ew")

        logs_label = ttk.Label(logs_frame, text="Logs")
        logs_label.pack(pady=10)

        logs_text = tk.Text(logs_frame, height=10)
        logs_text.pack(fill=tk.X, expand=1)

if __name__ == "__main__":
    app = NetworkSimulatorApp()
    app.mainloop()
