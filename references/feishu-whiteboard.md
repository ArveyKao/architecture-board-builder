# Delivering a board into Feishu

画板是原生白板：导入 `.drawio` 后每个形状都可双击编辑。整条链路只有三步——
**打开画板 → 清空旧内容（仅替换时）→ 导入 drawio**。

## 0. 前置

```bash
SK=~/skills-manager/architecture-board-builder
python3 "$SK/scripts/serve_cors.py" 8766 /tmp/board   # 后台跑，页面跨域 fetch 用
```

画板页面在 Qoder 内置浏览器里，CSS 视口约 568×750，截图是它的 2 倍。
用坐标定位时把截图坐标除以 2。

## 1. 找到并打开画板

文档滚动容器是 `.bear-web-x-container`，块元素带
`data-block-type` / `data-block-id`（白板为 `whiteboard`）。

```js
const el = document.querySelector('[data-block-type="whiteboard"][data-block-id="16"]');
el.scrollIntoView({block:'center'});          // 先滚到可见
const r = el.getBoundingClientRect();
const x = r.x + r.width/2, y = r.y + 60;
const t = document.elementFromPoint(x, y) || el;
['pointerdown','mousedown','pointerup','mouseup','click'].forEach(type =>
  t.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, clientX:x, clientY:y, button:0})));
t.dispatchEvent(new MouseEvent('dblclick', {bubbles:true, cancelable:true, clientX:x, clientY:y, button:0}));
```

块 id 不等于视觉顺序（图片、白板会混排）。不确定是哪块时，打开后截图确认标题，
不要凭 id 猜。

## 2. 清空旧内容（替换时）

在画板里点一下空白处取得焦点，然后按 `Meta+A` → `Delete`。
空画板会弹出「从模板创建」面板，点右上角 X 关掉。

键盘事件走真实按键（browser-use `press_key`），不要用合成 KeyboardEvent。

## 3. 导入

1. 点右上角 `⋯`（画板头部最后一个无标签按钮），菜单里有「导入 / 导出」。
2. 悬停「导入」（提示：支持导入 Draw.io 格式），再点它。
3. 此时 DOM 里出现隐藏的 `input[type=file][accept=".drawio"]`。
4. 用 `fetch` 从本地 CORS 服务取文件，装进 `DataTransfer` 注入：

```js
async () => {
  const txt = await (await fetch('http://127.0.0.1:8766/order-platform.drawio')).text();
  const inp = [...document.querySelectorAll('input[type=file]')]
    .find(i => (i.accept || '').includes('drawio'));
  if (!inp) return 'no input';
  const dt = new DataTransfer();
  dt.items.add(new File([txt], 'board.drawio', {type:'application/xml'}));
  inp.files = dt.files;
  inp.dispatchEvent(new Event('input',  {bubbles:true}));
  inp.dispatchEvent(new Event('change', {bubbles:true}));
  return 'injected ' + txt.length;
}
```

看到绿色提示「图形已导入」即成功。点击等菜单项时优先用可访问性快照里的 uid +
`hover`，纯文本匹配在菜单里可能落空。

**导入是追加，不是替换。** 新内容会落在现有内容右侧；所以替换必须先清空。

## 4. 校验

- 截图看整体；`ctrl + wheel` 缩放检查字号、文字是否换行、卡片是否越界。
- 退出画板后看文档内嵌缩略图（约 420px 宽）是否还读得出三层结构。
- 刷新文档再确认一次持久化。

## 5. 陷阱清单

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 画板突然一片空白 | wheel 事件把镜头平移走了，内容还在 | 刷新文档重开画板，**不要**删除 |
| 合成的 pointer 事件点不中形状 | 画板引擎只认真实指针手势 | 用键盘（全选/删除），或整板重导 |
| 导出图片没落到 `~/Downloads` | 内置浏览器的临时下载文件会被清掉 | 不依赖导出做备份，保留 `.drawio` |
| 文字在导入后被截断 | 文本框比实际文字窄 | 先跑 `lint_board.py`，再调宽或减字 |
| 圆角过大/过小 | `arcSize` 是短边百分比，50 = 胶囊 | 容器 3，卡片 5，胶囊 50 |
| 缩略图里一片浅色 | 分区色过于接近白色 | 加深描边，或让编号徽标用饱和色 |
| 找不到 ⋯ 菜单项 | 菜单项文本被拆分 | 用快照 uid 点击，不要用文本筛选 |

## 6. 备份与回滚

- 画板的权威备份是「文档历史」；出问题先在飞书里回滚版本。
- 本地长期保留三件套：`*.drawio`（可再导入）、`preview.png`（视觉对照）、
  生成脚本（可再生成）。不要只留截图。
