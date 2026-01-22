from django.db import models


class Gate(models.Model):
    """
    Represents a hyperspace gate.

    connections format (stored as JSON):
    [
      {"id": "RAN", "hu": "100"},
      {"id": "PRX", "hu": "90"}
    ]
    """

    id = models.CharField(
        max_length=3,
        primary_key=True,
        help_text="Gate code (e.g. SOL, PRX)"
    )

    name = models.CharField(
        max_length=128,
        null=True,
        blank=True
    )

    connections = models.JSONField(
        default=list,
        help_text="List of outgoing connections with HU distance"
    )

    class Meta:
        db_table = "gate"
        verbose_name = "Gate"
        verbose_name_plural = "Gates"

    def __str__(self):
        return f"{self.id} - {self.name}"
