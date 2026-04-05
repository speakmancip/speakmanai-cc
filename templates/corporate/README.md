# Corporate Template

Drop your corporate brand assets here to produce documents in your organisation's visual identity.

## Required Files

| File | Spec |
|---|---|
| `logo.png` | Your corporate logo. PNG format. Recommended height: 36px. White or light version works best on the dark header bar. |

After running the install script, this template is available at:
```
~/.claude/speakmanai-cc/templates/corporate/
```

Add your `logo.png` there, then select `[corporate]` when prompted by any skill, or pass the path directly:

```bash
python ~/.claude/speakmanai-cc/scripts/doc_writer.py my-project_clean.md \
  --template ~/.claude/speakmanai-cc/templates/corporate \
  --output /absolute/path/to/outputs/my-project/my-project \
  --yes
```
