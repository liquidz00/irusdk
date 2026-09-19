# Models

:::{warning}
These models describe responses; they are not input validation. Every field is optional and unknown
fields are preserved, because Iru adds fields between releases and a model that rejected them would
break the SDK on the vendor's schedule rather than ours. Do not rely on a field being present.
:::

Every model is re-exported from `irusdk.models`, so the submodule layout is an implementation
detail:

```python
from irusdk.models import Blueprint, Device
```

Some models add fields derived from the wire data — {attr}`~irusdk.models.devices.Device.os_major`
for counting devices by OS release without comparing version strings, and
{attr}`~irusdk.models.blueprints.Blueprint.present_percent` for how much of a blueprint is
reporting in. Those appear in `model_dump()`; the few that depend on the current clock, such as
{attr}`~irusdk.models.devices.Device.days_since_check_in`, are plain properties and do not.

## Base classes

```{eval-rst}
.. autopydantic_model:: irusdk.models.Model

.. autoproperty:: irusdk.models.Model.unknown_fields

.. autopydantic_model:: irusdk.models.UpstreamModel
```

## Devices

```{eval-rst}
.. autopydantic_model:: irusdk.models.devices.Device

.. autoproperty:: irusdk.models.devices.Device.os_major

.. autoproperty:: irusdk.models.devices.Device.os_version_info

.. autoproperty:: irusdk.models.devices.Device.days_since_check_in
```

## Blueprints

```{eval-rst}
.. autopydantic_model:: irusdk.models.blueprints.Blueprint

.. autoproperty:: irusdk.models.blueprints.Blueprint.present_count

.. autoproperty:: irusdk.models.blueprints.Blueprint.present_percent

.. autopydantic_model:: irusdk.models.blueprints.EnrollmentCode
```

## Users

```{eval-rst}
.. autopydantic_model:: irusdk.models.users.User

.. autopydantic_model:: irusdk.models.users.UserIntegration
```

## Tags

```{eval-rst}
.. autopydantic_model:: irusdk.models.tags.Tag
```

## Library items

Read-only, as they appear on a blueprint or device. This SDK does not author library content — see
{doc}`../guide/scope`.

```{eval-rst}
.. autopydantic_model:: irusdk.models.library.LibraryItem
```

## Custom scripts

```{eval-rst}
.. autopydantic_model:: irusdk.models.custom_scripts.CustomScript

.. autoclass:: irusdk.models.custom_scripts.ExecutionFrequency
   :members:
   :undoc-members:
```

## Shared

```{eval-rst}
.. autopydantic_model:: irusdk.models.common.UserRef

.. autopydantic_model:: irusdk.models.common.BlueprintRef
```
