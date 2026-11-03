/** 平顶圆角六边形 SVG path（EvolutionTree / LayerBranchTree 共用） */
export function roundHexPath(cx, cy, r, cr, rot = -Math.PI / 6) {
  const corner = Math.min(cr, r * 0.32)
  const verts = []
  for (let i = 0; i < 6; i++) {
    const a = rot + (Math.PI / 3) * i
    verts.push({ x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) })
  }

  const norm = (x, y) => {
    const len = Math.hypot(x, y) || 1
    return { x: x / len, y: y / len }
  }

  const parts = []
  for (let i = 0; i < 6; i++) {
    const prev = verts[(i + 5) % 6]
    const curr = verts[i]
    const next = verts[(i + 1) % 6]
    const v1 = norm(prev.x - curr.x, prev.y - curr.y)
    const v2 = norm(next.x - curr.x, next.y - curr.y)
    const p1 = { x: curr.x + v1.x * corner, y: curr.y + v1.y * corner }
    const p2 = { x: curr.x + v2.x * corner, y: curr.y + v2.y * corner }
    parts.push(i === 0 ? `M ${p1.x},${p1.y}` : `L ${p1.x},${p1.y}`)
    parts.push(`Q ${curr.x},${curr.y} ${p2.x},${p2.y}`)
  }
  parts.push('Z')
  return parts.join(' ')
}
