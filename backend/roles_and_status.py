import enum

class ForumRoles(enum.Enum):
    ADMIN = 'ADMIN'
    MODERATOR = 'MODERATOR'
    USER = 'USER'

class UserStatus(enum.Enum):
    # No restrictions
    NORMAL = 'NORMAL'
    # Can't read or post
    BANNED = 'BANNED'
    # Read only
    PROBATION = 'PROBATION'
    # TODO User restricted to reading / posting certain forums only
    RESTRICTED = 'RESTRICTED'
    # Flags problem user
    WATCH = 'WATCH'