"""
Componentes de UI para Streamlit.
"""

from .header import (
    render_header,
    render_sidebar_info,
    render_progress_steps,
    render_footer,
)
from .property_form import (
    render_property_form,
    render_property_summary,
)
from .work_selector import (
    render_work_selector,
    render_work_summary,
    clear_selections,
)
from .results_display import (
    render_results,
    render_download_section,
    render_empty_results,
    render_comparison,
)
from .customer_form import (
    render_customer_form,
    render_customer_summary,
    render_quick_customer_form,
)

__all__ = [
    # Header
    "render_header",
    "render_sidebar_info",
    "render_progress_steps",
    "render_footer",
    # Property Form
    "render_property_form",
    "render_property_summary",
    # Work Selector
    "render_work_selector",
    "render_work_summary",
    "clear_selections",
    # Results
    "render_results",
    "render_download_section",
    "render_empty_results",
    "render_comparison",
    # Customer Form
    "render_customer_form",
    "render_customer_summary",
    "render_quick_customer_form",
]