// 论文作者串解析：兼容“|”“;”“,”分隔、空格分隔加单位角标与邮箱（知网格式）以及 (#)(*) 标记
const CJK=/[㐀-鿿]/
const EMAIL_TAIL=/[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\.?$/
function splitAuthors(raw){
 const s=String(raw||'').trim().replace(/[|;；,，\s]+$/,'')
 if(!s)return []
 if(s.includes('|'))return s.split('|')
 if(/[;；]/.test(s))return s.split(/[;；]/)
 if(CJK.test(s.replace(/\([^)]*\)|（[^）]*）/g,'')))return s.split(/\s+/)
 if(/\d|@/.test(s))return s.split(/(?<=\d|@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\.?)\s+/)
 if(s.includes(','))return s.split(',')
 return [s]
}
function parseOne(part){
 let t=String(part).trim(),corr=false,cofirst=false
 if(/\(\*\)|\*/.test(t)){corr=true;t=t.replace(/\(\*\)|\*/g,'')}
 if(/\(#\)/.test(t)){cofirst=true;t=t.replace(/\(#\)/g,'')}
 let email='',aff=''
 const at=t.indexOf('@')
 if(at>0){
  let i=at;while(i>0&&/[A-Za-z0-9._%+-]/.test(t[i-1]))i--
  let local=t.slice(i,at),pre=t.slice(0,i)
  const m=local.match(/^(\d{1,2})([A-Za-z_].*)$/)
  // 英文姓名与邮箱粘连：Wei5yusheng.wei@… / Dai6278206145@…
  const e1=!CJK.test(pre)&&local.match(/^([A-Za-z-]+)(\d{1,2}(?:,\d{1,2})*)([A-Za-z_].*)$/)
  const e2=!CJK.test(pre)&&local.match(/^([A-Za-z-]+)(\d+)$/)
  if(m){aff=m[1];local=m[2]}
  else if(e1){pre+=e1[1];aff=e1[2];local=e1[3]}
  else if(e2){pre+=e2[1];local=e2[2]}
  email=(local+t.slice(at)).replace(/\.$/,'')
  const pm=pre.match(/([\d,]+)$/);if(pm){aff=pm[1]+aff;pre=pre.slice(0,-pm[1].length)}
  t=pre
 }else{const m=t.match(/^(.*?\D)(\d{1,2}(?:,\d{1,2})*)$/);if(m){t=m[1];aff=m[2]}}
 const name=t.replace(/[\s.,，]+$/,'').trim()
 return name?{name,aff:aff.replace(/^,|,$/g,''),email,corr,cofirst}:null
}
export function parseAuthors(raw){return Array.isArray(raw)?raw.map(x=>parseOne(String(x))).filter(Boolean):splitAuthors(raw).map(parseOne).filter(Boolean)}
export const isEmail=s=>EMAIL_TAIL.test(s)
