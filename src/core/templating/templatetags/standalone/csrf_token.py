from jinja2_simple_tags import StandaloneTag


class CSRFTokenTag(StandaloneTag):
    safe_output = True
    tags = {"csrf_token"}

    def render(self):
        csrf_token = self.context.get("csrf_token")
        return f'<input type="hidden" name="csrf_token" value="{csrf_token}"/>'
