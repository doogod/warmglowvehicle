# WARMGLOW — 日本右舵超跑车源展示网页

面向马来西亚客户（主要在 iPad 上演示）的静态车辆展示网站。汇总 Cornes Motors 与 Carsensor 上的右舵高端车源，提供筛选、精选推荐与车辆详情。

- 线上地址：https://doogod.github.io/warmglowvehicle/
- 托管：GitHub Pages（`main` 分支，根目录 `/`）
- 网页为单文件：`index.html`（数据内嵌，图片直接引用来源网站的原图地址）
- 最近一次数据更新：2026-11-21

---

## 1. 数据范围（需求）

| 项目 | 规则 |
|---|---|
| 数据来源 | Cornes Motors 官网 `cornesmotors.com/usedcar/`（Bentley / Lamborghini / Rolls-Royce）与 `/usedcar/ferrari`；Carsensor `carsensor.net`（全国经销商） |
| 品牌 | Ferrari、Lamborghini、Rolls-Royce、Porsche、Bentley、Maserati、McLaren |
| Porsche | **只收录 911**（Carsensor 车系 911 / 911 カブリオレ / 911 ダカール，含 Targa、GT3、Turbo 等） |
| 方向盘 | 仅右舵（Cornes：`handlePosition = 右`；Carsensor：搜索条件 `ST=R`） |
| 年份 | 首次登记 2022 年及以后（Carsensor：`YMIN=2022`） |
| 马来西亚进口规则 | 马来西亚只允许登记满 12 个月的二手车进口。我们可先购买并暂放日本等待满一年，因此：<br>• 登记 ≥ 12 个月：标「可立即进口」<br>• 登记 6–12 个月：保留，标「需在日本等待」及可进口月份（登记月 + 12 个月）<br>• 登记 < 6 个月：暂不显示<br>规则在网页中按**打开当天日期**动态计算，车辆满 6 个月后自动出现 |
| 去重 | Cornes 自家车辆同时挂在 Carsensor 上时只保留一条（Cornes 官网数据优先）。匹配条件：品牌 + 车架号末三位 + 登记年份，且 Carsensor 店铺属于 Cornes 系展厅 |
| 左右舵冲突 | 同一车架号在 Carsensor 标右舵、Cornes 官网标左舵时，仍收录，但详情页提示「请确认」，且不进入精选 |
| 新车源判断 | 每次更新与上一版的车源编号（Cornes `sfid` / Carsensor `AU…` 编号）对比：新出现的标「新 / NEW」，已下架的删除 |

### Carsensor 品牌代码
`FE` Ferrari · `LG` Lamborghini · `RR` Rolls-Royce · `PO` Porsche（911 车系：`s001`、`s002`、`s027`） · `BE` Bentley · `MS` Maserati · `ML` McLaren

搜索地址格式：`https://www.carsensor.net/usedcar/search.php?STID=CS210610&BRDC={代码}&YMIN=2022&ST=R`，翻页 `…/usedcar/b{代码}/index{N}.html?YMIN=2022&ST=R`

---

## 2. 页面功能（需求）

### 通用
- 网站名称 **WARMGLOW**，使用公司 logo（橙金渐变 `#f38c47 → #ffc957`），暗色暖光风格
- 默认语言**英文**，右上角可切换**中文**
- 已删除：顶部 hero banner、车辆统计区
- 列表每次显示 48 台，底部「加载更多」

### 品牌筛选
- 8 个按钮：全部品牌 + 7 个品牌，类似 Cornes 官网的品牌卡片
- 每个按钮：圆形字母徽章、品牌名、产地、车辆数、半透明大字母水印、品牌色光晕
- **暂时不使用车辆照片作为按钮背景**（已去掉）
- 不使用真实品牌 logo（商标）。如有授权 logo 文件，可在 `index.html` 的 `BRAND_LOGOS` 中填写图片路径，自动替换字母

### 其他筛选
- **精选**：全部车辆 / ★ WARMGLOW 精选 / 按标签（同车型首选、超值、价格合理、低里程、准新车、Cornes 认证、稀有）
- **车型**：选中品牌后出现该品牌的车型系列
- **马来西亚进口**：全部 / 可立即进口 / 需在日本等待
- **来源**：全部 / Cornes Motors / Carsensor / 本次更新新增
- **排序**：登记日期最新、价格低→高、价格高→低、里程最少
- **汇率**：1 JPY = X MYR，默认 `0.0258`（约值，可在页面修改，记忆在浏览器本地）

### 车辆卡片
登记年月、来源、★精选、新上架、需等待进口的月份、车型名、精选标签、里程、外观色、所在地、税前日元价、税前马币价

### 详情页
- **上下排列**：照片铺满屏幕宽度在上（竖屏 4:3 不裁切；横屏 16:10），缩略图在下，车辆信息在最下（宽屏分左右两栏：价格 / 参数）
- 照片：左右滑动切换，点击全屏查看原图，键盘左右键 / Esc
- 显示内容：
  - 车辆型号名称（含版本，如 911 Carrera 4 GTS Cabriolet）
  - 车辆图片（每台最多约 14 张）
  - **税前日元价**（= 含税标价 ÷ 1.1，出口买家通常按此价支付）
  - **税前价换算马币**
  - **含税日元价**（日本标价含 10% 消费税）
  - 支付总额（含手续费）
  - 里程
  - **登记年月**（月份缺失时用车检月份，并注明「月份取自车检」）
  - 外观颜色、内饰颜色
  - 马来西亚进口状态、方向盘、车检到期、排量、变速箱、展厅/经销商（英文）
  - 精选理由（比预期价格高/低多少、对比了多少台同款）
  - 原始页面链接（Cornes 或 Carsensor）
- 价格面议（応談）的车显示「价格面议」，按价格排序时排最后

### iPad / 触屏适配
- 所有按钮触控面积 ≥ 44px；输入框字号 16px（避免 iOS 自动放大）
- 触屏无悬停效果，按下有缩放反馈；去除双击放大延迟
- 适配刘海与底部安全区；支持「添加到主屏幕」全屏使用（`apple-touch-icon.png`）
- 已在 820×1180、1180×820、744×1133、390×844、1440×900 下检查，无横向溢出

---

## 3. 精选（WARMGLOW Picks）方法

1. 按车型系列分组（如 911、911 Cabriolet、Roma Spider、Urus、Grecale、Artura…）
2. 每个系列内，对税前价格取对数，用 **版本（固定效应）+ 年份 + log(里程)** 做岭回归，得到每台车的「预期价格」；样本少于 4 台时用中位数
3. 偏差 = 实际税前价 ÷ 预期价 − 1（负数 = 比市场便宜）
4. 每个系列分配 1–3 个名额（`round(√n × 0.32)`，至少 1、至多 3），保证**每个车型都有精选**
5. 排序分数 = −偏差×100，加分：里程 ≤ 1,000 km（+2）、Cornes 车源（+1.5）、已可进口（+1）；扣分：里程 > 25,000 km（−2）、> 40,000 km（−4）
6. 只从「登记满 6 个月、无左右舵冲突」的车中挑选
7. 当前共 46 台（33 个车型系列，原需求「约 30 台，无需严格」）

标签规则：同车型首选（系列第 1 名）、超值（偏差 ≤ −5% 且同系列 ≥ 3 台）、价格合理（−5% ~ +2%）、低里程（≤ 1,000 km）、准新车（≤ 300 km）、Cornes 认证（Cornes 车源）、稀有（同系列 ≤ 2 台）

「市场」指本次抓取的全部日本右舵在售车，不含成交数据。

---

## 4. 已知限制

- Carsensor 没有内饰颜色字段，大多数 Carsensor 车辆显示「未标注」
- Carsensor 只提供登记年份，月份由车检月份推算（新车首次车检为 3 年后）
- 部分 Cornes 车在 Carsensor 上只有 1–3 张照片
- 约 29 台价格面议
- 车架号只有末三位，去重存在极小概率误判（如两台 2025 年 296 GTS 末三位同为 904，但颜色、价格不同，均保留）
- 图片直接引用来源网站地址：在 Claude 应用的文件预览中不会显示，需在浏览器或线上地址打开；来源网站下架后图片会失效
- 汇率为约值，需按实际调整

---

## 5. 数据更新流程

抓取需要在 Claude 桌面应用的内置浏览器（或 Chrome 插件）中执行，云端环境无法直接访问 Cornes / Carsensor。

1. **Carsensor**：按第 1 节的品牌代码获取搜索结果中所有车源编号，再逐个抓取详情页 `https://www.carsensor.net/usedcar/detail/{编号}/index.html`，解析：车名、车系、年式、走行距离、車検、色、ハンドル、車台末尾番号、ミッション、排気量、車両本体価格、支払総額、店铺、所在地、图片（`ccsrpcma…/bkkn/…L.JPG` 主图 + `ccsrpcml…/ml/…_N_00X.jpg`）
2. **Cornes**：在 `/usedcar/`、`/usedcar/ferrari` 点击「さらに読み込む」加载全部车辆，从 React 状态读取车辆数组（含 `handlePosition`、`vinSuffix`、颜色、价格等），再逐台打开详情弹窗获取全部图片
3. 将数据保存为 `cs_new.json`、`cornes1.json`、`cornes_fer.json`、`cornes_main_allh.json`（左右舵对照）、`prev_ids.json`（上一版车源编号）
4. 运行 `tools/` 下脚本：
   - `python3 build.py`：翻译（车型/版本、颜色、经销商、都道府县，见 `maps.py`、`shops.py`）、去重、标记新车源 → `data.json`
   - `python3 picks.py`：计算精选 → `picks2.json`
   - `python3 emit.py`：压缩输出 `data_block.js`
5. 将 `data_block.js` 的内容替换到 `index.html` 中 `const PICKS = …` 与 `const DATA = …` 两行
6. 修改页脚中的「最近更新」日期，推送到 `main` 分支，GitHub Pages 约 1–2 分钟后生效

---

## 6. 文件结构

```
index.html             网页（含样式、脚本、数据）
apple-touch-icon.png   iPad「添加到主屏幕」图标
.nojekyll              GitHub Pages 直接发布静态文件
README.md              本文件
tools/
  build.py             合并、翻译、去重、标记新车源
  maps.py              车型/版本解析、颜色与地名翻译
  shops.py             经销商名称英文对照
  picks.py             精选计算
  emit.py              输出页面数据块
```

---

## 7. 更新记录

| 日期 | 内容 |
|---|---|
| 2026-11-20 | 初版：Cornes 的 Ferrari / Lamborghini / Rolls-Royce，右舵、2022 年起，30 台；画廊、品牌与车型筛选、详情页、税前/含税日元与马币 |
| 2026-11-20 | 加入 Carsensor 并去重（134 台）；改名 WARMGLOW 并使用 logo；删除统计区 |
| 2026-11-20 | 删除 hero banner；品牌筛选改为卡片；新增 32 台精选与标签筛选 |
| 2026-11-20 | 部署到 GitHub Pages；iPad 触屏适配；详情页改为上下排列、照片铺满屏幕宽度 |
| 2026-11-21 | 马来西亚进口规则（隐藏 < 6 个月，6–12 个月标注等待）；新增 Porsche 911、Bentley、Maserati、McLaren；重新抓取全部数据（681 台，显示 650 台）；按车源编号标记新车源；精选 46 台；品牌卡片 8 个；分页加载 |
| 2026-11-21 | 品牌筛选按钮去掉车辆照片背景 |
