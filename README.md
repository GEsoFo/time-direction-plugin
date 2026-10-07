# 择时与方位插件 / Time Direction Plugin

当前版本：**0.3.2** · 维护者：[GEsoFo](https://github.com/GEsoFo) · [源码仓库](https://github.com/GEsoFo/time-direction-plugin) · [问题反馈](https://github.com/GEsoFo/time-direction-plugin/issues)

本地运行的六壬、奇门与真实北斗方位联合择时插件，适用于支持 stdio MCP 与 Skill 的 AI 客户端。

一个组合插件，包含通用、可离线计算的 stdio MCP 服务器和 `time-direction-election` Skill。提供六壬、奇门和北斗方位的
**固定事实与候选材料**，由调用它的模型按事项和全部本命作取舍。
不使用吉神加分、凶神扣分，不自动给出“最佳方位”。没有模型 API 密钥依赖。

## 能力

- 六壬完整式盘：天地盘、四课、九宗门三传、十二天将、旬遁、六亲长生。
- 奇门：时家转盘拆补/置闰可选，星、门、神、天地干、值符值使、时旬空。
- 具名九遁组合，含龙遁、虎遁主式与另说；门迫、击刑、三奇入墓及
  乙加辛等条件一起提供，格名不自动等于通用吉方。
- 六壬贵人所临地盘方、式盘辰天罡斗柄方，保留原文事类边界。
- 真实北斗七星：每次传入任意经纬度，计算具体时刻的几何方位、高度、
  是否在地平线上及近似太阳高度。没有默认城市，也不要求在线星历下载。
- 多个具名本命分别比较；婚姻需双方资料，缺一方不能回填可用结论。
- 判断材料按小批次读取，模型回填后生成离线 HTML；用方留空时可用段
  必须附模型选择的方位和理由。

## 安装与启动

Python 3.11+、Node.js 18+。

```sh
git clone https://github.com/GEsoFo/time-direction-plugin.git
cd time-direction-plugin
python -m pip install .
time-direction-mcp
```

也可通过仓库的 Code → Download ZIP 下载源码后解压，在解压目录执行安装命令。启动命令供客户端接入或协议调试使用，交互时请在 AI 客户端加载 MCP 配置与配套 Skill。

源代码方式可运行 `python /path/to/time-direction-mcp/server.py`，先安装
`lunar-python==1.4.8 skyfield==1.54 tzdata`。所有资源跟随包安装，
不依赖开发者的盘符、用户目录、另一个项目 checkout 或私人配置。

服务器采用 MCP 标准 UTF-8 JSON-RPC stdio，支持初始化、工具列举、
工具调用与 ping。它是专用 stdio 实现；不声称提供 HTTP、SSE、OAuth
或通用 MCP 框架的所有可选能力。日志不混入 stdout。

## MCP 配置

安装后可使用仓库的 `.mcp.json`：

```json
{"mcpServers":{"time-direction":{"command":"time-direction-mcp","args":[]}}}
```

若使用源码，把 `command` 设为实际 Python 命令，`args` 设为
服务器入口的绝对路径；不同客户端的配置存放位置由其产品决定。
可通过 `TIME_DIRECTION_OUTPUT_ROOT` 指定生成文件的根目录；默认使用
系统临时目录下的独立目录。观测地点只由工具参数提供，没有环境里的
隐藏默认城市。

## 工具

| 工具 | 用途 |
|---|---|
| `get_qimen_chart` | 指定时刻起奇门局 |
| `get_beidou_sky` | 指定时刻和经纬度计算真实七星 |
| `get_direction_facts` | 联合六壬、奇门、式盘斗柄、真实七星及各本命 |
| `build_election_request` | 创建1–7日材料和未判断 HTML，跨月不丢窗口 |
| `build_year_election` | 完整公历年365/366日；按月加载HTML，模型逐批判断 |
| `preview_election_calendar` | 恢复日历HTTP预览与已登记书签 |
| `read_election_windows` | 每次读取最多14个窗口供模型审阅 |
| `render_election_calendar` | 校验并累积合并各批判断后回填 HTML |

示例工具参数（地点是本次请求的示例，不是服务器默认值）：

```json
{
  "datetime":"2026-10-06T20:00:00+08:00",
  "purpose":"祈福",
  "participants":[{"name":"本人","branch":"午"}],
  "observer":{"latitude":30.0,"longitude":120.0,"elevation_m":0,"label":"本次观测点"}
}
```

不传 `observer` 时，六壬、奇门和式盘斗柄仍正常计算，真实七星返回
`needs_observer`，不会假定城市或编造地平坐标。

## 计算口径和来源

本版术数时钟明确使用北京时间、默认23:00换日；`input_timezone` 仅用于
解析无偏移的输入时间，有时区偏移的 ISO 时间会先转换到北京时间起课。
观测地点影响真实星空，**不暗改术数时钟为当地真太阳时**。海外地点也可
调用真实天文工具，但不能把此默认术盘误称当地太阳时盘。

奇门采用具名现代拆补转盘口径：天禽寄芮、中五寄坤二，值符随时干，
值使按阴阳顺逆计时落宫，八门转八宫，八神阳顺阴逆。
局表、符首三元、八门九星及格局参考：

- [《协纪辨方书》卷三十五](https://zh.wikisource.org/wiki/欽定協紀辨方書_(四庫全書本)/卷35)
- [《遁甲演义》卷二](https://zh.wikisource.org/wiki/遁甲演義_(四庫全書本)/卷2)
- [《武经总要》后集卷二十](https://zh.wikisource.org/wiki/武經總要_(四庫全書本)/後集卷20)
- [《六壬大全》卷四斗柄所指](https://zh.wikisource.org/wiki/六壬大全/4)

`qimen_method` 可传 `chaibu`（拆补，默认）或 `zhirun`（置闰）。
置闰按[《遁甲演义》超接引例](https://zh.wikisource.org/zh-hant/遁甲演義#超神接氣置閏訣)，采用含符首九日阈值、芒种/大雪重复三元、接气借新节下元；以1899-12-07甲午大雪正授连续推算，支持1900–2099。
两法均用时家转盘；不是九星飞宫。每次判断绑定所选起局法。龙遁“休乙加癸”引文含伏吟文字歧义，作为条件候选，
不宣称该另说完整成立。虎遁休门主式、生门另说分别保留。

天文使用 SIMBAD/CDS ICRS J2000 坐标与自行、Skyfield 公共接口的岁差章动
及地球转动转换。返回巡天级几何方位，不含周年光行差、视差、大气折射、
天气或地形；地平线上不等于肉眼可见。太阳高度是日光提醒的近似计算。
日历中的七星是窗口**中点快照**，并非两小时内方位恒定；要具体分钟请
再次调用 `get_beidou_sky`。

## 模型工作流

1. 明确事项、每个参与者本命、范围和是否有观测坐标。
2. 创建材料，按小批次读取所有需要的窗口，不能只挑漂亮案例。
3. 模型比较每个方位的多体系证据、事类用途和矛盾；填写
   `verdict/reason/evidence`。未指定用方的可用段还需
   `suggested_direction`（单一地支、理由、证据）。
4. 不能把吉格、贵人方或真实星空坐标机械累加成吉凶分数。
5. 回填工具绑定参与者、观测点、事实摘要；不完整或旧参数不能冒充已审。

资料不足的窗口可以明确标待定。盘面事实和文化择时不构成中奖、疾病
结果、婚姻结局或其他现实事件的保证。

## 验证与发布

```sh
python -m unittest discover -s tests -v
```

测试覆盖原文天遁示例、局盘排列不变量、主式/另说分离、太阳节气边界、
跨地点星空、MCP 初始化和真实工具调用、跨月材料及回填约束。

MIT 许可适用于本插件原创代码，派生六壬引擎保留 BSD-3-Clause；见
`THIRD_PARTY_NOTICES.md`。发布目录不包含开发环境、私人判断或个人坐标。
由 [GEsoFo](https://github.com/GEsoFo) 维护；问题与改进建议可提交到 [GitHub Issues](https://github.com/GEsoFo/time-direction-plugin/issues)。反馈请使用虚构示例，不要提交个人生成日历、真实坐标或凭据。

## 全年择日

调用 `build_year_election`，传入 `year`（1900–2099），以及事项、具名多本命、所选奇门方法和可选观测坐标。生成12个月全部365/366日事实。年度材料只保留窗口索引，每批 `read_election_windows` 最多14窗才展开完整盘面。

模型回填每批 `render_election_calendar` 后，会保留并合并之前已判断窗口；同ID再次提交可纠正结论。每批返回累计覆盖数及 `complete`，部分判断不会冒充全年完成。HTML只载入当前月份，保留同目录全部 `.data.js` 文件才能离线切月。

CLI：`python <resources/calendar/scripts/calendar.py> --year 2027 --output <输出目录>`。默认显示当前日期所在月；没有该月时从生成范围第一月开始。离线页面只浏览已有年份，要新年份由 MCP 或 CLI 重新生成。

## 组合插件安装与使用

发布 ZIP 解压后根目录包含 `plugin.json`、`mcp.json`、`skills/time-direction-election/`，以及兼容旧客户端的 `.codex-plugin/plugin.json`、`.mcp.json`。Skill 的 MCP 依赖标识与服务名称统一为 `time-direction`。

1. 准备 Python 3.11+、Node.js 18+；在解压目录执行 `python -m pip install .` 安装计算运行时。也可安装同版 wheel，依赖仍需通过合法包源安装。插件管理器不会自动安装 Python/Node，这一步是运行前提。
2. 在支持本地插件的客户端中添加解压目录/本地插件源并启用插件。新客户端读取根 `plugin.json/mcp.json`，兼容客户端读取 `.codex-plugin/plugin.json/.mcp.json`。仅支持 MCP 的客户端可单独导入 `.mcp.json`，并手动加载配套 Skill。
3. 新会话确认 `time-direction` 的8个工具与 `time-direction-election` Skill 可见，输入“用择时与方位插件，为2027年开业择日，本命午，用方未指定”。多本命用名称与地支逐人提供。

如果客户端找不到 `time-direction-mcp`，将本机客户端配置的 command 改为实际 Python 环境的该入口绝对路径；发布包不包含开发者机器路径。该包是本地 stdio 插件，未部署远程服务、未提交官方公共插件目录，也没有自动修改用户的客户端配置。官方公共目录提交需满足其当前远程 HTTPS 接入要求。

MCP固定事实，Skill组织事项判断、全年的逐批审阅、上下文绑定和日历回填。安装两者不代表模型已经审阅任何日期。

开发者重建发布包：`python scripts/package_release.py <包外输出目录>`。不要把个人事实/判断输出、虚拟环境或密钥加入发布包。

官方包装规范：https://developers.openai.com/plugins/build/plugins ，Skill连接规范：https://developers.openai.com/plugins/build/skills 。

## 本地日历预览（0.3.0）

生成、回填工具现在自动返回标准 HTTP `preview_url`。预览在 MCP 进程中运行，仅绑定127.0.0.1，只提供明确注册的日历 HTML 与 `.data.js`，不暴露事实JSON、配置、目录列表或任意磁盘路径。地址使用ASCII路径；支持UTF-8脚本名。页面显示实际已回填/总窗口数，未回填不冒充全审阅。

服务随 MCP 进程存活，应用重启后请调用 `preview_election_calendar(artifact_id)` 恢复地址。默认自动分配空闲端口；`TIME_DIRECTION_PREVIEW_PORT` 可设首选端口，占用时回退空闲端口，返回实际地址。启动失败仍保留离线HTML与数据文件，返回 preview_error。没有自动关闭或绕过浏览器策略。

独立预览命令：`time-direction-preview --artifact <artifact_id> --output-root <生成根目录> --port 8767`。该命令保持运行才能提供预览；可用 `--alias <短名>` 兼容现有书签。本地 `/health` 返回服务名和版本。它只预览文件，不是远程HTTP MCP服务。

0.3.1 在每个已预览 artifact 内保存 preview.json（仅本机使用，不通过预览提供），MCP启动时恢复已登记的日历与别名。设置固定首选端口且该端口空闲时，重启后原书签可继续用；端口回退时以工具返回的新地址为准。

## 0.3.2 发布审查修复

- 从明确的 `release-files.json` 清单在干净目录构建，扫描最终 ZIP 和 wheel；排除 Python 缓存，并在 wheel 内携带第三方许可说明。
- 修复重启后第一次读取年度材料的导入错误、无效起盘口径未提前拒绝、北京时间转换和跨年范围越界。
- 修复异常预览记录导致启动失败及别名/令牌冲突，增加跨站读取限制。
- 未判断的日历保留请求事项、参与者和口径；页面导入时拒绝无效建议方位。
- 隐私边界和发布步骤见 `SECURITY.md`。公开仓库只使用新发布 ZIP 解压内容。


## 使用示例

在已连接的 AI 客户端输入：

> 用择时与方位插件，为 2027 年开业择日。参与者本命为午，用方未指定。先生成全年事实，再逐批判断并回填日历；报告已经判断的窗口数量与未完成部分。

只看盘面可输入：

> 查看北京时间 2027-01-01 12:00 的六壬和奇门盘，只列固定事实。

真实北斗方位须另行提供本次观测坐标；没有观测点时仍可查看术盘。参与者姓名可以使用“甲方”“乙方”等代号。

## 开发与贡献

- `src/time_direction_mcp/`：服务器、文件材料管理与本机预览。
- `src/time_direction_mcp/resources/calendar/`：历法、六壬桥接、奇门、神煞、天文与离线页面。
- `skills/time-direction-election/`：事项澄清、逐批判断与回填工作流。
- `tests/`：排盘不变量、日历、协议、发布和隐私边界的回归测试。

欢迎通过 Issue 或 Pull Request 提交可复现问题与修复。修改计算规则时，请附具名口径、原始出处与虚构案例，并保持“固定事实、真实天文、模型判断”之间的界限。

0.3.2 在 Windows / Python 3.14 环境通过 23 项测试及隔离安装验证；其他系统与 Python 版本尚未逐一验证。常规算例测试不等于所有规则和日期逐例校勘。
