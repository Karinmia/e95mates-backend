from google.cloud import speech
# import io
import logging
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from accounts.serializers import SavedLocationSerializer
from accounts.models import SavedLocation

logger = logging.getLogger(__name__)


def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    # with io.open(speech_file, "rb") as audio_file:
    #     content = audio_file.read()

    # languages = ["en-US", "ru-RU", "uk-UA"]

    audio = speech.RecognitionAudio(content=speech_file.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,  # for .mp3 format
        sample_rate_hertz=16000,
        language_code="uk-UA",
    )

    response = client.recognize(config=config, audio=audio)
    if response:
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            logger.info(u"Transcript: {}".format(result.alternatives[0].transcript))
        return response.results[0].alternatives[0].transcript


class SpeechView(APIView):
    """
    Get location from voice command
    """
    permission_classes = [IsAuthenticated]
    # serializer_class = UserFullSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        # search through user's saved locations
        saved_locations = request.user.saved_locations.all()

        if len(saved_locations) == 0:
            return Response(
                data={"details": "You don't have any saved location", "error": True},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            try:
                # get transcribed speech
                text_result = transcribe_file(request.data['file'])
                text_result_splitted = text_result.split()

                # search location by key words from transcribed test result
                if any(x in text_result_splitted for x in ["от", "до", "к", "в", "на", "домой"]):
                    name_from = ""
                    name_to = ""

                    # search location by reserved keywords
                    if "от" in text_result_splitted:
                        name_from = text_result_splitted[text_result_splitted.index("от") + 1]
                    elif "из" in text_result_splitted:
                        name_from = text_result_splitted[text_result_splitted.index("из") + 1]

                    if "до" in text_result_splitted:
                        name_to = text_result_splitted[text_result_splitted.index("до") + 1]
                    elif "к" in text_result_splitted:
                        name_to = text_result_splitted[text_result_splitted.index("к") + 1]
                    elif "в" in text_result_splitted:
                        name_to = text_result_splitted[text_result_splitted.index("в") + 1]
                    elif "на" in text_result_splitted:
                        name_to = text_result_splitted[text_result_splitted.index("на") + 1]
                    elif "домой" in text_result_splitted:
                        name_to = "Дом"

                    if name_from != "":
                        if "работ" in name_from:
                            name_from = "Работа"
                        elif "дом" in name_from:
                            name_from = "Дом"
                        elif "избран" in name_from or "любим":
                            name_from = "Избранное"

                    if name_to != "":
                        if "работ" in name_to or "робот" in name_to:
                            name_to = "Работа"
                        elif "дом" in name_to:
                            name_to = "Дом"
                        elif "избран" in name_to or "любим" in name_to:
                            name_to = "Избранное"

                    print(f"--- name_from: {name_from}")
                    print(f"--- name_to: {name_to}")

                    to_location = None
                    from_location = None

                    # for saved_location in saved_locations:
                    if name_from != "":
                        from_location = get_object_or_404(SavedLocation, user=request.user, name=name_from)
                        if not from_location:
                            return Response(
                                data={"details": "Can't find location by your request", "error": True},
                                status=status.HTTP_404_NOT_FOUND
                            )

                    if name_to != "":
                        to_location = get_object_or_404(SavedLocation, user=request.user, name=name_to)
                        # to_location = saved_locations.get(name=name_to)
                        if not to_location:
                            return Response(
                                data={"details": "Can't find location by your request", "error": True},
                                status=status.HTTP_404_NOT_FOUND
                            )

                    return Response(
                        data={
                            "from_location": SavedLocationSerializer(from_location).data if from_location else None,
                            "to_location": SavedLocationSerializer(to_location).data,
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        data={"details": "Can't find location by your request", "error": True},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                logger.error(e)
                raise ValidationError({'detail': e})
