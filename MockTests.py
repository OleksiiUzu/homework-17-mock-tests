import unittest
from unittest.mock import Mock, patch, ANY
import pokemon_name_translator
from pokemon_report import PokemonReport
from pokemon_service import PokemonService
from main import main


class TestMock(unittest.TestCase):
    @patch('pokemon_name_translator.translate.TranslationServiceClient')
    def test_translate_method(self, mock_client):

        mock_translate_client = mock_client.return_value

        mock_translate_client.translate_text.return_value.translations = [
            Mock(translated_text='Some_text')
        ]

        some_obj = pokemon_name_translator.PokemonNameTranslator()

        translation = some_obj.translate('Input_text', target_language='fr')

        self.assertEqual(translation, 'Some_text')

    @patch('pdfkit.from_file')
    def test_generate_report(self, mock_pdfkit):
        pokemon_info = {
            'name': 'Pikachu',
            'height': 40,
            'weight': 60,
            'abilities': [{'ability': {'name': 'Static'}}, {'ability': {'name': 'Lightning Rod'}}]
        }
        translated_name = 'Пікачу'
        output_pdf = 'test_report.pdf'

        report = PokemonReport()
        report.generate_report(pokemon_info, translated_name, output_pdf)

        mock_pdfkit.assert_called_once_with('report_template.html', output_pdf, configuration=ANY)

    @patch('pokemon_service.requests.get')
    def test_get_pokemon_info(self, mock_get):
        pokemon_name = 'pikachu'
        response_json = {'name': 'Pikachu', 'height': 40, 'weight': 60}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_json
        mock_get.return_value = mock_response

        service = PokemonService()
        result = service.get_pokemon_info(pokemon_name)

        mock_get.assert_called_once_with(f"{service.BASE_URL}/{pokemon_name}")

        self.assertEqual(result, response_json)

    @patch('main.PokemonService')
    @patch('main.PokemonNameTranslator')
    @patch('main.PokemonReport')
    def test_main(self, mock_report, mock_translator, mock_service):
        mock_service_instance = mock_service.return_value
        mock_translator_instance = mock_translator.return_value
        mock_report_instance = mock_report.return_value

        pokemon_info = {'name': 'Pikachu', 'height': 40, 'weight': 60}
        mock_service_instance.get_pokemon_info.return_value = pokemon_info

        mock_translator_instance.translate.return_value = "Pikachu (French)"

        main()

        mock_service_instance.get_pokemon_info.assert_called_once_with("pikachu")
        mock_translator_instance.translate.assert_called_once_with("pikachu", target_language="fr")
        mock_report_instance.generate_report.assert_called_once_with(pokemon_info, "Pikachu (French)",
                                                                     "pokemon_report.pdf")
