# Services

Each service is reached as an attribute of a client — `client.devices`, `client.blueprints`, and so
on. The async twins carry the same methods and signatures; only `await` and `async for` differ.

## Devices

```{eval-rst}
.. autoclass:: irusdk.services.devices.DevicesAPI
   :members:

.. autoclass:: irusdk.services.devices.AsyncDevicesAPI
   :members:
```

## Blueprints

```{eval-rst}
.. autoclass:: irusdk.services.blueprints.BlueprintsAPI
   :members:

.. autoclass:: irusdk.services.blueprints.AsyncBlueprintsAPI
   :members:
```

## Users

```{eval-rst}
.. autoclass:: irusdk.services.users.UsersAPI
   :members:

.. autoclass:: irusdk.services.users.AsyncUsersAPI
   :members:
```

## Tags

```{eval-rst}
.. autoclass:: irusdk.services.tags.TagsAPI
   :members:

.. autoclass:: irusdk.services.tags.AsyncTagsAPI
   :members:
```

## Custom scripts

```{eval-rst}
.. autoclass:: irusdk.services.custom_scripts.CustomScriptsAPI
   :members:

.. autoclass:: irusdk.services.custom_scripts.AsyncCustomScriptsAPI
   :members:
```
