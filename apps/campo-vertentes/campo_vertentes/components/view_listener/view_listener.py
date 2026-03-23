from typing import Any, Callable, Dict

import solara


@solara.component_vue("view_listener.vue")
def ViewListener(
	view_data: Dict[str, Any] | None = None,
	on_view_data: Callable[[Dict[str, Any]], None] | None = None,
	children=[],
	style: Dict[str, Any] | None = None,
): ...
