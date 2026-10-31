import tkinter as tk

from app.config import get_theme


class RoundedScrollbar(tk.Canvas):
    def __init__(self, parent, command=None, width=12, bg=None, thumb_color=None, hover_color=None, **kwargs):
        t = get_theme(getattr(parent.winfo_toplevel(), "steam_theme", "dark"))
        super().__init__(parent, width=width, bg=bg or t["SCROLL_TRACK"], highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.thumb_color = thumb_color or t["SCROLL_THUMB"]
        self.hover_color = hover_color or t["SCROLL_THUMB_HOVER"]
        self.first = 0.0
        self.last = 1.0
        self.dragging = False
        self.drag_offset = 0
        self.thumb_id = None
        self.bind("<Configure>", self.redraw)
        self.bind("<Button-1>", self.mouse_down)
        self.bind("<B1-Motion>", self.mouse_drag)
        self.bind("<ButtonRelease-1>", lambda e: setattr(self, "dragging", False))
        self.bind("<Enter>", lambda e: self.itemconfigure("thumb", fill=self.hover_color) if self.thumb_id else None)
        self.bind("<Leave>", lambda e: self.itemconfigure("thumb", fill=self.thumb_color) if self.thumb_id else None)

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self.redraw()

    def redraw(self, event=None):
        self.delete("thumb")
        h = self.winfo_height()
        if h <= 1 or (self.first <= 0 and self.last >= 1):
            self.thumb_id = None
            return
        top = self.first * h
        bottom = self.last * h
        if bottom - top < 34:
            center = (top + bottom) / 2
            top, bottom = center - 17, center + 17
        top, bottom = max(3, top), min(h - 3, bottom)
        self.thumb_id = self.create_rounded_rectangle(2, top, self.winfo_width() - 2, bottom,
                                                       radius=(self.winfo_width() - 4) / 2,
                                                       fill=self.thumb_color, outline="", tags="thumb")

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        pts = [x1 + radius, y1, x2 - radius, y1, x2, y1 + radius,
               x2, y2 - radius, x2 - radius, y2, x1 + radius, y2,
               x1, y2 - radius, x1, y1 + radius]
        return self.create_polygon(pts, smooth=True, splinesteps=24, **kwargs)

    def bounds(self):
        h = self.winfo_height()
        top, bottom = self.first * h, self.last * h
        if bottom - top < 34:
            center = (top + bottom) / 2
            top, bottom = center - 17, center + 17
        return max(3, top), min(h - 3, bottom)

    def mouse_down(self, event):
        top, bottom = self.bounds()
        if top <= event.y <= bottom:
            self.dragging = True
            self.drag_offset = event.y - top
        elif self.command:
            self.command("scroll", -1 if event.y < top else 1, "pages")

    def mouse_drag(self, event):
        if not self.dragging or not self.command:
            return
        h = self.winfo_height()
        top, bottom = self.bounds()
        thumb_height = bottom - top
        usable = h - thumb_height - 6
        if usable <= 0:
            return
        fraction = (event.y - self.drag_offset - 3) / usable
        self.command("moveto", max(0, min(1, fraction)))


class RoundedCard(tk.Canvas):
    """A real rounded visual surface with an inset child content frame."""
    def __init__(self, parent, radius=24, bg=None, border=None, border_width=1, height=180, **kwargs):
        t = get_theme(getattr(parent.winfo_toplevel(), "steam_theme", "dark"))
        self.surface = bg or t["PANEL"]
        self.border = border or t["BORDER"]
        self.radius = radius
        self.border_width = border_width
        self.requested_height = height
        super().__init__(parent, bg=t["BG"], highlightthickness=0, bd=0, height=height, **kwargs)
        self.content = tk.Frame(self, bg=self.surface, bd=0, highlightthickness=0)
        self._window = self.create_window(0, 0, window=self.content, anchor="nw")
        self.bind("<Configure>", self._redraw)
        self._redraw()

    def _redraw(self, event=None):
        w = max(2, self.winfo_width())
        h = max(2, self.winfo_height())
        self.delete("surface")
        r = min(self.radius, w / 2, h / 2)
        self.create_rounded_rectangle(self.border_width, self.border_width, w - self.border_width, h - self.border_width,
                                      r, fill=self.surface, outline=self.border, width=self.border_width, tags="surface")
        inset = max(8, int(r * 0.48))
        self.coords(self._window, inset, inset)
        self.itemconfigure(self._window, width=max(1, w - inset * 2), height=max(1, h - inset * 2))

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        pts = [x1 + radius, y1, x2 - radius, y1, x2, y1 + radius,
               x2, y2 - radius, x2 - radius, y2, x1 + radius, y2,
               x1, y2 - radius, x1, y1 + radius]
        return self.create_polygon(pts, smooth=True, splinesteps=32, **kwargs)


class PillButton(tk.Canvas):
    def __init__(self, parent, text, command, primary=False, width=None, height=34):
        t = get_theme(getattr(parent.winfo_toplevel(), "steam_theme", "dark"))
        self.t = t
        self.text = text
        self.command = command
        self.primary = primary
        self.hovered = False
        self.w = width or max(92, len(text) * 8 + 28)
        self.h = height
        super().__init__(parent, width=self.w, height=self.h, bg=t["BG"], highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", lambda e: self.command())
        self.redraw()

    def redraw(self):
        self.delete("all")
        t = self.t
        fill = t["STEAM_BLUE"] if self.primary else t["PANEL_ALT"]
        if self.hovered:
            fill = t["STEAM_BLUE_HOVER"] if self.primary else t["PANEL_HOVER"]
        self.create_rounded_rectangle(1, 1, self.w - 1, self.h - 1, self.h / 2, fill=fill, outline=t["BORDER"] if not self.primary else fill)
        self.create_text(self.w / 2, self.h / 2, text=self.text, fill="#fff" if self.primary else t["TEXT"],
                         font=("Segoe UI", 8, "bold"))

    def _enter(self, _):
        self.hovered = True
        self.redraw()

    def _leave(self, _):
        self.hovered = False
        self.redraw()

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        pts = [x1 + radius, y1, x2 - radius, y1, x2, y1 + radius,
               x2, y2 - radius, x2 - radius, y2, x1 + radius, y2,
               x1, y2 - radius, x1, y1 + radius]
        return self.create_polygon(pts, smooth=True, splinesteps=28, **kwargs)


class CustomDropdown(tk.Frame):
    def __init__(self, parent, variable, values, width=15, command=None):
        t = get_theme(getattr(parent.winfo_toplevel(), "steam_theme", "dark"))
        super().__init__(parent, bg=t["PANEL_ALT"], highlightthickness=1, highlightbackground=t["BORDER"], bd=0)
        self.variable = variable
        self.values = list(values)
        self.width = width
        self.command = command
        self.popup = None
        self.opened = False
        self.label = tk.Label(self, text=variable.get(), bg=t["PANEL_ALT"], fg=t["TEXT"], anchor="w",
                              font=("Segoe UI", 8, "bold"), padx=10, cursor="hand2")
        self.label.pack(side="left", fill="both", expand=True, ipady=5)
        self.arrow = tk.Label(self, text="▾", bg=t["PANEL_ALT"], fg=t["MUTED"], font=("Segoe UI Symbol", 9), width=3, cursor="hand2")
        self.arrow.pack(side="right", fill="y")
        for w in (self.label, self.arrow, self):
            w.bind("<Button-1>", self.toggle)
        self.bind("<Destroy>", self._on_destroy)
        variable.trace_add("write", self._sync)

    def _on_destroy(self, _=None): self.close()
    def _sync(self, *_):
        if self.winfo_exists(): self.label.configure(text=self.variable.get())
    def toggle(self, _=None): self.close() if self.opened else self.open()
    def open(self):
        if self.popup and self.popup.winfo_exists(): return
        t = get_theme(getattr(self.winfo_toplevel(), "steam_theme", "dark"))
        self.update_idletasks(); self.opened = True
        self.configure(highlightbackground=t["STEAM_BLUE"])
        self.popup = tk.Toplevel(self); self.popup.overrideredirect(True); self.popup.configure(bg=t["BORDER"]); self.popup.attributes("-topmost", True)
        outer = tk.Frame(self.popup, bg=t["BORDER"], padx=1, pady=1); outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=t["PANEL"]); inner.pack(fill="both", expand=True)
        for value in self.values:
            row = tk.Label(inner, text=value, bg=t["PANEL"], fg=t["TEXT"], anchor="w", padx=10, pady=7, width=self.width,
                           font=("Segoe UI", 8), cursor="hand2")
            row.pack(fill="x")
            row.bind("<Enter>", lambda e, r=row: r.configure(bg=t["PANEL_HOVER"]))
            row.bind("<Leave>", lambda e, r=row: r.configure(bg=t["STEAM_BLUE"] if r.cget("text") == self.variable.get() else t["PANEL"]))
            row.bind("<Button-1>", lambda e, v=value: self.select(v))
        self._position_popup(); self._highlight_selected()
        self.root().bind("<Button-1>", self._outside_click, add="+")
    def root(self): return self.winfo_toplevel()
    def _position_popup(self):
        self.popup.update_idletasks(); x=self.winfo_rootx(); y=self.winfo_rooty()+self.winfo_height()+4
        self.popup.geometry(f"{max(self.winfo_width(), self.popup.winfo_reqwidth())}x{self.popup.winfo_reqheight()}+{x}+{y}")
    def _highlight_selected(self):
        if not self.popup or not self.popup.winfo_exists(): return
        t=get_theme(getattr(self.winfo_toplevel(), "steam_theme", "dark")); inner=self.popup.winfo_children()[0].winfo_children()[0]
        for row in inner.winfo_children():
            sel=row.cget("text")==self.variable.get(); row.configure(bg=t["STEAM_BLUE"] if sel else t["PANEL"], fg="#fff" if sel else t["TEXT"])
    def _outside_click(self,event):
        if not self.opened or not self.popup or not self.popup.winfo_exists(): return
        x,y=event.x_root,event.y_root
        inside=self.winfo_rootx()<=x<=self.winfo_rootx()+self.winfo_width() and self.winfo_rooty()<=y<=self.winfo_rooty()+self.winfo_height()
        px=self.popup.winfo_rootx()<=x<=self.popup.winfo_rootx()+self.popup.winfo_width() and self.popup.winfo_rooty()<=y<=self.popup.winfo_rooty()+self.popup.winfo_height()
        if not inside and not px: self.close()
    def select(self,value):
        self.variable.set(value); self.close()
        if self.command: self.command(value)
    def close(self):
        if self.popup and self.popup.winfo_exists():
            try: self.root().unbind("<Button-1>", self._outside_click)
            except Exception: pass
            self.popup.destroy()
        self.popup=None; self.opened=False
        if self.winfo_exists():
            t=get_theme(getattr(self.winfo_toplevel(), "steam_theme", "dark")); self.configure(highlightbackground=t["BORDER"]); self.arrow.configure(text="▾", fg=t["MUTED"])


class StyledDialog(tk.Toplevel):
    def __init__(self, parent, title, message, kind="info", confirm_text="OK", cancel_text=None):
        super().__init__(parent)
        self.steam_theme = getattr(parent, "steam_theme", "dark")
        t=get_theme(self.steam_theme); self.configure(bg=t["BG"]); self.resizable(False,False); self.transient(parent); self.grab_set(); self.result=False
        try:
            from app.config import ICON_FILE
            if ICON_FILE.exists(): self.iconbitmap(default=str(ICON_FILE))
        except Exception: pass
        self.title(title)
        accent={"info":t["STEAM_BLUE"],"warning":t["ORANGE"],"error":t["RED"],"question":t["STEAM_BLUE"]}.get(kind,t["STEAM_BLUE"])
        eyebrow={"info":"INFORMATION","warning":"WARNING","error":"ERROR","question":"CONFIRM ACTION"}.get(kind,"STEAM SWAPPER")
        body=tk.Frame(self,bg=t["BG"],padx=28,pady=26); body.pack(fill="both",expand=True)
        top=tk.Frame(body,bg=t["BG"]); top.pack(fill="x")
        tk.Label(top,text=eyebrow,bg=t["BG"],fg=t["MUTED"],font=("Segoe UI",7,"bold")).pack(side="left")
        tk.Label(top,text="STEAM SWAPPER",bg=t["BG"],fg=t["STEAM_BLUE_HOVER"],font=("Segoe UI",7,"bold")).pack(side="right")
        tk.Frame(body,bg=accent,height=3).pack(fill="x",pady=(12,18))
        tk.Label(body,text=title,bg=t["BG"],fg=t["TEXT"],font=("Segoe UI",16,"bold")).pack(anchor="w")
        tk.Label(body,text=message,bg=t["BG"],fg=t["MUTED"],justify="left",anchor="w",wraplength=500,font=("Segoe UI",9)).pack(fill="x",pady=(14,25))
        buttons=tk.Frame(body,bg=t["BG"]); buttons.pack(fill="x")
        if cancel_text: PillButton(buttons,cancel_text.upper(),self.cancel,primary=False).pack(side="right",padx=(8,0))
        PillButton(buttons,confirm_text.upper(),self.confirm,primary=True).pack(side="right")
        self.bind("<Escape>",lambda e:self.cancel()); self.bind("<Return>",lambda e:self.confirm()); self.update_idletasks(); self.geometry(f"{max(500,self.winfo_reqwidth())}x{self.winfo_reqheight()}")
        self.after(50,lambda:self._center(parent))
    def _center(self,parent):
        try:
            parent.update_idletasks(); x=parent.winfo_rootx()+(parent.winfo_width()-self.winfo_width())//2; y=parent.winfo_rooty()+(parent.winfo_height()-self.winfo_height())//2; self.geometry(f"+{max(0,x)}+{max(0,y)}")
        except tk.TclError: pass
    def confirm(self): self.result=True; self.destroy()
    def cancel(self): self.result=False; self.destroy()


def make_button(parent,text,command,bg,hover,fg="#f1f1f1",bold=False):
    return tk.Button(parent,text=text,command=command,bg=bg,fg=fg,activebackground=hover,activeforeground="#fff",relief="flat",bd=0,highlightthickness=0,cursor="hand2",padx=17,pady=8,font=("Segoe UI",8,"bold" if bold else "normal"))


def show_info(parent,title,message):
    d=StyledDialog(parent,title,message,"info"); parent.wait_window(d); return d.result

def show_warning(parent,title,message):
    d=StyledDialog(parent,title,message,"warning"); parent.wait_window(d); return d.result

def show_error(parent,title,message):
    d=StyledDialog(parent,title,message,"error"); parent.wait_window(d); return d.result

def ask_yes_no(parent,title,message,confirm_text="Confirm",cancel_text="Cancel"):
    d=StyledDialog(parent,title,message,"question",confirm_text,cancel_text); parent.wait_window(d); return d.result

def button(parent,text,command,primary=False):
    t=get_theme(getattr(parent.winfo_toplevel(),"steam_theme","dark"))
    return make_button(parent,text,command,bg=t["STEAM_BLUE"] if primary else t["PANEL_ALT"],hover=t["STEAM_BLUE_HOVER"] if primary else t["PANEL_HOVER"],fg="#fff" if primary else t["TEXT"],bold=primary)
