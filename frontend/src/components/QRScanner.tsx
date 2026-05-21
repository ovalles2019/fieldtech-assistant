import { useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";

interface Props {
  onScan: (payload: string) => void;
  onClose: () => void;
}

async function cleanupScanner(scanner: Html5Qrcode) {
  try {
    await scanner.stop();
  } catch {
    /* scanner may already be stopped */
  }
  try {
    await scanner.clear();
  } catch {
    /* ignore */
  }
}

export default function QRScanner({ onScan, onClose }: Props) {
  const [error, setError] = useState<string | null>(null);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const scanned = useRef(false);

  useEffect(() => {
    const id = "qr-reader";
    const scanner = new Html5Qrcode(id);
    scannerRef.current = scanner;

    scanner
      .start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decoded) => {
          if (scanned.current) return;
          scanned.current = true;
          void cleanupScanner(scanner);
          onScan(decoded);
        },
        () => {}
      )
      .catch(() => setError("Camera access denied or unavailable"));

    return () => {
      void cleanupScanner(scanner);
    };
  }, [onScan]);

  return (
    <div className="card" style={{ marginTop: "1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <strong>Scan asset QR</strong>
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          Close
        </button>
      </div>
      {error ? (
        <p style={{ color: "var(--danger)" }}>{error}</p>
      ) : (
        <div id="qr-reader" style={{ marginTop: "0.75rem" }} />
      )}
      <p style={{ fontSize: "0.8rem", color: "var(--muted)", marginTop: "0.5rem" }}>
        Demo payloads: <code>fieldtech://asset/hvac-ctrl-001</code>
      </p>
    </div>
  );
}
