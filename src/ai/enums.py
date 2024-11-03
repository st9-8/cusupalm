from core.enums import CustomEnum


class DataType(CustomEnum):
    TEXT = 'TEXT'
    PDF = 'PDF'
    MARKDOWN = 'MARKDOWN'
    WEB_LINK = 'WEB_LINK'
    UNKNOWN = 'UNKNOWN'


class DataSourceType(CustomEnum):
    WEB = 'WEB'
    APP_FAQ = 'FAQ'
    APP_GUIDE = 'GUIDE'
    APP_TICKET = 'TICKET'
    APP_TUTORIAL = 'TUTORIAL'


