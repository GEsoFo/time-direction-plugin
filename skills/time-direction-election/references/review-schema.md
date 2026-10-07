# 判断格式

返回的 facts_digest/context 原样复制，包括 lives、observer、qimen_method、profile、direction_policy。不要手动重构旧字段或按当前页面改 context。每次回填可只有当前已审阅批次。

```json
{
  "facts_digest": "从 MCP 返回原样复制",
  "context": {},
  "decisions": [
    {
      "id": "从窗口返回原样复制",
      "verdict": "待定",
      "reason": "说明真实缺项或冲突以及对指定事项的影响。",
      "evidence": ["引用该窗口真实字段及实际值"]
    }
  ]
}
```

上面 context={} 仅说明占位位置，实际必须用完整返回对象。verdict 为优先/可选/避用/待定，每项 reason 非空、evidence 非空；ID不能重复、必须属于该 artifact。未指定用方且可用的项必须加：

```json
"suggested_direction": {
  "branch": "模型从真实候选选择的一个地支",
  "reason": "解释所选方怎样适合此事项和全部参与者，以及冲突如何取舍。",
  "evidence": ["该方真实盘面、关系和观测字段"]
}
```

这是结构示例，不是可直接提交的事实或推荐。服务器检查版本、上下文和结构，不能证明模型推理正确；提交前核对证据确实存在，避免把候选条件冒作确定结论。
