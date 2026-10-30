#The following CONTRIBUTIONS.md lists each team member's specific contributions to the service, monitor, security audit, and video demo.

Member: Alexa Tchakar 
Files: authentication_service.py, standby_service.py, adversary.py
- Part 1:
- Implemented the authentication/ticket service using TCP listener 
- Validated credentials and issued tokens
- Implemented hmac signed heartbeats each T seconds 
- Part 2:
- Implemented passive redundancy node which listens on port 9998, loads checkpoint upon failover and takes over port 8080
- Developed attack scenario 1 induced failover in adversary.py to spoof crash to simulate split brain 

Member: Adrian Mancinas Ponce
Files: monitor.py
- Implemented the first version of the heartbeat monitor, making sure the logic flows well with the critical service
- Fixed a bug causing false socket timeout to appear by increasing the timeout interval by a second to reduce any false positives.

Member: Braden Hollis
Files: adversary.py
- Coded adversary.py.
- Reviewed and fixed bugs in monitor.py and authentication_service.py
- Created repository and edited video.

Member: Jackson Reed
Files: adversary.py
- Looked at the code in adversary.py after Braden wrote it to ensure its usability
- Performed a complete audit of the PDF before the final submission.
- Ensured all video requirements were met as the demo was being recorded.
  

Whole Team:
-General debugging on each of the files
-Communicated via teams to fix mistakes and implemented the changes on github
-Reviewed and finished up the pdf report with each member's individual contribution
-Recorded the video demonstration and did the voiceover all via teams 
