class IngestionError(Exception):
    pass

class DocumentLoadError(IngestionError):
    pass

class ChunkingError(IngestionError):
    pass

class EmbeddingError(IngestionError):
    pass

class IndexBuildError(IngestionError):
    pass

class ConfigError(Exception):
    pass