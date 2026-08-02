# Langfuse disabled for local development

class DummyLangfuse:
    def update_current_span(self, *args, **kwargs):
        pass

    def get_current_trace_id(self):
        return None

    def get_trace_url(self, trace_id=None):
        return None

langfuse = DummyLangfuse()
