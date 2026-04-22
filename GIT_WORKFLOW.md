# OCCT Fork 工作流指南

本文档说明当前仓库的 Git 远程配置以及日常开发/同步流程。

---

## 远程仓库配置

当前配置采用标准的 Fork 工作流，将官方仓库和自己的 Fork 分开管理：

```bash
$ git remote -v
origin   git@github.com:amlblbd/OCCT.git (fetch)       # 你自己的仓库
origin   git@github.com:amlblbd/OCCT.git (push)
upstream https://github.com/Open-Cascade-SAS/OCCT.git (fetch)  # 官方上游
upstream https://github.com/Open-Cascade-SAS/OCCT.git (push)
```

| 远程名 | 用途 | 地址 |
|--------|------|------|
| `origin` | 自己的仓库（默认推送目标） | `git@github.com:amlblbd/OCCT.git` |
| `upstream` | 官方 OCCT 仓库（获取上游更新） | `https://github.com/Open-Cascade-SAS/OCCT.git` |

本地 `master` 分支已设置为跟踪 `origin/master`：

```bash
$ git status
On branch master
Your branch is up to date with 'origin/master'.
```

---

## 日常操作

### 1. 推送代码到自己的仓库

```bash
git add .
git commit -m "你的提交说明"
git push                    # 默认推送到 origin（即你的仓库）
```

### 2. 拉取自己仓库的更新（其他机器/协作者）

```bash
git pull                    # 默认从 origin 拉取
```

---

## 同步官方上游更新

当官方 OCCT 发布了新版本或有重要更新时，按以下步骤合并到自己的仓库：

### 步骤 1：获取上游最新代码

```bash
git fetch upstream
```

### 步骤 2：切换到本地 master 分支

```bash
git checkout master
```

### 步骤 3：合并上游更新

```bash
git merge upstream/master
```

如果合并过程中出现冲突，解决冲突后提交：

```bash
# 编辑冲突文件，解决冲突后
git add <冲突文件>
git commit                    # 如果没有冲突，merge 会自动提交
```

### 步骤 4：推送到自己的仓库

```bash
git push origin master
```

或者简写为：

```bash
git push
```

---

## 完整同步命令（一键版）

```bash
git checkout master && \
git fetch upstream && \
git merge upstream/master && \
git push
```

---

## 常见问题

### Q: `git status` 显示与 `origin/master` 不一致？

这是正常的。`origin` 现在指向你自己的仓库，`git status` 会显示本地分支与你仓库的对比状态。

### Q: 想查看官方仓库有没有新提交？

```bash
git fetch upstream
git log --oneline --graph --left-right HEAD...upstream/master
```

### Q: 如何恢复原来的配置？

```bash
# 如果你想把 origin 改回官方仓库
git remote rename origin amlblbd
git remote rename upstream origin
git branch --set-upstream-to=origin/master master
```

---

## 参考

- [GitHub Fork 工作流官方文档](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)
- [Configuring a remote for a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/configuring-a-remote-for-a-fork)
- [Syncing a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork)
