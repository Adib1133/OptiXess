"""
Intel Arc Signature Multi-Stream Real-Time Translation Pipeline Visualizer.
Visually diagrams the three simultaneous translation streams terminating at
Intel® XeSS (libxess.dll), XeSS Frame Generation (libxessfg.dll), and Intel® XeLL (libxell.dll).
"""

import customtkinter as ctk

class PipelineView(ctk.CTkFrame):
    """Intel Arc Styled visual diagram showing real-time translation proxy dataflow."""

    def __init__(
        self,
        master,
        starting_upscaler="DLSS",
        frame_gen=True,
        reflex_to_xell=True,
        quality="Quality",
        **kwargs
    ):
        super().__init__(master, fg_color=("#121622", "#0D111A"), corner_radius=12, border_width=1, border_color="#1F293D", **kwargs)

        self.starting_upscaler = starting_upscaler
        self.frame_gen = frame_gen
        self.reflex_to_xell = reflex_to_xell
        self.quality = quality
        self.hook_name = "dxgi.dll"

        self._build_ui()

    def _build_ui(self):
        for child in self.winfo_children():
            child.destroy()

        # Top Header Bar (Intel Arc Style)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(10, 6))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_frame,
            text="⚡ INTEL® ARC RENDERING PIPELINE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00C7FD"
        )
        title.pack(side="left")

        suite_badge = ctk.CTkLabel(
            title_frame,
            text=" CONFIGURATION PREVIEW ",
            font=ctk.CTkFont(size=8, weight="bold"),
            fg_color="#0071C5",
            corner_radius=4,
            text_color="#FFFFFF"
        )
        suite_badge.pack(side="left", padx=8)

        sub = ctk.CTkLabel(
            header,
            text="Requested backend: Intel XeSS • confirm activation in-game",
            font=ctk.CTkFont(size=10),
            text_color="#8E9297"
        )
        sub.pack(side="right")

        # Container for the 3 streams
        streams_container = ctk.CTkFrame(self, fg_color="transparent")
        streams_container.pack(fill="x", padx=12, pady=(4, 12))

        # Stream 1: Upscaling
        in_color = "#76B900" if self.starting_upscaler.upper() == "DLSS" else "#ED1C24"
        in_name = "NVIDIA DLSS" if self.starting_upscaler.upper() == "DLSS" else "AMD FSR 2/3"
        self._create_stream_row(
            streams_container,
            stream_label="UPSCALING",
            source_title=in_name,
            source_sub="Native Engine Calls",
            source_color=in_color,
            proxy_title=f"OptiScaler Proxy ({self.hook_name})",
            proxy_sub="DirectX & NVNGX Interception",
            target_title="Intel® XeSS Super Sampling",
            target_sub=f"libxess.dll ({self.quality})",
            target_color="#00C7FD",
            enabled=True
        )

        # Stream 2: Frame Generation (libxess_fg.dll)
        if self.frame_gen:
            self._create_stream_row(
                streams_container,
                stream_label="FRAME GEN",
                source_title="DLSSG 3 / FSR 3 FG",
                source_sub="Native Frame Interpolation Calls",
                source_color="#9B59B6",
                proxy_title="OptiScaler FG Interceptor",
                proxy_sub="Cadence & Optical Vector Pacing",
                target_title="Intel® XeSS Frame Generation",
                target_sub="libxess_fg.dll (AI Interpolated)",
                target_color="#00A3E0",
                enabled=True
            )

        # Stream 3: Low Latency (libxell.dll)
        if self.reflex_to_xell:
            self._create_stream_row(
                streams_container,
                stream_label="LATENCY",
                source_title="NVIDIA Reflex",
                source_sub="Low-Latency Driver Markers",
                source_color="#E67E22",
                proxy_title="Reflex ➔ XeLL Bridge",
                proxy_sub="Direct Queue Translation",
                target_title="Intel® XeLL (Xe Low Latency)",
                target_sub="libxell.dll (Direct Queue Drain)",
                target_color="#3ED598",
                enabled=True
            )

        # Stream 4: GPU Spoofing (fakenvapi.dll) for Intel Arc
        self._create_stream_row(
            streams_container,
            stream_label="GPU SPOOF",
            source_title="Engine Hardware Check",
            source_sub="DLSS/Reflex Availability Query",
            source_color="#F59E0B",
            proxy_title="FakeNvapi Spoofing Layer",
            proxy_sub="fakenvapi.dll (Auto NVAPI Spoof)",
            target_title="Intel® Arc Compatibility",
            target_sub="Direct Driver Passthrough",
            target_color="#0071C5",
            enabled=True
        )

    def _create_stream_row(
        self,
        parent,
        stream_label,
        source_title,
        source_sub,
        source_color,
        proxy_title,
        proxy_sub,
        target_title,
        target_sub,
        target_color,
        enabled
    ):
        row = ctk.CTkFrame(parent, fg_color=("#181E2C", "#131824"), corner_radius=8, border_width=1, border_color="#1E2738")
        row.pack(fill="x", pady=3)

        # Label tag
        tag_frame = ctk.CTkFrame(row, width=80, fg_color="transparent")
        tag_frame.pack(side="left", padx=8, pady=6)
        lbl = ctk.CTkLabel(
            tag_frame,
            text=stream_label,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#00C7FD"
        )
        lbl.pack(anchor="center")

        # Source Box
        src_card = ctk.CTkFrame(row, fg_color=("#0F131C", "#0B0E15"), corner_radius=6, border_width=1, border_color=source_color)
        src_card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        ctk.CTkLabel(src_card, text=source_title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#FFFFFF").pack(anchor="w", padx=8, pady=(4, 0))
        ctk.CTkLabel(src_card, text=source_sub, font=ctk.CTkFont(size=8), text_color="#8E9297").pack(anchor="w", padx=8, pady=(0, 4))

        # Arrow
        ctk.CTkLabel(row, text="➔", font=ctk.CTkFont(size=14, weight="bold"), text_color="#0071C5").pack(side="left", padx=2)

        # Proxy Middleware Box
        proxy_card = ctk.CTkFrame(row, fg_color=("#0F131C", "#0B0E15"), corner_radius=6, border_width=1, border_color="#0071C5")
        proxy_card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        ctk.CTkLabel(proxy_card, text=proxy_title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#00C7FD").pack(anchor="w", padx=8, pady=(4, 0))
        ctk.CTkLabel(proxy_card, text=proxy_sub, font=ctk.CTkFont(size=8), text_color="#8E9297").pack(anchor="w", padx=8, pady=(0, 4))

        # Arrow
        ctk.CTkLabel(row, text="➔", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00C7FD").pack(side="left", padx=2)

        # Intel Target Endpoint Box
        tgt_card = ctk.CTkFrame(row, fg_color=("#0F131C", "#0B0E15"), corner_radius=6, border_width=1, border_color=target_color)
        tgt_card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        ctk.CTkLabel(tgt_card, text=target_title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#FFFFFF").pack(anchor="w", padx=8, pady=(4, 0))
        ctk.CTkLabel(tgt_card, text=target_sub, font=ctk.CTkFont(size=8, weight="bold"), text_color=target_color).pack(anchor="w", padx=8, pady=(0, 4))

    def update_pipeline(
        self,
        starting_upscaler: str,
        frame_gen: bool,
        reflex_to_xell: bool,
        quality: str,
        hook_name: str = "dxgi.dll + nvngx.dll"
    ):
        """Updates pipeline representation with new multi-stream parameters."""
        self.starting_upscaler = starting_upscaler
        self.frame_gen = frame_gen
        self.reflex_to_xell = reflex_to_xell
        self.quality = quality
        self.hook_name = hook_name
        self._build_ui()
