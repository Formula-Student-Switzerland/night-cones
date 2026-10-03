''' Graphical tool to check the state of the night cones and to set their colors.

Start with "python NightConesGUI.py", or "python NightConesGUI.py --simulator" to start in simulator mode.
Ports can be changed with --tx-port and --rx-port. '''
import argparse
import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

try:
    import ifaddr
    import NightConesController as ncc
    import NightConesSimulator
except ImportError as e:
    tk.Tk().withdraw()
    messagebox.showerror("Night Cones", F"A required Python package is missing:\n\n{e}\n\n"
                         "Install it by running this command and start the program again:\n\npip install ifaddr")
    raise SystemExit(1)

AUTO_REFRESH_MS = 10000

# Simulated cones in simulator mode: one cone is stuck on its color, one is offline and every cone
# misses 20 % of the frames, so retries and error reports can be tried out.
SIM_CONE_IDS = [0, 0, 1, 1, 2, 3, 4, 5, 6, 7]
SIM_STUCK = 1
SIM_OFFLINE = 1
SIM_DROP_RATE = 0.2

# (Name, Color, Brightness) of the color buttons. None keeps the brightness selected.
PRESETS = [("Red", ncc.COLOR_RED, None), ("Yellow", ncc.COLOR_YELLOW, None), ("Green", ncc.COLOR_GREEN, None),
           ("Blue", ncc.COLOR_BLUE, None), ("White", ncc.COLOR_WHITE, None), ("Off", ncc.COLOR_WHITE, 0)]

MODE_NAMES = ["Steady", "Blinking", "Blinking short", "Blinking long", "Circulating", "Circulating smooth",
              "Fade", "Rainbow fade", "Rainbow circle", "Identification"]


def hex_color(color, brightness=15):
    ''' Returns the Tk color code of how a cone looks like. '''
    if brightness == 0:
        return "#303030"
    r, g, b = ncc.color_to_rgb(color)
    return F"#{r:02x}{g:02x}{b:02x}"


class NightConesGUI(tk.Tk):

    def __init__(self, tx_port, rx_port, simulator=False):
        super().__init__()
        self.title("Night Cones Control")
        self._simulator = None
        self.geometry("1250x880")
        self.minsize(1050, 820)
        self._tx_port = tx_port
        self._rx_port = rx_port
        self._controller = None
        self._busy = False
        self._events = queue.Queue()    # Results of the worker thread, handled in the Tk main loop
        self._swatches = {}
        self._rows = {}                 # Tree item -> cone ID
        self._last_responses = {}

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=1)
        style = ttk.Style(self)
        style.configure("Big.TButton", font=("TkDefaultFont", 13, "bold"), padding=8)
        style.configure("Treeview", rowheight=24)

        self._build_connection(simulator)
        self._build_cones()
        self._build_set_color()
        self._build_log()
        self._set_connected(False)
        self._update_mode()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(50, self._poll_events)

    # ---------------------------------------------------------------- Layout

    def _build_connection(self, simulator):
        frame = ttk.LabelFrame(self, text="1. Connect", padding=8)
        frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Mode:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._mode_select_var = tk.StringVar(value="sim" if simulator else "real")
        modes = ttk.Frame(frame)
        modes.grid(row=0, column=1, sticky="w")
        self._mode_buttons = [
            ttk.Radiobutton(modes, text="Real cones", value="real", variable=self._mode_select_var,
                            command=self._update_mode),
            ttk.Radiobutton(modes, text="Simulator (test without cones)", value="sim", variable=self._mode_select_var,
                            command=self._update_mode)]
        for button in self._mode_buttons:
            button.pack(side="left", padx=(0, 16))

        ttk.Label(frame, text="Network:").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0))
        self._network_var = tk.StringVar()
        self._network_box = ttk.Combobox(frame, textvariable=self._network_var, state="readonly")
        self._network_box.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        self._connect_button = ttk.Button(frame, text="Connect", command=self._toggle_connection)
        self._connect_button.grid(row=1, column=2, padx=6, pady=(6, 0))
        self._connection_label = tk.Label(frame, font=("TkDefaultFont", 11, "bold"))
        self._connection_label.grid(row=1, column=3, padx=6, pady=(6, 0))
        self._network_hint = ttk.Label(frame, foreground="#b06000")
        self._network_hint.grid(row=2, column=1, columnspan=3, sticky="w", pady=(4, 0))

        self._adapters = ncc.NightConesController.adapter_ips()
        self._network_names = [F"{ip.ip}  ({name})" for name, ip in self._adapters]
        # Preselect the cone network, otherwise the first adapter that is not localhost
        preferred = [i for i, (_, ip) in enumerate(self._adapters) if ip.ip.startswith(ncc.IP_PREFIX)]
        others = [i for i, (_, ip) in enumerate(self._adapters) if ip.ip != "127.0.0.1"]
        self._cone_network_found = bool(preferred)
        self._default_network = (preferred or others or [0])[0] if self._adapters else -1

        # Shown above everything in simulator mode, so nobody confuses it with the real cones
        self._sim_banner = tk.Label(self, text="SIMULATOR MODE  -  no real cones are controlled",
                                    bg="#ffd24d", fg="#402800", font=("TkDefaultFont", 12, "bold"), pady=4)

    def _build_cones(self):
        frame = ttk.LabelFrame(self, text="2. Cones", padding=8)
        frame.grid(row=2, column=0, sticky="nsew", padx=(8, 4), pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        top = ttk.Frame(frame)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        self._refresh_button = ttk.Button(top, text="⟳ Refresh", command=self._refresh)
        self._refresh_button.pack(side="left")
        self._auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Refresh automatically", variable=self._auto_refresh_var).pack(side="left", padx=10)
        self._summary_label = ttk.Label(top, font=("TkDefaultFont", 11, "bold"))
        self._summary_label.pack(side="right")

        columns = ("address", "status", "color", "brightness", "mode", "battery", "signal", "temp")
        self._tree = ttk.Treeview(frame, columns=columns, selectmode="extended")
        headings = {"#0": ("ID", 60), "address": ("Address", 120), "status": ("Status", 160), "color": ("Color", 60),
                    "brightness": ("Brightness", 75), "mode": ("Mode", 95), "battery": ("Battery", 60),
                    "signal": ("Signal", 70), "temp": ("Temp.", 55)}
        for column, (text, width) in headings.items():
            self._tree.heading(column, text=text)
            self._tree.column(column, width=width, minwidth=40, stretch=column in ("address", "status"))
        self._tree.tag_configure("missing", foreground="#c00000")
        self._tree.grid(row=1, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        ttk.Label(frame, foreground="#606060", text="Tip: click cones in the list (Ctrl/Shift for several) to select them for step 3."
                  ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _build_set_color(self):
        frame = ttk.LabelFrame(self, text="3. Set color", padding=8)
        frame.grid(row=2, column=1, sticky="nsew", padx=(4, 8), pady=4)
        frame.columnconfigure(1, weight=1)

        # Which cones
        ttk.Label(frame, text="Which cones?", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        self._which_var = tk.StringVar(value="ids")
        ttk.Radiobutton(frame, text="All connected cones", value="all", variable=self._which_var,
                        command=self._update_preview).grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(frame, text="Cone IDs:", value="ids", variable=self._which_var,
                        command=self._update_preview).grid(row=2, column=0, sticky="w")
        self._ids_var = tk.StringVar()
        self._ids_var.trace_add("write", lambda *args: (self._which_var.set("ids"), self._update_preview()))
        self._ids_entry = tk.Entry(frame, textvariable=self._ids_var, font=("TkDefaultFont", 12))
        self._ids_entry.grid(row=2, column=1, sticky="ew")
        self._ids_hint = ttk.Label(frame, text="e.g.  3   or   1,4,7   or   10-20")
        self._ids_hint.grid(row=3, column=1, sticky="w")

        # Color
        ttk.Label(frame, text="Color", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 2))
        presets = ttk.Frame(frame)
        presets.grid(row=5, column=0, columnspan=2, sticky="ew")
        self._preset_buttons = []
        for i, (name, color, brightness) in enumerate(PRESETS):
            presets.columnconfigure(i, weight=1)
            button = tk.Label(presets, text=name, bg=hex_color(color, 15 if brightness is None else brightness),
                              fg="white" if name in ("Blue", "Off", "Red") else "black", font=("TkDefaultFont", 10, "bold"),
                              height=2, relief="raised", bd=3, cursor="hand2")
            button.grid(row=0, column=i, sticky="ew", padx=2)
            button.bind("<Button-1>", lambda event, c=color, b=brightness: self._select_preset(c, b))
            self._preset_buttons.append((button, color, brightness))
        custom = ttk.Frame(frame)
        custom.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        custom.columnconfigure(1, weight=1)
        ttk.Label(custom, text="Other color:").grid(row=0, column=0)
        self._color_var = tk.IntVar(value=ncc.COLOR_RED)
        ttk.Scale(custom, from_=0, to=255, variable=self._color_var,
                  command=lambda v: (self._color_var.set(int(float(v))), self._update_preview())).grid(row=0, column=1, sticky="ew", padx=6)
        self._color_number = ttk.Label(custom, width=4)
        self._color_number.grid(row=0, column=2)

        # Brightness
        ttk.Label(frame, text="Brightness", font=("TkDefaultFont", 10, "bold")).grid(row=7, column=0, sticky="w", pady=(10, 0))
        self._brightness_var = tk.IntVar(value=ncc.BRIGHTNESS_HIGH)
        bright = ttk.Frame(frame)
        bright.grid(row=7, column=1, sticky="ew", pady=(10, 0))
        bright.columnconfigure(0, weight=1)
        ttk.Scale(bright, from_=0, to=15, variable=self._brightness_var,
                  command=lambda v: (self._brightness_var.set(int(float(v))), self._update_preview())).grid(row=0, column=0, sticky="ew")
        self._brightness_number = ttk.Label(bright, width=6)
        self._brightness_number.grid(row=0, column=1)

        # Mode
        ttk.Label(frame, text="Mode", font=("TkDefaultFont", 10, "bold")).grid(row=8, column=0, sticky="w", pady=(10, 0))
        self._mode_var = tk.StringVar(value=MODE_NAMES[0])
        mode_box = ttk.Combobox(frame, textvariable=self._mode_var, values=MODE_NAMES, state="readonly")
        mode_box.grid(row=8, column=1, sticky="ew", pady=(10, 0))
        mode_box.bind("<<ComboboxSelected>>", lambda event: self._update_preview())
        self._speed_label = ttk.Label(frame, text="Cycle time")
        self._speed_label.grid(row=9, column=0, sticky="w")
        self._speed_var = tk.IntVar(value=10)
        speed = ttk.Frame(frame)
        speed.grid(row=9, column=1, sticky="ew")
        speed.columnconfigure(0, weight=1)
        self._speed_scale = ttk.Scale(speed, from_=1, to=255, variable=self._speed_var,
                                      command=lambda v: (self._speed_var.set(int(float(v))), self._update_preview()))
        self._speed_scale.grid(row=0, column=0, sticky="ew")
        self._speed_number = ttk.Label(speed, width=7)
        self._speed_number.grid(row=0, column=1)
        self._phase_label = ttk.Label(frame, text="Phase shift")
        self._phase_label.grid(row=10, column=0, sticky="w")
        self._phase_var = tk.IntVar(value=0)
        phase = ttk.Frame(frame)
        phase.grid(row=10, column=1, sticky="ew")
        phase.columnconfigure(0, weight=1)
        self._phase_scale = ttk.Scale(phase, from_=0, to=255, variable=self._phase_var,
                                      command=lambda v: (self._phase_var.set(int(float(v))), self._update_preview()))
        self._phase_scale.grid(row=0, column=0, sticky="ew")
        self._phase_number = ttk.Label(phase, width=7)
        self._phase_number.grid(row=0, column=1)

        # Preview and apply
        preview = ttk.Frame(frame)
        preview.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(14, 6))
        preview.columnconfigure(1, weight=1)
        self._preview_swatch = tk.Label(preview, width=4, height=2, relief="sunken", bd=2)
        self._preview_swatch.grid(row=0, column=0, padx=(0, 8))
        self._preview_label = ttk.Label(preview, justify="left")
        self._preview_label.grid(row=0, column=1, sticky="ew")
        preview.bind("<Configure>", lambda event: self._preview_label.configure(wraplength=max(100, event.width - 70)))
        self._apply_button = ttk.Button(frame, text="Apply", style="Big.TButton", command=self._apply)
        self._apply_button.grid(row=12, column=0, columnspan=2, sticky="ew")

    def _build_log(self):
        frame = ttk.LabelFrame(self, text="Result", padding=8)
        frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=8, pady=(4, 8))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        self._banner = tk.Label(frame, anchor="w", font=("TkDefaultFont", 12, "bold"), padx=8, pady=4)
        self._banner.grid(row=0, column=0, sticky="ew")
        self._progress = ttk.Progressbar(frame, mode="indeterminate", length=160)
        self._progress.grid(row=0, column=1, padx=(8, 0))
        self._progress.grid_remove()
        self._log = scrolledtext.ScrolledText(frame, height=7, state="disabled", wrap="word")
        self._log.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(4, 0))
        self._log.tag_configure("ok", foreground="#007000")
        self._log.tag_configure("error", foreground="#c00000")
        self._log.tag_configure("warn", foreground="#b06000")

    # ---------------------------------------------------------------- Helpers

    def _swatch(self, color):
        ''' Small colored square shown in the cone list '''
        if color not in self._swatches:
            image = tk.PhotoImage(width=16, height=16)
            image.put(color, to=(0, 0, 16, 16))
            self._swatches[color] = image
        return self._swatches[color]

    def _log_line(self, text, tag=None):
        self._log.configure(state="normal")
        self._log.insert("end", F"{datetime.now().strftime('%H:%M:%S')}  {text}\n", tag)
        self._log.see("end")
        self._log.configure(state="disabled")

    def _show_banner(self, text, kind):
        colors = {"ok": ("#d8f5d8", "#005000"), "error": ("#fadada", "#a00000"), "warn": ("#fdeccc", "#804000"),
                  "info": ("#e4ecf7", "#203050")}
        bg, fg = colors[kind]
        self._banner.configure(text=text, bg=bg, fg=fg)

    def _target(self):
        ''' [Color, Brightness, LightMode, RepetitionTime, Phase] as selected '''
        mode = MODE_NAMES.index(self._mode_var.get())
        steady = mode == ncc.LIGHTMODE_CONT
        return [self._color_var.get(), self._brightness_var.get(), ncc.LightMode(mode),
                0 if steady else self._speed_var.get(), 0 if steady else self._phase_var.get()]

    def _selected_ids(self):
        ''' Returns the IDs to set, or raises ValueError with a message for the user. '''
        if self._which_var.get() == "all":
            ids = sorted({data.ID for data in self._last_responses.values()})
            if not ids:
                raise ValueError("No cone is connected. Press Refresh first.")
            return ids
        if not self._ids_var.get().strip():
            raise ValueError("Enter the cone IDs to set, or click cones in the list.")
        return ncc.parse_ids(self._ids_var.get())

    def _update_preview(self):
        target = self._target()
        self._color_number.configure(text=str(target[0]))
        self._brightness_number.configure(text="Off" if target[1] == 0 else F"{target[1]}/15")
        steady = target[2] == ncc.LightMode(ncc.LIGHTMODE_CONT)
        for widget in (self._speed_scale, self._phase_scale):
            widget.state(["disabled"] if steady else ["!disabled"])
        for widget in (self._speed_label, self._phase_label, self._speed_number, self._phase_number):
            widget.configure(foreground="#a0a0a0" if steady else "")
        self._speed_number.configure(text=F"{self._speed_var.get() / 10:.1f} s")
        self._phase_number.configure(text=F"{self._phase_var.get() * 100 // 255} %")
        for button, color, brightness in self._preset_buttons:
            active = color == target[0] and (brightness == 0) == (target[1] == 0)
            button.configure(relief="sunken" if active else "raised", bd=5 if active else 3)
        self._preview_swatch.configure(bg=hex_color(target[0], target[1]))

        try:
            ids = self._selected_ids()
            which = (F"ALL {len(ids)} connected cone IDs" if self._which_var.get() == "all"
                     else F"cone ID{'s' if len(ids) > 1 else ''} {ncc.format_ids(ids)}")
            what = ("off" if target[1] == 0 else
                    F"color {ncc.format_color(target[0])}, brightness {target[1]}, {self._mode_var.get().lower()}")
            self._preview_label.configure(text=F"Will set {which} to {what}.", foreground="")
            self._ids_entry.configure(bg="white")
            valid = True
        except ValueError as e:
            invalid_entry = self._which_var.get() == "ids" and self._ids_var.get().strip()
            self._preview_label.configure(text=str(e), foreground="#c00000" if invalid_entry else "#606060")
            self._ids_entry.configure(bg="#fadada" if invalid_entry else "white")
            valid = False
        self._apply_button.state(["!disabled"] if valid and self._controller and not self._busy else ["disabled"])

    def _select_preset(self, color, brightness):
        self._color_var.set(color)
        if brightness is not None:
            self._brightness_var.set(brightness)
        elif self._brightness_var.get() == 0:
            self._brightness_var.set(ncc.BRIGHTNESS_HIGH)
        self._update_preview()

    def _on_select(self, event):
        ids = sorted({self._rows[item] for item in self._tree.selection() if self._rows.get(item) is not None})
        if ids:
            self._ids_var.set(ncc.format_ids(ids))

    def _simulator_mode(self):
        return self._mode_select_var.get() == "sim"

    def _update_mode(self):
        if self._simulator_mode():
            self._network_box["values"] = ["Simulated cones on this computer"]
            self._network_box.current(0)
            self._network_hint.configure(text=F"{len(SIM_CONE_IDS)} simulated cones: one never changes its color, one drops out "
                                              "after the first refresh, one is offline and messages get lost sometimes.")
            self._sim_banner.grid(row=0, column=0, columnspan=2, sticky="ew")
            self.title("Night Cones Control - SIMULATOR")
        else:
            self._network_box["values"] = self._network_names
            if self._default_network >= 0:
                self._network_box.current(self._default_network)
            self._network_hint.configure(text="" if self._cone_network_found else
                                         F"No {ncc.IP_PREFIX}x network found. Connect this computer to the cone WiFi "
                                         "first, or pick the network manually.")
            self._sim_banner.grid_remove()
            self.title("Night Cones Control")

    def _set_connected(self, connected):
        if connected:
            self._connection_label.configure(text="● Connected", fg="#008000")
            self._connect_button.configure(text="Disconnect")
            self._network_box.state(["disabled"])
        else:
            self._connection_label.configure(text="● Not connected", fg="#c00000")
            self._connect_button.configure(text="Connect")
            self._network_box.state(["!disabled", "readonly"])
            self._tree.delete(*self._tree.get_children())
            self._rows = {}
            self._last_responses = {}
            self._summary_label.configure(text="")
        for button in self._mode_buttons:
            button.state(["disabled"] if connected else ["!disabled"])
        self._set_busy(False)

    def _set_busy(self, busy, text=""):
        self._busy = busy
        enabled = self._controller is not None and not busy
        self._refresh_button.state(["!disabled"] if enabled else ["disabled"])
        self._connect_button.state(["disabled"] if busy else ["!disabled"])
        if busy and text:
            self._show_banner(F"⏳ {text}", "info")
        if busy:
            self._progress.grid()
            self._progress.start(10)
        else:
            self._progress.stop()
            self._progress.grid_remove()
        self._update_preview()

    # ---------------------------------------------------------------- Worker thread

    def _run(self, text, work, done):
        ''' Runs work() in a worker thread so the window does not freeze, then done(result) in the main loop. '''
        self._set_busy(True, text)

        def worker():
            try:
                self._events.put((done, work()))
            except Exception as e:
                self._events.put((self._on_error, e))
        threading.Thread(target=worker, daemon=True).start()

    def _poll_events(self):
        try:
            while True:
                handler, value = self._events.get_nowait()
                if handler in (self._on_progress,):
                    handler(value)
                else:
                    self._set_busy(False)
                    handler(value)
        except queue.Empty:
            pass
        self.after(50, self._poll_events)

    def _on_error(self, error):
        self._show_banner("✖ Something went wrong, see below", "error")
        self._log_line(F"Error: {error}", "error")

    def _on_progress(self, text):
        self._show_banner(F"⏳ {text}", "info")
        self._log_line(text, "warn")

    # ---------------------------------------------------------------- Actions

    def _toggle_connection(self):
        if self._controller:
            self._disconnect()
            self._set_connected(False)
            self._show_banner("Disconnected", "info")
            self._log_line("Disconnected")
            return
        if self._simulator_mode():
            name, ip = "simulator", ifaddr.IP("127.0.0.1", 8, "simulator")
        elif not self._adapters or self._network_box.current() < 0:
            messagebox.showwarning("Night Cones", "Select the network the cones are connected to.")
            return
        else:
            name, ip = self._adapters[self._network_box.current()]
        try:
            if self._simulator_mode():
                self._simulator = NightConesSimulator.NightConeSimulator(
                    self._rx_port, self._tx_port, SIM_CONE_IDS, SIM_DROP_RATE, SIM_OFFLINE, SIM_STUCK,
                    drop_out=1, verbose=False)
                threading.Thread(target=self._simulator.start, daemon=True).start()
            self._controller = ncc.NightConesController()
            self._controller.connect(ip, self._tx_port, self._rx_port)
        except OSError as e:
            self._disconnect()
            messagebox.showerror("Night Cones", F"Could not connect to {ip.ip}:\n\n{e}\n\n"
                                 "Is the Night Cones CLI, the simulator or another copy of this program still running? "
                                 "Close it and try again.")
            return
        self._set_connected(True)
        self._log_line(F"Connected to {ip.ip} ({name})", "ok")
        self._refresh()
        self.after(AUTO_REFRESH_MS, self._auto_refresh)

    def _auto_refresh(self):
        if not self._controller:
            return
        if self._auto_refresh_var.get() and not self._busy:
            self._refresh(quiet=True)
        self.after(AUTO_REFRESH_MS, self._auto_refresh)

    def _refresh(self, quiet=False):
        if not self._controller or self._busy:
            return
        controller = self._controller
        self._run("" if quiet else "Asking the cones for their state...", controller.request_states,
                  lambda responses: self._show_states(responses, quiet))

    def _show_states(self, responses, quiet=False):
        if not self._controller:
            return
        self._last_responses = responses
        missing = self._controller.not_connected(responses)
        selected_ids = {self._rows.get(item) for item in self._tree.selection()}
        self._tree.delete(*self._tree.get_children())
        self._rows = {}

        rows = [(addr, data, None) for addr, data in responses.items()]
        rows += [(addr, last[1] if last else None, last[0] if last else None) for addr, last in missing.items()]
        rows.sort(key=lambda row: (row[1] is None, row[1].ID if row[1] else 0, row[0]))
        for addr, data, last_seen in rows:
            connected = last_seen is None and data is not None
            if data is None:
                values = (ncc.format_addr(addr), "✖ Never seen", "", "", "", "", "", "")
                item = self._tree.insert("", "end", text="?", image=self._swatch("#d0d0d0"), values=values, tags=("missing",))
                self._rows[item] = None
                continue
            names = [name.capitalize() for name, value in ncc.COLOR_NAMES.items() if value == data.Color]
            status = "✔ Connected" if connected else F"✖ Lost, last seen {datetime.fromtimestamp(last_seen).strftime('%H:%M')}"
            values = (ncc.format_addr(addr), status, names[0] if names else str(data.Color),
                      "Off" if data.Brightness == 0 else F"{data.Brightness}/15",
                      MODE_NAMES[data.LightMode] if data.LightMode < len(MODE_NAMES) else str(data.LightMode),
                      F"{data.SoC * 100 // 255} %", F"{ncc.signed(data.RSSI)} dBm", F"{data.Temp} °C")
            swatch = self._swatch(hex_color(data.Color, data.Brightness) if connected else "#d0d0d0")
            item = self._tree.insert("", "end", text=str(data.ID), image=swatch, values=values,
                                     tags=() if connected else ("missing",))
            self._rows[item] = data.ID
            if data.ID in selected_ids:
                self._tree.selection_add(item)

        self._summary_label.configure(text=F"{len(responses)} connected   ·   {len(missing)} not connected",
                                      foreground="#c00000" if missing else "#008000")
        self._update_preview()
        if not quiet:
            if not responses:
                self._show_banner("✖ No cone answered. Are the cones on and connected to the same WiFi?", "error")
            elif missing:
                self._show_banner(F"⚠ {len(responses)} cones connected, {len(missing)} not connected (red in the list)", "warn")
            else:
                self._show_banner(F"✔ All {len(responses)} cones connected", "ok")
            self._log_line(F"State: {len(responses)} connected, {len(missing)} not connected",
                           "warn" if missing or not responses else "ok")

    def _apply(self):
        try:
            ids = self._selected_ids()
        except ValueError as e:
            messagebox.showwarning("Night Cones", str(e))
            return
        target = self._target()
        if self._which_var.get() == "all" and not messagebox.askyesno(
                "Night Cones", F"{self._preview_label.cget('text')}\n\nContinue?"):
            return
        controller = self._controller

        def on_progress(retry, pending):
            self._events.put((self._on_progress, F"Retry {retry} of {ncc.SET_RETRIES}: cone ID(s) "
                                                 F"{ncc.format_ids(pending)} did not change yet..."))
        self._log_line(self._preview_label.cget("text"))
        self._run("Setting color and checking the cones...", lambda: controller.set_color(ids, target, on_progress),
                  lambda result: self._show_result(ids, target, result))

    def _show_result(self, ids, target, result):
        if result.changed:
            self._log_line(F"Changed: ID(s) {ncc.format_ids(result.changed)}", "ok")
        for addr, data in sorted(result.wrong.items(), key=lambda item: (item[1].ID, item[0])):
            self._log_line(F"NOT changed: ID {data.ID} at {ncc.format_addr(addr)} still shows "
                           F"color {ncc.format_color(data.Color)}, brightness {data.Brightness}, "
                           F"{ncc.format_mode(data.LightMode)}", "error")
        if result.no_answer:
            self._log_line(F"No cone answered for ID(s) {ncc.format_ids(result.no_answer)}, "
                           "the change could not be checked", "error")

        if not result.wrong and not result.no_answer:
            self._show_banner(F"✔ Done: all {len(ids)} cone ID(s) changed", "ok")
        elif not result.changed:
            self._show_banner(F"✖ Nothing changed after {ncc.SET_RETRIES} retries, see the details below", "error")
        else:
            problems = len(result.wrong) + len(result.no_answer)
            self._show_banner(F"⚠ {len(result.changed)} ID(s) changed, {problems} problem(s) after "
                              F"{ncc.SET_RETRIES} retries, see the details below", "warn")
        self._show_states(result.responses, quiet=True)

    def _disconnect(self):
        if self._controller:
            self._controller.close()
            self._controller = None
        if self._simulator:
            self._simulator.stop()
            self._simulator = None

    def _on_close(self):
        self._disconnect()
        self.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tx-port", type=int, default=ncc.UDP_TX_PORT, help="Port the cones listen on")
    parser.add_argument("--rx-port", type=int, default=ncc.UDP_RX_PORT, help="Port the cones answer to")
    parser.add_argument("--simulator", action="store_true", help="Start in simulator mode")
    args = parser.parse_args()
    NightConesGUI(args.tx_port, args.rx_port, args.simulator).mainloop()
