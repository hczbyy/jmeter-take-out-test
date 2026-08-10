# api_test

用 JMeter 对外卖平台接口进行功能测试的练习仓库，包含被测系统源码与 JMeter 测试脚本。

## 仓库结构

```text
api_test/
├── 外卖平台搭建/              # 被测外卖系统源码（Flask + JSON）
│   ├── main.py                # 后端：注册、登录、搜索、购物车、订单、支付、评价等接口
│   ├── web/index.html         # 外卖点餐平台前端
│   └── data/database.json     # 系统数据（用户、商品、订单等）
├── 登录模块.jmx               # 登录接口测试
├── 测试注册模块.jmx           # 注册接口测试
├── 提取token.jmx              # 登录并提取 Token
├── 搜索功能.jmx               # 商品搜索功能测试
├── 加购物车.jmx               # 加入购物车
├── 购物车功能.jmx             # 购物车功能测试
├── 提交订单.jmx               # 提交订单
├── 订单支付.jmx               # 订单支付
├── 取消订单.jmx               # 取消订单
├── Test Plan.jmx              # 主测试计划（全业务链路）
├── 外卖系统简单接口文档.docx  # 接口说明文档
├── index.html                 # JMeter HTML 报告（可浏览器打开）
└── README.md                  # 本文件
```

## 外卖平台搭建（被测系统）

基于 Flask + JSON 文件存储的外卖点餐平台，提供注册/登录、用户信息与地址、商品/分类/店铺查询、收藏、购物车、下单/支付/取消、评价以及管理后台等 RESTful 接口。

### 启动方式

```bash
cd 外卖平台搭建
pip install flask flask-cors
python main.py
```

启动后访问：

- 用户端：<http://127.0.0.1:8080>
- 商家端：<http://127.0.0.1:8080/admin>

测试账号密码均为 `123456`（哈希存储，如管理员 `admin`）。

### 主要接口

| 模块 | 接口 |
| --- | --- |
| 注册 / 登录 | `POST /api/register`、`POST /api/login` |
| 用户信息 | `GET /api/user/info`、`POST /api/user/address`、`GET /api/user/addresses` |
| 商品查询 | `GET /api/foods`、`GET /api/categories`、`GET /api/shops`、`GET /api/foods/<id>` |
| 收藏 | `POST /api/favorites`、`GET /api/favorites` |
| 购物车 | `POST /api/cart`、`GET /api/cart` |
| 订单 | `POST /api/orders`、`GET /api/orders`、`POST /api/orders/<id>/pay`、`POST /api/orders/<id>/cancel` |
| 评价 | `POST /api/reviews`、`GET /api/reviews` |
| 管理后台 | `GET /api/admin/orders`、`PUT /api/admin/orders/<id>/status` |

## JMeter 测试说明

JMeter 脚本均指向 `http://127.0.0.1:8080`，覆盖注册、登录、搜索、购物车、下单、支付、取消订单等业务模块；`Test Plan.jmx` 为主测试计划，串联完整业务链路。接口字段说明详见 `外卖系统简单接口文档.docx`。
