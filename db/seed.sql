-- AEx RAG – seed data for development and testing
-- Embeddings are zero vectors; replace with real embeddings in production.
-- Run schema.sql first.

INSERT INTO case_contexts (title, description, embedding, raw_context, created_at) VALUES

-- 1. Fiber connector damage causing OLT port link loss
(
  'OLT Port Link Down – Damaged Fiber Connector',
  'Fiber link on OLT-CPT-001 port 0/1/3 dropped. OTDR pinpointed a reflection event at 340 m indicating a damaged connector at the splice box outside Building A. Re-terminating the connector restored full signal.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "OLT-CPT-001",
      "port": "0/1/3",
      "issue": "Fiber link down",
      "reported_by": "noc_alert",
      "affected_onus": 42
    },
    "actions": [
      "Checked OLT port status via NMS – confirmed no optical signal",
      "Ran OTDR sweep on fiber span from OLT to Building A",
      "Located reflection event at 340 m near Building A splice box",
      "Dispatched field tech to inspect splice box",
      "Cleaned and re-terminated damaged SC/APC connector",
      "Re-seated fiber in OLT port and verified link up"
    ],
    "results": {
      "otdr_fault_distance_m": 340,
      "rx_power_before_dbm": -35.2,
      "rx_power_after_dbm": -18.4,
      "link_restored": true,
      "downtime_minutes": 47
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '30 days'
),

-- 2. ONT authentication failure after config push
(
  'ONT Authentication Failure – LOID Mismatch After Config Push',
  'Following a bulk config push, 12 ONTs on OLT-JHB-003 failed to authenticate. Investigation revealed the LOID values in ZMS were overwritten with template defaults. Restoring the correct LOIDs resolved authentication for all affected ONTs.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "OLT-JHB-003",
      "port": "0/2/0",
      "issue": "ONT authentication failure",
      "reported_by": "customer_complaint",
      "affected_onus": 12
    },
    "actions": [
      "Pulled ONT auth logs from ZMS – all 12 showing LOID_MISMATCH",
      "Compared current LOID values in ZMS against provisioning database",
      "Identified bulk config push 2 hours prior had overwritten LOIDs with template defaults",
      "Exported correct LOID mapping from provisioning DB",
      "Bulk-updated ZMS with correct LOID values for affected ONTs",
      "Triggered ONT re-registration and confirmed authentication success"
    ],
    "results": {
      "affected_ont_count": 12,
      "root_cause": "LOID overwritten by config push template",
      "onus_recovered": 12,
      "onus_still_failing": 0
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '21 days'
),

-- 3. High packet loss due to upstream SNR degradation
(
  'High Packet Loss on ONU – SNR Degradation from Fiber Bend',
  'Customers on PON port 0/0/7 of OLT-DBN-002 reported intermittent packet loss peaking at 18%. SNR measurement showed a 4 dB drop traced to a tight fiber bend introduced during recent cabinet maintenance.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "OLT-DBN-002",
      "port": "0/0/7",
      "issue": "Intermittent packet loss",
      "reported_by": "customer_complaint",
      "affected_onus": 8
    },
    "actions": [
      "Confirmed packet loss via NMS – upstream error counters elevated",
      "Measured ONU optical power levels – average rx power -22.1 dBm (within spec)",
      "Measured SNR on affected ONUs – 24.3 dB vs expected 28+ dB",
      "Reviewed recent change log – cabinet maintenance performed previous day",
      "Opened cabinet and inspected fiber routing",
      "Found tight 60 mm radius bend on distribution fiber near cable clamp",
      "Re-routed fiber with correct bend radius (minimum 30 mm)",
      "Re-measured SNR – 28.9 dB; confirmed packet loss resolved"
    ],
    "results": {
      "packet_loss_before_pct": 18.2,
      "packet_loss_after_pct": 0.01,
      "snr_before_db": 24.3,
      "snr_after_db": 28.9,
      "root_cause": "Tight fiber bend radius in distribution cabinet"
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '18 days'
),

-- 4. BGP session drop to upstream provider
(
  'BGP Session Drop to Upstream Transit Provider',
  'BGP session to upstream transit provider AS65001 dropped, causing a partial routing blackhole for 200+ subscribers. Root cause was an expired MD5 authentication password that had not been rotated in line with the quarterly security policy.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "CORE-RTR-CPT-01",
      "port": "eth0/0",
      "issue": "BGP session down to AS65001",
      "reported_by": "noc_alert",
      "affected_onus": 0
    },
    "actions": [
      "Confirmed BGP session state IDLE in NMS routing table",
      "Checked BGP neighbour logs – authentication failure messages present",
      "Verified MD5 password expiry date – password expired 2 days prior",
      "Coordinated with upstream NOC to confirm their current password",
      "Updated MD5 password on core router and upstream peer simultaneously",
      "BGP session re-established; verified full route table received",
      "Confirmed subscriber connectivity restored"
    ],
    "results": {
      "session_downtime_minutes": 23,
      "routes_affected": 412,
      "subscribers_impacted": 214,
      "root_cause": "Expired BGP MD5 authentication password"
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '15 days'
),

-- 5. Fiber cut affecting multiple subscribers on a shared span
(
  'Fiber Cut – Buried Cable Damage During Civil Works',
  'A civil contractor struck a buried feeder cable during road works, severing a 24-fibre cable and taking down 3 OLT ports serving 126 subscribers. A temporary aerial bypass was deployed within 4 hours while permanent repairs were scheduled.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "OLT-CPT-002",
      "port": "0/0/1,0/0/2,0/0/3",
      "issue": "Multiple OLT ports down – suspected fiber cut",
      "reported_by": "noc_alert",
      "affected_onus": 126
    },
    "actions": [
      "Confirmed 3 OLT ports showing no rx power simultaneously",
      "OTDR traced cut to 1.2 km from OLT near Main Road excavation site",
      "Contacted civil contractor on site – confirmed accidental cable strike",
      "Dispatched emergency fiber crew with aerial bypass cable",
      "Deployed 1.4 km aerial bypass secured to existing pole infrastructure",
      "Spliced bypass into feeder distribution points either side of cut",
      "Restored all 3 OLT ports; verified subscriber service restored",
      "Raised permanent buried repair work order"
    ],
    "results": {
      "cut_distance_from_olt_km": 1.2,
      "fibres_severed": 24,
      "ports_affected": 3,
      "subscribers_restored": 126,
      "temporary_bypass_deployed": true,
      "total_downtime_minutes": 237
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '10 days'
),

-- 6. Switch port flapping due to duplex mismatch
(
  'Access Switch Port Flapping – Duplex Mismatch on Uplink',
  'An access switch uplink port was flapping every 30–90 seconds, causing periodic connectivity drops for an entire office block. The port was auto-negotiating while the upstream distribution switch had the uplink hard-coded to full-duplex 1G.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "ACC-SW-BLK7-01",
      "port": "gi0/1",
      "issue": "Uplink port flapping",
      "reported_by": "customer_complaint",
      "affected_onus": 0
    },
    "actions": [
      "Confirmed port flap events in NMS syslog – 14 flaps in last hour",
      "Checked interface counters – high late-collision and CRC error counts",
      "Reviewed upstream distribution switch config – gi0/24 hard-set to full-duplex 1000",
      "Confirmed access switch uplink set to auto-negotiate",
      "Hard-coded access switch gi0/1 to full-duplex 1000",
      "Port stabilised immediately; no further flap events after 30 minutes monitoring"
    ],
    "results": {
      "flaps_per_hour_before": 14,
      "flaps_per_hour_after": 0,
      "crc_errors_before": 8421,
      "root_cause": "Duplex mismatch – one end auto-negotiate, one hard-set"
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '7 days'
),

-- 7. ONU low rx power – fiber crimped under door seal
(
  'ONU Low Rx Power – Drop Cable Crimped Under Door Seal',
  'A single ONU reported persistent low rx power (-28.5 dBm) causing degraded speeds. Field inspection found the drop cable had been crimped under a metal door seal during installation, creating a micro-bend loss point.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "OLT-CPT-003",
      "port": "0/1/5",
      "issue": "ONU low receive power",
      "reported_by": "customer_complaint",
      "affected_onus": 1
    },
    "actions": [
      "Confirmed ONU rx power -28.5 dBm in ZMS (threshold -27 dBm)",
      "Checked patch panel and splitter – all connections clean, no loss",
      "Dispatched field tech to customer premises",
      "Inspected drop cable route from building entry to ONT",
      "Found drop cable crimped under metal door weather seal at front entrance",
      "Re-routed drop cable through dedicated cable entry gland",
      "Re-measured ONU rx power – -19.2 dBm"
    ],
    "results": {
      "rx_power_before_dbm": -28.5,
      "rx_power_after_dbm": -19.2,
      "root_cause": "Micro-bend from drop cable crimped under door seal"
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '3 days'
),

-- 8. DHCP lease exhaustion on access subnet
(
  'DHCP Lease Exhaustion – /24 Pool Saturated by Stale Leases',
  'Subscribers on VLAN 100 began failing to obtain IP addresses. The DHCP pool (192.168.100.0/24) was exhausted due to a misconfigured lease time of 30 days leaving stale entries from decommissioned CPEs. Clearing stale leases and reducing lease time to 24 hours resolved the issue.',
  ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector,
  '{
    "inputs": {
      "device_id": "BRAS-JHB-01",
      "port": "vlan100",
      "issue": "Subscribers unable to obtain IP address",
      "reported_by": "customer_complaint",
      "affected_onus": 31
    },
    "actions": [
      "Checked DHCP pool utilisation in NMS – 254/254 leases allocated",
      "Exported active lease table and cross-referenced with active subscriber list",
      "Identified 87 stale leases from decommissioned CPE MAC addresses",
      "Checked lease time config – 30-day lease time found (should be 24 h)",
      "Cleared 87 stale leases from DHCP server",
      "Updated lease time to 24 hours",
      "Verified new subscribers able to obtain leases immediately"
    ],
    "results": {
      "pool_utilisation_before_pct": 100,
      "pool_utilisation_after_pct": 66,
      "stale_leases_cleared": 87,
      "lease_time_before_days": 30,
      "lease_time_after_hours": 24,
      "subscribers_unblocked": 31
    },
    "outcome": "resolved"
  }',
  NOW() - INTERVAL '1 day'
);
