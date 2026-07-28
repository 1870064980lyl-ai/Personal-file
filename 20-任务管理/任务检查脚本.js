// 任务检查脚本 - 用于检测即将到期的任务
// 将此脚本放入 Templater 插件的脚本目录中使用

module.exports = async (app) => {
  const today = new Date();
  const warningDays = 3;
  const warningDate = new Date(today);
  warningDate.setDate(today.getDate() + warningDays);

  // 获取所有待办事项文件
  const files = app.vault.getMarkdownFiles();
  const tasks = [];

  for (const file of files) {
    const content = await app.vault.read(file);
    const lines = content.split('\n');

    for (const line of lines) {
      // 匹配任务格式: - [ ] 任务名 [due:: YYYY-MM-DD]
      const taskMatch = line.match(/- \[([ x])\] (.+) \[due:: (\d{4}-\d{2}-\d{2})\]/);
      if (taskMatch) {
        const completed = taskMatch[1] === 'x';
        const taskName = taskMatch[2];
        const dueDate = new Date(taskMatch[3]);

        if (!completed && dueDate >= today && dueDate <= warningDate) {
          tasks.push({
            name: taskName,
            due: dueDate,
            file: file.path,
            daysLeft: Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24))
          });
        }
      }
    }
  }

  // 按截止日期排序
  tasks.sort((a, b) => a.due - b.due);

  if (tasks.length === 0) {
    return "没有即将到期的任务。";
  }

  // 生成提醒内容
  let reminder = `## ⚠️ 即将到期任务 (${tasks.length}个)\n\n`;
  for (const task of tasks) {
    const urgency = task.daysLeft <= 1 ? '🔴' : task.daysLeft <= 2 ? '🟡' : '🟢';
    reminder += `${urgency} **${task.name}**\n`;
    reminder += `   - 截止日期: ${task.due.toISOString().split('T')[0]}\n`;
    reminder += `   - 剩余天数: ${task.daysLeft}天\n`;
    reminder += `   - 文件: [[${task.file}]]\n\n`;
  }

  return reminder;
};
