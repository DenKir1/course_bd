class HeadHunterAPI():
    def __init__(self):
        self.params = {
            'per_page': 100,
            'page': 1
        }
        self.url = 'https://api.hh.ru/vacancies/'
        self.vacancies = []

    def get_vacancies(self, words):
        """Запрос по API """
        self.params['text'] = words
        req = requests.get(self.url, params=self.params)
        vacancies = json.loads(req.text)['items']
        self.vacancies = vacancies
        return vacancies