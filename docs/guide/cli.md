# Command line

Install the `cli` extra to get the `irusdk` command:

```console
$ pip install "irusdk[cli]"
```

## Credentials

Every command reads credentials from the environment, or takes them as options:

```console
$ export IRU_SUBDOMAIN=mycompany
$ export IRU_API_TOKEN=...
$ export IRU_REGION=us          # optional; defaults to us

$ irusdk devices list
$ irusdk --subdomain mycompany --token ... devices list
```

## Commands

```console
$ irusdk devices list --platform Mac --limit 20
$ irusdk devices get 2cfeb3ac-3b5d-423e-bcff-e2676a3a32da
$ irusdk devices get 2cfeb3ac-... --details
$ irusdk devices delete 2cfeb3ac-... --yes

$ irusdk blueprints list
$ irusdk blueprints get bp-1
$ irusdk blueprints library-items bp-1

$ irusdk users list --limit 50
$ irusdk users get u-1

$ irusdk tags list
$ irusdk tags create "lab-machines"
$ irusdk tags delete t-9 --yes
```

:::{note}
There are no library-authoring commands. Use [`iructl`](https://github.com/kandji-inc/iructl) to
pull, push, and version-control Custom Profiles, Scripts, and Apps — see {doc}`scope`.
:::

## JSON output

Every read command takes `--json`, which emits the raw records instead of a table — useful with
`jq`:

```console
$ irusdk devices list --json | jq -r '.[] | select(.is_missing) | .serial_number'
```

## Limits

`devices list` and `users list` walk the entire fleet by default. On a large tenant use `--limit`
to stop early; the remaining pages are never requested.

```console
$ irusdk devices list --limit 100
```
