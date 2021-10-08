class ServiceWizardException(Exception):
    """General SW Exception Class"""


class IncorrectParamsException(ServiceWizardException):
    """Incorrect params passed to a method"""