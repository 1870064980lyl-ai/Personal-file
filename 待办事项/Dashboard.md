# 待办事项管理

## 快速操作

- [[新建待办事项]] - 创建新的待办事项
- [[待办事项模板]] - 查看模板格式
- [[本月待办]] - 查看本月所有任务

---

## 🔴 即将到期任务 (3天内)

> ⚠️ 以下任务将在3天内到期，请优先处理！

```dataview
TASK
WHERE !completed
AND due
AND due <= date(today) + dur(3 days)
AND due >= date(today)
SORT due ASC
LIMIT 10
```

---

## 今日待办

```dataview
TASK
WHERE !completed
AND due = date(today)
SORT due ASC
```

---

## 本周待办

```dataview
TASK
WHERE !completed
AND due
AND due >= date(today)
AND due <= date(today) + dur(7 days)
SORT due ASC
```

---

## 所有待办事项

```dataview
TASK
WHERE !completed
AND due
SORT due ASC
```

---

## 已完成任务

```dataview
TASK
WHERE completed
SORT completed ASC
LIMIT 10
```

---

## 已过期任务

```dataview
TASK
WHERE !completed
AND due
AND due < date(today)
SORT due ASC
```

---

## 待办事项管理技巧

### 1. 定期回顾
- 每天查看 Dashboard
- 每周回顾所有待办事项
- 每月清理已完成的任务

### 2. 使用标签
- #待办事项 - 所有待办事项
- #高优先级 - 紧急任务 (红色显示)
- #中优先级 - 重要任务 (橙色显示)
- #低优先级 - 可推迟任务 (绿色显示)
- #紧急 - 需要立即处理

### 3. 任务格式
```markdown
- [ ] 任务名称 [due:: YYYY-MM-DD] #标签
```

### 4. 设置提醒
- 使用 Obsidian 的提醒插件
- 设置截止日期提醒
- 创建每日待办事项清单

### 5. 归档完成的任务
- 定期将已完成的任务移到归档文件夹
- 保持 Dashboard 整洁

---

## 配置说明

- **CSS样式**: `.obsidian/snippets/tasks-auto-highlight.css`
- **本月待办**: [[本月待办]]
- **配置说明**: [[任务管理配置说明]]