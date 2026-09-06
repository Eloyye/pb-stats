# Use Python for coordination and a separate inference worker

Use a Python/FastAPI coordinator and separate Python inference process for the first benchmark-driven version, with uv, Ruff, and ty as the Python toolchain. A Rust coordinator was considered, but Python keeps backend contracts and model experimentation in one language while the model pipeline is unsettled; no coordinator performance bottleneck has been measured. Separating inference from the browser and request lifecycle preserves interactive review and lets worker failures leave durable human corrections intact.
