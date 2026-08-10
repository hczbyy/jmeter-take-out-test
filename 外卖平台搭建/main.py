from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import json
import hashlib
import uuid
from datetime import datetime, timedelta
import os
import re
import time

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'food-delivery-secret-key-2026'
CORS(app, supports_credentials=True, origins='*')

# ============ 数据管理 ============

DATA_FILE = 'data/database.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return init_data()


def save_data(data):
    os.makedirs('data', exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_data():
    return {
        'users': {},
        'foods': [],
        'orders': {},
        'favorites': {},
        'coupons': {},
        'reviews': [],
        'cart': {},
        'current_order_id': 1000,
        'payment_records': {},
        'addresses': {}
    }


db = load_data()


# ============ 初始化外卖数据 ============

def init_foods():
    if db['foods']:
        return
    db['foods'] = [
        # 汉堡类
        {"id": 1, "name": "招牌炸鸡汉堡", "shop": "麦当劳", "category": "汉堡", "price": 25.0, "rating": 4.8,
         "sales": 999, "image": "🍔", "desc": "香脆鸡腿肉+生菜+特制酱料"},
        {"id": 2, "name": "巨无霸汉堡", "shop": "麦当劳", "category": "汉堡", "price": 32.0, "rating": 4.7,
         "sales": 888, "image": "🍔", "desc": "双层牛肉+芝士+酸黄瓜"},
        {"id": 3, "name": "香辣鸡腿堡", "shop": "肯德基", "category": "汉堡", "price": 28.0, "rating": 4.6,
         "sales": 777, "image": "🍔", "desc": "香辣鸡腿+生菜+沙拉酱"},
        {"id": 4, "name": "嫩牛五方", "shop": "肯德基", "category": "汉堡", "price": 30.0, "rating": 4.7, "sales": 555,
         "image": "🌯", "desc": "牛肉+生菜+番茄+酱料"},

        # 中餐类
        {"id": 5, "name": "麻辣香锅套餐", "shop": "海底捞", "category": "中餐", "price": 38.0, "rating": 4.9,
         "sales": 888, "image": "🌶️", "desc": "麻辣鲜香，配料丰富，可选荤素搭配"},
        {"id": 6, "name": "酸菜鱼", "shop": "太二酸菜鱼", "category": "中餐", "price": 58.0, "rating": 4.8,
         "sales": 666, "image": "🐟", "desc": "酸爽开胃，鱼肉鲜嫩，配菜丰富"},
        {"id": 7, "name": "烤鸭套餐", "shop": "全聚德", "category": "中餐", "price": 88.0, "rating": 4.9, "sales": 555,
         "image": "🦆", "desc": "皮脆肉嫩，片片美味，配薄饼甜面酱"},
        {"id": 8, "name": "红烧肉饭", "shop": "外婆家", "category": "中餐", "price": 35.0, "rating": 4.5, "sales": 444,
         "image": "🍖", "desc": "肥而不腻，入口即化，配时蔬"},
        {"id": 9, "name": "宫保鸡丁", "shop": "川味馆", "category": "中餐", "price": 32.0, "rating": 4.6, "sales": 333,
         "image": "🍗", "desc": "麻辣鲜香，鸡丁嫩滑，花生酥脆"},
        {"id": 10, "name": "水煮牛肉", "shop": "川味馆", "category": "中餐", "price": 45.0, "rating": 4.7, "sales": 222,
         "image": "🥩", "desc": "麻辣鲜香，牛肉嫩滑，配菜丰富"},

        # 披萨类
        {"id": 11, "name": "至尊披萨", "shop": "必胜客", "category": "披萨", "price": 45.0, "rating": 4.7, "sales": 777,
         "image": "🍕", "desc": "培根+香肠+蘑菇+芝士，9寸"},
        {"id": 12, "name": "海鲜披萨", "shop": "必胜客", "category": "披萨", "price": 52.0, "rating": 4.6, "sales": 333,
         "image": "🍕", "desc": "虾仁+鱿鱼+蟹柳+芝士，9寸"},

        # 日料
        {"id": 13, "name": "三文鱼寿司拼盘", "shop": "寿司郎", "category": "日料", "price": 68.0, "rating": 4.9,
         "sales": 666, "image": "🍣", "desc": "新鲜三文鱼+醋饭+海苔，12贯"},
        {"id": 14, "name": "鳗鱼饭", "shop": "寿司郎", "category": "日料", "price": 42.0, "rating": 4.8, "sales": 222,
         "image": "🍱", "desc": "蒲烧鳗鱼+米饭+蛋丝，配味增汤"},

        # 面食
        {"id": 15, "name": "牛肉拉面", "shop": "兰州拉面", "category": "面食", "price": 18.0, "rating": 4.6,
         "sales": 555, "image": "🍜", "desc": "手工拉面+牛肉+香菜+清汤"},
        {"id": 16, "name": "炸酱面", "shop": "老北京炸酱面", "category": "面食", "price": 22.0, "rating": 4.5,
         "sales": 333, "image": "🍜", "desc": "手擀面+肉酱+黄瓜丝+豆芽"},
        {"id": 17, "name": "重庆小面", "shop": "重庆小面馆", "category": "面食", "price": 16.0, "rating": 4.4,
         "sales": 444, "image": "🍜", "desc": "麻辣鲜香，劲道爽滑，配花生碎"},
        {"id": 18, "name": "酸辣粉", "shop": "重庆小面馆", "category": "面食", "price": 14.0, "rating": 4.3,
         "sales": 222, "image": "🍜", "desc": "酸辣开胃，粉条Q弹，配花生"},

        # 饮品
        {"id": 19, "name": "珍珠奶茶", "shop": "喜茶", "category": "饮品", "price": 22.0, "rating": 4.8, "sales": 444,
         "image": "🧋", "desc": "Q弹珍珠+香浓奶茶，大杯"},
        {"id": 20, "name": "芝士茶", "shop": "喜茶", "category": "饮品", "price": 28.0, "rating": 4.7, "sales": 333,
         "image": "🧋", "desc": "咸香芝士奶盖+清茶，大杯"},
        {"id": 21, "name": "鲜榨果汁", "shop": "鲜果时光", "category": "饮品", "price": 18.0, "rating": 4.6,
         "sales": 222, "image": "🧃", "desc": "新鲜水果现榨，可选混合"},

        # 甜品
        {"id": 22, "name": "草莓蛋糕", "shop": "好利来", "category": "甜品", "price": 32.0, "rating": 4.7, "sales": 199,
         "image": "🍰", "desc": "新鲜草莓+奶油蛋糕，切块"},
        {"id": 23, "name": "提拉米苏", "shop": "好利来", "category": "甜品", "price": 38.0, "rating": 4.8, "sales": 188,
         "image": "🍰", "desc": "咖啡+马斯卡彭+可可粉，切块"},
        {"id": 24, "name": "芒果千层", "shop": "好利来", "category": "甜品", "price": 35.0, "rating": 4.6, "sales": 166,
         "image": "🎂", "desc": "芒果+奶油+千层皮"},

        # 烧烤
        {"id": 25, "name": "烤串套餐", "shop": "烧烤大师", "category": "烧烤", "price": 48.0, "rating": 4.6,
         "sales": 188, "image": "🍢", "desc": "羊肉串5串+鸡翅2个+烤蔬菜"},
        {"id": 26, "name": "烤鱼", "shop": "烤鱼王", "category": "烧烤", "price": 68.0, "rating": 4.7, "sales": 166,
         "image": "🐟", "desc": "外焦里嫩，麻辣鲜香，配菜"},

        # 粥
        {"id": 27, "name": "皮蛋瘦肉粥", "shop": "粥员外", "category": "粥", "price": 15.0, "rating": 4.4, "sales": 177,
         "image": "🥣", "desc": "皮蛋+瘦肉+葱花，大碗"},
        {"id": 28, "name": "海鲜粥", "shop": "粥员外", "category": "粥", "price": 25.0, "rating": 4.5, "sales": 155,
         "image": "🥣", "desc": "虾+蟹+干贝，大碗"},
        {"id": 29, "name": "香菇鸡丝粥", "shop": "粥员外", "category": "粥", "price": 18.0, "rating": 4.3, "sales": 133,
         "image": "🥣", "desc": "香菇+鸡丝+葱花，大碗"},

        # 快餐
        {"id": 30, "name": "照烧鸡腿饭", "shop": "吉野家", "category": "快餐", "price": 30.0, "rating": 4.5,
         "sales": 299, "image": "🍱", "desc": "照烧鸡腿+米饭+蔬菜"},
        {"id": 31, "name": "牛肉饭", "shop": "吉野家", "category": "快餐", "price": 28.0, "rating": 4.4, "sales": 266,
         "image": "🍱", "desc": "肥牛+洋葱+米饭+蔬菜"},
    ]
    save_data(db)


init_foods()


# ============ 工具函数 ============

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token():
    return str(uuid.uuid4())


def find_user_by_token(token):
    for username, user in db['users'].items():
        if user.get('token') == token:
            return username, user
    return None, None


def save_and_return(data):
    save_data(db)
    return jsonify(data), 200


def get_user_coupons(username):
    return db['coupons'].get(username, [])


# ============ 用户接口 ============

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()

    if not username or not password:
        return save_and_return({'code': 1001, 'msg': '用户名和密码不能为空'})
    if len(username) < 3:
        return save_and_return({'code': 1001, 'msg': '用户名至少3个字符'})
    if len(password) < 6:
        return save_and_return({'code': 1001, 'msg': '密码至少6个字符'})
    if username in db['users']:
        return save_and_return({'code': 1001, 'msg': '用户名已存在'})

    db['users'][username] = {
        'password': hash_password(password),
        'username': username,
        'phone': phone,
        'balance': 0,
        'created_at': datetime.now().isoformat()
    }

    # 新用户赠送优惠券
    db['coupons'][username] = [
        {'id': 1, 'code': 'NEWUSER', 'discount': 10, 'min_amount': 30, 'desc': '新用户立减10元', 'used': False,
         'expire': (datetime.now() + timedelta(days=30)).isoformat()}
    ]

    return save_and_return({'code': 0, 'msg': '注册成功', 'data': {'username': username}})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # === 在这里插入下面两行 ===
    print("=" * 50)
    print(f"后端收到登录请求: username={username}, password={password}")

    if not username or not password:
        return save_and_return({'code': 1001, 'msg': '用户名和密码不能为空'})
    if username not in db['users']:
        return save_and_return({'code': 2001, 'msg': '用户名或密码错误'})
    if db['users'][username]['password'] != hash_password(password):
        return save_and_return({'code': 2001, 'msg': '用户名或密码错误'})

    token = generate_token()
    db['users'][username]['token'] = token
    db['users'][username]['last_login'] = datetime.now().isoformat()

    return save_and_return({
        'code': 0,
        'msg': '登录成功',
        'data': {
            'username': username,
            'token': token,
            'coupons': get_user_coupons(username)
        }
    })


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    return save_and_return({
        'code': 0,
        'data': {
            'username': username,
            'phone': user.get('phone', ''),
            'balance': user.get('balance', 0),
            'created_at': user.get('created_at'),
            'coupons': get_user_coupons(username)
        }
    })


@app.route('/api/user/address', methods=['POST'])
def add_address():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    data = request.json
    address = data.get('address', '').strip()

    if not address:
        return save_and_return({'code': 1001, 'msg': '地址不能为空'})

    if username not in db['addresses']:
        db['addresses'][username] = []

    db['addresses'][username].append({
        'id': len(db['addresses'][username]) + 1,
        'address': address,
        'is_default': len(db['addresses'][username]) == 0
    })

    return save_and_return({'code': 0, 'msg': '地址添加成功', 'data': db['addresses'][username]})


@app.route('/api/user/addresses', methods=['GET'])
def get_addresses():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    return save_and_return({'code': 0, 'data': db['addresses'].get(username, [])})


# ============ 外卖接口 ============

@app.route('/api/foods', methods=['GET'])
def get_foods():
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    shop = request.args.get('shop', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    sort_by = request.args.get('sort_by', '')

    result = db['foods'].copy()

    if keyword:
        result = [f for f in result if keyword.lower() in f['name'].lower()
                  or keyword.lower() in f['shop'].lower()
                  or keyword.lower() in f['desc'].lower()]
    if category:
        result = [f for f in result if f['category'] == category]
    if shop:
        result = [f for f in result if shop.lower() in f['shop'].lower()]
    if min_price:
        result = [f for f in result if f['price'] >= min_price]
    if max_price:
        result = [f for f in result if f['price'] <= max_price]
    if min_rating:
        result = [f for f in result if f['rating'] >= min_rating]

    if sort_by == 'price':
        result.sort(key=lambda x: x['price'])
    elif sort_by == 'price_desc':
        result.sort(key=lambda x: x['price'], reverse=True)
    elif sort_by == 'rating':
        result.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'sales':
        result.sort(key=lambda x: x['sales'], reverse=True)

    return save_and_return({'code': 0, 'data': result, 'total': len(result)})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = sorted(list(set([f['category'] for f in db['foods']])))
    return save_and_return({'code': 0, 'data': categories})


@app.route('/api/shops', methods=['GET'])
def get_shops():
    shops = sorted(list(set([f['shop'] for f in db['foods']])))
    return save_and_return({'code': 0, 'data': shops})


@app.route('/api/foods/<int:food_id>', methods=['GET'])
def get_food_detail(food_id):
    for food in db['foods']:
        if food['id'] == food_id:
            # 获取该外卖的评价
            reviews = [r for r in db['reviews'] if r.get('food_id') == food_id]
            return save_and_return({'code': 0, 'data': {**food, 'reviews': reviews[:10]}})
    return save_and_return({'code': 4001, 'msg': '外卖不存在'})


# ============ 收藏接口 ============

@app.route('/api/favorites', methods=['POST'])
def toggle_favorite():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    data = request.json
    food_id = data.get('food_id')

    if username not in db['favorites']:
        db['favorites'][username] = []

    if food_id in db['favorites'][username]:
        db['favorites'][username].remove(food_id)
        return save_and_return({'code': 0, 'msg': '已取消收藏'})
    else:
        db['favorites'][username].append(food_id)
        return save_and_return({'code': 0, 'msg': '收藏成功'})


@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    favorites = db['favorites'].get(username, [])
    result = [f for f in db['foods'] if f['id'] in favorites]
    return save_and_return({'code': 0, 'data': result})


# ============ 购物车接口 ============

@app.route('/api/cart', methods=['POST'])
def update_cart():

    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    data = request.json
    # 1. 关键校验：必须存在 food_id，且不能为 None
    food_id = data.get('food_id')
    if food_id is None:
        return save_and_return({'code': 400, 'msg': '缺少参数 food_id'})
    # 转字符串前先判断是否合法数字
    food_id_str = str(food_id)
    if not food_id_str.isdigit():
        return save_and_return({'code': 400, 'msg': '商品ID必须是数字'})

    quantity = data.get('quantity', 1)

    if username not in db['cart']:
        db['cart'][username] = {}

    if quantity <= 0:
        db['cart'][username].pop(food_id_str, None)
    else:
        db['cart'][username][food_id_str] = quantity

    return save_and_return({'code': 0, 'data': db['cart'][username]})


@app.route('/api/cart', methods=['GET'])
def get_cart():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    cart = db['cart'].get(username, {})
    result = []
    total = 0
    for food_id, quantity in cart.items():
        for food in db['foods']:
            if food['id'] == int(food_id):
                item = food.copy()
                item['quantity'] = quantity
                item['subtotal'] = food['price'] * quantity
                total += item['subtotal']
                result.append(item)
                break

    return save_and_return({'code': 0, 'data': {'items': result, 'total': total, 'count': len(result)}})


# ============ 订单接口 ============

@app.route('/api/orders', methods=['POST'])
def create_order():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    data = request.json
    items = data.get('items', [])
    address = data.get('address', '').strip()
    coupon_code = data.get('coupon_code', '').strip()
    remark = data.get('remark', '').strip()

    if not items:
        return save_and_return({'code': 1001, 'msg': '购物车为空'})
    if not address:
        return save_and_return({'code': 1001, 'msg': '请填写收货地址'})

    # 防重复下单检查
    pending_orders = [o for o in db['orders'].values()
                      if o['username'] == username and o['status'] in ['待接单', '配送中']]
    current_food_ids = set([item.get('food_id') for item in items])
    for order in pending_orders:
        for order_item in order['items']:
            if order_item['food']['id'] in current_food_ids:
                return save_and_return({
                    'code': 4002,
                    'msg': f'您已下单"{order_item["food"]["name"]}"，状态"{order["status"]}"，请等待完成后再次下单'
                })

    # 计算价格
    total_price = 0
    order_items = []
    for item in items:
        food_id = item.get('food_id')
        quantity = item.get('quantity', 1)
        for food in db['foods']:
            if food['id'] == food_id:
                subtotal = food['price'] * quantity
                total_price += subtotal
                order_items.append({'food': food, 'quantity': quantity, 'subtotal': subtotal})
                break

    discount = 0
    if coupon_code:
        user_coupons = get_user_coupons(username)
        for coupon in user_coupons:
            if coupon['code'] == coupon_code and not coupon.get('used', False):
                if total_price >= coupon.get('min_amount', 0):
                    discount = coupon['discount']
                    coupon['used'] = True
                    break

    final_price = max(0, total_price - discount)

    order_id = db['current_order_id'] + 1
    db['current_order_id'] = order_id

    order = {
        'id': order_id,
        'username': username,
        'items': order_items,
        'total_price': total_price,
        'discount': discount,
        'final_price': final_price,
        'address': address,
        'remark': remark,
        'status': '待接单',
        'paid': False,
        'created_at': datetime.now().isoformat()
    }
    db['orders'][order_id] = order
    db['cart'][username] = {}

    return save_and_return({'code': 0, 'msg': '下单成功', 'data': order})


@app.route('/api/orders', methods=['GET'])
def get_my_orders():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    status = request.args.get('status', '')
    user_orders = [o for o in db['orders'].values() if o['username'] == username]
    if status:
        user_orders = [o for o in user_orders if o['status'] == status]
    user_orders.sort(key=lambda x: x['created_at'], reverse=True)
    return save_and_return({'code': 0, 'data': user_orders})


@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})
    if order_id not in db['orders']:
        return save_and_return({'code': 4001, 'msg': '订单不存在'})

    order = db['orders'][order_id]
    if order['username'] != username:
        return save_and_return({'code': 1003, 'msg': '无权操作'})
    if order['status'] != '待接单':
        return save_and_return({'code': 1001, 'msg': '订单已接单或已完成，无法取消'})

    order['status'] = '已取消'
    return save_and_return({'code': 0, 'msg': '订单已取消', 'data': order})


# ============ 支付接口 ============

payment_locks = {}


@app.route('/api/orders/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})
    if order_id not in db['orders']:
        return save_and_return({'code': 4001, 'msg': '订单不存在'})

    order = db['orders'][order_id]
    if order['username'] != username:
        return save_and_return({'code': 1003, 'msg': '无权操作'})
    if order['status'] == '已取消':
        return save_and_return({'code': 1001, 'msg': '订单已取消'})
    if order.get('paid', False):
        return save_and_return({'code': 4003, 'msg': '订单已支付，请勿重复支付'})

    # 防并发支付锁
    if order_id in payment_locks and time.time() - payment_locks[order_id] < 30:
        return save_and_return({'code': 4004, 'msg': '订单正在支付中...'})
    payment_locks[order_id] = time.time()

    try:
        order['paid'] = True
        order['paid_at'] = datetime.now().isoformat()
        order['status'] = '支付成功'
        return save_and_return({'code': 0, 'msg': '支付成功', 'data': order})
    finally:
        if order_id in payment_locks:
            del payment_locks[order_id]


# ============ 评价接口 ============

@app.route('/api/reviews', methods=['POST'])
def add_review():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username:
        return save_and_return({'code': 1002, 'msg': '请先登录'})

    data = request.json
    order_id = data.get('order_id')
    food_id = data.get('food_id')
    rating = data.get('rating', 5)
    content = data.get('content', '').strip()

    if order_id not in db['orders']:
        return save_and_return({'code': 4001, 'msg': '订单不存在'})
    order = db['orders'][order_id]
    if order['username'] != username:
        return save_and_return({'code': 1003, 'msg': '无权操作'})
    if order['status'] != '支付成功' and order['status'] != '已完成':
        return save_and_return({'code': 1001, 'msg': '订单未完成，无法评价'})

    review = {
        'id': len(db['reviews']) + 1,
        'username': username,
        'order_id': order_id,
        'food_id': food_id,
        'rating': rating,
        'content': content,
        'created_at': datetime.now().isoformat()
    }
    db['reviews'].append(review)
    return save_and_return({'code': 0, 'msg': '评价成功', 'data': review})


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    food_id = request.args.get('food_id', type=int)
    if food_id:
        result = [r for r in db['reviews'] if r.get('food_id') == food_id]
        return save_and_return({'code': 0, 'data': result[-20:]})
    return save_and_return({'code': 0, 'data': db['reviews'][-20:]})


# ============ 商家后台 ============

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')


@app.route('/api/admin/orders', methods=['GET'])
def admin_get_orders():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username or username != 'admin':
        return save_and_return({'code': 1002, 'msg': '需要管理员权限'})

    all_orders = list(db['orders'].values())
    all_orders.sort(key=lambda x: x['created_at'], reverse=True)
    return save_and_return({'code': 0, 'data': all_orders})


@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def admin_update_status(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username, user = find_user_by_token(token)
    if not username or username != 'admin':
        return save_and_return({'code': 1002, 'msg': '需要管理员权限'})
    if order_id not in db['orders']:
        return save_and_return({'code': 4001, 'msg': '订单不存在'})

    data = request.json
    new_status = data.get('status', '')
    if new_status not in ['待接单', '配送中', '已完成', '已取消']:
        return save_and_return({'code': 1001, 'msg': '无效状态'})

    db['orders'][order_id]['status'] = new_status
    return save_and_return({'code': 0, 'msg': '状态更新成功'})


# ============ 首页 ============

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    print("🍔 饿了么 - 外卖平台启动中...")
    print("📱 用户端: http://127.0.0.1:8080")
    print("🏪 商家端: http://127.0.0.1:8080/admin")
    app.run(debug=True, host='0.0.0.0', port=8080)