import customtkinter as ctk
from tkinter import messagebox, filedialog
import webbrowser
import time
import threading

RED        = "#FF0000"
RED_HOVER  = "#cc0000"
RED_DIM    = "#7a0000"
DARK_BG    = "#0f0f0f"
CARD_BG    = "#1a1a1a"
CARD_BG2   = "#212121"
BORDER     = "#2e2e2e"
TEXT_MUTED = "#aaaaaa"
TEXT_LINK  = "#3ea6ff"
GREEN      = "#2ecc71"
WHITE      = "#ffffff"


class Video:
    def __init__(self, title: str, duration: int, views: int):
        self.title    = title
        self.duration = duration
        self.views    = views

    def __str__(self):
        return f"{self.title} | {self.duration}s | {self.views} views"


class Playlist:
    def __init__(self, playListName: str, plID: int):
        self.playListName = playListName
        self.plID         = plID
        self.videos       = []

    def add_video(self, video: Video):
        self.videos.append(video)

    def save_playlist_to_file(self, filename: str):
        try:
            with open(filename, "w") as f:
                for v in self.videos:
                    f.write(f"{v.title},{v.duration},{v.views}\n")
            return True
        except IOError:
            return False

    def load_playlist_from_file(self, filename: str):
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) != 3:
                        continue
                    title, duration, views = parts
                    self.videos.append(Video(title, int(duration), int(views)))
            return True
        except FileNotFoundError:
            return False

    def __str__(self):
        return f"{self.playListName} (ID: {self.plID}) — {len(self.videos)} video(s)"


class Channel:
    def __init__(self):
        self.playlists = []

    def add_playlist(self, playlist: Playlist):
        self.playlists.append(playlist)

    def search_playlist(self, name: str):
        for pl in self.playlists:
            if pl.playListName.lower() == name.lower():
                return pl
        return None


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, on_done):
        super().__init__()
        self.on_done    = on_done
        self._dot_count = 0
        self._bar_val = 0.0

        self.overrideredirect(True)
        self.configure(fg_color=DARK_BG)
        self.attributes("-topmost", True)

        w, h = 480, 300
        sw   = self.winfo_screenwidth()
        sh   = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        outer = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=20,
                             border_color=BORDER, border_width=1)
        outer.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.92)

        ctk.CTkLabel(outer, text="●", font=ctk.CTkFont(size=48),
                     text_color=RED).pack(pady=(30, 0))

        ctk.CTkLabel(outer, text="YouTube Channel Manager",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=WHITE).pack(pady=(6, 0))

        self.name_label = ctk.CTkLabel(outer, text="",
                                       font=ctk.CTkFont(size=13),
                                       text_color=TEXT_MUTED)
        self.name_label.pack(pady=(4, 16))

        self.progress = ctk.CTkProgressBar(outer, width=340, height=6,
                                           fg_color=CARD_BG2,
                                           progress_color=RED)
        self.progress.pack(pady=(0, 10))
        self.progress.set(0)

        self.dot_label = ctk.CTkLabel(outer, text="Loading",
                                      font=ctk.CTkFont(size=12),
                                      text_color=TEXT_MUTED)
        self.dot_label.pack()

        ctk.CTkLabel(outer, text="Made by  Alaa Soudy",
                     font=ctk.CTkFont(size=11),
                     text_color="#555555").pack(side="bottom", pady=10)

        self._animate_name("Alaa Soudy", 0)
        self._animate_bar()

    def _animate_name(self, full_text: str, idx: int):
        if idx <= len(full_text):
            self.name_label.configure(text=full_text[:idx])
            self.after(80, self._animate_name, full_text, idx + 1)

    def _animate_bar(self):
        self._bar_val += 0.008
        if self._bar_val > 1.0:
            self.progress.set(1.0)
        else:
            self.progress.set(self._bar_val)

        self._dot_count = (self._dot_count + 1) % 4
        self.dot_label.configure(text="Loading" + "." * self._dot_count)

        if self._bar_val < 1.0:
            self.after(30, self._animate_bar)
        else:
            self.after(500, self._finish)

    def _finish(self):
        self.destroy()
        self.master.after(50, self.on_done)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Channel Manager")
        self.geometry("960x700")
        self.minsize(800, 580)
        self.configure(fg_color=DARK_BG)
        self.withdraw()

        self.channel = Channel()
        self._next_id = 1

        splash = SplashScreen(self._show_main)
        self.wait_window(splash)

    def _show_main(self):
        self._build_header()
        self._build_tabs()
        self._build_footer()
        self.deiconify()
        self._fade_in(0)

    def _fade_in(self, step: int):
        alpha = min(1.0, step * 0.07)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(20, self._fade_in, step + 1)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=20, fill="y")

        self._logo_dot = ctk.CTkLabel(left, text="●",
                                      font=ctk.CTkFont(size=22), text_color=RED)
        self._logo_dot.pack(side="left", padx=(0, 8))
        self._pulse_logo(True)

        ctk.CTkLabel(left, text="YouTube",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=WHITE).pack(side="left")
        ctk.CTkLabel(left, text=" Channel Manager",
                     font=ctk.CTkFont(size=20),
                     text_color=TEXT_MUTED).pack(side="left")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=20, fill="y")

        self.status_label = ctk.CTkLabel(right, text="",
                                         font=ctk.CTkFont(size=12),
                                         text_color=GREEN)
        self.status_label.pack(side="right", padx=(12, 0))

        ctk.CTkLabel(right, text="made by  Alaa Soudy",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(side="right")

    def _pulse_logo(self, big: bool):
        size = 26 if big else 18
        self._logo_dot.configure(font=ctk.CTkFont(size=size))
        self.after(600, self._pulse_logo, not big)

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(
            self, corner_radius=10,
            fg_color=CARD_BG,
            segmented_button_fg_color=CARD_BG2,
            segmented_button_selected_color=RED,
            segmented_button_selected_hover_color=RED_HOVER,
            segmented_button_unselected_color=CARD_BG2,
            segmented_button_unselected_hover_color=BORDER
        )
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(14, 6))
        self.tabs.add("  Playlists  ")
        self.tabs.add("  Add Video  ")
        self.tabs.add("  Search  ")
        self._build_playlists_tab()
        self._build_add_video_tab()
        self._build_search_tab()

    def _build_playlists_tab(self):
        tab = self.tabs.tab("  Playlists  ")

        top = ctk.CTkFrame(tab, fg_color=CARD_BG2, corner_radius=10)
        top.pack(fill="x", pady=(10, 6), padx=4)

        row1 = ctk.CTkFrame(top, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(14, 6))

        ctk.CTkLabel(row1, text="New playlist",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=WHITE).pack(side="left")

        self.pl_name_entry = ctk.CTkEntry(
            row1, placeholder_text="Playlist name...",
            width=220, height=34,
            fg_color=DARK_BG, border_color=BORDER, border_width=1
        )
        self.pl_name_entry.pack(side="left", padx=12)
        self.pl_name_entry.bind("<Return>", lambda e: self._create_playlist())

        ctk.CTkButton(row1, text="+ Create", width=110, height=34,
                      fg_color=RED, hover_color=RED_HOVER,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._create_playlist).pack(side="left")

        row2 = ctk.CTkFrame(top, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(row2, text="Active playlist",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=WHITE).pack(side="left")

        self.pl_selector = ctk.CTkOptionMenu(
            row2, values=["— no playlists —"],
            width=220, height=34,
            fg_color=DARK_BG, button_color=BORDER,
            button_hover_color="#3a3a3a",
            dropdown_fg_color=CARD_BG2
        )
        self.pl_selector.pack(side="left", padx=12)

        ctk.CTkButton(row2, text="⬇  Save", width=100, height=34,
                      fg_color="#1e5c1e", hover_color="#174d17",
                      command=self._save_playlist).pack(side="left", padx=(0, 6))

        ctk.CTkButton(row2, text="⬆  Load", width=100, height=34,
                      fg_color="#1a3f6f", hover_color="#142f52",
                      command=self._load_playlist).pack(side="left")

        ctk.CTkLabel(tab, text="All playlists & videos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=6, pady=(10, 4))

        self.playlist_box = ctk.CTkTextbox(
            tab, font=ctk.CTkFont(family="Courier", size=13),
            fg_color=CARD_BG2, border_color=BORDER,
            border_width=1, corner_radius=10
        )
        self.playlist_box.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.playlist_box.configure(state="disabled")

    def _create_playlist(self):
        name = self.pl_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Enter a playlist name first!")
            return
        self.channel.add_playlist(Playlist(name, self._next_id))
        self._next_id += 1
        self.pl_name_entry.delete(0, "end")
        self._refresh_selectors()
        self._refresh_playlist_box()
        self._set_status(f"Playlist '{name}' created")

    def _save_playlist(self):
        pl = self._get_active_playlist()
        if not pl:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"{pl.playListName}.txt"
        )
        if path:
            self._set_status("Saved  ✓" if pl.save_playlist_to_file(path) else "Save failed!")

    def _load_playlist(self):
        pl = self._get_active_playlist()
        if not pl:
            return
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            ok = pl.load_playlist_from_file(path)
            self._refresh_playlist_box()
            self._set_status("Loaded  ✓" if ok else "File not found!")

    def _get_active_playlist(self):
        pl = self.channel.search_playlist(self.pl_selector.get())
        if not pl:
            messagebox.showwarning("Warning", "Create a playlist first!")
        return pl

    def _refresh_playlist_box(self):
        self.playlist_box.configure(state="normal")
        self.playlist_box.delete("1.0", "end")
        if not self.channel.playlists:
            self.playlist_box.insert("end", "\n  No playlists yet. Create one above ↑\n")
        for pl in self.channel.playlists:
            self.playlist_box.insert("end", f"\n  ▶  {pl}\n")
            self.playlist_box.insert("end", "  " + "─" * 50 + "\n")
            if pl.videos:
                for v in pl.videos:
                    self.playlist_box.insert("end", f"       •  {v}\n")
            else:
                self.playlist_box.insert("end", "       (no videos)\n")
        self.playlist_box.configure(state="disabled")

    def _build_add_video_tab(self):
        tab  = self.tabs.tab("  Add Video  ")
        form = ctk.CTkFrame(tab, fg_color=CARD_BG2, corner_radius=12)
        form.pack(padx=60, pady=30, fill="x")

        ctk.CTkLabel(form, text="Add a new video",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=WHITE).pack(pady=(20, 16))

        ctk.CTkLabel(form, text="Video title",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        self.v_title = ctk.CTkEntry(
            form, placeholder_text="e.g.  Python Full Course",
            height=36, fg_color=DARK_BG,
            border_color=BORDER, border_width=1
        )
        self.v_title.pack(padx=28, pady=(4, 14), fill="x")

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=(0, 14))

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(left, text="Duration (seconds)",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w")
        self.v_duration = ctk.CTkEntry(
            left, placeholder_text="e.g. 300",
            height=36, fg_color=DARK_BG,
            border_color=BORDER, border_width=1
        )
        self.v_duration.pack(fill="x", pady=(4, 0))

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(right, text="Views",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w")
        self.v_views = ctk.CTkEntry(
            right, placeholder_text="e.g. 15000",
            height=36, fg_color=DARK_BG,
            border_color=BORDER, border_width=1
        )
        self.v_views.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(form, text="Add to playlist",
                     font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=28)
        self.v_pl_selector = ctk.CTkOptionMenu(
            form, values=["— no playlists —"],
            height=36, width=280,
            fg_color=DARK_BG, button_color=BORDER,
            button_hover_color="#3a3a3a",
            dropdown_fg_color=CARD_BG2
        )
        self.v_pl_selector.pack(padx=28, pady=(4, 16), anchor="w")

        self._add_btn = ctk.CTkButton(
            form, text="+ Add Video", height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=RED, hover_color=RED_HOVER,
            command=self._add_video
        )
        self._add_btn.pack(padx=28, pady=(0, 24), fill="x")

    def _add_video(self):
        title    = self.v_title.get().strip()
        duration = self.v_duration.get().strip()
        views    = self.v_views.get().strip()
        pl_name  = self.v_pl_selector.get()

        if not title:
            messagebox.showwarning("Warning", "Enter a video title!")
            return
        if not duration.isdigit() or not views.isdigit():
            messagebox.showwarning("Warning", "Duration and Views must be whole numbers!")
            return
        pl = self.channel.search_playlist(pl_name)
        if not pl:
            messagebox.showwarning("Warning", "Create a playlist first from the Playlists tab!")
            return

        pl.add_video(Video(title, int(duration), int(views)))
        self.v_title.delete(0, "end")
        self.v_duration.delete(0, "end")
        self.v_views.delete(0, "end")
        self._refresh_playlist_box()
        self._set_status(f"'{title}' added to '{pl_name}'")
        self._flash_button(self._add_btn)

    def _flash_button(self, btn, step=0):
        colors = [GREEN, RED_HOVER, RED]
        if step < len(colors):
            btn.configure(fg_color=colors[step])
            self.after(120, self._flash_button, btn, step + 1)

    def _build_search_tab(self):
        tab         = self.tabs.tab("  Search  ")
        search_card = ctk.CTkFrame(tab, fg_color=CARD_BG2, corner_radius=10)
        search_card.pack(fill="x", padx=4, pady=(10, 8))

        row = ctk.CTkFrame(search_card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(row, text="Search by name",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=WHITE).pack(side="left")

        self.search_entry = ctk.CTkEntry(
            row, placeholder_text="Playlist name...",
            width=280, height=36,
            fg_color=DARK_BG, border_color=BORDER, border_width=1
        )
        self.search_entry.pack(side="left", padx=12)
        self.search_entry.bind("<Return>", lambda e: self._search())

        ctk.CTkButton(row, text="Search", width=110, height=36,
                      fg_color=RED, hover_color=RED_HOVER,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._search).pack(side="left")

        ctk.CTkLabel(tab, text="Results",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=6, pady=(4, 4))

        self.search_result = ctk.CTkTextbox(
            tab, font=ctk.CTkFont(family="Courier", size=13),
            fg_color=CARD_BG2, border_color=BORDER,
            border_width=1, corner_radius=10
        )
        self.search_result.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.search_result.configure(state="disabled")

    def _search(self):
        name = self.search_entry.get().strip()
        if not name:
            return
        pl = self.channel.search_playlist(name)
        self.search_result.configure(state="normal")
        self.search_result.delete("1.0", "end")
        if pl:
            self.search_result.insert("end", f"\n  ▶  Found: {pl}\n")
            self.search_result.insert("end", "  " + "─" * 50 + "\n")
            if pl.videos:
                for v in pl.videos:
                    self.search_result.insert("end", f"       •  {v}\n")
            else:
                self.search_result.insert("end", "       (no videos)\n")
            self._set_status(f"Found '{pl.playListName}'")
        else:
            self.search_result.insert("end", f"\n  No playlist named '{name}' was found.\n")
            self._set_status(f"'{name}' not found")
        self.search_result.configure(state="disabled")

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=38)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self._footer_name = ctk.CTkLabel(footer, text="",
                                         font=ctk.CTkFont(size=11),
                                         text_color=TEXT_MUTED)
        self._footer_name.pack(side="left", padx=(16, 4))
        self._type_footer("Made by  Alaa Soudy  •", 0)

        for text, url in [
            ("GitHub",    "https://github.com/AlaaSoudy/python-projects"),
            ("LinkedIn",  "https://www.linkedin.com/in/alaa-soudy-65378a288/"),
            ("Portfolio", "https://my-portfolio-b3s7.vercel.app"),
        ]:
            lbl = ctk.CTkLabel(footer, text=text,
                               font=ctk.CTkFont(size=11, underline=True),
                               text_color=TEXT_LINK, cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            lbl.bind("<Enter>", lambda e, l=lbl: l.configure(text_color=WHITE))
            lbl.bind("<Leave>", lambda e, l=lbl: l.configure(text_color=TEXT_LINK))

            ctk.CTkLabel(footer, text="•",
                         font=ctk.CTkFont(size=11),
                         text_color=BORDER).pack(side="left")

    def _type_footer(self, full: str, idx: int):
        self._footer_name.configure(text=full[:idx])
        if idx < len(full):
            self.after(55, self._type_footer, full, idx + 1)

    def _refresh_selectors(self):
        names = [pl.playListName for pl in self.channel.playlists]
        opts  = names if names else ["— no playlists —"]
        self.pl_selector.configure(values=opts)
        self.v_pl_selector.configure(values=opts)
        if names:
            self.pl_selector.set(names[-1])
            self.v_pl_selector.set(names[-1])

    def _set_status(self, msg: str):
        self.status_label.configure(text=f"✓  {msg}")
        self.after(3000, lambda: self.status_label.configure(text=""))


if __name__ == "__main__":
    app = App()
    app.mainloop()