from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel
from zgw_consumers.api_models.constants import VertrouwelijkheidsAanduidingen
from zgw_consumers.constants import APITypes

from openforms.utils.validators import validate_rsin


class ZgwConfig(SingletonModel):
    """
    global configuration and defaults
    """

    default_zgw_api_group = models.ForeignKey(
        to="ZGWApiGroupConfig",
        on_delete=models.PROTECT,
        verbose_name=_("default ZGW API set."),
        help_text=_("Which set of ZGW APIs should be used as default."),
        null=True,
    )

    class Meta:
        verbose_name = _("ZGW API's configuration")


class ZGWApiGroupConfig(models.Model):
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("A recognisable name for this set of ZGW APIs."),
    )
    zrc_service = models.ForeignKey(
        "zgw_consumers.Service",
        verbose_name=_("Zaken API"),
        on_delete=models.PROTECT,
        limit_choices_to={"api_type": APITypes.zrc},
        related_name="zgwset_zrc_config",
        null=True,
    )
    drc_service = models.ForeignKey(
        "zgw_consumers.Service",
        verbose_name=_("Documenten API"),
        on_delete=models.PROTECT,
        limit_choices_to={"api_type": APITypes.drc},
        related_name="zgwset_drc_config",
        null=True,
    )
    ztc_service = models.ForeignKey(
        "zgw_consumers.Service",
        verbose_name=_("Catalogi API"),
        on_delete=models.PROTECT,
        limit_choices_to={"api_type": APITypes.ztc},
        related_name="zgwset_ztc_config",
        null=True,
    )
    # Overridable defaults
    zaaktype = models.URLField(
        _("zaaktype"),
        max_length=1000,
        blank=True,
        help_text=_("Default URL of the ZAAKTYPE in the Catalogi API"),
    )
    informatieobjecttype = models.URLField(
        _("informatieobjecttype"),
        max_length=1000,
        blank=True,
        help_text=_("Default URL of the INFORMATIEOBJECTTYPE in the Catalogi API"),
    )
    organisatie_rsin = models.CharField(
        _("organisation RSIN"),
        max_length=9,
        blank=True,
        validators=[validate_rsin],
        help_text=_("Default RSIN of organization, which creates the ZAAK"),
    )
    zaak_vertrouwelijkheidaanduiding = models.CharField(
        _("vertrouwelijkheidaanduiding zaak"),
        max_length=24,
        choices=VertrouwelijkheidsAanduidingen.choices,
        blank=True,
        help_text=_(
            "Indication of the level to which extend the ZAAK is meant to be public. "
            "Can be overridden in the Registration tab of a given form."
        ),
    )
    doc_vertrouwelijkheidaanduiding = models.CharField(
        _("vertrouwelijkheidaanduiding document"),
        max_length=24,
        choices=VertrouwelijkheidsAanduidingen.choices,
        blank=True,
        help_text=_(
            "Indication of the level to which extend the document associated with the "
            "ZAAK is meant to be public. Can be overridden in the file upload "
            "component of a given form."
        ),
    )
    auteur = models.CharField(
        _("auteur"),
        max_length=200,
        default="Aanvrager",
    )

    class Meta:
        verbose_name = _("ZGW API set")
        verbose_name_plural = _("ZGW API sets")

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        if self.ztc_service and self.zaaktype:
            if not self.zaaktype.startswith(self.ztc_service.api_root):
                raise ValidationError(
                    {"zaaktype": _("ZAAKTYPE is not part of the Catalogi API")}
                )

        if self.ztc_service and self.informatieobjecttype:
            if not self.informatieobjecttype.startswith(self.ztc_service.api_root):
                raise ValidationError(
                    {
                        "informatieobjecttype": _(
                            "INFORMATIEOBJECTTYPE is not part of the Catalogi API"
                        )
                    }
                )

    def apply_defaults_to(self, options):
        options.setdefault("zaaktype", self.zaaktype)
        options.setdefault("informatieobjecttype", self.informatieobjecttype)
        options.setdefault("organisatie_rsin", self.organisatie_rsin)
        options.setdefault(
            "zaak_vertrouwelijkheidaanduiding", self.zaak_vertrouwelijkheidaanduiding
        )
        options.setdefault(
            "doc_vertrouwelijkheidaanduiding",
            self.doc_vertrouwelijkheidaanduiding,
        )
        options.setdefault("auteur", self.auteur)
