opinionated-hooks
=================

Opinionated hooks for the [pre-commit framework](https://github.com/pre-commit/pre-commit).


### Usage with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
-   repo: https://github.com/jf/opinionated-hooks
    rev: 0.0.2  # Use the ref you want to point at
    hooks:
    -   id: terraform-fmt-tabifypp
    # -   id: ...
```

### Hooks available

#### `terraform-fmt-tabifypp`
'terraform fmt'-tabify++. Opinionated formatter that leans on `terraform fmt` (`cat` and `terraform` will need to be in your path):
  - tabs for accessibility and freedom (you're free to decide your own visual indentation) instead of spaces for indentation
  - opinionated spacing within '()', '[]', and interpolation expressions
