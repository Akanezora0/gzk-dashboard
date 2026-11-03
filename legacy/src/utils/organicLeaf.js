/** 层详情枝干的叶形与树皮纹理（LayerBranchTree 专用） */

export const LEAF_VARIANTS = ['broad', 'lance', 'maple', 'heart', 'rippled']

function basis(bx, by, tipX, tipY) {
  const dx = tipX - bx
  const dy = tipY - by
  const len = Math.hypot(dx, dy) || 1
  const ux = dx / len
  const uy = dy / len
  const px = -uy
  const py = ux
  return { bx, by, tipX, tipY, len, ux, uy, px, py }
}

function pt(b, along, perp) {
  return {
    x: b.bx + b.ux * along + b.px * perp,
    y: b.by + b.uy * along + b.py * perp,
  }
}

function broadLeaf(b, width) {
  const w = width * 1.35
  const l1 = pt(b, b.len * 0.52, w)
  const l2 = pt(b, b.len * 0.52, -w)
  return {
    path: `M ${b.bx} ${b.by} Q ${l1.x} ${l1.y} ${b.tipX} ${b.tipY} Q ${l2.x} ${l2.y} ${b.bx} ${b.by} Z`,
    veins: [centralVein(b), sideVein(b, 0.38, w * 0.45), sideVein(b, 0.38, -w * 0.45)],
  }
}

function lanceLeaf(b, width) {
  const w = width * 0.78
  const tip = pt(b, b.len * 1.02, 0)
  const l1 = pt(b, b.len * 0.55, w)
  const l2 = pt(b, b.len * 0.55, -w)
  return {
    path: `M ${b.bx} ${b.by} Q ${l1.x} ${l1.y} ${tip.x} ${tip.y} Q ${l2.x} ${l2.y} ${b.bx} ${b.by} Z`,
    veins: [centralVein(b, tip.x, tip.y), sideVein(b, 0.42, w * 0.5), sideVein(b, 0.42, -w * 0.5)],
  }
}

function mapleLeaf(b, width) {
  const w = width * 1.22
  const tip = pt(b, b.len * 0.96, 0)
  const lL = pt(b, b.len * 0.52, w * 0.95)
  const lR = pt(b, b.len * 0.52, -w * 0.95)
  const uL = pt(b, b.len * 0.72, w * 0.52)
  const uR = pt(b, b.len * 0.72, -w * 0.52)
  const cL = pt(b, b.len * 0.86, w * 0.22)
  const cR = pt(b, b.len * 0.86, -w * 0.22)
  return {
    path: [
      `M ${b.bx} ${b.by}`,
      `Q ${lL.x} ${lL.y} ${uL.x} ${uL.y}`,
      `Q ${cL.x} ${cL.y} ${tip.x} ${tip.y}`,
      `Q ${cR.x} ${cR.y} ${uR.x} ${uR.y}`,
      `Q ${lR.x} ${lR.y} ${b.bx} ${b.by}`,
      'Z',
    ].join(' '),
    veins: [centralVein(b, tip.x, tip.y), sideVein(b, 0.42, w * 0.38), sideVein(b, 0.42, -w * 0.38)],
  }
}

function heartLeaf(b, width) {
  const w = width * 1.28
  const notch = pt(b, b.len * 0.06, 0)
  const lobeL = pt(b, b.len * 0.78, w * 0.95)
  const lobeR = pt(b, b.len * 0.78, -w * 0.95)
  const tip = pt(b, b.len * 0.98, 0)
  const cL = pt(b, b.len * 0.35, w)
  const cR = pt(b, b.len * 0.35, -w)
  return {
    path: [
      `M ${notch.x} ${notch.y}`,
      `C ${cL.x} ${cL.y} ${lobeL.x} ${lobeL.y} ${tip.x} ${tip.y}`,
      `C ${lobeR.x} ${lobeR.y} ${cR.x} ${cR.y} ${notch.x} ${notch.y}`,
      'Z',
    ].join(' '),
    veins: [centralVein(b, tip.x, tip.y), sideVein(b, 0.5, w * 0.35), sideVein(b, 0.5, -w * 0.35)],
  }
}

function rippledLeaf(b, width) {
  const w = width * 1.28
  const l1 = pt(b, b.len * 0.46, w * 1.06)
  const l2 = pt(b, b.len * 0.58, w * 0.82)
  const r1 = pt(b, b.len * 0.46, -w * 1.06)
  const r2 = pt(b, b.len * 0.58, -w * 0.82)
  return {
    path: [
      `M ${b.bx} ${b.by}`,
      `Q ${l1.x} ${l1.y} ${l2.x} ${l2.y}`,
      `Q ${b.tipX} ${b.tipY} ${b.tipX} ${b.tipY}`,
      `Q ${r2.x} ${r2.y} ${r1.x} ${r1.y}`,
      `Q ${b.bx} ${b.by} ${b.bx} ${b.by}`,
      'Z',
    ].join(' '),
    veins: [centralVein(b), sideVein(b, 0.44, w * 0.38), sideVein(b, 0.44, -w * 0.38)],
  }
}

function centralVein(b, tipX = b.tipX, tipY = b.tipY) {
  const mx = b.bx + (tipX - b.bx) * 0.55
  const my = b.by + (tipY - b.by) * 0.55
  return `M ${b.bx} ${b.by} Q ${mx} ${my} ${tipX} ${tipY}`
}

function sideVein(b, t, offset) {
  const p = pt(b, b.len * t, offset * 0.55)
  const tip = pt(b, b.len * (t + 0.28), offset * 0.15)
  return `M ${p.x} ${p.y} L ${tip.x} ${tip.y}`
}

export function buildLeafShape(variant, bx, by, tipX, tipY, width = 22) {
  const b = basis(bx, by, tipX, tipY)
  switch (variant) {
    case 'lance': return lanceLeaf(b, width)
    case 'maple': return mapleLeaf(b, width)
    case 'heart': return heartLeaf(b, width)
    case 'rippled': return rippledLeaf(b, width)
    default: return broadLeaf(b, width)
  }
}

export function pickLeafVariant(index, id = '') {
  if (id) {
    let h = 0
    for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0
    return LEAF_VARIANTS[h % LEAF_VARIANTS.length]
  }
  return LEAF_VARIANTS[index % LEAF_VARIANTS.length]
}

export function buildBarkTexture(trunkAt, trunkTangent) {
  const vertical = []
  const horizontal = []
  const knots = []

  for (let i = 0; i < 14; i++) {
    const t = 0.06 + (0.88 * i) / 13
    const p = trunkAt(t)
    const tan = trunkTangent(t)
    const len = Math.hypot(tan.x, tan.y) || 1
    const ux = tan.x / len
    const uy = tan.y / len
    const nx = -uy
    const ny = ux
    const half = 7 + (1 - t) * 12
    const side = i % 2 === 0 ? 1 : -1
    const jitter = ((i * 17) % 7) - 3

    vertical.push({
      d: [
        `M ${p.x + nx * (half * 0.12 * side + jitter * 0.4) - ux * 8} ${p.y + ny * (half * 0.12 * side + jitter * 0.4) - uy * 8}`,
        `Q ${p.x + nx * (half * 0.28 * side + jitter * 0.3)} ${p.y + ny * (half * 0.28 * side + jitter * 0.3)}`,
        `${p.x + nx * (half * 0.18 * side - jitter * 0.2) + ux * 10} ${p.y + ny * (half * 0.18 * side - jitter * 0.2) + uy * 10}`,
      ].join(' '),
      opacity: 0.18 + (i % 3) * 0.06,
    })

    for (const sign of [-1, 1]) {
      const ax = p.x + nx * half * sign * 0.62
      const ay = p.y + ny * half * sign * 0.62
      const bx = p.x + nx * half * sign * 0.38
      const by = p.y + ny * half * sign * 0.38
      horizontal.push({
        d: `M ${ax} ${ay} Q ${p.x + nx * half * sign * 0.78 + ux * 4} ${p.y + ny * half * sign * 0.78 + uy * 4} ${bx} ${by}`,
        opacity: 0.14 + (i % 4) * 0.04,
      })
    }
  }

  for (const t of [0.28, 0.55, 0.78]) {
    const p = trunkAt(t)
    knots.push({ cx: p.x + 4, cy: p.y, r: 2.2 + (1 - t) * 2, opacity: 0.2 })
  }

  return { vertical, horizontal, knots }
}
