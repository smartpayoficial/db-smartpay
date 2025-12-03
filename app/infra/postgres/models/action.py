from enum import Enum

from tortoise import fields
from tortoise.models import Model


class ActionState(str, Enum):
    APPLIED = "applied"
    PENDING = "pending"
    FAILED = "failed"


class ActionType(str, Enum):
    BLOCK = "block"
    LOCATE = "locate"
    REFRESH = "refresh"
    NOTIFY = "notify"
    UN_ENROLL = "unenroll"
    UN_BLOCK = "unblock"
    EXCEPTION = "exception" 
    BLOCK_SIM = "block_sim"
    UNBLOCK_SIM = "unblock_s"


class Action(Model):
    action_id = fields.UUIDField(pk=True)
    device = fields.ForeignKeyField(
        "models.Device",
        related_name="actions",
        null=True,
        on_delete=fields.RESTRICT,
    )
    television = fields.ForeignKeyField(
        "models.Television",
        related_name="actions",
        null=True,
        on_delete=fields.RESTRICT,
    )
    state = fields.CharEnumField(ActionState, default=ActionState.PENDING)
    applied_by = fields.ForeignKeyField("models.User", related_name="applied_actions")
    action = fields.CharEnumField(ActionType)
    description = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "action"

    def __str__(self):
        return (
            f"{self.action} on {self.device_id} by {self.applied_by_id} ({self.state})"
        )
