# 贡献与 git 使用建议

Theseus 的主仓库 [`theseus-os/Theseus`](https://github.com/theseus-os/Theseus) 就是我们所说的*上游（upstream）*。
要参与贡献，你应当在 GitHub 网站上创建你自己的该仓库的派生仓库（fork），然后检出（check out）你自己的 fork。
这样，你的 fork 默认会成为 `origin` 远程仓库，随后你可以把上游添加为另一个远程仓库，方法是运行：

```sh
git remote add upstream https://github.com/theseus-os/Theseus
```

### 绝不要直接推送到 main 分支

目前，上游的 `theseus-os/Theseus/theseus_main` 上的 main 分支受到保护，无法直接推送（push）。
即使对于 `theseus-os` 组织中拥有 Theseus 仓库写权限的 GitHub 用户，也是如此。
向它贡献代码的唯一方式，是把一个拉取请求（pull request）合并进 main 分支，而这只有获得授权的用户才能做到。
正确做法是：像上文那样检出你自己的 fork，创建一个名字具有描述性的新分支（branch），例如 `kevin/logging_typo`，
在该分支上开发你的功能，然后提交一个拉取请求。
这是一种标准的 Git 工作流，他人在代码进入 main 分支之前，可以审查你的代码、检查其中是否有陷阱和兼容性问题，
并提出意见与建议。
*所有更改都必须这样做，哪怕是一些看起来微不足道的小改动。*

### 提交拉取请求

要提交一个拉取请求（PR），请前往你的 Theseus 派生仓库的 GitHub 页面，
在下拉菜单中选中你创建的那个分支，然后点击 "New pull request"。
默认情况下，GitHub 会创建一个新的 PR，把你创建的分支合并到上游的 `theseus_main` 分支，
这通常正是你想要的结果。
现在，为你的 PR 起一个好标题并写好描述，向下滚动以查看提交（commit）和改动的文件，
如果一切看起来都没问题，就点击 "Create pull request"，通知维护者你有需要他们审查的贡献。

### 审查你自己的工作

在提交拉取请求之前，先对自己的代码做一次初步审查。
请不要把修一大堆琐碎问题的全部负担，都推给那些也必须审查你代码的人。
这包括构建文档并在浏览器中以 HTML 形式查看它（`make view-doc`），
以确保所有内容格式正确、所有超链接都能正常工作。

### 仔细核对 commit 的内容

在创建一个 commit 时，请用 `git status` 和 `git diff`，以及在 GitHub 的比较页面上，检查你的改动，
以确保你没有提交意外的修改，也没有改动不应改动的文件。
这会让维护者的日子好过得多，也意味着你的 PR 更有可能被接受。

你不必担心 commit 太多太小，因为在把你的 PR 合并进上游 main 分支时，我们会把它的所有 commit 压缩（squash，即合并）为一个大的 commit。
