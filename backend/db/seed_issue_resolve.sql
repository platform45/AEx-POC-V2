-- AEx RAG – seed data for issue_resolve table
-- Run schema.sql first.

INSERT INTO issue_resolve (device_id, issue_description, resolved, resolution_description, created_at, resolved_at) VALUES

-- 1. Resolved – OLT port optical alarm cleared
(
  'OLT-CPT-001',
  'Port 0/0/2 raising persistent los-of-signal alarm. Downstream ONTs on the PON segment intermittently losing registration.',
  TRUE,
  'OTDR sweep located a high-loss splice at 820 m from the OLT. Field technician re-spliced the joint, reducing insertion loss from 1.8 dB to 0.2 dB. All ONTs re-registered within 5 minutes of the repair.',
  NOW() - INTERVAL '45 days',
  NOW() - INTERVAL '44 days'
),

-- 2. Resolved – ONT stuck in activating state
(
  'OLT-JHB-003',
  'Single ONT (S/N: ZTEG1A2B3C4D) stuck in ACTIVATING state for over 6 hours following a planned maintenance window. Customer has no service.',
  TRUE,
  'ZMS showed the ONT profile had been assigned an incorrect service template during the maintenance window. Re-applying the correct GPON service template and issuing an ONT reset restored service within 3 minutes.',
  NOW() - INTERVAL '38 days',
  NOW() - INTERVAL '38 days'
),

-- 3. Resolved – Core router CPU spike
(
  'CORE-RTR-CPT-01',
  'CPU utilisation spiked to 94% causing SNMP polling timeouts and delayed BGP keepalives. NMS flagged potential routing instability.',
  TRUE,
  'Process accounting identified a misconfigured SNMP community string on a monitoring server triggering bulk walks every 10 seconds. Correcting the polling interval to 300 seconds and the community string dropped CPU utilisation to 18% within 2 minutes.',
  NOW() - INTERVAL '29 days',
  NOW() - INTERVAL '29 days'
),

-- 4. Resolved – VLAN misconfiguration on access switch
(
  'ACC-SW-BLK7-01',
  'Newly provisioned subscriber on port gi0/12 unable to obtain DHCP lease. Other ports on the same switch unaffected.',
  TRUE,
  'Port gi0/12 was in access VLAN 200 (management) instead of VLAN 100 (subscriber). Updated the switchport access VLAN to 100 and subscriber obtained a lease within 30 seconds.',
  NOW() - INTERVAL '22 days',
  NOW() - INTERVAL '22 days'
),

-- 5. Resolved – ONT rx power degradation
(
  'OLT-DBN-002',
  'ONT on port 0/1/4 reporting rx power of -26.8 dBm, below the -25 dBm alarm threshold. Customer reporting slow speeds and frequent disconnections.',
  TRUE,
  'Field inspection revealed the SC/APC connector at the subscriber patch panel had heavy contamination. Cleaning with a fibre optic cassette cleaner restored rx power to -18.3 dBm and resolved customer complaints.',
  NOW() - INTERVAL '17 days',
  NOW() - INTERVAL '17 days'
),

-- 6. Resolved – DNS resolution failures for subscribers
(
  'BRAS-JHB-01',
  'Multiple subscribers on VLAN 110 reporting intermittent DNS resolution failures. Internal services unaffected; issue appears limited to external DNS queries.',
  TRUE,
  'Upstream DNS forwarder IP had changed following a provider maintenance window but the BRAS configuration still pointed to the old address. Updated the DNS forwarder IP on BRAS-JHB-01 and flushed the resolver cache. Subscriber DNS resolution confirmed working across all affected accounts.',
  NOW() - INTERVAL '12 days',
  NOW() - INTERVAL '12 days'
),

-- 7. Unresolved – Intermittent OLT port errors
(
  'OLT-CPT-002',
  'Port 0/2/6 accumulating upstream FEC corrected error counts at an abnormal rate (~1200/hr). No customer complaints yet but trend is worsening over the past 4 days. Suspected deteriorating SFP or dirty connector.',
  FALSE,
  NULL,
  NOW() - INTERVAL '4 days',
  NULL
),

-- 8. Unresolved – BGP route flap to secondary peer
(
  'CORE-RTR-CPT-01',
  'BGP session to secondary transit peer AS65002 has flapped 3 times in the past 48 hours. Each flap lasts under 2 minutes but causes brief packet loss for a subset of subscribers. Root cause not yet identified.',
  FALSE,
  NULL,
  NOW() - INTERVAL '2 days',
  NULL
),

-- 9. Unresolved – High memory utilisation on BRAS
(
  'BRAS-JHB-01',
  'Memory utilisation on BRAS-JHB-01 has risen steadily from 62% to 81% over the past week without a corresponding increase in subscriber count. Possible memory leak in PPPoE process. No service impact observed yet.',
  FALSE,
  NULL,
  NOW() - INTERVAL '7 days',
  NULL
),

-- 10. Resolved – Fiber span loss increase after heavy rain
(
  'OLT-CPT-003',
  'Optical loss on the feeder span to Zone 5 increased by 3.1 dB following overnight heavy rainfall. Several ONTs dropped below minimum rx power threshold.',
  TRUE,
  'Ground-level inspection found an unsealed splice closure in the feeder route had ingressed water, causing swelling in the ribbon fibre matrix. Splice closure was drained, fibres re-spliced and the enclosure resealed with waterproof compound. Loss returned to baseline within 2 hours.',
  NOW() - INTERVAL '9 days',
  NOW() - INTERVAL '8 days'
);
