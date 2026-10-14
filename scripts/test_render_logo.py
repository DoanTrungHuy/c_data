import os

svg_content = """<svg viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080C14" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>

    <!-- Outer C Arc Gradient (Cyber Azure to Tech Indigo) -->
    <linearGradient id="neon-c" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#7C3AED" />
    </linearGradient>

    <!-- Inner Data Beacon Gradient (Emerald to Cyan) -->
    <linearGradient id="core-spark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981" />
      <stop offset="50%" stop-color="#06B6D4" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>

    <!-- Subtle Outer Glow -->
    <filter id="soft-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Container Squircle with Tech Border -->
  <rect width="128" height="128" rx="34" fill="url(#bg-grad)" />
  <rect x="1" y="1" width="126" height="126" rx="33" stroke="url(#neon-c)" stroke-width="1.5" stroke-opacity="0.35" />

  <!-- The Cyber Wave "C" Monogram (Bold, aerodynamic curve inspired by Ha Long bay contours) -->
  <path
    d="M86 40 C75 26 48 26 36 40 C22 56 22 72 36 88 C48 102 75 102 86 88"
    stroke="url(#neon-c)"
    stroke-width="13"
    stroke-linecap="round"
    stroke-linejoin="round"
    filter="url(#soft-glow)"
  />

  <!-- High-Precision Data Beacon Diamond (Representing verified opportunities) -->
  <polygon points="76,64 88,52 100,64 88,76" fill="url(#core-spark)" />
  
  <!-- Star Spark Center Node -->
  <circle cx="88" cy="64" r="3" fill="#FFFFFF" />
  <circle cx="88" cy="64" r="7" stroke="#38BDF8" stroke-width="1.5" stroke-opacity="0.6" />
</svg>"""

os.makedirs("frontend/public", exist_ok=True)
with open("frontend/public/icon.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("Icon SVG generated successfully.")
