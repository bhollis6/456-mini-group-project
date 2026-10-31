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

Part 1:
Files: adversary.py
- Looked at the code in adversary.py after Braden wrote it to ensure its usability
- Performed a complete audit of the PDF before the final submission.
- Ensured all video requirements were met as the demo was being recorded.

Part 2:
Files: adversary.py, monitor.py, login.py
- Added attack scenario 2 (tampered/corrupted checkpoint) in adversary.py: a tamper mode that injects a forged session into checkpoint.json and a corrupt mode that invalidates it
- Added a dropped-heartbeat variant of attack scenario 1 (delay) that freezes the primary with SIGSTOP to force a false failover while the primary stays alive
- Added the [Crash Detected] -> [Failover Triggered] -> [Service Restored] log markers in monitor.py (Task 3)
- Fixed login.py to report a failed login instead of always printing success
- Ran the adversarial test suite and wrote the Adversarial Audit Summary section of the report
- Performed a final audit of report document and demo video

Whole Team:
-General debugging on each of the files
-Communicated via teams to fix mistakes and implemented the changes on github
-Reviewed and finished up the pdf report with each member's individual contribution
-Recorded the video demonstration and did the voiceover all via teams 
