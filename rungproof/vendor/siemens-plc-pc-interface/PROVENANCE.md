# Siemens PLC/PC Interface provenance

This package is a pinned source snapshot with local patches used by RungProof's
guarded PLC runtime, read-only diagnostic adapter and retained PyInstaller build.

- Upstream repository: `https://github.com/mnwinter/Siemens-PLC-PC-Interface`
- Upstream commit: `754fcfb88192f2a932bd7df70feea0d08088ab97`
- Snapshot path: `src/siemens_plc_pc_interface`
- Local audited patch: `Snap7Transport.read_many_diagnostic()` delegates to the
  existing batched read implementation without adding any write route.
- Local audited heartbeat patch: health advances only when the PLC echo exactly
  acknowledges the heartbeat written during the preceding cycle; an unrelated
  changing DINT cannot satisfy readiness.
- Local transport patch: configure the pinned Snap7 timeout parameters and
  socket timeout so communication/shutdown remain bounded.
- Migration review 2026-10-04: the tracked source already contained the above
  heartbeat/runtime/update-loop and transport patches, but its manifest retained
  older hashes. Source was compared with the canonical interface and the
  existing native runtime tests, including unrelated echo rejection, passed.
  No adapter implementation was changed by this manifest repair.
- Exact local Python-source hashes, with CRLF normalized to LF:
  `SOURCE-SHA256.txt`; the package build
  rejects missing, additional, or modified adapter source.
- Runtime dependency: `python-snap7==3.1.0`

The snapshot removes the former build-time dependency on an adjacent, mutable
working tree. Update it only by selecting a new reviewed commit, rerunning the
upstream tests, reapplying/reviewing the local patches, and updating this
provenance record and source/package hashes.
