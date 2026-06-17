---
cssclasses:
  - homepage-dashboard
---

## 快捷操作
```dataviewjs
const actions = [
  { label: "今日笔记", shortLabel: "今日笔记", command: "periodic-notes:open-daily-note", variant: "accent", row: "top" },
  { label: "本周总结", shortLabel: "本周总结", command: "periodic-notes:open-weekly-note", variant: "muted", row: "top" },
  { label: "新建 Task", shortLabel: "Task", command: "templater-obsidian:create-10.Template/projects/task - template.md", variant: "dark", row: "bottom" },
  { label: "新建 Project", shortLabel: "Project", command: "templater-obsidian:create-10.Template/projects/项目- template.md", variant: "dark", row: "bottom" },
  { label: "New Book", shortLabel: "Book", command: "obsidian-book-search-plugin:open-book-search-modal", variant: "dark", row: "bottom" },
  { label: "New Movie", shortLabel: "Movie", command: "obsidian-media-db-plugin:open-media-db-search-modal-with-movie", variant: "dark", row: "bottom" },
];

// 命令不存在时(改了模板名/路径、插件没开)给出提示，而不是点了没反应
const runCommand = (action) => {
  const ok = app.commands.executeCommandById(action.command);
  if (!ok) {
    new Notice(`命令未找到，请检查：${action.command}`);
  }
};

const wrap = dv.el("div", "", { cls: "hp-quick-launch" });
const topRow = wrap.createEl("div", { cls: "hp-quick-actions hp-quick-actions-top" });
const bottomRow = wrap.createEl("div", { cls: "hp-quick-links" });

for (const action of actions) {
  if (action.row === "top") {
    const button = topRow.createEl("button", {
      text: action.label,
      cls: `hp-quick-action hp-quick-action-${action.variant}`,
    });
    button.type = "button";
    button.setAttr("aria-label", action.label);
    button.addEventListener("click", () => runCommand(action));
  } else {
    const link = bottomRow.createEl("button", {
      text: action.shortLabel,
      cls: "hp-quick-link",
    });
    link.type = "button";
    link.setAttr("aria-label", action.label);
    link.addEventListener("click", () => runCommand(action));
  }
}
```

## 快速导航
> [!multi-column]
> 
>
>> [!tip]+  阅读
>>  ### #mcl/list-card
>> - [[Shelf]]
>> - [[Media Library]]
>> - [[1_to read]]
>> - [[0_read list 个人成长维度]]
>> - [[2_to watch]]
>> - [[阅读统计]]
>> - [[阅读复习]]
>
>> [!summary]+ 项目
>>  ### #mcl/list-card
>> - [[a1.博客网站]]
>> - [[a2.影响力]]
>> - [[a3.obsidian探索]]
>> - [[a4.项目idea]]
>> - [[a5.AI工作流]]
>> - [[b1.make money]]
>> - [[c1.read]]
>> - [[d1.身体健康]]
>
>> [!warning]+  备忘
>>  ### #mcl/list-card
>> - [[2.obsidian]]
>> - [[5.ai]]
>> - [[剪辑]]
>> - [[tag]]
>> - [[最近删除文件]]
>
>> [!todo]+  Todo
>>  ### #mcl/list-card
>> - [[5.todo/0_view/todo|todo]]
>> - [[draft-todo]]
>> - [[回顾本周]]
>> - [[0.core]]
>> - [[long-term]]
>> - [[schedule-task]]
>> - [[token-todo]]
>> - [[0-fleeting]]


## 常用项目
> [!multi-column]
> 
>
>> [!info]+ Projects
>>  ### #mcl/list-card
>> - [[项目总览]]
>> - [[task总览]]
>> - [[a2-02-视频制作发布SOP]]
>> - [[a2-01-视频可选列表]]
>
>> [!note]+ 最近笔记
>> ```dataview
>> LIST FROM "1.Rough" OR "2.Read" OR "3.learn" OR "4.Projects" OR "5.todo" OR "12.skills" OR "JC-open"
>> SORT file.ctime DESC
>> LIMIT 5
>> ```
>
>> [!todo]+  今日任务
>> ```tasks
>> not done
>> scheduled on today
>> path includes 5.todo
>> hide backlink
>> limit 7
>> ```

## 常用模板
> [!multi-column]
> 
>
>> [!summary]+ 项目模板
>>  ### #mcl/list-card
>> - [[10.Template/projects/项目- template|project模板]]
>> - [[10.Template/projects/task - template|task模板]]
>> - [[10.Template/projects/try|try模板]]
>
>> [!todo]+ 计划模板
>>  ### #mcl/list-card
>> - [[10.Template/todo/daily|Daily]]
>> - [[10.Template/todo/weekly|Weekly]]
>> - [[10.Template/todo/每天任务|每天任务]]
>> - [[10.Template/todo/每天+周任务|每天+周任务]]
>
>> [!tip]+ 书影模板
>>  ### #mcl/list-card
>> - [[book-ch]]
>> - [[book-en]]
>> - [[movie-ch|影视记录]]
>
>> [!info]+ 记录模板
>>  ### #mcl/list-card
>> - [[10.Template/想法验证模版|想法验证]]
>> - [[10.Template/阅读/复习|阅读复习]]
>> - [[10.Template/阅读/复习+prepare|复习准备]]


## 热力图
### 活跃度热力图
```contributionGraph
title: Contributions
graphType: default
dateRangeValue: 1
dateRangeType: LATEST_YEAR
startOfWeek: "0"
showCellRuleIndicators: true
titleStyle:
  textAlign: left
  fontSize: 17px
  fontWeight: normal
dataSource:
  type: PAGE
  value: ""
  dateField:
    type: FILE_MTIME
  filters: []
fillTheScreen: false
enableMainContainerShadow: true
cellStyleRules:
  - id: default_b
    color: "#9be9a8"
    min: 1
    max: 2
  - id: default_c
    color: "#40c463"
    min: 2
    max: 5
  - id: default_d
    color: "#30a14e"
    min: 5
    max: 10
  - id: default_e
    color: "#216e39"
    min: 10
    max: 999
cellStyle:
  minWidth: 12px
  minHeight: 12px

```
### 字数热力图
```dataviewjs
let data = [];
try {
  const jsonString = await app.vault.adapter.read(".obsidian/vault-stats.json");
  const history = JSON.parse(jsonString).history;
  data = Object.entries(history).map(([date, v]) => ({
      date,
      value: (v && v.words) || 0,
  }));
} catch (e) {
  data = [];
}

const year = new Date().getFullYear();
const box = this.container.createEl("div");

window.renderContributionGraph(box, {
    title: "字数热力图",
    data,
    graphType: "default",
    fromDate: `${year}-01-01`,
    toDate: `${year}-12-31`,
    startOfWeek: "0",
    showCellRuleIndicators: true,
    enableMainContainerShadow: true,
    titleStyle: { textAlign: "left", fontSize: "17px", fontWeight: "normal" },
    cellStyle: { minWidth: "12px", minHeight: "12px" },
    cellStyleRules: [
        { color: "#deebf7", min: 1, max: 61 },
        { color: "#c6dbef", min: 61, max: 151 },
        { color: "#9ecae1", min: 151, max: 351 },
        { color: "#6baed6", min: 351, max: 651 },
        { color: "#3182bd", min: 651, max: 1501 },
        { color: "#08519c", min: 1501, max: 9999999 },
    ],
});
```