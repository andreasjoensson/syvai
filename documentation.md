For at køre programmet skal følgende trin først følges:

1. Download de påkrævede biblioteker ved at køre følgende kommando i terminalen:

   pip install -r requirements.txt

2. Efter installationen kan scriptet eksekveres ved at bruge følgende kommando:

   python linkedin_automation.py <email> <kodeord> <linkedin-tråd-url>

   Erstat <email> og <kodeord> med dine LinkedIn-kontooplysninger og <linkedin-tråd-url> med den specifikke LinkedIn-tråds URL.

   For eksempel: python linkedin_automation.py and@live.dk testkodeord https://www.linkedin.com/posts/mathias-gladteknik-as_gladforedrag-gladteknik-diagnosersomstyrker-ugcPost-7170426317891481600-37lg

3. Efter kørslen oprettes en ChromaDB-kollektion med kommentarer fra LinkedIn-opslaget, og der køres en testforespørgsel for at sikre, at alt fungerer korrekt.
