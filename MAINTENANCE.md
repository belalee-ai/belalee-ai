# 主页维护指南

这个公开仓库名为 `belalee-ai`，与 GitHub 用户名一致。GitHub 会把根目录的 `README.md` 显示到 [个人主页](https://github.com/belalee-ai)。本地目录为 `/Users/zhoumenglin/github/belalee-ai`。

## 日常只需要维护这些文件

| 文件或目录 | 用途 |
| --- | --- |
| `README.md` | 主页文案、项目顺序、图片引用和所有可点击链接 |
| `assets/hero.svg` | 顶部个人横幅占位 |
| `assets/latest.svg` | 近期项目封面占位 |
| `assets/project-01.svg` 至 `project-03.svg` | 三个精选项目封面占位 |
| `assets/tool-01.svg` 至 `tool-03.svg` | 三个工具封面占位 |
| `assets/learning.svg` | 内容、教程或文章封面占位 |
| `assets/accounts/` | 各平台二维码与缺失二维码的占位 |
| `.github/workflows/update-stats.yml` | 自动刷新主页统计 |
| `scripts/update_stats.py` | 统计脚本，日常不用修改 |

所有栏目都可以改名、调整顺序、增加或删除。未填的文案目前明确显示为待补充。

## 换成自己的封面

1. 将图片上传到 `assets/`。推荐 JPG、PNG 或 WebP，横幅宽约 1600 像素，项目封面比例约 4:1，个人横幅比例约 10:3。
2. 在 `README.md` 中把对应 `src` 改成实际文件名，例如 `assets/hero.webp`。不要把 JPG 文件直接改名为 `.svg`。
3. 把 `alt` 改成图片的简短说明。
4. 把占位介绍改成自己的内容，并添加项目链接。

图片也可以直接点击：

```html
<a href="https://github.com/belalee-ai/你的仓库名">
  <img src="assets/你的封面.webp" alt="项目名称与一句话介绍" width="100%" />
</a>
```

文字链接写法：

```markdown
[查看项目 →](https://github.com/belalee-ai/你的仓库名)
```

## 更新全平台账号

修改 `README.md` 中的 `ACCOUNTS-START` 与 `ACCOUNTS-END` 之间的内容。二维码保存在本仓库中；同时保留文字链接，便于手机读者直接访问。缺失二维码用明确的占位显示，不用其他账号替代。

视频号保留独立占位。后续将真实二维码放入 `assets/accounts/wechat-channels.png`，再修改 README 对应图片路径、账号名和说明。

主页只展示公开账号信息，不包含表格中的绑定手机号、运营商、登录邮箱等管理信息。

## 自动统计

工作流每天北京时间 08:17 更新，也可以到仓库的 **Actions → Update profile stats → Run workflow** 手动运行。只改写 `STATS-START` 与 `STATS-END` 之间的徽章，请保留这两个标记。

统计采用 GitHub 公开 API：所有公开非 Fork 仓库的 Star 总和、关注者数量、公开非 Fork 仓库数量。它们不会复制参考作者的数据，也不包含私有项目。工作流只使用 GitHub 自动提供的 `GITHUB_TOKEN`，无需填写个人访问令牌。

如果 GitHub 因长时间没有仓库活动而暂停定时任务，可到 Actions 重新启用。Fork 仓库首次需要启用工作流。

## 通过 GitHub 网页维护

打开仓库 → 点开 `README.md` → 铅笔编辑 → Preview 预览 → Commit changes。上传图片用 **Add file → Upload files**。修改默认分支后刷新个人主页即可看到结果。

## 在本地维护

```bash
cd /Users/zhoumenglin/github/belalee-ai

git pull --rebase origin main
# 修改 README.md，放入自己的图片

git add README.md assets
git commit -m "Update profile content"
git push origin main
```

提交前先拉取，因为自动统计也可能更新 README。需要开分支时，推送目标始终是自己的 `origin`。本地已关闭 Fork 向上游仓库推送的地址。

## 哪些展示不由 README 控制

左侧头像、显示名、Bio、位置和社交链接在 GitHub **Settings → Public profile** 中设置。下方仓库卡片可以通过个人主页的 **Customize your pins** 选择，最多六项。主页仓库本身不需要启用 GitHub Pages。

## 结构来源

本仓库 Fork 自 [alchaincyf/alchaincyf](https://github.com/alchaincyf/alchaincyf)，参考其「个人横幅、统计、近期项目、精选项目、工具、学习内容、社交账号」排版。当前版本已移除原作者的文案、图片、账号、推广内容与一次性广告清理任务，并独立重写统计逻辑。Fork 的历史提交仍保留上游记录。
