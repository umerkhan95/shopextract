"""Explicitly loaded one-process stdout truncation fault; never auto-collected."""
def pytest_configure(config):
    import shopextract._cli_extract as binding
    original=binding.extraction_data
    def truncated(result):
        data=original(result)
        data['products']=data['products'][:10]
        return data
    binding.extraction_data=truncated
