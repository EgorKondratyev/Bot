from databases.client_side import TopDB, StatisticDB, ScoresDB


async def update_top():
    """Обновление топа и вычисление всех значений к нему"""
    top_db = TopDB()
    statistic_db = StatisticDB()
    scores_db = ScoresDB()
    info = statistic_db.get_all_user_id_and_their_scores()
    scores = []
    if info:
        # Сортируем всех пользователей по возрастанию
        for attribute in info:
            user_id = attribute[0]
            their_score = attribute[1]
            scores.append(their_score)
        scores_sorted = sorted(scores)
        scores = []
        # Нахождение топ 5 пользователей
        for attribute in info:
            user_id = attribute[0]
            their_score = attribute[1]
            if their_score == scores_sorted[-1]:
                new_info = (1, user_id, their_score)
                scores.append(new_info)

            elif their_score == scores_sorted[-2]:
                new_info = (2, user_id, their_score)
                scores.append(new_info)

            elif their_score == scores_sorted[-3]:
                new_info = (3, user_id, their_score)
                scores.append(new_info)

            elif their_score == scores_sorted[-4]:
                new_info = (4, user_id, their_score)
                scores.append(new_info)

            elif their_score == scores_sorted[-5]:
                new_info = (5, user_id, their_score)
                scores.append(new_info)
        top_db.delete_all()
        for score in reversed(scores):
            # Нахождение средней отметки среди 20 последних
            smiles = scores_db.get_all_their_smile(user_id=score[1])
            summa = 0
            for smile in smiles:
                smile = int(smile[0][:1])
                summa += smile
            try:
                average = summa / len(smiles)
            except ZeroDivisionError:
                continue
            average_their_scores = float("{:.2f}".format(average))
            top_db.add_user(place=score[0], user_id=score[1], amount_their_scores=score[2],
                            average_their_scores=average_their_scores)



