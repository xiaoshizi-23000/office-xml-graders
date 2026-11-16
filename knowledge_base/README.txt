# 信息系统知识库（四川对口升学计算机类）

面向小程序的考纲知识库，依据四川省 2023 版职业技能考试大纲计算机类整理。

## 文件说明

```
knowledge_base/
  syllabus_2023.json       考纲框架：13 模块、143 条知识点、分值与题型结构
  knowledge_base.json      知识库主体：每条含考纲依据、教材出处、版本差异、练习题
  point_refs.json          知识点到教材小节的映射（中间产物，可留作校验）
  textbook_sections.json   教材 236 个小节，含页码和正文（中间产物）
  tasks_up.json            上册 50 个任务目录与页码
  tasks_down.json          下册 15 个任务目录与页码
  keyword_map.json         考纲术语到教材关键词的映射
```

## 数据来源

考纲是扫描件，17 页逐页图像识别，没有走文字解析。教材是 HTML 打印版，有完整文字层，全文提取并导出图片：

```
上册 675 页  353568 字  327 张图
下册 832 页  364571 字  357 张图
```

图片在 `_kb_extract/book_up/images/` 和 `_kb_extract/book_down/images/`，文件名格式 `p页码_i序号.ext`，知识库里用 `images` 字段关联。

## 数据结构

每条知识点长这样：

```
{
  "id": "A1-01",                     模块号-序号
  "module_id": "A1",
  "module_name": "计算机基础",
  "part": "专业知识",                 专业知识 / 技能操作
  "point": "了解计算机的发展、特点、分类及应用领域",
  "syllabus": {
    "version": "2023",
    "module": "计算机基础",
    "ratio": "约30%",
    "score": null,                   技能操作模块有具体分值
    "exam_note": null                题型示例里的考试要求
  },
  "textbook": [
    {
      "book": "上册",
      "page": 26,
      "section": "1.6.2 ...",
      "excerpt": "教材原文前 400 字",
      "images": ["p0026_i01.png"]
    }
  ],
  "version_diff": {                  仅 Win7/Office2010 相关模块有
    "env": "教材 Windows 10，考纲 Windows 7",
    "same": [...],                   两边一致，直接用教材
    "different": [...],              有差异，按考纲来
    "source": "..."
  },
  "question": {
    "type": "简答 / 判断选择 / 操作",
    "q": "题目",
    "a_hint": "答案提示或教材原文"
  }
}
```

## 版本差异处理

教材环境是 Windows 10 + Office 2016 + Access 2016，考纲要求 Windows 7 + Office 2010 + Dreamweaver CS6。处理原则：

相同的部分直接用教材内容。已经查证一致的包括文件或文件夹命名规则（255 字符、禁用字符、不区分大小写、同目录不可同名）、资源管理器树形结构和基本操作、cmd 命令、SUM/AVERAGE 等函数语法、Word 的查找替换和段落格式、IE 的 Internet 选项设置项、HTML/CSS 标记写法。

有差异的部分单独标注在 `version_diff.different` 里，按考纲环境为准。主要是界面路径：Win7 工具栏的「组织」按钮对应 Win10 的「主页」选项卡，Win7 的控制面板入口和 Win10 的设置应用不同，Office 2016 的「设计→变体」对应 2010 的「设计→主题」。

差异来源写在 `version_diff.source` 字段，便于复核。

## 覆盖情况

143 条知识点全部挂上了教材出处（原文节选或任务页码），其中 66 条带版本差异标注，142 条生成了练习题骨架。少量知识点是同模块任务级对应，textbook 里有 note 字段标明；中英文录入没有教材对应内容，用的是考纲题型示例。

## 后续接入小程序

按 `module_id` 和 `part` 分组即可。`question` 是题目骨架，`a_hint` 是答案提示，正式上线前建议人工过一遍题目表述。图片路径可以直接指向导出的 images 目录。
