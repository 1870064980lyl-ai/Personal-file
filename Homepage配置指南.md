# Homepage 配置指南

## 已完成的配置

### 1. CSS代码片段
- ✅ 已安装 `MCL Multi Column.css` 到 `.obsidian/snippets/`
- ✅ 已安装 `homepage-columns.css` 到 `.obsidian/snippets/`
- ✅ 已在外观设置中启用这两个CSS代码片段

### 2. Homepage文件
- ✅ 已创建 `homepage.md` 文件到知识库根目录

### 3. 插件目录
- ✅ 已创建 `homepage` 插件目录
- ✅ 已创建 `contribution-graph` 插件目录
- ✅ 已创建 `better-word-count` 插件目录
- ✅ 已更新 `community-plugins.json` 文件

## 需要手动完成的步骤

### 步骤1：安装插件
由于插件文件需要从GitHub下载，请按照以下步骤操作：

1. **Homepage插件**
   - 访问: https://github.com/mnowosad/obsidian-homepage/releases
   - 下载最新的 `main.js` 和 `manifest.json` 文件
   - 将文件放入 `.obsidian/plugins/homepage/` 目录

2. **Contribution Graph插件**
   - 访问: https://github.com/Developer/obsidian-contribution-graph/releases
   - 下载最新的 `main.js` 和 `manifest.json` 文件
   - 将文件放入 `.obsidian/plugins/contribution-graph/` 目录

3. **Better Word Count插件**
   - 访问: https://github.com/Developer/obsidian-better-word-count/releases
   - 下载最新的 `main.js` 和 `manifest.json` 文件
   - 将文件放入 `.obsidian/plugins/better-word-count/` 目录

### 步骤2：启用插件
1. 打开Obsidian
2. 进入 `设置` → `第三方插件`
3. 启用以下插件：
   - Homepage
   - Contribution Graph
   - Better Word Count

### 步骤3：配置Homepage插件
1. 进入 `设置` → `Homepage`
2. 设置首页为 `homepage`
3. 启用 `Pin homepage`
4. 启用 `Open in reading view`

### 步骤4：配置Dataview插件
1. 进入 `设置` → `Dataview`
2. 启用 `Enable JavaScript Queries`

### 步骤5：调整homepage.md内容
根据你的实际目录结构，修改 `homepage.md` 文件中的链接：

1. 修改"快速导航"部分的链接
2. 修改"常用项目"部分的链接
3. 修改"常用模板"部分的链接
4. 确保所有链接都指向你实际存在的文件

## 注意事项
1. 确保你已经安装了Templater插件（已安装）
2. 确保你已经安装了Dataview插件（已安装）
3. 热力图功能需要插件支持，请确保相关插件已启用
4. 首次使用时，可能需要重启Obsidian

## 自定义建议
1. 根据你的工作流程调整快捷操作按钮
2. 根据你的项目结构调整常用项目部分
3. 根据你的模板结构调整常用模板部分
4. 可以添加更多模块到homepage.md文件中