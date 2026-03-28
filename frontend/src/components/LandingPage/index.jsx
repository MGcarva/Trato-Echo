const PRODUCTS = [
  { name: 'Pasto Deportivo', height: '25mm', price: '$12.000', use: 'Canchas de fútbol, multideporte', emoji: '⚽' },
  { name: 'Ornamental Básico', height: '20mm', price: '$8.500', use: 'Jardines, terrazas, balcones', emoji: '🌿' },
  { name: 'Ornamental Premium', height: '35mm', price: '$15.000', use: 'Jardines de lujo, decoración', emoji: '✨' },
]

export default function LandingPage() {
  return (
    <div style={{ fontFamily: 'inherit', color: 'var(--gray-800)' }}>
      {/* Hero */}
      <header style={{
        background: 'linear-gradient(135deg, #14532d 0%, #166534 50%, #15803d 100%)',
        color: '#fff',
        padding: '0 24px',
      }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          {/* Nav */}
          <nav style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 28 }}>🌿</span>
              <div>
                <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: '-0.3px' }}>Césped Sintético SpA</div>
                <div style={{ fontSize: 11, opacity: 0.7 }}>Melipilla, Chile</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 24, fontSize: 14 }}>
              <a href="#productos" style={{ color: 'rgba(255,255,255,0.85)', textDecoration: 'none' }}>Productos</a>
              <a href="#calculadora" style={{ color: 'rgba(255,255,255,0.85)', textDecoration: 'none' }}>Calculadora</a>
              <a href="#contacto" style={{ color: 'rgba(255,255,255,0.85)', textDecoration: 'none' }}>Contacto</a>
            </div>
          </nav>

          {/* Hero content */}
          <div style={{ padding: '80px 0 100px', textAlign: 'center' }}>
            <div style={{ display: 'inline-block', background: 'rgba(255,255,255,0.15)', padding: '6px 16px', borderRadius: 999, fontSize: 13, marginBottom: 20, backdropFilter: 'blur(4px)' }}>
              ✅ Instalación disponible · Melipilla y alrededores
            </div>
            <h1 style={{ fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: 900, lineHeight: 1.1, marginBottom: 20, letterSpacing: '-1px' }}>
              Pasto Sintético de Calidad<br />
              <span style={{ color: '#86efac' }}>para tu Hogar o Cancha</span>
            </h1>
            <p style={{ fontSize: 18, opacity: 0.85, maxWidth: 520, margin: '0 auto 36px', lineHeight: 1.6 }}>
              Cotiza en segundos con nuestro asistente inteligente. Calculamos el metraje exacto y generamos tu link de pago al instante.
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                onClick={() => document.querySelector('.cw-fab')?.click()}
                style={{
                  background: '#22c55e', color: '#fff', padding: '14px 28px', borderRadius: 999,
                  fontWeight: 700, fontSize: 16, border: 'none', cursor: 'pointer',
                  boxShadow: '0 4px 16px rgba(34,197,94,0.4)', transition: 'transform 0.1s',
                }}
                onMouseEnter={e => e.target.style.transform = 'translateY(-2px)'}
                onMouseLeave={e => e.target.style.transform = 'translateY(0)'}
              >
                💬 Cotizar ahora →
              </button>
              <a
                href="#calculadora"
                style={{
                  background: 'rgba(255,255,255,0.15)', color: '#fff', padding: '14px 28px',
                  borderRadius: 999, fontWeight: 600, fontSize: 16, backdropFilter: 'blur(4px)',
                  border: '1px solid rgba(255,255,255,0.25)',
                }}
              >
                📐 Ver calculadora
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Stats bar */}
      <div style={{ background: '#f0fdf4', borderBottom: '1px solid #dcfce7', padding: '16px 24px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto', display: 'flex', justifyContent: 'center', gap: 48, flexWrap: 'wrap' }}>
          {[
            ['🕐', 'Respuesta en < 30 seg'],
            ['📋', 'Cotización instantánea'],
            ['💳', 'Pago 100% online'],
            ['🔧', 'Instalación incluida'],
          ].map(([icon, text]) => (
            <div key={text} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, color: '#15803d', fontWeight: 600 }}>
              <span>{icon}</span><span>{text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Products */}
      <section id="productos" style={{ padding: '80px 24px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <h2 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>Nuestros Productos</h2>
            <p style={{ color: 'var(--gray-500)', fontSize: 16 }}>Precios por metro cuadrado + IVA. Instalación opcional.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 24 }}>
            {PRODUCTS.map(p => (
              <div key={p.name} style={{
                border: '1.5px solid var(--gray-200)', borderRadius: 16, padding: 24,
                transition: 'box-shadow 0.2s, transform 0.2s',
                cursor: 'default',
              }}
                onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
                onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; e.currentTarget.style.transform = 'translateY(0)' }}
              >
                <div style={{ fontSize: 40, marginBottom: 12 }}>{p.emoji}</div>
                <h3 style={{ fontWeight: 700, fontSize: 18, marginBottom: 4 }}>{p.name}</h3>
                <div style={{ fontSize: 13, color: 'var(--gray-500)', marginBottom: 12 }}>
                  Altura de fibra: {p.height} · {p.use}
                </div>
                <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--green-700)' }}>
                  {p.price} <span style={{ fontSize: 14, fontWeight: 400, color: 'var(--gray-500)' }}>CLP/m²</span>
                </div>
                <button
                  onClick={() => document.querySelector('.cw-fab')?.click()}
                  style={{
                    marginTop: 16, width: '100%', padding: '10px', background: 'var(--green-50)',
                    color: 'var(--green-700)', border: '1px solid var(--green-100)', borderRadius: 999,
                    fontSize: 14, fontWeight: 600, cursor: 'pointer', transition: 'background 0.15s',
                  }}
                  onMouseEnter={e => e.target.style.background = 'var(--green-100)'}
                  onMouseLeave={e => e.target.style.background = 'var(--green-50)'}
                >
                  Cotizar este producto
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Calculadora visual */}
      <section id="calculadora" style={{ background: 'var(--gray-50)', padding: '80px 24px', borderTop: '1px solid var(--gray-200)' }}>
        <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: 32, fontWeight: 800, marginBottom: 8 }}>¿Cómo medir tu espacio?</h2>
          <p style={{ color: 'var(--gray-500)', fontSize: 16, marginBottom: 48 }}>3 pasos simples para saber exactamente cuánto pasto necesitas</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 24, textAlign: 'left' }}>
            {[
              { step: '1', icon: '📏', title: 'Mide el largo', desc: 'Usa una cinta métrica. Anota el largo en metros.' },
              { step: '2', icon: '📐', title: 'Mide el ancho', desc: 'Mide el ancho perpendicular al largo.' },
              { step: '3', icon: '🧮', title: 'Multiplica', desc: 'Largo × Ancho = m². Suma un 10% de margen extra.' },
            ].map(s => (
              <div key={s.step} style={{ background: 'var(--white)', border: '1px solid var(--gray-200)', borderRadius: 12, padding: 20 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--green-600)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 14 }}>{s.step}</div>
                  <span style={{ fontSize: 22 }}>{s.icon}</span>
                </div>
                <div style={{ fontWeight: 700, marginBottom: 4 }}>{s.title}</div>
                <div style={{ fontSize: 13, color: 'var(--gray-500)', lineHeight: 1.5 }}>{s.desc}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 36, padding: 20, background: 'var(--green-50)', borderRadius: 12, border: '1px solid var(--green-100)', textAlign: 'left' }}>
            <div style={{ fontWeight: 700, color: 'var(--green-700)', marginBottom: 8 }}>💡 Ejemplo práctico</div>
            <div style={{ fontSize: 14, color: 'var(--gray-700)', lineHeight: 1.7 }}>
              Jardín de <strong>5 metros de largo</strong> × <strong>3 metros de ancho</strong> = <strong>15 m²</strong><br />
              Con 10% de margen: <strong>16.5 m²</strong> (siempre conviene tener material extra para cortes)
            </div>
          </div>
          <button
            onClick={() => document.querySelector('.cw-fab')?.click()}
            style={{
              marginTop: 32, background: 'var(--green-600)', color: '#fff', padding: '14px 32px',
              borderRadius: 999, fontWeight: 700, fontSize: 16, border: 'none', cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(22,163,74,0.3)',
            }}
          >
            🌿 Cotizar con el asistente →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer id="contacto" style={{ background: 'var(--gray-900)', color: 'rgba(255,255,255,0.7)', padding: '40px 24px', textAlign: 'center' }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 20 }}>🌿</span>
            <span style={{ fontWeight: 700, color: '#fff', fontSize: 16 }}>Césped Sintético SpA</span>
          </div>
          <p style={{ fontSize: 13 }}>Melipilla, Región Metropolitana · Chile</p>
          <p style={{ fontSize: 12, marginTop: 16, opacity: 0.5 }}>
            Sistema de cotizaciones Trato Hecho · Powered by Claude AI & n8n
          </p>
        </div>
      </footer>
    </div>
  )
}
