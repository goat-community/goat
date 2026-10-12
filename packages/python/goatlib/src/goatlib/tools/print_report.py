"""PrintReport Tool - Generate PDF/PNG reports from map layouts.

This tool uses Playwright to render map layouts in a headless browser,
generating PDF or PNG exports. Supports atlas mode for multi-page reports.

The generated files are uploaded to S3 and a presigned download URL is returned.

Usage:
    from goatlib.tools.print_report import PrintReportParams, main

    result = main(PrintReportParams(
        user_id="...",
        project_id="...",
        layout_id="...",
        format="pdf",
    ))
"""

import asyncio
import io
import json
import logging
import os
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from goatlib.config.print import print_base_url
from goatlib.config.settings import settings
from goatlib.tools.base import SimpleToolRunner
from goatlib.tools.schemas import ToolInputBase

logger = logging.getLogger(__name__)

# Default timeouts
DEFAULT_PAGE_TIMEOUT = 120000  # 120 seconds
DEFAULT_RENDER_TIMEOUT = 90000  # 90 seconds (SwiftShader WebGL rendering is slow)

# Batch size for parallel atlas rendering — configurable via ATLAS_BATCH_SIZE env var.
# Default is 2 because each page runs a full MapLibre GL map with software WebGL (SwiftShader),
# which is CPU-intensive. Recommended: 1 per CPU core.


class PrintReportParams(ToolInputBase):
    """Parameters for PrintReport tool."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-ui-sections": [
                {"id": "input", "order": 1},
                {"id": "output", "order": 2},
            ]
        }
    )

    project_id: str = Field(
        ...,
        description="ID of the project containing the report layout",
        json_schema_extra={
            "x-ui": {"section": "input", "field_order": 1, "hidden": True}
        },
    )
    layout_id: str = Field(
        ...,
        description="ID of the report layout to print",
        json_schema_extra={
            "x-ui": {"section": "input", "field_order": 2, "hidden": True}
        },
    )
    format: Literal["pdf", "png", "jpeg"] = Field(
        default="pdf",
        description="Output format (pdf, png or jpeg)",
        json_schema_extra={
            "x-ui": {
                "section": "output",
                "field_order": 1,
                "widget": "select",
                "widget_options": {
                    "options": [
                        {"value": "pdf", "label": "PDF"},
                        {"value": "png", "label": "PNG"},
                        {"value": "jpeg", "label": "JPEG"},
                    ]
                },
            }
        },
    )
    total_atlas_pages: int = Field(
        default=1,
        le=settings.print.atlas_max_pages,
        description="Total number of atlas pages to render. Ignored if atlas_page_indices is provided.",
        json_schema_extra={
            "x-ui": {"section": "output", "field_order": 2, "hidden": True}
        },
    )
    atlas_page_indices: list[int] | None = Field(
        default=None,
        description="Specific atlas page indices to render (0-based). Overrides total_atlas_pages.",
        json_schema_extra={
            "x-ui": {"section": "output", "field_order": 3, "hidden": True}
        },
    )
    layout_name: str | None = Field(
        default=None,
        description="Name of the report layout (used for output filename)",
        json_schema_extra={"x-ui": {"hidden": True}},
    )
    dpi: int = Field(
        default=300,
        description="Output resolution in DPI (72=screen, 150=low, 300=high, 600=print)",
        json_schema_extra={
            "x-ui": {
                "section": "output",
                "field_order": 4,
                "widget": "select",
                "widget_options": {
                    "options": [
                        {"value": 72, "label": "72 (Screen)"},
                        {"value": 150, "label": "150 (Low)"},
                        {"value": 300, "label": "300 (High)"},
                        {"value": 600, "label": "600 (Print)"},
                    ]
                },
            }
        },
    )
    paper_width_mm: float = Field(
        default=210.0,
        description="Paper width in millimeters",
        json_schema_extra={"x-ui": {"hidden": True}},
    )
    paper_height_mm: float = Field(
        default=297.0,
        description="Paper height in millimeters",
        json_schema_extra={"x-ui": {"hidden": True}},
    )
    file_name_template: str | None = Field(
        default=None,
        description=(
            "Template for output filenames (atlas image exports). "
            "Placeholders: {{@layout_name}}, {{@page_number}}, {{@total_pages}}, {{@feature.ATTR}}. "
            "Use '/' for folder structure in ZIP."
        ),
        json_schema_extra={"x-ui": {"hidden": True}},
    )
    access_token: str | None = Field(
        default=None,
        description="Access token for API authentication (passed by GeoAPI)",
        json_schema_extra={"x-ui": {"hidden": True}},
    )
    refresh_token: str | None = Field(
        default=None,
        description="Refresh token for renewing expired access tokens during long jobs",
        json_schema_extra={"x-ui": {"hidden": True}},
    )

    @model_validator(mode="after")
    def _page_renders(self: Self) -> Self:
        """The page must be one the browser can render at the requested DPI."""
        for name, side in (
            ("paper_width_mm", self.paper_width_mm),
            ("paper_height_mm", self.paper_height_mm),
        ):
            if not MIN_PAGE_SIDE_MM <= side <= MAX_PAGE_SIDE_MM:
                raise ValueError(
                    f"{name} must be between {MIN_PAGE_SIDE_MM:g} and {MAX_PAGE_SIDE_MM:g} mm, got {side:g}"
                )
        longest = max(self.paper_width_mm, self.paper_height_mm)
        longest_px = output_side_px(longest, self.dpi)
        if longest_px > MAX_RENDER_SIDE_PX:
            raise ValueError(
                f"{longest:g} mm at {self.dpi} DPI is {longest_px} px on its longest side; "
                f"the renderer allows at most {MAX_RENDER_SIDE_PX} px. Lower the DPI."
            )
        return self


# One side of a page, in millimetres, as the layout editor bounds a custom page.
MIN_PAGE_SIDE_MM = 50.0
MAX_PAGE_SIDE_MM = 1500.0

# The longest side an export may have in output pixels. Chromium and WebGL
# refuse canvases past 16384 px and the map frame is such a canvas; this
# leaves headroom under that. The web client hides DPI options by the same number.
MAX_RENDER_SIDE_PX = 14000

_BASE_DPI = 96
_MM_PER_INCH = 25.4


def output_side_px(mm: float, dpi: int) -> int:
    """The output pixels a side of ``mm`` millimetres comes out at, at ``dpi``."""
    return int(mm / _MM_PER_INCH * dpi)


class PrintReportOutput(BaseModel):
    """Output from PrintReport tool.

    Note: Does NOT inherit from ToolOutputBase since PrintReport
    creates a downloadable file, not a layer.
    """

    download_url: str = Field(..., description="Presigned URL to download the report")
    file_name: str = Field(..., description="Name of the generated file")
    format: str = Field(..., description="Output format (pdf or png)")
    page_count: int = Field(default=1, description="Number of pages/images generated")
    # Windmill job labels - returned at runtime for job tracking
    wm_labels: list[str] = Field(default_factory=list)


@dataclass
class RenderedPage:
    """Result from rendering a single page."""

    data: bytes
    page_index: int | None = None
    feature_properties: dict[str, str] = field(default_factory=dict)
    page_label: str = ""


def _sanitize_path_segment(value: str, allow_slash: bool = False) -> str:
    """Sanitize a string for safe use in filenames/paths.

    - Replaces invalid characters with underscores
    - Collapses consecutive underscores
    - Strips leading/trailing whitespace, dots, and underscores
    - Truncates to max_length
    """
    allowed = "-_ /" if allow_slash else "-_ "
    result = "".join(c if c.isalnum() or c in allowed else "_" for c in value)
    result = re.sub(r"_+", "_", result)  # collapse consecutive underscores
    result = result.strip().strip(".").strip("_")
    result = result.replace(" ", "_")
    return result


# Maximum filename length (without extension). Leaves room for extension + dedup suffix.
_MAX_FILENAME_LENGTH = 200


def _sanitize_filename(name: str) -> str:
    """Sanitize a fully resolved filename (may contain / for folder structure).

    Sanitizes each path segment individually, truncates long names,
    and provides a fallback for empty results.
    """
    # Split on / to preserve folder structure
    parts = name.split("/")
    sanitized_parts: list[str] = []
    for part in parts:
        clean = _sanitize_path_segment(part)
        if clean:
            # Truncate individual segments
            if len(clean) > _MAX_FILENAME_LENGTH:
                clean = clean[:_MAX_FILENAME_LENGTH].rstrip("_")
            sanitized_parts.append(clean)

    result = "/".join(sanitized_parts)
    if not result:
        result = "page"
    return result


def _resolve_file_name_template(
    template: str,
    page_number: int,
    total_pages: int,
    layout_name: str,
    feature_properties: dict[str, str],
) -> str:
    """Resolve a filename template with placeholders.

    Placeholders:
      {{@page_number}}      -> 1-based page number
      {{@total_pages}}       -> total page count
      {{@layout_name}}       -> sanitized layout name
      {{@feature.ATTR_NAME}} -> feature attribute value

    The final result is sanitized for safe filesystem use.
    """
    result = template
    result = result.replace("{{@page_number}}", str(page_number))
    result = result.replace("{{@total_pages}}", str(total_pages))
    result = result.replace("{{@layout_name}}", _sanitize_path_segment(layout_name))

    # Resolve feature attribute placeholders
    def replace_feature_attr(match: re.Match) -> str:  # type: ignore[type-arg]
        attr_name = match.group(1)
        value = feature_properties.get(attr_name, "")
        # Allow / in feature values for folder structure
        return _sanitize_path_segment(str(value), allow_slash=True)

    result = re.sub(r"\{\{@feature\.([^}]+)\}\}", replace_feature_attr, result)

    # Final sanitization of the complete resolved name
    return _sanitize_filename(result)


def _deduplicate_filenames(filenames: list[str]) -> list[str]:
    """Append _2, _3, etc. to duplicate filenames.

    Only adds a suffix when there are actual conflicts.
    First occurrence keeps its original name.
    """
    counts: dict[str, int] = {}
    result: list[str] = []

    for name in filenames:
        if name in counts:
            counts[name] += 1
            # Split at last dot to insert suffix before extension
            if "/" in name:
                # Preserve folder path
                folder, basename = name.rsplit("/", 1)
                if "." in basename:
                    base, ext = basename.rsplit(".", 1)
                    result.append(f"{folder}/{base}_{counts[name]}.{ext}")
                else:
                    result.append(f"{folder}/{basename}_{counts[name]}")
            elif "." in name:
                base, ext = name.rsplit(".", 1)
                result.append(f"{base}_{counts[name]}.{ext}")
            else:
                result.append(f"{name}_{counts[name]}")
        else:
            counts[name] = 1
            result.append(name)

    return result


class PrintReportRunner(SimpleToolRunner):
    """Runner for PrintReport tool using Playwright."""

    def __init__(self: Self) -> None:
        super().__init__()
        self._browser = None
        self._playwright = None
        self._current_access_token: str | None = None
        self._refresh_token: str | None = None
        self._keycloak_token_url: str | None = None
        self._keycloak_client_id: str | None = None
        self._keycloak_client_secret: str | None = None

    async def _get_browser(self: Self):  # noqa: ANN202
        """Get or create Playwright browser instance."""
        if self._browser is None:
            from playwright.async_api import async_playwright

            from goatlib.utils.browser_trust import ensure_extra_ca_trusted

            ensure_extra_ca_trusted()
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    # Enable WebGL for MapLibre (software rendering)
                    "--enable-unsafe-swiftshader",
                    "--use-gl=swiftshader",
                    "--use-angle=swiftshader",
                    "--ignore-gpu-blocklist",
                ],
            )
        return self._browser

    async def _close_browser(self: Self) -> None:
        """Close browser and playwright instances."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def _can_refresh_token(self: Self) -> bool:
        """Check if we have the credentials needed to refresh the access token."""
        return bool(
            self._refresh_token
            and self._keycloak_token_url
            and self._keycloak_client_id
            and self._keycloak_client_secret
        )

    async def _refresh_access_token(self: Self) -> str | None:
        """Refresh the access token using the Keycloak refresh token.

        Returns the new access token, or None if refresh failed.
        """
        if not self._can_refresh_token():
            return self._current_access_token

        try:
            import httpx

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self._keycloak_token_url,
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self._keycloak_client_id,
                        "client_secret": self._keycloak_client_secret,
                        "refresh_token": self._refresh_token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                tokens = response.json()

                self._current_access_token = tokens["access_token"]
                # Update refresh token if a new one was issued
                if tokens.get("refresh_token"):
                    self._refresh_token = tokens["refresh_token"]

                logger.info("Successfully refreshed access token")
                return self._current_access_token

        except Exception as e:
            logger.warning(f"Failed to refresh access token: {e}")
            return self._current_access_token

    def _get_report_url(
        self: Self, params: PrintReportParams, page_index: int | None = None
    ) -> str:
        """Build the report preview URL."""
        base_url = print_base_url()

        # Use the public /print route that doesn't require authentication
        url = f"{base_url}/print/{params.project_id}/{params.layout_id}"

        if page_index is not None:
            url += f"?page={page_index}"

        return url

    async def _render_page(
        self: Self,
        url: str,
        output_format: Literal["pdf", "png", "jpeg"],
        access_token: str | None = None,
        dpi: int = 300,
        paper_width_mm: float = 210.0,
        paper_height_mm: float = 297.0,
        page_index: int | None = None,
    ) -> RenderedPage:
        """Render a single page to PDF or PNG.

        The device_scale_factor is calculated to achieve the target DPI:
        - Screen renders at 96 DPI base resolution
        - device_scale_factor = target_dpi / 96
        - For 300 DPI: factor = 3.125
        - For 600 DPI: factor = 6.25

        Viewport is sized to match paper dimensions at target DPI.
        """
        browser = await self._get_browser()

        # Calculate viewport and scale factor for target DPI
        # Base screen DPI is 96
        base_dpi = 96
        mm_per_inch = 25.4

        # Calculate required pixel dimensions at target DPI
        target_width_px = int(paper_width_mm / mm_per_inch * dpi)
        target_height_px = int(paper_height_mm / mm_per_inch * dpi)

        # Calculate device scale factor to achieve target resolution
        # We use a base viewport at 96 DPI and scale up
        base_width_px = int(paper_width_mm / mm_per_inch * base_dpi)
        base_height_px = int(paper_height_mm / mm_per_inch * base_dpi)
        device_scale_factor = dpi / base_dpi

        logger.info(
            f"Rendering at {dpi} DPI: paper={paper_width_mm}x{paper_height_mm}mm, "
            f"viewport={base_width_px}x{base_height_px}px, scale={device_scale_factor:.2f}, "
            f"output={target_width_px}x{target_height_px}px"
        )

        context = await browser.new_context(
            viewport={"width": base_width_px, "height": base_height_px},
            device_scale_factor=device_scale_factor,
        )
        page = await context.new_page()

        # Capture console logs for debugging
        page.on(
            "console",
            lambda msg: logger.info(f"Browser console [{msg.type}]: {msg.text}"),
        )
        page.on("pageerror", lambda exc: logger.error(f"Browser page error: {exc}"))

        try:
            # First navigate to the base URL to set localStorage for auth token
            base_url = print_base_url()
            logger.info(f"Navigating to base URL first: {base_url}/print")
            await page.goto(
                f"{base_url}/print", wait_until="domcontentloaded", timeout=10000
            )

            # Inject access token into localStorage for API authentication
            if access_token:
                await page.evaluate(
                    f"localStorage.setItem('print_access_token', '{access_token}')"
                )
                logger.info("Injected access token into localStorage")

            # Now navigate to the actual print page
            logger.info(f"Navigating to print page: {url}")
            await page.goto(url, wait_until="networkidle", timeout=DEFAULT_PAGE_TIMEOUT)

            # Wait for the page to signal it's ready
            # The print page sets data-print-ready="true" when all elements are loaded
            try:
                await page.wait_for_selector(
                    "[data-print-ready='true']",
                    state="attached",
                    timeout=DEFAULT_RENDER_TIMEOUT,
                )
                logger.info("Page signaled ready via data-print-ready")
            except Exception as e:
                # Fallback: page didn't signal ready, check if critical elements exist
                logger.warning(
                    f"data-print-ready timeout ({DEFAULT_RENDER_TIMEOUT}ms): {e}"
                )

                # Check for the print paper element (always present)
                paper = await page.query_selector("#print-paper")
                if not paper:
                    raise RuntimeError(
                        "Print paper element not found - page failed to load"
                    )

                logger.info("Print paper found, proceeding with render")

            # Wait for network to be idle (images, tiles, fonts, etc.)
            await page.wait_for_load_state("networkidle", timeout=30000)
            logger.info("Network idle")

            # Small buffer for any final CSS/layout calculations
            await asyncio.sleep(0.5)

            # Get page dimensions and atlas metadata
            metadata = await page.query_selector("#print-metadata")
            feature_properties: dict[str, str] = {}
            page_label = ""
            if metadata:
                width_mm = await metadata.get_attribute("data-width-mm") or "210"
                height_mm = await metadata.get_attribute("data-height-mm") or "297"
                # Extract atlas feature properties for filename templates
                props_json = await metadata.get_attribute(
                    "data-atlas-feature-properties"
                )
                if props_json:
                    try:
                        raw = json.loads(props_json)
                        feature_properties = {
                            k: str(v) for k, v in raw.items() if v is not None
                        }
                    except (json.JSONDecodeError, TypeError):
                        pass
                page_label = await metadata.get_attribute("data-atlas-page-label") or ""
            else:
                width_mm = "210"
                height_mm = "297"

            if output_format == "pdf":
                # Generate PDF with actual page dimensions
                pdf_bytes = await page.pdf(
                    width=f"{width_mm}mm",
                    height=f"{height_mm}mm",
                    print_background=True,
                    margin={
                        "top": "0mm",
                        "right": "0mm",
                        "bottom": "0mm",
                        "left": "0mm",
                    },
                )
                return RenderedPage(
                    data=pdf_bytes,
                    page_index=page_index,
                    feature_properties=feature_properties,
                    page_label=page_label,
                )
            else:
                # Capture the print paper area as PNG or JPEG
                screenshot_type = "jpeg" if output_format == "jpeg" else "png"
                screenshot_kwargs = {"type": screenshot_type}
                if screenshot_type == "jpeg":
                    screenshot_kwargs["quality"] = 95

                # Use locator for more reliable element selection
                paper_locator = page.locator("#print-paper")
                if await paper_locator.count() > 0:
                    # Wait for the element to be visible
                    await paper_locator.wait_for(state="visible", timeout=5000)
                    img_bytes = await paper_locator.screenshot(**screenshot_kwargs)
                else:
                    # Fallback to full page
                    logger.warning(
                        "Print paper element not found, using full page screenshot"
                    )
                    img_bytes = await page.screenshot(
                        **screenshot_kwargs, full_page=False
                    )
                return RenderedPage(
                    data=img_bytes,
                    page_index=page_index,
                    feature_properties=feature_properties,
                    page_label=page_label,
                )

        finally:
            await context.close()

    async def _merge_pdfs(self: Self, pdf_list: list[bytes]) -> bytes:
        """Merge multiple PDFs into one."""
        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()

        for pdf_bytes in pdf_list:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    async def run_async(self: Self, params: PrintReportParams) -> PrintReportOutput:
        """Execute the print report job."""
        from goatlib.services.s3 import S3Service

        try:
            # Initialize token refresh state
            # Access/refresh tokens come from job inputs (same as existing access_token pattern)
            # Keycloak credentials come from env vars (NOT job inputs) to avoid
            # exposing secrets in Windmill's job argument storage
            self._current_access_token = params.access_token
            self._refresh_token = params.refresh_token
            keycloak_url = os.environ.get("KEYCLOAK_SERVER_URL", "")
            keycloak_realm = os.environ.get("REALM_NAME", "")
            if keycloak_url and keycloak_realm:
                self._keycloak_token_url = (
                    f"{keycloak_url}/realms/{keycloak_realm}"
                    f"/protocol/openid-connect/token"
                )
            self._keycloak_client_id = os.environ.get("KEYCLOAK_CLIENT_ID")
            self._keycloak_client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")

            # Refresh the access token immediately to start with a fresh one
            # (the original token may already be close to expiry by the time the worker starts)
            if self._can_refresh_token():
                await self._refresh_access_token()

            # Determine pages to render
            max_pages = settings.print.atlas_max_pages
            if params.atlas_page_indices is not None:
                # Specific pages requested — enforce limit
                page_indices = params.atlas_page_indices[:max_pages]
            elif params.total_atlas_pages > 1:
                # Render all atlas pages — enforce limit
                page_indices = list(range(min(params.total_atlas_pages, max_pages)))
            else:
                # Single page (no atlas or atlas with 1 page)
                page_indices = [None]

            logger.info(
                f"Rendering {len(page_indices)} pages in {params.format} format "
                f"(batch size: {settings.print.atlas_batch_size})"
            )

            # Render pages in batches
            rendered_pages: list[RenderedPage] = []

            for i in range(0, len(page_indices), settings.print.atlas_batch_size):
                batch = page_indices[i : i + settings.print.atlas_batch_size]

                # Refresh access token before each batch to prevent 401 errors
                # during long-running atlas jobs
                if i > 0 and self._can_refresh_token():
                    await self._refresh_access_token()

                tasks = []
                for page_idx in batch:
                    url = self._get_report_url(params, page_idx)
                    tasks.append(
                        self._render_page(
                            url,
                            params.format,
                            self._current_access_token,
                            params.dpi,
                            params.paper_width_mm,
                            params.paper_height_mm,
                            page_idx,
                        )
                    )

                batch_results = await asyncio.gather(*tasks)
                rendered_pages.extend(batch_results)
                logger.info(
                    f"Rendered batch {i // settings.print.atlas_batch_size + 1}"
                )

            # Generate output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            layout_name = params.layout_name or f"report_{params.layout_id}"

            # Create filename base from layout name or ID
            safe_name = (
                "".join(c if c.isalnum() or c in "-_ " else "_" for c in layout_name)
                .strip()
                .replace(" ", "_")
            )
            file_base = f"{safe_name}_{timestamp}"

            if params.format == "pdf":
                if len(rendered_pages) > 1:
                    # Merge PDFs
                    output_bytes = await self._merge_pdfs(
                        [rp.data for rp in rendered_pages]
                    )
                else:
                    output_bytes = rendered_pages[0].data

                file_name = f"{file_base}.pdf"
                content_type = "application/pdf"

            else:  # PNG or JPEG
                ext = params.format  # "png" or "jpeg"
                mime = f"image/{ext}"

                if len(rendered_pages) > 1:
                    # Resolve filenames from template (or default)
                    template = (
                        params.file_name_template or "{{@layout_name}}_{{@page_number}}"
                    )
                    total_pages = len(rendered_pages)
                    raw_names: list[str] = []
                    for idx, rp in enumerate(rendered_pages):
                        page_num = idx + 1
                        resolved = _resolve_file_name_template(
                            template,
                            page_number=page_num,
                            total_pages=total_pages,
                            layout_name=layout_name,
                            feature_properties=rp.feature_properties,
                        )
                        raw_names.append(f"{resolved}.{ext}")

                    # Deduplicate filenames (appends _2, _3 etc. on conflicts)
                    final_names = _deduplicate_filenames(raw_names)

                    # Create ZIP of images
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for rp, name in zip(rendered_pages, final_names):
                            zf.writestr(name, rp.data)
                    output_bytes = zip_buffer.getvalue()
                    file_name = f"{file_base}.zip"
                    content_type = "application/zip"
                else:
                    # Single image - use template if provided
                    if params.file_name_template:
                        rp = rendered_pages[0]
                        resolved = _resolve_file_name_template(
                            params.file_name_template,
                            page_number=1,
                            total_pages=1,
                            layout_name=layout_name,
                            feature_properties=rp.feature_properties,
                        )
                        # Strip folder structure for single files (no ZIP)
                        resolved = (
                            resolved.rsplit("/", 1)[-1] if "/" in resolved else resolved
                        )
                        file_name = f"{resolved}.{ext}"
                    else:
                        file_name = f"{file_base}.{ext}"
                    output_bytes = rendered_pages[0].data
                    content_type = mime

            # Upload to S3
            s3_service = S3Service()
            s3_key = f"exports/{params.user_id}/reports/{file_name}"

            s3_service.upload_file(
                io.BytesIO(output_bytes),
                s3_key,
                content_type=content_type,
            )

            # Generate presigned download URL
            download_url = s3_service.generate_presigned_get(
                s3_key, expires_in=86400
            )  # 24 hours

            # Build wm_labels for Windmill job tracking
            wm_labels: list[str] = []
            if params.triggered_by_email:
                wm_labels.append(params.triggered_by_email)

            return PrintReportOutput(
                download_url=download_url,
                file_name=file_name,
                format=params.format,
                page_count=len(rendered_pages),
                wm_labels=wm_labels,
            )

        finally:
            await self._close_browser()

    def run(self: Self, params: PrintReportParams) -> PrintReportOutput:
        """Synchronous wrapper for run_async."""
        return asyncio.run(self.run_async(params))


def main(params: PrintReportParams) -> dict:
    """Entry point for Windmill."""
    runner = PrintReportRunner()
    runner.init_from_env()  # Configure logging for Windmill
    result = runner.run(params)
    return result.model_dump()
