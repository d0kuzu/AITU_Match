from datetime import datetime, time, timedelta, date
from io import BytesIO

from aiogram.types import BufferedInputFile
from sqlalchemy.dialects.postgresql import insert as pginsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert, func, exists, text, cast, Integer, delete, literal
import json
import logging
from typing import Any, Dict, List

from sqlalchemy.orm import selectinload

from config import env
from database.models.daily_question_answer import DailyQuestionResponse
from database.models.held_out_answers import HeldOutAnswer
from database.repo.repo import Repo
from database.models import *
import pandas as pd


class UserRepo(Repo):
    def __init__(self, session):
        super().__init__(session)


    async def get_user(self, user_id: int) -> User|None:
        try:
            async with self.session.begin():
                stmt = (
                    select(User)
                    .where(User.user_id == user_id)
                )
                result = await self.session.execute(stmt)
                user = result.scalar()
            return user
        except Exception as e:
            logging.error(f"get user error: {e}")
            return None


    async def get_user_with_goals(self, user_id: int) -> User|None:
        try:
            async with self.session.begin():
                stmt = (
                    select(User)
                    .where(User.user_id == user_id)
                    .options(selectinload(User.goals))
                )
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logging.error(f"Ошибка при получении пользователя: {e}")
            return None


    async def add_message(self, user_id: int, message_id: int) -> bool:
        try:
            async with self.session.begin():
                stmt = pginsert(Chat).values(
                    user_id=user_id,
                    history=[str(message_id)]
                    # или используйте пустой список, если не хотите вставлять начальную историю
                )

                # Если запись с таким user_id уже существует, обновляем поле history, добавляя новый message_id
                stmt = stmt.on_conflict_do_update(
                    index_elements=[Chat.user_id],  # Индекс или уникальный ключ, по которому проверяется наличие записи
                    set_={
                        "history": Chat.history.concat([str(message_id)])  # Добавляем новый message_id в history
                    }
                )
                await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
            return False


    async def check_user(self, user_id: int) -> tuple[bool, bool]:
        try:
            async with self.session.begin():
                stmt = (
                    select(User)
                    .where(User.user_id == user_id)
                    .options(selectinload(User.goals))
                )
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()

            if user:
                return user.name, len(user.goals) > 0
            else:
                return False, False
        except Exception as e:
            logging.error(f"Ошибка при проверке пользователя: {e}")
            return False, False


    async def save_user_data(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        try:
            async with self.session.begin():
                user = User(
                    user_id=user_id,
                    name=user_data.get("name", ""),
                    age=user_data.get("age", 0),
                    addiction=user_data.get("addiction", ""),
                    motivation=user_data.get("motivation", ""),
                    progress=1
                )

                await self.session.merge(user)
            logging.info(f"Данные пользователя сохранены: {user_data}, user_id: {user_id}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении данных пользователя: {e}")
            return False


    async def save_user_goal(self, user_id: int, goal_data: Dict[str, Any]) -> bool:
        try:
            goal_plan: list = goal_data.get("goal_plan").get("days")
            for day in goal_plan:
                for day_field in list(day.keys()):
                    if day_field not in ["day", "task"]:
                        day.pop(day_field)
            print(goal_plan)

            async with self.session.begin():
                user_goal = UserGoal(
                    user_id=user_id,
                    goal=goal_data.get("goal"),
                    goal_area=goal_data.get("goal_area"),
                    goal_plan={"plan": goal_plan}
                )
                await self.session.merge(user_goal)
            logging.info(f"Цель пользователя {user_id} сохранена: {goal_data}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении цели пользователя {user_id}: {e}")
            return False


    async def subscribe_user_notifications(self, user_id: int) -> bool:
        try:
            now = datetime.now()
            # start_time = time(**env.morning_notification)
            # 
            # if now.time() > start_time:
            #     notification_time = datetime.combine(now.date() + timedelta(days=1), time(0, 0))
            # else:
            #     notification_time = now
            notification_time = now
            async with self.session.begin():
                stmt = update(User).where(User.user_id == user_id).values(should_notify=True, notification_enabled=notification_time)
                await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении уведомлений пользователя {user_id}: {e}")
            return False


    async def describe_user_notifications(self, user_id: int) -> bool:
        try:
            async with self.session.begin():
                stmt = update(User).where(User.user_id == user_id).values(should_notify=False)
                await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении уведомлений пользователя {user_id}: {e}")
            return False


    async def get_notify_users(self) -> list[User]:
        try:
            async with self.session.begin():
                stmt = select(User).where(
                    User.should_notify == True,
                    User.notification_enabled <= func.now()
                ).options(selectinload(User.goals))

                result = await self.session.execute(stmt)
                users = result.scalars().all()
            return users
        except Exception as e:
            logging.error(f"Ошибка при получаения времени среди всех пользователей: {e}")
            return []


    async def promote_progress(self, user_id):
        try:
            async with self.session.begin():
                smt = (
                    update(User)
                       .where(User.user_id == user_id)
                       .values(progress=User.progress + 1, overdue_task=None)
                )
                await self.session.execute(smt)
        except Exception as e:
            logging.error(f"Произвошла ошибка при продвижении цели пользователя {user_id}: {e}")


    async def get_progress(self, user_id: int) -> int|bool:
        try:
            async with self.session.begin():
                smt = (
                    select(User.progress)
                       .where(User.user_id == user_id)
                )
                answer = await self.session.execute(smt)
                result = answer.scalar_one_or_none()
            return result
        except Exception as e:
            logging.error(f"Произвошла ошибка при получения програсса пользователя {user_id}: {e}")
            return False


    async def save_overdue_task(self, user_id, text):
        try:
            async with self.session.begin():
                smt = (
                    update(User)
                    .where(User.user_id == user_id)
                    .values(overdue_task=text)
                )
                await self.session.execute(smt)
        except Exception as e:
            logging.error(f"Произошла ошибка при сохранении задания пользователя {user_id} ({text}): {e}")


    async def save_user_affirmation(self, user_id: int, feedback: str, affirmation_text: str) -> bool:
        try:
            async with self.session.begin():
                result = await self.session.execute(select(exists().where(User.user_id == user_id)))
                if not result.scalar():
                    logging.error(f"Пользователь с ID {user_id} не найден")
                    return False
                is_useful = True if feedback == "affirmation_useful" else False
                await self.session.execute(insert(AffirmationFeedback).values(
                    user_id=user_id,
                    text=affirmation_text,
                    is_useful=is_useful,
                    created_at=func.now()
                ))
            logging.info(f"Отзыв пользователя {user_id} об аффирмации сохранен: {feedback}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении отзыва пользователя {user_id}: {e}")
            return False


    async def save_survey_response(self, survey_data: Dict[str, Any], user_id: int) -> bool:
        try:
            async with self.session.begin():
                await self.session.execute(insert(SurveyResponse).values(
                    user_id=user_id,
                    satisfaction=survey_data.get("satisfaction"),
                    improvements=survey_data.get("improvements"),
                    features=survey_data.get("features"),
                    overall_score=survey_data.get("overall_score"),
                    created_at=func.now()
                ))
            logging.info(f"Ответы на опрос сохранены: {survey_data}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении ответов на опрос: {e}")
            return False


    async def select_all_users_full(self) -> list[User]:
        try:
            async with self.session.begin():
                stmt = select(User).options(
                    selectinload(User.goals),
                    selectinload(User.affirmations),
                    selectinload(User.surveys),
                    selectinload(User.daily_questions),
                    selectinload(User.held_out_answers),
                )
                result = await self.session.execute(stmt)
                all_records = result.scalars().all()
            return all_records
        except Exception as e:
            logging.error(f"Ошибка при сохранении ответов на опрос: {e}")
            return []


    async def export_users_to_excel(self, today=False) -> BufferedInputFile|None:
        try:
            users: list[User] = await self.select_all_users_full()

            data = {"Пользователи": [], "Аффирмации": [], "Опросы": [], "Вопросы дня": [], "Вечерний опросник": []}
            for user in users:
                user_data = {
                    "Имя пользователя": user.name,
                    "Возраст": user.age,
                    "UTM-метка": user.utm,
                    "Тип зависимости": user.addiction,
                    "Мотивация": user.motivation,
                    "Дата регистрации": user.notification_enabled.strftime('%Y-%m-%d %H:%M:%S') if user.notification_enabled else None,
                    "Доп опрос": user.extra_survey_answer if user.extra_survey_answer else "Нет ответа",
                }
                if user.goals:
                    goal: UserGoal = user.goals[0]
                    user_data["Цель"] = goal.goal
                    user_data["Область цели"] = goal.goal_area
                data["Пользователи"].append(user_data)


                for affirmation in user.affirmations:
                    if not today or (affirmation.created_at.date() == date.today()):
                        user_data = {"Имя пользователя": user.name,
                                     "Текст": affirmation.text,
                                     "Был ли полезен": affirmation.is_useful,
                                     "Время": affirmation.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                        data["Аффирмации"].append(user_data)


                for survey in user.surveys:
                    if not today or (survey.created_at.date() == date.today()):
                        user_data = {"Имя пользователя": user.name,
                                     "Удовлетворенность": survey.satisfaction,
                                     "Улучшения": survey.improvements,
                                     "Функции в будущем": survey.features,
                                     "Оценка": survey.overall_score,
                                     "Время ответа": survey.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                        data["Опросы"].append(user_data)


                for question in user.daily_questions:
                    if not today or (question.answered_at.date() == date.today()):
                        user_data = {"Имя пользователя": user.name,
                                     "Вопрос": question.question,
                                     "Овет": question.answer,
                                     "Время ответа": question.answered_at.strftime('%Y-%m-%d %H:%M:%S')}
                        data["Вопросы дня"].append(user_data)


                for answer in user.held_out_answers:
                    print(answer.start_date.date())
                    print(date.today())
                    if not today or (answer.start_date.date() == date.today()):
                        user_data = {"Имя пользователя": user.name,
                                     "День/прогресс": answer.day,
                                     "Как прошел твой день?": answer.how_is_day_question,
                                     "Какие чувства ты сегодня испытывал?": answer.emotions_question,
                                     "Коментарий по дню": answer.comment_question,
                                     "Удалось ли тебе выполнить задачу на сегодня?": answer.task_question,
                                     "Время начала опросника": answer.start_date.strftime('%Y-%m-%d %H:%M:%S')}
                        data["Вечерний опросник"].append(user_data)

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                for (table_name, frame) in data.items():
                    pd.DataFrame(frame).to_excel(writer, index=False, sheet_name=table_name)

                for sheetname in writer.sheets:
                    worksheet = writer.sheets[sheetname]
                    for column_cells in worksheet.columns:
                        column_letter = column_cells[0].column_letter
                        worksheet.column_dimensions[column_letter].width = 20

            buffer.seek(0)
            return BufferedInputFile(buffer.read(), filename="users_export.xlsx")
        except Exception as e:
            logging.error(f"Ошибка при создании таблицы: {e}")
            return None


    async def load_user_daily_answer(self, question, answer, user_id):
        try:
            async with self.session.begin():
                await self.session.execute(insert(DailyQuestionResponse).values(
                    user_id=user_id,
                    question=question,
                    answer=answer,
                ))
            return True
        except Exception as e:
            logging.error(f"Ошибка при записи ответа пользователя: {e}")
            return False


    async def load_user_extra_survey_answer(self, answer, user_id):
        try:
            async with self.session.begin():
                await self.session.execute(update(User).where(User.user_id == user_id).values(
                    extra_survey_answer=answer,
                ))
            return True
        except Exception as e:
            logging.error(f"Ошибка при записи ответа пользователя (extra survey): {e}")
            return False


    async def reset_counters(self, user_id: int) -> bool:
        try:
            async with self.session.begin():
                stmt = update(User).where(User.user_id == user_id).values(last_use=func.now(), notification_enabled=func.now())
                await self.session.execute(stmt)
            return True
        except Exception as e:
            logging.error(f"Ошибка при сбросе счетчиков пользователя {user_id}: {e}")
            return False


    async def set_user_utm(self, user_id, came_from) -> bool:
        try:
            async with self.session.begin():
                user = User(
                    user_id=user_id,
                    utm=came_from.get("utm_source", "")
                )
                await self.session.merge(user)
            return True
        except Exception as e:
            logging.error(f"Не удалось задать utm пользователя {user_id}: {e}")
            return False


    async def save_held_out_how_is_day_answer(self, user_id: int, answer: str, progress: int) -> bool:
        try:
            async with self.session.begin():
                smtm = insert(HeldOutAnswer).values(
                    user_id=user_id,
                    day=progress,
                    how_is_day_question=answer
                )
                await self.session.execute(smtm)
            return True
        except Exception as e:
            logging.error(f"Не записать вечерний ответ пользователя {user_id}: {e}")
            return False


    async def save_held_out_emotions_answer(self, user_id: int, answer: list[str]) -> bool:
        try:
            emotions_question = ', '.join(answer)
            async with self.session.begin():
                smtm = (
                    update(HeldOutAnswer)
                    .where(HeldOutAnswer.user_id==user_id)
                    .values(emotions_question=emotions_question)
                )
                await self.session.execute(smtm)
            return True
        except Exception as e:
            logging.error(f"Не записать вечерний ответ пользователя {user_id}: {e}")
            return False


    async def save_held_out_comment_answer(self, user_id: int, answer: str) -> bool:
        try:
            async with self.session.begin():
                smtm = (
                    update(HeldOutAnswer)
                    .where(HeldOutAnswer.user_id==user_id)
                    .values(comment_question=answer)
                )
                await self.session.execute(smtm)
            return True
        except Exception as e:
            logging.error(f"Не записать вечерний ответ пользователя {user_id}: {e}")
            return False


    async def save_held_out_task_answer(self, user_id: int, answer: str) -> bool:
        try:
            async with self.session.begin():
                smtm = (
                    update(HeldOutAnswer)
                    .where(HeldOutAnswer.user_id==user_id)
                    .values(task_question=answer)
                )
                await self.session.execute(smtm)
            return True
        except Exception as e:
            logging.error(f"Не записать вечерний ответ пользователя {user_id}: {e}")
            return False

