# a-stock-data-codex 交接文档（Handoff）
> 更新日期：2026-07-27 · 由 Claude Code 自动生成

## 一、这个项目是什么
「A 股全栈数据工具包」的本地 Codex 适配 fork。上游为 simonlin1212/a-stock-data（README 安装命令指向该仓库），本地 fork 推送到 jzhu29git/a-stock-data。核心是一个 73KB 的自包含 `SKILL.md`（结构化 Markdown + 内嵌 Python），把 13 个数据源、28 个端点整合为 AI 编程助手可直接调用的工具集：

- 七层架构：行情（mootdx/腾讯/百度K线）、研报（东财/同花顺/iwencai）、信号（热点/北向/龙虎榜/解禁/资金流）、资金面（融资融券/大宗/股东户数/分红）、新闻（东财/财联社）、基础数据（季报/F10/三表）、公告（巨潮）。
- 当前版本 V3.1（2026-05-19）：已彻底移除 akshare，全部直连 HTTP API；替换了 4 个失效接口；28 端点全量实测通过（详见 `CHANGELOG.md`）。
- 除 iwencai 语义搜索需 API Key 外，其余数据源全部免费无 Key。

本 fork 的增量在 `codex/` 目录（commit 918a9e8）：Windows 下 Codex 的落地件——快速查询助手 `a_stock_basic.py`、固定版本依赖 `requirements-codex.txt`、iwencai SkillHub CLI 的 vendored 副本、`announcement-search` 技能副本、Windows 安装脚本与本地补丁脚本。README 末尾「Codex Adaptation Notes (2026-05-28)」一节是本机完整部署记录。

## 二、如何使用
Claude Code 用户（3 步）：
```bash
mkdir -p ~/.claude/skills/a-stock-data
# 把本仓库的 SKILL.md 复制进去
pip install mootdx requests pandas stockstats
```

本机 Codex 部署（Windows，README 已验证流程）：
```powershell
Copy-Item .\SKILL.md "$env:USERPROFILE\.codex\skills\a-stock-data\SKILL.md" -Force
python -m venv "$env:USERPROFILE\.codex\skills\a-stock-data\.venv"
& "...\.venv\Scripts\python.exe" -m pip install -r .\codex\requirements-codex.txt
```
注意：mootdx 钉死 `httpx<0.26`，与 Codex/MCP 工具链的新版 httpx 冲突，**必须用独立 venv**，不要装到全局。

快速查询助手（免 Key）：
```powershell
& "...\.venv\Scripts\python.exe" .\codex\a_stock_basic.py quote 600519 000858
& "...\.venv\Scripts\python.exe" .\codex\a_stock_basic.py info 600519
& "...\.venv\Scripts\python.exe" .\codex\a_stock_basic.py industry --top 10
```

iwencai / announcement-search（需环境变量 `IWENCAI_BASE_URL`、`IWENCAI_API_KEY`）：
```powershell
.\codex\install_iwencai_skillhub_windows.ps1   # 用 vendored 安装器，别用官方 sh 脚本
python .\codex\patch_announcement_search.py    # 安装后必跑的本地补丁
```

## 三、遗留问题 / 未解决的问题
1. **announcement-search 官方包自带 bug**：其 CLI 期望 `search.search()` 返回 tuple，实际返回 dict。vendored 副本已修，但**每次从 SkillHub 重装/升级后都必须重跑 `codex\patch_announcement_search.py`**，否则运行报错。
2. 官方 announcement-search 的 `requirements.txt` 把 `json`、`csv`、`os-sys`、`sys` 等标准库当 pip 依赖列出，不能盲目 `pip install -r`；真正需要的第三方库只有 requests、pandas、python-dotenv。
3. 官方 iwencai 安装脚本在 Windows 上找 `aime-install.sh`（zip 内实际是 `iwencai-install.sh`），且 wrapper 调 `python3` 会命中微软商店存根——所以才 vendored 了 PowerShell 安装器，此上游问题未解决。
4. **东财 push2 系列端点对本地代理敏感**（本机 Clash 可能干扰），`a_stock_basic.py` 已做「系统网络优先、失败直连」的回退；服务器直连验证正常。
5. 数据源接口经常性失效（V3.1 一次就替换了 4 个），属长期维护项：建议定期用 CHANGELOG 中的方式对 28 端点做回归（基准票 600519）。
6. 北向资金历史数据为本地 CSV 自缓存模式（东财 2024-08 断供后），换机器缓存从零开始积累。
7. 代码内无 TODO/FIXME 注释，无未提交改动。

## 四、远程仓库信息
- remote：`origin  https://github.com/jzhu29git/a-stock-data.git`（fetch/push）；注意仓库名是 a-stock-data，本地文件夹名带 -codex 后缀
- 当前分支：`main`，与 `origin/main` 同步，工作区干净（0 个未提交文件）
- 全部提交（共 2 个）：
  - `918a9e8` docs: add Codex setup notes（2026-05-28，新增 codex/ 目录与 README 适配章节）
  - `cc54fb6` fix: 修复 §2.2 ths_eps_forecast pandas 3.0 崩溃 + §7.1 cninfo 时间戳类型错误（初始提交）
