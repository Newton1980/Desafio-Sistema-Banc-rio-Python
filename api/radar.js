/**
 * Proxy serverless — REDEMET DECEA MaxCAPPI
 * Mantém a chave de API fora do bundle client-side.
 * Vercel runtime: Node.js (edge não é necessário aqui).
 */
export default async function handler(req, res) {
  const key = process.env.REDEMET_API_KEY;

  if (!key) {
    return res.status(500).json({ error: 'REDEMET_API_KEY não configurada' });
  }

  try {
    const upstream = await fetch(
      `https://api-redemet.decea.mil.br/produtos/radar/maxcappi?api_key=${key}`,
      { headers: { Accept: 'application/json' } }
    );

    const body = await upstream.text();

    res
      .setHeader('Content-Type', 'application/json')
      .setHeader('Cache-Control', 'public, s-maxage=60, stale-while-revalidate=30')
      .status(upstream.status)
      .send(body);
  } catch (err) {
    console.error('[api/radar]', err);
    res.status(502).json({ error: 'Erro ao contatar REDEMET' });
  }
}
