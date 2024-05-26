# Goal
To create an assistant that is capable of completing tasks for you that arent common features of other assistants created using similar technology.

## Needed to run
Deepgram (api key)
<br>
Twilio (api key, number, Twilio bin)
<br>
Groq (api key)
<br>
~~GPT (api key)~~
<br>
Phone number (calling Twilio number)
<br>
Using Ngrok host on 5000 ->```ngrok http 5000``` should return something similar to ```d7d7-24-151-91-112.ngrok-free.app```

## Feature list
### Device Features (Discontinued)
- [X] TTV Device
- [X] STT Device
- [ ] Complete Integration

### Twilio Phone features
- [X] TTV Phone
- [X] STT Phone
- [X] Complete Integration

### Both
- [X] GPT response
- [X] Groq implemntation for complete sentences (removed from main part since it increased latency)
- [ ] Database to hold previous chats
- [ ] Complete Integration of system
- [ ] Implementation of Google Calendar's API
- [ ] Integration of Playwright

### Future Implentations
- [ ] Calling on anothers behalf 
- [ ] Sending texts for you
- [ ] After handling a Call sends user summary of what happened

## Current issues
Trying to lower latency as much as possible for the phone call
Stopped working on device portion since main focus is on the call aspect
