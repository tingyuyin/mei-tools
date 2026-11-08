# mei-tools

庭雨湄写的小工具（也收别人写的，但**必须标明来路**）。每条都小而独立，不依赖彼此。

## 收录规矩

1. 自己写的：署名 `湄`，MIT。
2. 别人的：README 里写清原仓库、原作者、许可证；代码原样保留其许可文件，**不改成自己的名字**。
3. 只借了想法、代码是自己写的：写进「致谢」，说明借鉴了什么。

## 工具

| 目录 | 做什么 | 依赖 |
|---|---|---|
| `ctx/ctx-usage.js` | 读 DSH 会话日志，算上下文用了多少、每轮涨多少 | Node ≥ 20，标准库 |
| `backup/backup-memory.py` | 把记忆类 Markdown 拍快照，留 N 份 | Python ≥ 3.10，标准库 |
| `qq/qq-night.py` | 夜里把某个 QQ 群的接收关掉 / 早上打开（改 `~/.dsh/qq-bridge-config.json` 里那一行的「开」） | Python ≥ 3.10，标准库 |

## 用法

```sh
node ctx/ctx-usage.js                       # 取最近改动的会话日志
node ctx/ctx-usage.js <session.v4.jsonl.zstd>

python backup/backup-memory.py --root "D:\mei 11.2"
python backup/backup-memory.py --root "D:\mei 11.2" --list

python qq/qq-night.py --off 645937444
python qq/qq-night.py --on 645937444
python qq/qq-night.py --status
```

## 致谢

- `qq/qq-night.py` 配合 [dsh-qq-link](https://github.com/Yuuyuko-uu/dsh-qq-link) 使用；**没有改它的代码**，只读写它自己的配置文件。它的许可是「Yuuyuko-uu 插件许可 1.2」，这里不复制其代码。
- `backup/backup-memory.py` 的「备份 + 还原演练」想法来自 [鱼神双子星](https://github.com/abyss-kun/yushen-dx)（AGPL-3.0-or-later）；**代码是重写的**，没有复制。
- `ctx/ctx-usage.js` 无第三方代码。

## 许可

MIT，见 [LICENSE](LICENSE)。
