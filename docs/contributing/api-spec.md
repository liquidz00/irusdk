# Working with the API spec

Iru publishes no OpenAPI document. What this project works from is a local, disposable conversion
of Iru's Postman collection, and understanding its status matters before you rely on it.

## It is a working tool, not a contract

`spec/` is **not** tracked in version control, and that is deliberate.

A spec file in git implies it is kept in step with the vendor's API. Keeping it in step would
require three things: a job polling Iru for changes, a job updating the file when one is found, and
a job propagating the change into the models. The first of those is not currently possible — see
[Why it cannot be automated](#why-it-cannot-be-automated) — so the other two have nothing to
trigger them.

A committed-but-unsynced spec would be worse than none at all. It would read as authoritative,
contributors would trust it, and any test validating against it would keep passing long after it
had stopped describing reality. So the file stays local: a thing you fetch when you need it and
discard when you are done.

## Getting a copy

1. Open [Iru's API documentation](https://api-docs.iru.com) and follow it through to the Postman
   collection.
2. Export the collection as Postman Collection v2.1 JSON.
3. Convert it to OpenAPI 3 and save the result as `spec/iru-openapi.json`.

The conversion carries inline JSON Schemas and realistic response examples for 96 of its 133
operations — enough to write models against without guessing field names.

### Known defects in the conversion

The Postman-to-OpenAPI conversion is imperfect. Two artefacts to ignore:

- A stray `POST /` entry, which is really the S3 presigned upload for Custom Apps.
- A typo'd path, `/api/v1/devices/{device_id}}/action/togglepersonalhotspot`.

## Why it cannot be automated

There is no fetchable source for the collection:

- `https://www.postman.com/collections/{uid}` returns `404` — it is not published as a public link.
- `https://api.getpostman.com/collections/{uid}` returns `401` — the Postman API requires a key,
  and a key only reaches collections in **your own** workspace.

Automation is therefore possible only after a manual prerequisite: fork the collection into your
own Postman workspace and hold an API key for it. That makes the pipeline depend on one person's
workspace and credential, which is a poor foundation for a public SDK.

If Iru ever publishes a spec at a stable URL, this calculus changes and the file becomes worth
tracking.

## How API changes actually surface today

Honestly: through use. A field the SDK does not declare is absorbed silently by `extra="allow"`,
and a new endpoint simply goes unwrapped until someone needs it.

That is a real limitation, and it is a consequence of the vendor's tooling rather than a choice
this project made. Two things soften it:

- Models never reject unknown fields, so a vendor addition cannot break callers at runtime. The
  cost of finding out late is a missing convenience, not an outage.
- `model_extra` is populated on every model, so you can inspect what the API sent that the SDK does
  not know about:

  ```python
  device = client.devices.get(device_id)
  if device.model_extra:
      print("Undeclared fields:", sorted(device.model_extra))
  ```

  That is the quickest way to check whether a model has fallen behind.

## Updating models after a refresh

By hand, from your local spec, following {doc}`adding-an-endpoint`.

Full code generation was considered and set aside. The schemas are regular enough that it would
work, but generated models would lose the field-level docstrings that make
{doc}`../reference/models` useful, and the hand-written models are a small, stable surface — the
vendor adds fields far more often than endpoint families.
