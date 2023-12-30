class FeretUIError(Exception):
    pass


class RequestError(FeretUIError):
    pass


class ActionError(FeretUIError):
    pass


class ActionValidatorError(ActionError):
    pass


class UnexistingAction(ActionError):
    pass


class PageError(FeretUIError):
    pass


class ResourceError(FeretUIError):
    pass


class UnexistingResource(ResourceError):
    pass


class ResourceFilterError(ResourceError):
    pass


class ResourceRouterError(ResourceError):
    pass


class ViewError(ResourceError):
    pass


class FieldError(ResourceError):
    pass


class DatasetError(FeretUIError):
    pass
