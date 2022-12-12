from pyrogram import Client, filters
import logging


from configs import Config as C


# LMAO, isso está registrando
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Importar do Framework
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from pyrogram.types import *

from database.broadcast import broadcast
from database.verifier import handle_user_status
from database.database import Database

LOG_CHANNEL = C.LOG_CHANNEL
AUTH_USERS = C.AUTH_USERS
DB_URL = C.DB_URL
DB_NAME = C.DB_NAME

db = Database(DB_URL, DB_NAME)

# Não mude nada, exceto se quiser agregar valor
bot = Client('Feedback bot',
             api_id=C.API_ID,
             api_hash=C.API_HASH,
             bot_token=C.BOT_TOKEN)

donate_link=C.DONATE_LINK

owner_id=C.OWNER_ID

LOG_TEXT = "🆔: <code>{}</code>\n👤: <a href='tg://user?id={}'>{} \n🤔: {}</a>\n🖥 DC ID: <code>{}</code> \n\n<b>Acabou de da</b> /start <b>no Bot</b>"

IF_TEXT = "<b>🆔:</b> <code>{}</code>\n<b>👤:</b> {}\n\n💬️= {}"

IF_CONTENT = "<b>🆔:</b> <code>{}</code> \n<b>👤:</b> {}"

# Ligue de volta
@bot.on_callback_query()
async def callback_handlers(bot: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    if "closeMeh" in cb.data:
        await cb.message.delete(True)
    elif "notifon" in cb.data:
        notif = await db.get_notif(cb.from_user.id)
        if notif is True:
            # 
            await db.set_notif(user_id, notif=False)
        else:
            # 
            await db.set_notif(user_id, notif=True)
        await cb.message.edit(
            f"`Aqui você pode definir suas configurações:`\n\nNotificações definidas com sucesso para **{await db.get_notif(user_id)}**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                            callback_data="notifon",
                        )
                    ],
                    [InlineKeyboardButton("Close", callback_data="closeMeh")],
                ]
            ),
        )
        await cb.answer(
            f"Notificações Definidas Com Sucesso Para{await db.get_notif(user_id)}"
        )
        
        
@bot.on_message((filters.private | filters.group))
async def _(bot, cmd):
    await handle_user_status(bot, cmd)

@bot.on_message(filters.command('start') & (filters.private | filters.group))
async def start(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
        return
      
    # 
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
      
    await bot.send_message(
        chat_id=owner_id,
        text=LOG_TEXT.format(message.chat.id,message.chat.id,message.chat.first_name,message.chat.last_name,message.chat.dc_id),
        parse_mode="html"
    )
    await message.reply_text(
        text="**OLÁ {} !**\n\n<b>SEJA BEM VINDO</b>\n\n<b>Se você precisar de alguma ajuda mande</b>/help".format(message.chat.first_name)
    )

@bot.on_message(filters.command('help') & (filters.group | filters.private))
async def help(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
        
    await message.reply_text(
    "<b>RSS para Telegram Bot, um robot de telegrama que se preocupa com a sua experiência de leitura.</b> \n\n<b>GitHub:</b> https://github.com \n\n<b>Comandos:</b> \n/list: Confira a lista de assinaturas \n/set: Personalizar assinaturas \n/set_default: Personalizar as configurações padrão \n/import: Importar assinaturas de um arquivo OPML \n/export: Exportar assinaturas para um arquivo OPML \n/activate_subs: Ativar assinaturas \n/deactivate_subs: Desativar assinaturas \n/help: Ver ajuda"
    )


@bot.on_message(filters.command('donate') & (filters.group | filters.private))
async def donate(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
        
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
        
    await message.reply_text(
        text=C.DONATE + "Se Você Gostou Deste Bot, Acesse O Link E O Apoie Com Algo",
        reply_markup=InlineKeyboardMarkup([
            [ InlineKeyboardButton(text="DOAR", url=f"{donate_link}")]
        ])
    )


@bot.on_message(filters.command('helpis') & (filters.group | filters.private))
async def donate(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
        
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
        
    await message.reply_text(
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
    )



#@bot.on_message(filters.command("settings") & filters.private)
#async def opensettings(bot, cmd):
    #user_id = cmd.from_user.id
    # Adding to DB
    #if not await db.is_user_exist(user_id):
        #data = await bot.get_me()
        #BOT_USERNAME = data.username
        #await db.add_user(user_id)
        #await bot.send_message(
            #LOG_CHANNEL,
            #f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        #)#
    #try:
        #await cmd.reply_text(
            #text=f"⚙ `Aqui você pode definir suas configurações:` ⚙\n\nNotificações definidas com sucesso para **{await db.get_notif(user_id)}**",
            #reply_markup=InlineKeyboardMarkup(
                #[#
                    #[InlineKeyboardButton(text=f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",callback_data="notifon")],
                    #[InlineKeyboardButton(text="CLOSE", callback_data="closeMeh")],
                #]#
            #)#
        #)#
    #except Exception as e:
        #await cmd.reply_text(e)#


@bot.on_message(filters.private & filters.command(["broadcast", "bc", "tm", "transmitir"]))
async def broadcast_handler_open(_, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if m.reply_to_message is None:
        await m.delete()
        return
    await broadcast(m, db)


@bot.on_message((filters.group | filters.private) & filters.command(["stats", "status"]))
async def sts(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**Total de Usuários no Banco de Dados 📂:** `{await db.total_users_count()}`\n\n**Total de Usuários com Notificação Habilitada 🔔 :** `{await db.total_notif_users_count()}`",
        parse_mode="Markdown",
        quote=True,
    )


@bot.on_message(filters.private & filters.command("ban_user"))
async def ban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use este comando para Banir 🛑 \nqualquer usuário do bot 🤖.\n\nUse:\n\n`/ban_user user_id ban_duration ban_reason`\n\nPor exemplo: \n`/ban_user 1234567 28 Você fez mal uso do BOT.`\n\n Isso banirá o usuário com id <b>1234567</b> por <b>28</b> dias pelo motivo <b>Você fez mal uso do BOT</b>.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banindo usuário {user_id} for {ban_duration} dias pelo motivo {ban_reason}."
        
        if user_id == owner_id:
            await message.reply_text("**Você Não Pode Banir O Proprietário Bro")
            return
        try:
            await c.send_message(
                user_id,
                f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**",
            )
            ban_log_text += "\n\nUsuário Notificado Com Sucesso!"
        except BaseException:
            traceback.print_exc()
            ban_log_text += (
                f"\n\n ⚠️ A Notificação Do Usuário Falhou! ⚠️ \n\n`{traceback.format_exc()}`"
            )
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"Ocorreu Um Erro ⚠️! Rastreamento Dado Abaixo\n\n`{traceback.format_exc()}`",
            quote=True,
        )


@bot.on_message((filters.group | filters.private) & filters.command("unban_user"))
async def unban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use Este Comando Para Desbanir 😃 Qualquer Usuário.\n\nUse:\n\n`/unban_user user_id` \n\nPor Exemplo: `/unban_user 1234567` \n\nIsso Irá Desbanir O Usuário Com ID `1234567`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Usuário Desbanido 🤪 \n\n{user_id}"

        try:
            await c.send_message(user_id, f"Você Foi Desbanido Por Um Adm! 🤪")
            unban_log_text += "\n\n✅ Usuário Notificado Com Sucesso! ✅"
        except BaseException:
            traceback.print_exc()
            unban_log_text += (
                f"\n\n⚠️ A Notificação Do Usuário Falhou! ⚠️\n\n`{traceback.format_exc()}`"
            )
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"⚠️ Ocorreu Um Erro ⚠️! Rastreamento Dado Abaixo\n\n`{traceback.format_exc()}`",
            quote=True,
        )


@bot.on_message((filters.group | filters.private) & filters.command("banned_users"))
async def _banned_usrs(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ""
    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"> **ID do usuário**: `{user_id}`, **Duração do banimento**: `{ban_duration}`, **Banido em**: `{banned_on}`, **Motivo**: `{ban_reason}`\n\n"
    reply_text = f"Total de Usuário(s) banido(s) 🤭: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-users.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-users.txt", True)
        os.remove("banned-users.txt")
        return
    await m.reply_text(reply_text, True)

    return


@bot.on_message((filters.group | filters.private) & filters.text)
async def pm_text(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
      
    if message.from_user.id == owner_id:
        await reply_text(bot, message)
        return
    info = await bot.get_users(user_ids=message.from_user.id)
    reference_id = int(message.chat.id)
    await bot.send_message(
        chat_id=owner_id,
        text=IF_TEXT.format(reference_id, info.first_name, message.text),
        parse_mode="html"
    )


@bot.on_message((filters.group | filters.private) & filters.media)
async def pm_media(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
    ban_status = await db.get_ban_status(chat_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"🚫 Você foi BANIDO e não pode usar este BOT \n\nPor: **{ban_duration}** dia(s) \n\Motivo: __{ban_reason}__ \n\n**Mensagem do Administrador 🤠**")
        return
      
    if message.from_user.id == owner_id:
        await replay_media(bot, message)
        return
    info = await bot.get_users(user_ids=message.from_user.id)
    reference_id = int(message.chat.id)
    await bot.copy_message(
        chat_id=owner_id,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
        caption=IF_CONTENT.format(reference_id, info.first_name),
        parse_mode="html"
    )


@bot.on_message(filters.user(owner_id) & filters.text)
async def reply_text(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
    
    reference_id = True
    if message.reply_to_message is not None:
        file = message.reply_to_message
        try:
            reference_id = file.text.split()[2]
        except Exception:
            pass
        try:
            reference_id = file.caption.split()[2]
        except Exception:
            pass
        await bot.send_message(
            chat_id=int(reference_id),
            #from_chat_id=message.chat.id,
            #message_id=message.message_id,
            text=message.text
        )


@bot.on_message(filters.user(owner_id) & filters.media)
async def replay_media(bot, message):
    chat_id = message.from_user.id
    # Adding to DB
    if not await db.is_user_exist(chat_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        await bot.send_message(
            LOG_CHANNEL,
            f"#NOVOUSUARIO: \n\nNOVO USUÁRIO: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) \nComeçou A utilizar o Bot @{BOT_USERNAME}.",
        )
    reference_id = True
    if message.reply_to_message is not None:
        file = message.reply_to_message
        try:
            reference_id = file.text.split()[2]
        except Exception:
            pass
        try:
            reference_id = file.caption.split()[2]
        except Exception:
            pass
        await bot.copy_message(
            chat_id=int(reference_id),
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            parse_mode="html"
        )

bot.run()
