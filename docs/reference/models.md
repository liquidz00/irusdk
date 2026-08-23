# Models

:::{warning}
These models describe responses; they are not input validation. Every field is optional and unknown
fields are preserved, because Iru adds fields between releases and a model that rejected them would
break the SDK on the vendor's schedule rather than ours. Do not rely on a field being present.
:::

## Base classes

```{eval-rst}
.. autopydantic_model:: irusdk.models.Model

.. autopydantic_model:: irusdk.models.UpstreamModel
```

## Devices

```{eval-rst}
.. autopydantic_model:: irusdk.models.devices.Device
```

## Blueprints

```{eval-rst}
.. autopydantic_model:: irusdk.models.blueprints.Blueprint

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

## Shared

```{eval-rst}
.. autopydantic_model:: irusdk.models.common.UserRef

.. autopydantic_model:: irusdk.models.common.BlueprintRef
```
