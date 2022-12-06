import asyncio
from cgitb import html
from email.mime import application
from re import L
from weakref import proxy
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import os
from dotenv import load_dotenv
import postgre
import datetime

load_dotenv(".env")
bot = Bot(os.environ.get("token"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

applications = ['Анализ информации', 'Планирование', 'Стрессоустойчивость', 'Ориентация на результат',
 'Партнерство/сотрудничество', 'Рынок НТИ: Homenet', 'Рынок НТИ: Healthnet', 'Рынок НТИ: NeuroNet', 
 'Рынок НТИ: EduNet и сквозные технологии', 'Онлайн 5','Технологии в здравоохранении', 'Рынок НТИ: Homenet',
 'Рынок НТИ: TechNet', 'Рынок НТИ: EnergyNet','Рынок НТИ: FoodNet', 'Рынок НТИ: Wearnet' ,'Веревочный парк', 
 'Тур в пещеры "Царская тропа"', 'Рафтинг', 'Wearnet и передовые технические средства реабилитации для людей с ограниченными возможностями' ]

count_sprav = {

    'day_1':
{
    'Веревочный парк': 33,
    'Тур в пещеры "Царская тропа"': 18,
    'Рафтинг': 45
},
    'day_2':
{
    'Веревочный парк': 33,
    'Тур в пещеры "Царская тропа"': 45,
    'Рафтинг': 18

}
}
# создаём форму и указываем поля
class Form(StatesGroup):
    typeStart = State()
    typeDate = State()
    timeDate = State()
    typeApplication = State()
    formApplication = State()
    lastname = State() 
    name = State() 
    quastion = State()
    


# Старт
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.typeStart.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    now = datetime.date.today()
    markup.add("28.09.2022")
    markup.add("29.09.2022")
    await Form.next()
    await message.reply("Здравствуйте! Выберите желаемую дату посещения мероприяти", reply_markup=markup)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("/start")

    await state.finish()
    await message.reply('Действие отменено', reply_markup=markup)


@dp.message_handler(state=Form.typeDate)
async def process_name(message: types.Message, state: FSMContext):

    if message.text in ('28.09.2022', '29.09.2022','Вернуться к выбору времени'):
        async with state.proxy() as data:
            data['date'] = message.text
            if message.text == '28.09.2022':
                data['typeDate'] = 'day_1'
            elif message.text == '29.09.2022':
                 data['typeDate'] = 'day_2'
                 
            data['shag'] = 1    

        await Form.next()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Дневное")
        markup.add("Вечернее")
        markup.add("Назад")
        await message.reply("Выберите время мероприятия", reply_markup=markup)

@dp.message_handler(state=Form.timeDate)
async def process_name(message: types.Message, state: FSMContext):

    if message.text in ('Дневное', 'Вечернее', 'Назад'):

        async with state.proxy() as data:
        
            data['timeDate'] = message.text
            data['shag'] = 2
        
        
            if data['timeDate'] == 'Дневное':
                
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                data['form'] = ''
                markup.add("Веревочный парк")
                markup.add('Тур в пещеры "Царская тропа"')
                markup.add("Рафтинг")
                markup.add("Вернуться к выбору времени")
                await Form.typeApplication.set()
                await message.reply("Выберите мероприятие", reply_markup=markup)
            elif data['timeDate'] == 'Вечернее':
                data['fact'] = 12
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add("Оффлайн")
                markup.add("Онлайн")
                markup.add("Вернуться к выбору времени")
                await Form.formApplication.set()
                await message.reply("Выберите формат участия", reply_markup=markup)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add("28.09.2022")
                markup.add("29.09.2022")
                await Form.previous()
                await message.reply("Здравствуйте! Выберите желаемую дату посещения мероприятия", reply_markup=markup)


        


@dp.message_handler(state=Form.typeApplication)
async def process_name(message: types.Message, state: FSMContext):


    if message.text in applications:

        async with state.proxy() as data:
        
            data['typeApplication'] = message.text
            data['shag'] = 2

            for dateTime in count_sprav:
                if dateTime == data['typeDate']:
                    for k, v in count_sprav[dateTime].items():
                        if k == data['typeApplication']:
                            itog = v
            if data['timeDate'] == 'Дневное':

                data['fact'] = itog

            

        markup = types.ReplyKeyboardRemove()    
        await Form.lastname.set()
        await message.reply("Введите Вашу фамилию\nДля отмены напишите /cancel", reply_markup=markup)

    elif message.text == "Вернуться к выбору времени":

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Дневное")
        markup.add("Вечернее")
        markup.add("Назад")
        await Form.timeDate.set()
        await message.reply("Выберите время мероприятия", reply_markup=markup)


@dp.message_handler(state=Form.formApplication)
async def process_middlename(message: types.Message, state: FSMContext):

    if message.text in ('Онлайн', 'Оффлайн', 'Вернуться к выбору времени'):

        async with state.proxy() as data:
            data['shag'] = 4
            data['form'] = message.text

        if data['form'] == 'Оффлайн':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Анализ информации")
            markup.add("Планирование")
            markup.add("Стрессоустойчивость")
            markup.add("Ориентация на результат")
            markup.add("Партнерство/сотрудничество")
            markup.add("Вернуться к выбору времени")
            await Form.typeApplication.set()
            await message.reply("Выбирите мероприятие", reply_markup=markup)
        elif data['form'] == 'Онлайн' and  data['typeDate'] == 'day_1':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Технологии в здравоохранении")
            markup.add("Рынок НТИ: Homenet")
            markup.add("Рынок НТИ: TechNet")
            markup.add("Рынок НТИ: EnergyNet")
            markup.add("Рынок НТИ: FoodNet")
            markup.add("Вернуться к выбору времени")
            await Form.typeApplication.set()
            await message.reply("Выбирите мероприятие", reply_markup=markup)
        elif data['form'] == 'Онлайн' and  data['typeDate'] == 'day_2':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Рынок НТИ: Healthnet")
            markup.add("Wearnet и передовые технические средства реабилитации для людей с ограниченными возможностями")
            markup.add("Рынок НТИ: NeuroNet")
            markup.add("Рынок НТИ: EduNet и сквозные технологии")
            markup.add("Рынок НТИ: Wearnet")
            markup.add("Вернуться к выбору времени")
            await Form.typeApplication.set()
            await message.reply("Выбeрите мероприятие", reply_markup=markup)
        else:

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Дневное")
            markup.add("Вечернее")
            markup.add("Назад")
            await message.reply("Выберите время мероприятия", reply_markup=markup)
            await Form.timeDate.set()

            
 




@dp.message_handler(state=Form.lastname)
async def process_middlename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        
        data['lastname'] = message.text
        data['shag'] = 3
  
        data['id'] = message.from_user.id

    await Form.next()
    await message.reply("Введите Ваше имя")

@dp.message_handler(state=Form.name)
async def process_middlename(message: types.Message, state: FSMContext):
    async with state.proxy() as data:

        
        data['name'] = message.text
        #data['now'] = datetime.date.today()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("/start")

        if data['form'] != 'Онлайн':

            records = postgre.checkID(data)
            if len(records) != 0:
                await bot.send_message(
                    message.chat.id,
                    
                    md.text(f"Добрый день, <b>{records[0][0]}</b>!\nВы уже зарегистрированы на мероприятие <b>{records[0][1]}</b>\nДата проведения: <b>{data['date']}</b>")
                    ,parse_mode=ParseMode.HTML, reply_markup=markup)
            else:

                data['text_1'], data['text_2'] = postgre.count(data)
            
                if data['text_1'] == '' and data['text_2'] == '':


                    postgre.day_write_offline(data)
                

                    await bot.send_message(
                            message.chat.id,
                            
                            md.text(f"Добрый день, <b>{data['lastname']} {data['name']}</b>!\nВы успешно зарегистрированы на мероприятие <b>{data['typeApplication']}</b>\nДата проведения: <b>{data['date']}</b>")
                            ,parse_mode=ParseMode.HTML, reply_markup=markup)
                        
                else:
                    if data['timeDate'] == 'Дневное':
                        typeText = 'дневные'
                    else:
                        typeText = 'вечерние'

                    await bot.send_message(
                            message.chat.id,
                            
                                md.text(f'''К сожалению, все места заняты. Можете ознакомиться со списком свободных мест на {typeText} мероприятия\n\n28.09.2022\n{data['text_1']}\n29.09.2022\n{data['text_2']}\nЕсли вы не видите мероприятие в списке, значит на него еще никто не зарегистрировался, Вы можете стать первыми!'''),
                            parse_mode=ParseMode.HTML, reply_markup=markup
                            )
                
            await state.finish()

        else:
                await Form.next()
                await message.reply("Для регистрации на данное мероприятие, задайте вопрос спикеру")

        
     
@dp.message_handler(state=Form.quastion)
async def process_middlename(message: types.Message, state: FSMContext):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("/start")
    
    async with state.proxy() as data:

        data['question'] = message.text
        #asyncio.sleep (1)
        records = postgre.checkID(data)
        if len(records) != 0:

            await bot.send_message(
                message.chat.id,
                md.text(f"Добрый день, <b>{records[0][0]}</b>!\nВы уже зарегистрированы на мероприятие <b>{records[0][1]}</b>\nДата проведения: <b>{data['date']}</b>")
                ,parse_mode=ParseMode.HTML, reply_markup=markup)
        else:

            data['text_1'], data['text_2'] = postgre.count(data)

            if data['text_1'] == '' and data['text_2'] == '':

                postgre.day_write_online(data)
                

                await bot.send_message(
                message.chat.id,
                
                    md.text(f"Добрый день, <b>{data['lastname']} {data['name']}</b>!\nВы успешно зарегистрированы на мероприятие <b>{data['typeApplication']}</b>\nДата проведения: <b>{data['date']}</b>")
                ,parse_mode=ParseMode.HTML, reply_markup=markup)
                
            else:

                if data['timeDate'] == 'Дневное':
                    typeText = 'дневные'
                else:
                    typeText = 'вечерние'


                await bot.send_message(
                message.chat.id,
                
                    md.text(f"К сожалению, все места заняты. Можете ознакомиться со списком свободных мест на {typeText} мероприятия\n\n28.09.2022\n{data['text_1']}\n29.09.2022\n{data['text_2']}"),
                parse_mode=ParseMode.HTML, reply_markup=markup
                )

        await state.finish()


  



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)