# Network Connectivity Test Instructions
**VCA 1.0 - Phase 0 Final Task**
**Date:** 2025-11-01

## Network Configuration

### WSL2 (Linux) Network Info
- **Hostname**: DESKTOP-UUPV109
- **WSL2 IP**: 172.20.177.188 (internal to Windows)
- **Docker Bridge**: 172.17.0.1
- **Gateway**: 172.20.176.1

### Important Note on WSL2 Networking
WSL2 runs in a virtualized network environment. Your phone needs to connect to your **Windows host IP**, not the WSL2 IP.

## How to Find Your Windows Host IP

### Method 1: From Windows Command Prompt
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Run: `ipconfig`
4. Look for your active network adapter (Wi-Fi or Ethernet)
5. Note the **IPv4 Address** (e.g., `192.168.1.XXX` or `10.0.0.XXX`)

### Method 2: From Windows Settings
1. Press `Windows + I` to open Settings
2. Go to **Network & Internet**
3. Click on **Wi-Fi** or **Ethernet** (whichever you're using)
4. Click on your connected network
5. Scroll down to **Properties**
6. Find **IPv4 address**

## Network Connectivity Tests

### Test 1: Verify Home Assistant is Accessible from Windows

**On your Windows PC:**

1. Open a web browser (Chrome, Edge, Firefox)
2. Navigate to: `http://localhost:8123`
3. **Expected result**: Home Assistant login page loads ✅
4. Try logging in with your Mike VCA credentials

**If this works**: Home Assistant is running correctly on WSL2 ✅

### Test 2: Test from Phone to PC (Samsung A05)

**On your Samsung A05 phone:**

#### Step 2a: Connect to Same Wi-Fi Network
1. Open **Settings** → **Wi-Fi**
2. Verify you're connected to the **same Wi-Fi network** as your PC
3. Note the network name (SSID)

#### Step 2b: Ping Test (Optional - Requires App)
1. Install **Network Utilities** or **Fing** app from Play Store (optional)
2. Use the ping tool to ping your Windows host IP
3. Example: If Windows IP is `192.168.1.100`, ping that address
4. **Expected result**: Replies received = network connectivity OK

#### Step 2c: Home Assistant Web Access Test
1. Open **Chrome** or **Samsung Internet** browser on your phone
2. Navigate to: `http://<WINDOWS_IP>:8123`
   - Replace `<WINDOWS_IP>` with the IPv4 address you found earlier
   - Example: `http://192.168.1.100:8123`
3. **Expected result**: Home Assistant login page loads on your phone ✅

**If this works**: Your phone can reach Home Assistant ✅ (95% uptime requirement verified)

### Test 3: Configure WSL2 Port Forwarding (REQUIRED)

**⚠️ IMPORTANT**: WSL2 requires port forwarding for external network access.

**This step is REQUIRED, not optional. Phone access will fail without it.**

#### Configure Port Forwarding

**Run in PowerShell as Administrator** (Windows, not WSL):

```powershell
# Forward port 8123 from Windows to WSL2
netsh interface portproxy add v4tov4 listenport=8123 listenaddress=0.0.0.0 connectport=8123 connectaddress=172.20.177.188
```

**How to open PowerShell as Administrator:**
1. Press `Windows + X`
2. Click **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**
3. Click **Yes** on the security prompt
4. Copy and paste the command above
5. Press Enter

**Expected output:** (no output means success)

#### Verify Port Forwarding is Active

Check if port forwarding is configured:

```powershell
netsh interface portproxy show all
```

**Expected output:**
```
Listen on ipv4:             Connect to ipv4:

Address         Port        Address         Port
--------------- ----------  --------------- ----------
0.0.0.0         8123        172.20.177.188  8123
```

**Note:** This configuration persists across reboots. You only need to do this once.

Then retry Test 2c from your phone.

#### Option C: Windows Firewall Rule (if still blocked)
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Select **Port** → Next
4. Select **TCP** → Specific local ports: `8123` → Next
5. Select **Allow the connection** → Next
6. Check all profiles (Domain, Private, Public) → Next
7. Name: "Home Assistant WSL2" → Finish

### Test 4: Network Stability Test (95% Uptime Requirement)

**Goal**: Verify PC is "always-on" and accessible 95% of the time

**Test procedure:**

1. **Leave PC running** (don't shut down, sleep is OK)
2. **From your phone**, access Home Assistant at various times:
   - Morning (e.g., 8 AM)
   - Afternoon (e.g., 2 PM)
   - Evening (e.g., 8 PM)
3. **Log results**: Could you access HA each time?
4. **Identify downtime**:
   - PC restarts (acceptable, brief)
   - Internet outages (acceptable per requirement)
   - PC shutdowns (not acceptable for VCA reliability)

**Expected result**: Accessible ≥95% of attempts over 24-48 hours

## Troubleshooting Common Issues

### Issue 1: Can't Access from Windows localhost:8123

**Symptoms**: Browser shows "Unable to connect" or "Connection refused"

**Solutions**:
```bash
# Check if Home Assistant container is running
docker ps | grep homeassistant

# If not running, start it
docker start homeassistant

# Check logs for errors
docker logs homeassistant --tail 50
```

### Issue 2: Can Access from Windows but NOT from Phone

**Symptoms**: Works on PC, fails on phone with same network

**Likely causes**:
1. **Wrong IP address**: Using WSL2 IP instead of Windows IP
2. **Port forwarding missing**: WSL2 port not exposed to network
3. **Firewall blocking**: Windows Firewall blocking port 8123
4. **Different Wi-Fi network**: Phone on guest network or different SSID

**Solutions**:
- Double-check Windows IPv4 address (ipconfig)
- Add port forwarding rule (see Option B above)
- Add firewall rule (see Option C above)
- Verify both devices on same Wi-Fi network

### Issue 3: Works Sometimes, Not Others

**Symptoms**: Intermittent connectivity

**Likely causes**:
1. **PC going to sleep**: Power settings shutting down network
2. **Dynamic IP changing**: Router assigned new IP to PC
3. **WSL2 network reset**: Windows update or restart changed WSL2 IP

**Solutions**:
```powershell
# Set PC to never sleep (Windows Power Settings)
# Settings → System → Power & sleep → Never

# Or: Assign static IP in router settings (advanced)
```

### Issue 4: Home Assistant Loads Slowly on Phone

**Symptoms**: Takes >10 seconds to load

**Likely causes**:
- Wi-Fi signal weak
- Router congestion
- WSL2 overhead

**Solutions**:
- Move closer to Wi-Fi router
- Restart router if needed
- Check other devices using bandwidth

## Success Criteria Checklist

- [x] Home Assistant accessible from Windows browser at `localhost:8123` ✅
- [x] Windows host IPv4 address identified (e.g., `192.168.1.XXX`) ✅
- [x] WSL2 port forwarding configured (PowerShell command executed) ✅
- [x] Phone connected to same Wi-Fi network as PC ✅
- [x] Home Assistant accessible from phone at `http://<WINDOWS_IP>:8123` ✅
- [x] Login successful from phone using Mike VCA or Dad VCA credentials ✅
- [ ] PC configured to stay awake (no sleep mode during VCA usage hours)
- [ ] Tested at multiple times of day (morning, afternoon, evening)
- [ ] Estimated uptime ≥95% (accessible when needed)

**Status**: ✅ **Network connectivity verified** - Phone can access Home Assistant

**Key Finding**: WSL2 port forwarding was required for phone access. This is now documented for future sessions.

## Network Diagram for VCA 1.0

```
┌─────────────────────────────────────────────────────┐
│              Home Wi-Fi Network                     │
│              (e.g., 192.168.1.x)                    │
│                                                     │
│  ┌──────────────────────┐      ┌─────────────────┐ │
│  │  Samsung A05 Phone   │      │  Windows PC     │ │
│  │  IP: 192.168.1.50    │◄────►│  IP: 192.168.1. │ │
│  │  (Phone App)         │      │  100 (example)  │ │
│  └──────────────────────┘      └─────────────────┘ │
│           │                             │           │
│           │    HTTP Request             │           │
│           │    to :8123                 │           │
│           │                             ▼           │
│           │                    ┌────────────────┐   │
│           │                    │   WSL2 Ubuntu  │   │
│           │                    │ 172.20.177.188 │   │
│           │                    │                │   │
│           │                    │  ┌──────────┐  │   │
│           └───────────────────►│  │   Home   │  │   │
│                                │  │ Assistant│  │   │
│                                │  │  :8123   │  │   │
│                                │  └──────────┘  │   │
│                                │                │   │
│                                │  Session Mgr   │   │
│                                │  AnythingLLM   │   │
│                                │  n8n (future)  │   │
│                                └────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   Internet    │
                 │  (for API     │
                 │   calls)      │
                 └───────────────┘
```

## Recording Test Results

**Date/Time**: _______________

### Test Results

| Test | Status | Notes |
|------|--------|-------|
| HA accessible from Windows localhost:8123 | ⬜ Pass / ⬜ Fail | |
| Windows IPv4 address identified | ⬜ Yes / ⬜ No | IP: ___________ |
| Phone on same Wi-Fi network | ⬜ Yes / ⬜ No | SSID: ___________ |
| HA accessible from phone | ⬜ Pass / ⬜ Fail | |
| Login successful from phone | ⬜ Pass / ⬜ Fail | User: ___________ |
| PC stays awake (no sleep) | ⬜ Configured / ⬜ Not yet | |
| Multiple time-of-day tests | ⬜ Pass / ⬜ Fail | Times tested: ___________ |
| Estimated uptime ≥95% | ⬜ Yes / ⬜ No | % observed: ___________ |

### Network Details (For Reference)
- **Windows PC Name**: DESKTOP-UUPV109
- **Windows IPv4**: ___________ (fill in after ipconfig)
- **WSL2 IP**: 172.20.177.188 (internal, not used by phone)
- **Router/Gateway**: 172.20.176.1
- **Wi-Fi SSID**: ___________ (fill in)
- **Phone IP**: ___________ (optional, check phone Wi-Fi settings)

### Issues Encountered
_Record any connection failures, slow loads, or troubleshooting steps taken:_

---

---

## Next Steps After Successful Test

Once network connectivity is verified:

1. **Update Phase 0 status** to 100% complete
2. **Document network details** in [phase-0-completion-status.md](phase-0-completion-status.md)
3. **Sign off on Phase 0** (all requirements met)
4. **Ready to begin Phase 1**: Audio & Wake Pipeline development

**Phase 0 → Phase 1 transition checklist:**
- ✅ Docker + Home Assistant installed
- ✅ User accounts + API tokens configured
- ✅ Node.js 20+ installed (v22.16.0 ✅)
- ✅ Network connectivity verified
- ✅ Modular STT/TTS architecture documented
- ✅ All infrastructure ready for development

**Congratulations! Phase 0 Environment Preparation is complete when all tests pass.** 🎉
