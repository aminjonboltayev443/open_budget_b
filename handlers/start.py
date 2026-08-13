from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.baza import Baza

router = Router()
db = Baza()

# Holatlar (FSM)
class Royxat(StatesGroup):
    ism = State()

class OvozKiritish(StatesGroup):
    raqam = State()

# Asosiy menyu tugmalari
def asosiy_menyu():
    kb = [
        [KeyboardButton(text="➕ Yangi ovoz kiritish")],
        [KeyboardButton(text="📊 Mening statistikalarim")],
        [KeyboardButton(text="ℹ️ Qoidalar va Ogohlantirish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# /start buyrug'i
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Bazada bormi-yo'qligini tekshirish kodi
    await message.answer(
        "Assalomu alaykum! Open Budget botiga xush kelibsiz.\n\n"
        "Iltimos, ism va familiyangizni kiriting:"
    )
    await state.set_state(Royxat.ism)

# Ismni qabul qilish
@router.message(Royxat.ism)
async def ism_qabul(message: Message, state: FSMContext):
    ism = message.text
    db.foydalanuvchi_qoshish(
        telegram_id=message.from_user.id,
        ism_familiya=ism,
        telefon="",
        tur="ovoz_yiguvchi"
    )
    await state.clear()
    await message.answer(
        f"Rahmat, {ism}! Muvaffaqiyatli ro'yxatdan o'tdingiz.",
        reply_markup=asosiy_menyu()
    )

# Yangi ovoz kiritish tugmasi
@router.message(F.text == "➕ Yangi ovoz kiritish")
async def ovoz_boshlash(message: Message, state: FSMContext):
    await message.answer(
        "📱 Ovoz beriladigan telefon raqamini kiriting:\n"
        "Masalan: 998901234567"
    )
    await state.set_state(OvozKiritish.raqam)

# Raqam qabul qilinganda chiqadigan Ogohlantirish xabari
@router.message(OvozKiritish.raqam)
async def raqam_qabul(message: Message, state: FSMContext):
    raqam = message.text
    ovoz_id = db.ovoz_qoshish(yiguvchi_id=message.from_user.id, telefon_raqam=raqam)
    await state.clear()
    
    await message.answer(
        f"⏳ **Ovoz tekshiruvga yuborildi!** (Raqam: {raqam})\n\n"
        "🚨 **OGOHLANTIRISH:**\n"
        "Ushbu raqam egasiga **HOZIRCHA PUL BERMANG!**\n"
        "Sababi: Uning nomida boshqa telefon raqamlar bo'lishi va u avval ovoz bergan bo'lishi mumkin.\n\n"
        "Ovoz **'🟢 Qabul qilindi'** holatiga o'tmaguncha pul bermasdan, biroz kutishni ayting.\n\n"
        "Siz bemalol navbatdagi odam bilan ishlashingiz mumkin!",
        reply_markup=asosiy_menyu()
    )