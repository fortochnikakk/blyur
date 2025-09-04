import asyncio
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
import logging

logging.basicConfig(level=logging.INFO)

# ==================== Env ====================
load_dotenv()
API_TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") and os.getenv("ADMIN_ID").isdigit() else None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

# ==================== Catalog ====================
Product = Dict[str, str]
Catalog = Dict[str, List[Product]]

def parse_price_to_int(price: str) -> int:
    s = price.replace("₽", "").replace("р.", "").replace("руб.", "").replace(" ", "").replace("\u00A0", "").strip()
    return int(s) if s else 0

def find_product_by_id(cat: Catalog, pid: str) -> Optional[Product]:
    for items in cat.values():
        for it in items:
            if it["id"] == pid:
                return it
    return None

catalog: Catalog = {
 "Очищение": [
        {
            "id": "enzyme_powder",
            "name": "Энзимная пудра с бромелайном",
            "price": "1 550 ₽",
            "desc": "мягко очищает кожу, удаляет ороговевшие клетки и излишки себума...",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1KgJ1Qez9E16OaDa2B5JCiuxXf-jRQRHD",
        },
        {
            "id": "foam_collagen_mint",
            "name": "Мусс для умывания с коллагеном \"Мята\"",
            "price": "1 680 ₽",
            "desc": "бережное очищение, коллаген поддерживает упругость, аллантоин успокаивает...",
            "volume": "150 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1tqhmIQgN3kIWHxOS-G-APytpIKtVDkI9",
        },
    ],
    "Тоники": [
        {
            "id": "tonic_hyaluron_aloe",
            "name": "Тоник для лица с гиалуроновой кислотой (зел. алоэ)",
            "price": "1 790 ₽",
            "desc": "увлажнение, тонизирование, г.к., аминокислоты, ниацинамид, вит.E, экстракты ромашки/ламинарии/алоэ.",
            "volume": "200 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1WS1LmgBkmaP9fseQ6MAMIi3jZYjYLp14",
        },
        {
            "id": "tonic_salic_ylang",
            "name": "Тоник-лосьон с салициловой кислотой \"Иланг-Иланг\"",
            "price": "1 440 ₽",
            "desc": "для проблемной кожи: BHA-отшелушивание, успокаивающие экстракты, увлажнение.",
            "volume": "200 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1bzVFjI2Bi795-2Tb3zHG-FBD2JePY2Yg",
        },
    ],
    "Сыворотки": [
        {
            "id": "serum_eyes_patches",
            "name": "Сыворотка тонизирующая для кожи вокруг глаз",
            "price": "1 750 ₽",
            "desc": "против отёков и тёмных кругов; ниацинамид, вит.E, коллаген, ГК, кофеин, каштан, зелёный чай, REBITIDE.",
            "volume": "30 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1ci2FXRz4P1v8MH3XWai769UUffwUjSfo",
        },
        {
            "id": "gel_serum_hyaluron",
            "name": "Гель‑сыворотка с гиалуроновой кислотой \"Зелёное Алоэ\"",
            "price": "2 130 ₽",
            "desc": "интенсивное увлажнение: низко- и высокомолекулярная ГК, коллаген, алоэ, ламинария, ромашка.",
            "volume": "30 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1-dB-a4wc2vgBy0ni4z6_zDSqLFhRBojJ",
        },
        {
            "id": "serum_antiage_blanche",
            "name": "Сыворотка для лица anti-age (BLANCHE)",
            "price": "2 520 ₽",
            "desc": "омоложение: REBITIDE AO8, коллаген, ГК, вит.E, экстракты зелёного чая и центеллы.",
            "volume": "30 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1hXR3rWg4SsSdC-5RKeDwqdll_NBCu3Vv",
        },
        {
            "id": "serum_niacin_zinc",
            "name": "Сыворотка с ниацинамидом и цинком",
            "price": "2 250 ₽",
            "desc": "для проблемной кожи: снижение воспалений, выравнивание тона, цинк, ромашка, ламинария, алоэ.",
            "volume": "30 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1JNJXjTyw_2oG9sit1u2NSq9TaRPznp8c",
        },
        {
            "id": "serum_emulsion_ceramides",
            "name": "Сыворотка‑эмульсия с церамидами, ниацинамидом и ГК (холодный шёлк)",
            "price": "3 280 ₽",
            "desc": "восстановление барьера: церамиды, сквалан, масла, ниацинамид, ГК, коллаген, пантенол, центелла, ромашка.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1-EUdrDfosEEpkYTKySWXBOaOChKeJ3k_",
        },
    ],
    "Крема": [
        {
            "id": "eye_cream_peptides_blanche",
            "name": "Крем для век anti‑age с пептидами (Blanche)",
            "price": "1 960 ₽",
            "desc": "пептиды REBITIDE AO8, коллаген, ГК, масла; уменьшение морщин и отёков.",
            "volume": "30 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1BX8FbMdNFJXj2_4kTVyJdljV9KRX-Td7",
        },
        {
            "id": "face_cream_peptides_blanche",
            "name": "Крем для лица с пептидами (Blanche)",
            "price": "2 380 ₽",
            "desc": "anti‑age: REBITIDE AO8, ниацинамид, масла ши/миндаль, сквалан, экстракты ламинарии/центеллы/каштан.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1SexUsuHVvKpsRjOb7UJ7L8FXqrBZKuaS",
        },
        {
            "id": "face_cream_hyaluron_aloe",
            "name": "Крем для лица с гиалуроновой кислотой \"Зелёное алоэ\"",
            "price": "2 350 ₽",
            "desc": "интенсивное увлажнение: ГК 2 форм, масла, сквалан/ланолин, экстракты алоэ/ромашки/ламинарии.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1x-j02RJE9HOJGg2--PuH6WwaNSY0ipt2",
        },
        {
            "id": "face_cream_tea_tree",
            "name": "Крем восстанавливающий для комб./жирной кожи \"Чайное дерево\"",
            "price": "1 540 ₽",
            "desc": "лёгкое питание без перегруза: масла, коллаген, алоэ; антисептическое действие чайного дерева.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1d-rvkwwKZ_ttEjwyD5SRBH_h_-Plf3JU",
        },
    ],
    "Маски": [
        {
            "id": "sheet_mask_peptides_silk",
            "name": "Маска тканевая омолаживающая с пептидами (хол. шёлк)",
            "price": "1 500 ₽",
            "desc": "пептиды, коллаген, алоэ; увлажнение, упругость, сияние.",
            "volume": "3 шт",
            "photo": "https://drive.google.com/uc?export=download&id=1ceMiGXz-DYxQxZZ3JSmd3UKJU0C5EeMG",
        },
        {
            "id": "sheet_mask_ceramides_centella",
            "name": "Маска тканевая с церамидами и центеллой (арбуз)",
            "price": "1 610 ₽",
            "desc": "укрепление барьера: церамиды, центелла, пантенол; увлажнение и мягкость.",
            "volume": "3 шт",
            "photo": "https://drive.google.com/uc?export=download&id=1yHjJEJacXHBuC3uPyvSGNVgx3ASQNSSD",
        },
        {
            "id": "mask_chocolate",
            "name": "Маска для лица шоколадная",
            "price": "1 470 ₽",
            "desc": "питание и восстановление: масла, какао, вит.E; мягкость и сияние.",
            "volume": "100 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1dwUrLmtdQfVC0IuvSGsIPE39XT1eN-yn",
        },
        {
            "id": "mask_sea_minerals",
            "name": "Оживляющая маска с морскими минералами",
            "price": "1 470 ₽",
            "desc": "очищение и тонизирование: зелёная глина, ламинария, спирулина, кислоты, витамин E, ментол.",
            "volume": "100 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1DGKed1npbNJyVg7sChcei_GUVE38gODH",
        },
        {
            "id": "mask_stop_acne_feet",
            "name": "Маска противовоспалительная стоп‑акне",
            "price": "1 470 ₽",
            "desc": "для кожи стоп: чёрная глина, уголь, чистотел, эвкалипт; очищение и уход.",
            "volume": "100 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1lJ5GfvgmJmkkt9p3Z2BzAM_1FDNbcQ3O",
        },
    ],
    "Руки и ноги": [
        {
            "id": "hand_cream_urea10",
            "name": "Крем для рук с мочевиной 10%",
            "price": "800 ₽",
            "desc": "интенсивное увлажнение и восстановление: мочевина, молочная кислота, масла, вит.E, ниацинамид.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1CAJMCASrcxkzrk6pMQS1QTR2eoLgOulH",
        },
        {
            "id": "foot_cream_urea12",
            "name": "Крем для ног с мочевиной 12%",
            "price": "1 300 ₽",
            "desc": "для сухой/огрубевшей кожи: мочевина+молочная к-та, масла, глицерин; мягкость и защита.",
            "volume": "200 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1CIAxcuL5_mklOzSGxlBJ5q_Zo5bbXtvX",
        },
    ],
    "Тело": [
        {
            "id": "deodorant_citrus",
            "name": "Дезодорант шариковый \"Взрывной цитрус\"",
            "price": "850 ₽",
            "desc": "защита от запаха, квасцы, увлажняющие компоненты, успокаивающие экстракты, лёгкий аромат.",
            "volume": "50 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1Wp2h1x2x0gDEpokgIpFfbQ7zqER71K",
        },
        {
            "id": "dry_oil_shimmer",
            "name": "Масло сухое для тела с шиммером (ваниль‑бергамот)",
            "price": "1 600 ₽",
            "desc": "питание и сияние: масла виноград.косточки/миндаль/аргана/жожоба, экстракт ромашки, вит.E.",
            "volume": "100 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1HXaAR0IIsKGbfq3KmocNJ8qrg5zQI93X",
        },
        {
            "id": "body_gel_silhouette",
            "name": "Гель для тела \"корректор силуэта\" (грейпфрут)",
            "price": "1 600 ₽",
            "desc": "тонус и упругость: кофеин, каштан, зелёный чай, ламинария, розмарин, кетон малины, ниацинамид.",
            "volume": "150 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1J6Rn51cYywjaKcbGoWlaLJnJE0Gppwzo",
        },
    ],
    "Губы и универсальное": [
        {
            "id": "lip_balm_coconut",
            "name": "Бальзам для губ \"Кокос\"",
            "price": "550 ₽",
            "desc": "питание, увлажнение и защита: пчелиный воск, масла кокоса/ши/миндаль/жожоба/зародыши пшеницы.",
            "volume": "5 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1p18yPdTSHyz4tDuIRAn-kfzWd3durAjm",
        },
        {
            "id": "gel_aloe_vera",
            "name": "Гель Алоэ Вера",
            "price": "1 650 ₽",
            "desc": "увлажнение и успокоение: алоэ-вера, лактат натрия, аллантоин; универсальный уход.",
            "volume": "250 мл",
            "photo": "https://drive.google.com/uc?export=download&id=1v0RFUGxJch4hnWN8RH79Yi-Y8GVafcDe",
        },
    ],
}

# ==================== Keyboards ====================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="🛒 Корзина")],
        [KeyboardButton(text="💼 Партнёрство"), KeyboardButton(text="ℹ️ О бренде")]
    ],
    resize_keyboard=True
)

def build_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"category:{cat}")] for cat in catalog.keys()
        ]
    )

def build_products_keyboard(cat_name: str) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=item["name"], callback_data=f"product:{item['id']}")] for item in catalog[cat_name]]
    kb.append([InlineKeyboardButton(text="⬅️ К категориям", callback_data="back:categories")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_product_keyboard(pid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ В корзину", callback_data=f"add:{pid}")],
        [InlineKeyboardButton(text="⬅️ К товарам", callback_data=f"back:products:{pid}")]
    ])

def build_cart_keyboard(uid: int) -> InlineKeyboardMarkup:
    items = carts.get(uid, [])
    kb = []
    for it in items:
        name = find_product_by_id(catalog, it["id"])["name"][:18]
        kb.append([
            InlineKeyboardButton(text=f"➖ {name}", callback_data=f"cart:dec:{it['id']}"),
            InlineKeyboardButton(text=f"{it['qty']} шт.", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cart:inc:{it['id']}"),
            InlineKeyboardButton(text="❌", callback_data=f"cart:del:{it['id']}")
        ])
    if items:
        kb.append([
            InlineKeyboardButton(text="🧹 Очистить", callback_data="cart:clear"),
            InlineKeyboardButton(text="✅ Оформить", callback_data="cart:checkout")
        ])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==================== Cart ====================
carts: Dict[int, List[Dict[str, int]]] = {}
waiting_for_phone: Dict[int, bool] = {}

def add_to_cart(user_id: int, product_id: str, qty: int = 1):
    if qty < 1: return
    carts.setdefault(user_id, [])
    for it in carts[user_id]:
        if it["id"] == product_id:
            it["qty"] += qty
            return
    carts[user_id].append({"id": product_id, "qty": qty})

def remove_from_cart(user_id: int, product_id: str):
    if user_id not in carts: return
    carts[user_id] = [it for it in carts[user_id] if it["id"] != product_id]

def set_qty(user_id: int, product_id: str, qty: int):
    if qty < 1:
        remove_from_cart(user_id, product_id)
        return
    carts.setdefault(user_id, [])
    for it in carts[user_id]:
        if it["id"] == product_id:
            it["qty"] = qty
            return
    carts[user_id].append({"id": product_id, "qty": qty})

def cart_total(user_id: int) -> Tuple[str, int]:
    lines, total = [], 0
    for it in carts.get(user_id, []):
        p = find_product_by_id(catalog, it["id"])
        if not p: continue
        price = parse_price_to_int(p["price"])
        subtotal = price * it["qty"]
        total += subtotal
        lines.append(f"{p['name']} — {it['qty']} шт. = {subtotal} ₽")
    return ("\n".join(lines), total)

# ==================== Handlers ====================
@router.message(lambda m: m.text and m.text.lower() in ["/start", "start"])
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в BLYUR Cosmetics 💖\nВыберите раздел:", reply_markup=main_kb)

@router.message(lambda m: m.text and "каталог" in m.text.lower())
async def show_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=build_categories_keyboard())

@router.callback_query(lambda c: c.data.startswith("category:"))
async def cb_show_products(callback: CallbackQuery):
    cat_name = callback.data.split(":", 1)[1]
    if cat_name not in catalog:
        await callback.answer("Категория не найдена", show_alert=True)
        return
    await callback.message.answer(f"Категория: {cat_name}\nВыберите товар:", reply_markup=build_products_keyboard(cat_name))
    await callback.answer()

@router.callback_query(lambda c: c.data == "back:categories")
async def cb_back_categories(callback: CallbackQuery):
    await callback.message.answer("Выберите категорию:", reply_markup=build_categories_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("back:products:"))
async def cb_back_products(callback: CallbackQuery):
    pid = callback.data.split(":", 2)[2]
    prod = find_product_by_id(catalog, pid)
    if not prod:
        await callback.answer("Товар не найден", show_alert=True)
        return
    cat_name = next((name for name, items in catalog.items() if any(i["id"] == pid for i in items)), None)
    await callback.message.answer(f"Категория: {cat_name}\nВыберите товар:", reply_markup=build_products_keyboard(cat_name))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("product:"))
async def cb_show_product(callback: CallbackQuery):
    pid = callback.data.split(":", 1)[1]
    product = find_product_by_id(catalog, pid)
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    kb = build_product_keyboard(pid)
    caption = f"📦 {product['name']}\n💰 {product['price']} ({product['volume']})\n\n{product['desc']}"
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=product['photo'],  # Используем прямую ссылку
        caption=caption,
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("add:"))
async def cb_add_to_cart(callback: CallbackQuery):
    pid = callback.data.split(":", 1)[1]
    add_to_cart(callback.from_user.id, pid)
    await callback.answer("Добавлено в корзину ✅")
    await callback.message.answer("Товар добавлен в корзину ✅\nОткройте \"🛒 Корзина\" для оформления заказа.")

@router.message(lambda m: m.text and "корзина" in m.text.lower())
async def show_cart(message: Message):
    uid = message.from_user.id
    lines, total = cart_total(uid)
    if not lines:
        await message.answer("Ваша корзина пуста 🛒")
        return
    await message.answer(f"🛍 Ваша корзина:\n\n{lines}\n\nИтого: {total} ₽", reply_markup=build_cart_keyboard(uid))

# Cart callbacks
@router.callback_query(lambda c: c.data.startswith("cart:inc:"))
async def cb_cart_inc(callback: CallbackQuery):
    pid = callback.data.split(":", 2)[2]
    add_to_cart(callback.from_user.id, pid)
    await callback.answer("Количество увеличено")
    lines, total = cart_total(callback.from_user.id)
    await callback.message.edit_text(f"🛍 Ваша корзина:\n\n{lines}\n\nИтого: {total} ₽", reply_markup=build_cart_keyboard(callback.from_user.id))

@router.callback_query(lambda c: c.data.startswith("cart:dec:"))
async def cb_cart_dec(callback: CallbackQuery):
    pid = callback.data.split(":", 2)[2]
    uid = callback.from_user.id
    for it in carts.get(uid, []):
        if it["id"] == pid:
            set_qty(uid, pid, it["qty"] - 1)
            break
    await callback.answer("Количество уменьшено")
    lines, total = cart_total(callback.from_user.id)
    await callback.message.edit_text(f"🛍 Ваша корзина:\n\n{lines}\n\nИтого: {total} ₽", reply_markup=build_cart_keyboard(callback.from_user.id))

@router.callback_query(lambda c: c.data.startswith("cart:del:"))
async def cb_cart_del(callback: CallbackQuery):
    pid = callback.data.split(":", 2)[2]
    remove_from_cart(callback.from_user.id, pid)
    await callback.answer("Удалено из корзины")
    lines, total = cart_total(callback.from_user.id)
    await callback.message.edit_text(f"🛍 Ваша корзина:\n\n{lines}\n\nИтого: {total} ₽", reply_markup=build_cart_keyboard(callback.from_user.id))

@router.callback_query(lambda c: c.data == "cart:clear")
async def cb_cart_clear(callback: CallbackQuery):
    carts[callback.from_user.id] = []
    await callback.answer("Корзина очищена")
    await callback.message.edit_text("Ваша корзина пуста 🛒")

@router.callback_query(lambda c: c.data == "cart:checkout")
async def cb_checkout(callback: CallbackQuery):
    uid = callback.from_user.id
    if not carts.get(uid):
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await callback.message.answer("Поделитесь вашим контактом для оформления заказа:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
    await callback.answer()

@router.message(F.contact)
async def receive_contact(message: Message):
    uid = message.from_user.id
    phone = message.contact.phone_number
    lines, total = cart_total(uid)
    await message.answer(f"Спасибо! Ваш заказ принят:\n\n{lines}\n\nИтого: {total} ₽\nТелефон: {phone}")
    carts[uid] = []

    # Отправка заказа администратору
    await bot.send_message(ADMIN_ID, f"Новый заказ:\n\n{lines}\n\nИтого: {total} ₽\nТелефон: {phone}")

    # Сохранение заказа в файл
    with open("orders.txt", "a", encoding="utf-8") as f:
        f.write(f"Новый заказ:\n\n{lines}\n\nИтого: {total} ₽\nТелефон: {phone}\n\n")

@router.message(F.text == "💼 Партнёрство")
async def partnership(message: Message):
    text = (
        "🤝 Условия сотрудничества:\n\n"
        "🔹 Опт — скидка 30% (от 100000 ₽).\n"
        "🔹 Опт — скидка 20% (от 60000 ₽).\n"
        "🔹 Опт — скидка 10% (от 30000 ₽).\n"
        "🔹 Первые 2 закупки для новых партнёров — по оптовым ценам.\n"
        "🔹 Реализация — срок 2 месяца, вознаграждение 10%-20%.\n\n"
        "Хотите оставить заявку? Напишите ваш телефон."
    )
    await message.answer(text)

@router.message(F.text == "ℹ️ О бренде")
async def about(message: Message):
    await message.answer("🌿 BLYUR Cosmetics — российский бренд профессиональной косметики для мастеров и салонов красоты.\n\n"
        "Мы делаем продукты высокого качества для маникюра, педикюра и косметологии.")

# Debug all callbacks
@router.callback_query()
async def debug_callback(callback: CallbackQuery):
    logging.info(f"Callback received: {callback.data}")
    await callback.answer()

# ==================== Bootstrap ====================
async def main():
    dp.include_router(router)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    asyncio.run(main())