class OrganizationMemberError(Exception):
    pass


class OrganizationMemberNotFoundError(OrganizationMemberError):
    pass


class OrganizationMemberAlreadyExistsError(OrganizationMemberError):
    pass


class OrganizationUserNotFoundError(OrganizationMemberError):
    pass


class OrganizationMemberPermissionError(OrganizationMemberError):
    pass


class LastOrganizationOwnerError(OrganizationMemberError):
    pass
