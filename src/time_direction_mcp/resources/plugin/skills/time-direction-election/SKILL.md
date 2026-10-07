---
name: time-direction-election
description: 按具体事项、日期或整年范围、多本命与用方要求进行六壬奇门联合择时，调用配套 MCP 取得固定事实，由模型选择日期和方位并回填离线日历。也可只查看排盘或真实北斗方位。
---

# 择时与方位

通过本插件 `time-direction` MCP 计算固定事实；你负责具体事类的取舍。工具名称以客户端实际注册的前缀为准，下文使用末段名称。不得自造盘面、用吉神加减分替代判断，或暗中换用黄历宜忌。用户明确提供的口径优先，未知特殊体系保留待核。

## 输入与口径

沿用已有年份/日期范围、事项、用方、具名参与者本命、奇门法；已给出的不重复询问。未指定事项做通用日历，全部时段待判断。用方为空时，为优先/可选时段亲自比较候选并给出建议。婚姻等共同事项逐人取本命，双方缺一不能给优先/可选；只给本命地支不能推定完整八字婚配。

`mountain` 是十二地支行动/朝向参考，非二十四山施工坐向。`participants` 为最多6人的 `[{"name":"本人","branch":"午"}]`，未填支可保留空串待定。奇门法 `chaibu` 默认拆补，`zhirun` 为具名九日含符首/接气借下元置闰法。贵人表默认 `liuren-common`，可选 `xieji`；北京时间，默认 `rollover=zi` 23时换日，不作真太阳时校正。

真实七星需要此次观测点 `observer.latitude/longitude`，可加 label/elevation_m。未给坐标时传统盘面照常计算，星空保留待提供，不猜城市；需要实际星空决策再询问坐标。七星几何方位不直接决定吉凶，地平线上不保证可见。日历星空仅窗口中点快照，具体分钟重查 `get_beidou_sky`。

## 选择工具

- 单时刻排盘/方位：`get_qimen_chart` 或 `get_direction_facts`；真实星空用 `get_beidou_sky`。明确时间偏移或 `input_timezone`。
- 1–7日比较：`build_election_request(start, days, purpose, participants, mountain, qimen_method, observer, ...)`。
- 完整公历年：`build_year_election(year, purpose, participants, mountain, qimen_method, observer, ...)`，自动覆盖365/366日。
- 长于7日的非全年范围，按连续1–7日建立批次，保存每个 artifact 的范围与判断进度；不要把分散批次声称为一个年度 artifact。

工具不可用时说明缺少本插件 MCP 连接，保留用户输入，按插件根 README 配置；不改用另一项目脚本或假造 MCP 结果。服务器没有模型 API 密钥要求；由调用它的模型执行推理。

## 判断与回填

1. 保存生成结果的 `artifact_id`、`facts_digest`、**原样 context**、`window_count`。全年材料是轻量索引，不能把索引当作完整盘面。
2. `read_election_windows` 从 offset=0 开始，每次最多14窗（通常7窗），根据返回 `next_offset/has_more` 继续。不要一次将全年展开，也不要遗漏困难窗口。
3. 阅读 [references/judgment.md](references/judgment.md)，逐窗核对事项、多本命、直接关系、神煞和联合方位证据，写出优先/可选/避用/待定。每个窗口给出事实引用、冲突和具体取舍；未审阅不能冒充已判断。
4. 写出 [references/review-schema.md](references/review-schema.md) 的 review，将它传给 `render_election_calendar`。此工具累积合并各批判断，同ID重交可纠正。回填失败时只修格式或事实引用，不能为了过校验改变原始摘要、context或本命。
5. 记录返回累计 `reviewed_windows/requested_windows/complete`，继续后续批次。用户仅要候选或限期/限预算时可报告实际覆盖范围与剩余未审阅数；只有 complete=true 才称全年均已审阅。规则事实生成完成不等于模型判断完成。

最终给出所选日期、时段、方位与理由、冲突/待核项、参与者适用范围、实际覆盖数及 HTML 路径。优先只表示该事项的相对选择，不保证现实结果。彩票类事项不声称提高随机中奖概率。

## 文件交付

生成或回填后优先使用返回的 `preview_url`（标准 HTTP、本机回环地址），按客户端可用的打开页面工具展示。预览服务随 MCP 进程存活；应用重启后调用 `preview_election_calendar(artifact_id)` 取得新地址，不沿用已失效的端口或进入错误页。若预览启动失败，交付 html_path 与同目录全部 `.data.js`，年度页面按月加载；不要内联整年数据或复制进超长编辑器。浏览器拒绝某动作时不得绕过其策略，可提供已生成文件供用户打开。客户端页面工具不可用时只给预览链接，不冒称已显示。
