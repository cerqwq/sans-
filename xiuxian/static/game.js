/**
 * 鬼谷修仙录 — 前端游戏逻辑
 * 墨雾山水主题
 */

const API = '/xiuxian/api';
let gameState = {
  character: null,
  combat: null,
  selectedElements: [],
  diceStats: null,
  gameData: null,
  combatCombo: 0,
  combatLastHitTime: 0,
};

// ============================================================
// 初始化
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initInkCanvas();
  initEventListeners();
  loadGameData();
  tryAutoLoad();
  initAmbientParticles();
});

function initEventListeners() {
  // 角色创建 — 灵根多选
  document.querySelectorAll('.element-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      gameState.selectedElements = Array.from(document.querySelectorAll('.element-btn.active')).map(b => b.dataset.element);
      updateCreationPreview();
      inkSplash(btn, getAccentColor(btn.dataset.element));
    });
  });

  // 骰子按钮
  document.getElementById('btnDice').addEventListener('click', rollDice);

  document.getElementById('btnCreate').addEventListener('click', createCharacter);
  document.getElementById('btnLoad').addEventListener('click', loadCharacter);

  // 游戏操作 — 印章按钮
  document.getElementById('btnCultivate').addEventListener('click', doCultivate);
  document.getElementById('btnExplore').addEventListener('click', doExplore);
  document.getElementById('btnBreakthrough').addEventListener('click', showBreakthrough);
  document.getElementById('btnAscend').addEventListener('click', doAscend);
  document.getElementById('btnInventory').addEventListener('click', showInventory);
  document.getElementById('btnNPC').addEventListener('click', showNPCList);
  document.getElementById('btnQuest').addEventListener('click', showQuests);
  document.getElementById('btnAchievement').addEventListener('click', showAchievements);
  document.getElementById('btnBestiary').addEventListener('click', showBestiary);
  document.getElementById('btnCraft').addEventListener('click', showCrafting);
  document.getElementById('btnMove').addEventListener('click', showMove);
  document.getElementById('btnRest').addEventListener('click', doRest);
  document.getElementById('btnSave').addEventListener('click', saveGame);
  document.getElementById('btnSettings').addEventListener('click', showSettings);
  document.getElementById('btnHelp').addEventListener('click', showHelp);

  // 移动端统计面板
  const mobileToggle = document.getElementById('mobileStatsToggle');
  const mobilePanel = document.getElementById('mobileStatsPanel');
  const mobileOverlay = document.getElementById('mobileStatsOverlay');
  if (mobileToggle && mobilePanel && mobileOverlay) {
    function closeMobileStats() {
      mobilePanel.classList.remove('open');
      mobileOverlay.classList.remove('open');
    }
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobilePanel.classList.contains('open');
      if (isOpen) closeMobileStats();
      else { mobilePanel.classList.add('open'); mobileOverlay.classList.add('open'); }
    });
    mobileOverlay.addEventListener('click', closeMobileStats);
    // 下滑关闭
    let touchStartY = 0;
    mobilePanel.addEventListener('touchstart', (e) => { touchStartY = e.touches[0].clientY; }, { passive: true });
    mobilePanel.addEventListener('touchmove', (e) => {
      const dy = e.touches[0].clientY - touchStartY;
      if (dy > 60) closeMobileStats();
    }, { passive: true });
  }

  // 印章按钮墨溅效果
  document.querySelectorAll('.seal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const color = getSealAccentColor(btn);
      inkSplash(btn, color);
    });
  });

  // 印章按钮音效反馈（视觉）
  document.querySelectorAll('.seal-btn').forEach(btn => {
    btn.addEventListener('mousedown', () => {
      btn.style.transition = 'transform 0.08s';
    });
    btn.addEventListener('mouseup', () => {
      btn.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
    });
  });

  // 键盘快捷键
  document.addEventListener('keydown', (e) => {
    // 忽略输入框内的按键
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    // 战斗中不响应快捷键
    if (document.getElementById('combatModal').style.display !== 'none') return;
    // 模态框打开时不响应
    if (document.querySelector('.modal.active')) return;

    const key = e.key.toLowerCase();
    const actions = {
      'c': () => document.getElementById('btnCultivate')?.click(),
      'e': () => document.getElementById('btnExplore')?.click(),
      'b': () => document.getElementById('btnBreakthrough')?.click(),
      'i': () => document.getElementById('btnInventory')?.click(),
      'r': () => document.getElementById('btnRest')?.click(),
      's': () => document.getElementById('btnSave')?.click(),
      'h': () => document.getElementById('btnHelp')?.click(),
    };
    if (actions[key]) {
      e.preventDefault();
      actions[key]();
    }
  });
}

function initAmbientParticles() {
  const container = document.getElementById('ambientParticles');
  if (!container) return;
  container.innerHTML = '';

  const types = ['mist', 'gold', 'jade'];
  for (let i = 0; i < 20; i++) {
    const p = document.createElement('div');
    p.className = `ambient-particle ${types[i % 3]}`;
    p.style.left = `${Math.random() * 100}%`;
    p.style.animationDelay = `${Math.random() * 8}s`;
    p.style.animationDuration = `${6 + Math.random() * 8}s`;
    container.appendChild(p);
  }
}

function getAccentColor(element) {
  const colors = {
    '金': '#a0a0b0', '木': '#5a8a50', '水': '#4a7ab0',
    '火': '#b84030', '土': '#8a7050'
  };
  return colors[element] || '#b8963e';
}

function getSealAccentColor(btn) {
  if (btn.classList.contains('cultivate')) return '#d4b060';
  if (btn.classList.contains('explore')) return '#7ec4b0';
  if (btn.classList.contains('breakthrough')) return '#a07ab0';
  if (btn.classList.contains('inventory')) return '#8a8a98';
  if (btn.classList.contains('npc')) return '#b8963e';
  if (btn.classList.contains('move')) return '#5a9e8f';
  if (btn.classList.contains('rest')) return '#6a6a78';
  return '#b8963e';
}

// 墨溅微交互
function inkSplash(el, color) {
  const rect = el.getBoundingClientRect();
  const splash = document.createElement('div');
  const size = Math.max(rect.width, rect.height) * 1.5;
  splash.style.cssText = `
    position: fixed;
    left: ${rect.left + rect.width / 2 - size / 2}px;
    top: ${rect.top + rect.height / 2 - size / 2}px;
    width: ${size}px;
    height: ${size}px;
    background: radial-gradient(circle, ${color}22, ${color}08 40%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 1000;
    animation: inkSplashAnim 0.6s ease-out forwards;
  `;
  document.body.appendChild(splash);
  setTimeout(() => splash.remove(), 600);
}

async function loadGameData() {
  try {
    const res = await fetch(`${API}/game_data`);
    const data = await res.json();
    if (data.success) gameState.gameData = data.data;
  } catch (e) {
    console.error('加载游戏数据失败:', e);
  }
}

async function tryAutoLoad() {
  try {
    const res = await fetch(`${API}/load_character`);
    const data = await res.json();
    if (data.success && data.character) {
      document.getElementById('btnLoad').style.display = 'block';
    }
  } catch (e) {}
}

// ============================================================
// 角色创建
// ============================================================
async function rollDice() {
  const btn = document.getElementById('btnDice');
  btn.disabled = true;
  btn.classList.add('rolling');

  const res = await fetch(`${API}/roll_dice`);
  const data = await res.json();

  if (data.success) {
    const { stats, elements } = data.result;
    gameState.diceStats = stats;

    // 更新属性预览
    document.getElementById('prevGengu').textContent = stats['根骨'];
    document.getElementById('prevWuxing').textContent = stats['悟性'];
    document.getElementById('prevQiyun').textContent = stats['气运'];
    document.getElementById('prevMeili').textContent = stats['魅力'];
    document.getElementById('prevTotal').textContent = Object.values(stats).reduce((a, b) => a + b, 0);

    // 更新灵根选择
    document.querySelectorAll('.element-btn').forEach(b => b.classList.remove('active'));
    gameState.selectedElements = elements;
    elements.forEach(e => {
      const el = document.querySelector(`.element-btn[data-element="${e}"]`);
      if (el) el.classList.add('active');
    });

    // 显示骰子结果
    const diceResult = document.getElementById('diceResult');
    diceResult.textContent = `灵根：${elements.join('·')}  属性：根${stats['根骨']} 悟${stats['悟性']} 气${stats['气运']} 魅${stats['魅力']}`;
    diceResult.classList.add('show');

    updateCreationPreview();
  }

  btn.disabled = false;
  btn.classList.remove('rolling');
}

async function createCharacter() {
  const name = document.getElementById('charName').value.trim();
  if (!name) {
    shakeInput(document.getElementById('charName'));
    return;
  }
  if (gameState.selectedElements.length === 0) {
    addLog('请至少选择一个灵根！', 'danger');
    return;
  }

  const btn = document.getElementById('btnCreate');
  btn.disabled = true;

  const payload = {
    name,
    elements: gameState.selectedElements,
  };
  if (gameState.diceStats) {
    payload.stats = gameState.diceStats;
  }

  const res = await apiPost('/create_character', payload);
  if (res.success) {
    gameState.character = res.character;
    document.querySelector('.creation-scroll').style.animation = 'scrollRoll 0.6s ease-in forwards';
    setTimeout(() => enterGame(), 500);
  } else {
    addLog(res.message, 'danger');
    btn.disabled = false;
  }
}

async function loadCharacter() {
  const res = await fetch(`${API}/load_character`);
  const data = await res.json();
  if (data.success) {
    gameState.character = data.character;
    enterGame();
  }
}

function enterGame() {
  document.getElementById('creationScreen').classList.remove('active');
  const gameScreen = document.getElementById('gameScreen');
  gameScreen.classList.add('active');
  gameScreen.style.animation = 'screenFadeIn 0.8s ease-out';
  updateUI();
  const c = gameState.character;
  const elems = Array.isArray(c.element) ? c.element : [c.element];
  addLog(`${c.name}，欢迎踏入修仙之路。`, 'welcome');
  addLog(`你是一名${elems.join('·')}灵根的练气修士，当前位于${c.location}。`, 'system');

  // 检查挂机修炼收益
  checkIdleCultivation();
}

async function checkIdleCultivation() {
  try {
    const res = await apiPost('/check_idle', { character: gameState.character });
    if (res.success && res.result && res.result.idle_gain > 0) {
      // 后端已修改 character 并保存，用返回的 summary 更新本地状态
      if (res.summary) {
        Object.assign(gameState.character, res.summary);
      }
      updateUI();
      addLog(res.result.message, 'success');
      if (res.result.can_breakthrough) {
        addLog('修为已满，可以尝试突破！', 'success');
      }
    }
  } catch (e) {
    // 静默失败，不影响游戏
  }
}

// ============================================================
// 创建界面预览
// ============================================================
// 五行关系常量（与后端同步）
const ELEMENT_GENERATING = { '金': '水', '水': '木', '木': '火', '火': '土', '土': '金' };
const ELEMENT_OVERCOMING = { '金': '木', '木': '土', '土': '水', '水': '火', '火': '金' };
const ELEMENT_PASSIVE = {
  '金': { atk_pct: 5 },
  '木': { hp_pct: 5 },
  '水': { mp_pct: 5 },
  '火': { hp_pct: 2.5, atk_pct: 2.5 },
  '土': { def_pct: 5 },
};

function computeElemBonuses(elements) {
  // 五灵根：五行齐聚，全属性+15%
  if (elements.length >= 5) {
    return { hp_pct: 15, mp_pct: 15, atk_pct: 15, def_pct: 15 };
  }
  const total = { hp_pct: 0, mp_pct: 0, atk_pct: 0, def_pct: 0 };
  elements.forEach(elem => {
    const base = { ...ELEMENT_PASSIVE[elem] };
    for (const other of elements) {
      if (other === elem) continue;
      if (ELEMENT_GENERATING[elem] === other) {
        for (const k in base) base[k] *= 2;
        break;
      }
      if (ELEMENT_OVERCOMING[elem] === other) {
        for (const k in base) base[k] *= 0.5;
        break;
      }
    }
    for (const k in total) total[k] += (base[k] || 0);
  });
  return total;
}

function updateCreationPreview() {
  const elems = gameState.selectedElements;
  const bonusList = document.getElementById('elemBonusList');

  if (elems.length === 0) {
    bonusList.innerHTML = '';
    return;
  }

  const bonuses = computeElemBonuses(elems);
  const labels = { hp_pct: '气血', mp_pct: '灵力', atk_pct: '攻击', def_pct: '防御' };
  let html = '';
  for (const [k, v] of Object.entries(bonuses)) {
    if (v > 0) {
      const isEnhanced = v > (ELEMENT_PASSIVE[elems[0]]?.[k] || 5);
      html += `<span class="bonus-tag${isEnhanced ? ' enhanced' : ''}">${labels[k]}+${v}%</span>`;
    }
  }

  // 检查相生/相克关系
  let relations = [];
  for (const e of elems) {
    for (const other of elems) {
      if (e === other) continue;
      if (ELEMENT_GENERATING[e] === other) relations.push(`${e}生${other}`);
      if (ELEMENT_OVERCOMING[e] === other) relations.push(`${e}克${other}`);
    }
  }
  if (relations.length > 0) {
    const hasSheng = relations.some(r => r.includes('生'));
    const hasKe = relations.some(r => r.includes('克'));
    html += `<span class="bonus-relation${hasSheng ? ' sheng' : ''}${hasKe ? ' ke' : ''}">${[...new Set(relations)].join(' ')}</span>`;
  }

  bonusList.innerHTML = html;
}

// ============================================================
// UI 更新
// ============================================================
function updateFromSummary(summary) {
  if (!summary || !gameState.character) return;
  const c = gameState.character;
  c.hp = summary.hp;
  c.max_hp = summary.max_hp;
  c.mp = summary.mp;
  c.max_mp = summary.max_mp;
  c.exp = summary.exp;
  c.exp_to_next = summary.exp_to_next;
  c.lifespan = summary.lifespan;
  c.age = summary.age;
  c.realm = summary.realm_full.replace(/初期|中期|后期|圆满/, '');
  c.attack = summary.attack;
  c.defense = summary.defense;
  if (summary.techniques) c.techniques = summary.techniques;
  if (summary.abilities) c.abilities = summary.abilities;
  if (summary.tech_bonuses) c.tech_bonuses = summary.tech_bonuses;
  if (summary.elem_bonuses) c.elem_bonuses = summary.elem_bonuses;
  if (summary.sword_uses !== undefined) c.sword_uses = summary.sword_uses;
  if (summary.sword_tier !== undefined) c.sword_tier = summary.sword_tier;
  if (summary.skills) c.skills = summary.skills;
  updateUI();
}

function updateUI() {
  const c = gameState.character;
  if (!c) return;

  // 状态栏
  const realmChar = c.realm.charAt(0);
  const realmIcon = document.getElementById('realmIcon');
  realmIcon.textContent = realmChar;
  document.getElementById('realmText').textContent = `${c.realm}${['初期','中期','后期','圆满'][c.stage]}`;

  // 突破提示脉冲
  if (c.exp >= c.exp_to_next) {
    realmIcon.classList.add('pulse');
  } else {
    realmIcon.classList.remove('pulse');
  }

  updateBar('hp', c.hp, c.max_hp);
  updateBar('mp', c.mp, c.max_mp);
  updateBar('exp', c.exp, c.exp_to_next);

  document.getElementById('lifespanValue').textContent = c.lifespan;
  document.getElementById('coinsValue').textContent = c.inventory['灵石'] || 0;
  document.getElementById('ageValue').textContent = `${c.age}岁`;

  // 属性
  document.getElementById('statGengu').textContent = c.stats.根骨;
  document.getElementById('statWuxing').textContent = c.stats.悟性;
  document.getElementById('statQiyun').textContent = c.stats.气运;
  document.getElementById('statMeili').textContent = c.stats.魅力;
  document.getElementById('statAttack').textContent = c.attack;
  document.getElementById('statDefense').textContent = c.defense;

  // 装备
  document.getElementById('equipWeapon').textContent = c.equipped.weapon || '无';
  document.getElementById('equipArmor').textContent = c.equipped.armor || '无';

  // 技能
  const skillList = document.getElementById('skillList');
  skillList.innerHTML = '';
  (c.skills || []).forEach(s => {
    const skillData = gameState.gameData?.skills?.[s];
    const elem = skillData?.element || '金';
    const tag = document.createElement('div');
    tag.className = 'skill-tag' + (skillData?.is_sword ? ' sword-skill' : '');
    tag.dataset.element = elem;
    if (skillData?.is_sword) {
      tag.textContent = `${s} [${skillData.sword_tier}重]`;
      tag.title = `使用次数: ${c.sword_uses || 0}，免费`;
    } else {
      tag.textContent = s;
      tag.title = skillData ? `伤害:${skillData.damage}+${skillData.atk_mult}x攻击 消耗:${skillData.cost}灵力` : '';
    }
    skillList.appendChild(tag);
  });

  // 灵根
  const elems = Array.isArray(c.element) ? c.element : [c.element];
  const elemNames = {'金': '金刚', '木': '长生', '水': '玄水', '火': '烈焰', '土': '厚土'};
  const elemGlyph = document.getElementById('elementGlyph');
  const elemName = document.getElementById('elementName');
  if (elemGlyph) elemGlyph.textContent = elems.length > 1 ? elems.map(e => e).join('') : elems[0];
  if (elemName) elemName.textContent = elems.map(e => elemNames[e] || e).join('·') + '灵根';

  // 功法
  const techList = document.getElementById('techniqueList');
  if (techList) {
    techList.innerHTML = '';
    (c.techniques || []).forEach(t => {
      const techData = gameState.gameData?.techniques?.[t];
      const tag = document.createElement('div');
      tag.className = 'technique-tag';
      tag.dataset.tier = techData?.tier || '黄级';
      tag.title = techData ? `气血+${techData.hp_pct}% 灵力+${techData.mp_pct}% 攻击+${techData.atk_pct}% 防御+${techData.def_pct}%` : '';
      tag.textContent = t;
      techList.appendChild(tag);
    });
    if (!c.techniques || c.techniques.length === 0) {
      techList.innerHTML = '<div class="empty-hint">尚未领悟功法</div>';
    }
  }

  // 神通
  const abilList = document.getElementById('abilityList');
  if (abilList) {
    abilList.innerHTML = '';
    (c.abilities || []).forEach(a => {
      const abilData = gameState.gameData?.abilities?.[a];
      const tag = document.createElement('div');
      tag.className = 'ability-tag';
      tag.dataset.tier = abilData?.tier || '黄级';
      tag.title = abilData ? (abilData.base_damage > 0 ? `伤害:${abilData.base_damage}+${abilData.atk_mult}x攻击 消耗:${abilData.cost}灵力` : `回复:${Math.abs(abilData.base_damage)}生命 消耗:${abilData.cost}灵力`) : '';
      tag.textContent = a;
      abilList.appendChild(tag);
    });
    if (!c.abilities || c.abilities.length === 0) {
      abilList.innerHTML = '<div class="empty-hint">尚未领悟神通</div>';
    }
  }

  // 位置
  document.getElementById('locationName').textContent = c.location;
  const region = gameState.gameData?.regions?.[c.location];
  document.getElementById('locationDesc').textContent = region?.desc || '';

  // 战绩统计
  document.getElementById('statKills').textContent = c.kills || 0;
  document.getElementById('statExplores').textContent = c.stats?.explore_count || 0;
  document.getElementById('statCultivates').textContent = c.stats?.cultivate_count || 0;
  document.getElementById('statAchievements').textContent = (c.achievements || []).length;

  // 地图背景切换
  drawRegionBackground(c.location);

  // 突破按钮
  const btnBT = document.getElementById('btnBreakthrough');
  if (c.exp >= c.exp_to_next) {
    btnBT.style.display = 'flex';
    btnBT.classList.add('pulse');
  } else {
    btnBT.style.display = 'none';
    btnBT.classList.remove('pulse');
  }

  // 飞升按钮（渡劫圆满 + 有渡劫丹 + 修为满）
  const btnAscend = document.getElementById('btnAscend');
  const isDujieMax = c.realm === '渡劫' && c.stage >= 3;
  const hasDujieDan = (c.inventory || {})['渡劫丹'] > 0;
  const expFull = c.exp >= c.exp_to_next;
  if (isDujieMax && hasDujieDan && expFull) {
    btnAscend.style.display = 'flex';
    btnAscend.classList.add('pulse');
  } else {
    btnAscend.style.display = 'none';
    btnAscend.classList.remove('pulse');
  }

  // 移动端统计面板同步
  const mElemName = document.getElementById('mElementName');
  if (mElemName) {
    mElemName.textContent = elems.map(e => elemNames[e] || e).join('·');
    document.getElementById('mStatGengu').textContent = c.stats.根骨;
    document.getElementById('mStatWuxing').textContent = c.stats.悟性;
    document.getElementById('mStatQiyun').textContent = c.stats.气运;
    document.getElementById('mStatMeili').textContent = c.stats.魅力;
    document.getElementById('mStatAttack').textContent = c.attack;
    document.getElementById('mStatDefense').textContent = c.defense;
    document.getElementById('mEquipWeapon').textContent = c.equipped.weapon || '无';
    document.getElementById('mEquipArmor').textContent = c.equipped.armor || '无';
    document.getElementById('mStatKills').textContent = c.kills || 0;
    document.getElementById('mStatExplores').textContent = c.stats?.explore_count || 0;
    document.getElementById('mStatCultivates').textContent = c.stats?.cultivate_count || 0;
    document.getElementById('mStatAchievements').textContent = (c.achievements || []).length;

    const mSkillList = document.getElementById('mSkillList');
    mSkillList.innerHTML = '';
    (c.skills || []).forEach(s => {
      const tag = document.createElement('span');
      tag.className = 'mobile-skill-tag';
      tag.textContent = s;
      mSkillList.appendChild(tag);
    });
    if (!c.skills || c.skills.length === 0) {
      mSkillList.innerHTML = '<span class="empty-hint">暂无技能</span>';
    }
  }
}

function updateBar(type, current, max) {
  const pct = Math.min(100, Math.max(0, (current / max) * 100));
  document.getElementById(`${type}Bar`).style.width = `${pct}%`;
  document.getElementById(`${type}Value`).textContent = `${current}/${max}`;
}

function flashBar(type) {
  const bar = document.getElementById(`${type}Bar`);
  if (!bar) return;
  bar.style.filter = 'brightness(1.8)';
  setTimeout(() => { bar.style.filter = 'brightness(1.3)'; }, 200);
  setTimeout(() => { bar.style.filter = ''; }, 500);
}

// ============================================================
// 游戏操作
// ============================================================
async function doCultivate() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  disableActions(true);
  const cultivateBtn = document.getElementById('btnCultivate');
  cultivateBtn.classList.add('cultivating');

  // 超时保护：15秒后自动恢复按钮
  const safetyTimer = setTimeout(() => {
    cultivateBtn.classList.remove('cultivating');
    disableActions(false);
    console.warn('[cultivate] safety timeout triggered');
  }, 15000);

  try {
    const res = await apiPost('/cultivate', { character: gameState.character });
    if (res.success) {
      addLog(`打坐修炼，感悟天地之道，修为增加 ${res.result.exp_gain}。`, 'success');
      if (res.result.can_breakthrough) {
        addLog('修为已满，可以尝试突破境界！', 'event');
      }
      if (res.result.lifespan_cost) {
        addLog(`岁月流转，寿元减少 ${res.result.lifespan_cost}。`, 'system');
      }
      if (res.summary) updateFromSummary(res.summary);
      // 进度条变化高亮
      flashBar('exp');
      await reloadCharacter();
      checkAchievementsAfterAction();
    } else {
      addLog(res.message || '修炼失败', 'danger');
    }
  } catch (e) {
    console.error('[cultivate]', e);
    addLog('修炼出错', 'danger');
  }

  clearTimeout(safetyTimer);
  cultivateBtn.classList.remove('cultivating');
  disableActions(false);
}

async function doAscend() {
  if (!gameState.character) return;
  const c = gameState.character;

  // 确认对话框
  const confirmed = confirm('飞升仙界？需要消耗一枚渡劫丹，失败将重伤。确定尝试？');
  if (!confirmed) return;

  disableActions(true);
  try {
    const res = await apiPost('/ascend', { character: gameState.character });
    if (res.success) {
      const r = res.result;
      if (r.success) {
        addLog(r.message, 'success');
        addLog(`飞升成功率：${r.rate}%`, 'system');
        // 飞升特效
        triggerAchievementFlash();
        if (typeof playSfx === 'function') playSfx('victory');
      } else {
        addLog(r.message, 'danger');
      }
      if (res.summary) Object.assign(gameState.character, res.summary);
      updateUI();
    } else {
      addLog(res.message || '飞升失败', 'danger');
    }
  } catch (e) {
    console.error('[ascend]', e);
    addLog('飞升出错', 'danger');
  }
  disableActions(false);
}

async function doExplore() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  disableActions(true);

  const safetyTimer = setTimeout(() => disableActions(false), 15000);

  try {
    const res = await apiPost('/explore', { character: gameState.character });
    if (res.success) {
      const r = res.result;
      if (r.type === 'combat') {
        addLog(r.message, 'danger');
        startCombat(r.enemy);
      } else if (r.type === 'event') {
        addLog(r.message, 'event');
        if (r.reward) {
          const items = Object.entries(r.reward).map(([k,v]) => `${k}×${v}`).join('、');
          addLog(`获得：${items}`, 'success');
        }
        if (r.stat_boost) {
          const boosts = Object.entries(r.stat_boost).map(([k,v]) => `${k}+${v}`).join('、');
          addLog(`属性提升：${boosts}`, 'success');
        }
        if (r.technique_found) {
          addLog(`领悟功法：${r.technique_found}`, 'success');
        }
        if (r.ability_found) {
          addLog(`领悟神通：${r.ability_found}`, 'success');
        }
      } else if (r.type === 'npc') {
        addLog(r.message, 'event');
        showNPCDialog(r.npc);
      } else if (r.type === 'chain_start') {
        addLog(r.message, 'event');
        showToast(`探索链开始：${r.chain}`, 'event', 5000);
      } else if (r.type === 'chain') {
        addLog(r.message, 'event');
        if (r.reward) {
          const items = Object.entries(r.reward).map(([k,v]) => `${k}×${v}`).join('、');
          addLog(`获得：${items}`, 'success');
        }
        if (r.stat_boost) {
          const boosts = Object.entries(r.stat_boost).map(([k,v]) => `${k}+${v}`).join('、');
          addLog(`属性提升：${boosts}`, 'success');
        }
        if (r.ability_found) {
          addLog(`领悟神通：${r.ability_found}`, 'success');
        }
      } else {
        addLog(r.message, 'success');
      }
      if (res.summary) updateFromSummary(res.summary);
      await reloadCharacter();
      checkAchievementsAfterAction();
    } else {
      addLog(res.message || '探索失败', 'danger');
    }
  } catch (e) {
    console.error('[explore]', e);
    addLog('探索出错', 'danger');
  }

  clearTimeout(safetyTimer);
  disableActions(false);
}

// ============================================================
// 成就检查
// ============================================================
async function checkAchievementsAfterAction() {
  if (!gameState.character) return;
  try {
    const res = await apiPost('/check_achievements', { character: gameState.character });
    if (res.success && res.new_achievements && res.new_achievements.length > 0) {
      res.new_achievements.forEach(ach => {
        showToast(`成就解锁：${ach}`, 'success', 5000);
        addLog(`成就解锁：${ach}`, 'success');
      });
      // 成就解锁闪光效果
      triggerAchievementFlash();
      if (res.summary) updateFromSummary(res.summary);
      await reloadCharacter();
    }
  } catch (e) {
    // 静默失败，不影响游戏体验
  }
}

async function doExploreChoice(choice) {
  if (!gameState.character) return;
  disableActions(true);

  try {
    const res = await apiPost('/explore_choice', {
      character: gameState.character,
      choice: choice,
    });
    if (res.success) {
      addLog(res.result.message, 'event');
      if (res.result.reward) {
        const items = Object.entries(res.result.reward).map(([k,v]) => `${k}×${v}`).join('、');
        addLog(`获得：${items}`, 'success');
      }
      if (res.result.stat_boost) {
        const boosts = Object.entries(res.result.stat_boost).map(([k,v]) => `${k}+${v}`).join('、');
        addLog(`属性提升：${boosts}`, 'success');
      }
      if (res.summary) updateFromSummary(res.summary);
      await reloadCharacter();
      checkAchievementsAfterAction();
    } else {
      addLog(res.message || '选择失败', 'danger');
    }
  } catch (e) {
    console.error('[explore_choice]', e);
    addLog('选择出错', 'danger');
  }

  disableActions(false);
}

function showBreakthrough() {
  const c = gameState.character;
  if (!c || c.exp < c.exp_to_next) return;

  const modal = document.getElementById('breakthroughModal');
  const info = document.getElementById('breakthroughInfo');
  const itemsDiv = document.getElementById('breakthroughItems');

  info.innerHTML = `
    <div class="current-realm">${c.realm}${['初期','中期','后期','圆满'][c.stage]}</div>
    <div class="success-rate">基础成功率：${getBreakthroughRate(c)}%</div>
  `;

  itemsDiv.innerHTML = '';
  const breakthroughItems = ['筑基丹', '金丹丹', '元婴丹', '化神丹', '破境丹'];
  breakthroughItems.forEach(item => {
    const count = c.inventory[item] || 0;
    if (count > 0) {
      const btn = document.createElement('div');
      btn.className = 'breakthrough-item available';
      btn.textContent = `${item} ×${count}`;
      btn.dataset.item = item;
      btn.addEventListener('click', () => btn.classList.toggle('selected'));
      itemsDiv.appendChild(btn);
    }
  });

  document.getElementById('btnDoBreakthrough').onclick = doBreakthrough;
  modal.classList.add('active');
}

function getBreakthroughRate(c) {
  const rates = { '练气': 80, '筑基': 60, '结丹': 40, '元婴': 25, '化神': 15 };
  return rates[c.realm] || 50;
}

async function doBreakthrough() {
  const selectedItems = [];
  document.querySelectorAll('.breakthrough-item.selected').forEach(el => {
    selectedItems.push(el.dataset.item);
  });

  closeModal('breakthroughModal');
  const res = await apiPost('/breakthrough', {
    character: gameState.character,
    use_items: selectedItems
  });

  if (res.success) {
    const r = res.result;
    if (r.success) {
      addLog(`${r.message}`, 'success');
      playBreakthroughEffect();
    } else {
      addLog(`${r.message}`, 'danger');
    }
    await reloadCharacter();
  }
}

function showInventory() {
  const c = gameState.character;
  if (!c) return;

  const grid = document.getElementById('inventoryGrid');
  grid.innerHTML = '';

  Object.entries(c.inventory).forEach(([name, count]) => {
    if (count <= 0) return;
    const itemData = gameState.gameData?.items?.[name] || {};
    const isEquipped = (c.equipped.weapon === name || c.equipped.armor === name);

    const div = document.createElement('div');
    div.className = `inventory-item${isEquipped ? ' equipped' : ''}`;
    div.innerHTML = `
      <div class="item-name">${name}</div>
      <div class="item-count">×${count}</div>
      <div class="item-desc">${itemData.desc || ''}</div>
    `;
    div.addEventListener('click', () => useItem(name));
    grid.appendChild(div);
  });

  document.getElementById('inventoryModal').classList.add('active');
}

async function useItem(name) {
  const res = await apiPost('/use_item', { character: gameState.character, item: name });
  if (res.success) {
    addLog(res.result.message, res.result.success ? 'success' : 'warning');
    // Use summary for immediate UI feedback
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    showInventory();
  }
}

// ============================================================
// 帮助系统
// ============================================================
function showHelp() {
  document.getElementById('helpModal').classList.add('active');
}

// ============================================================
// 设置系统
// ============================================================
function showSettings() {
  // 加载保存的设置
  const settings = loadSettings();

  // 设置控件值
  document.getElementById('animSpeed').value = settings.animSpeed;
  document.getElementById('animSpeedValue').textContent = settings.animSpeed + 'x';
  document.getElementById('fontSize').value = settings.fontSize;
  document.getElementById('fontSizeValue').textContent = settings.fontSize + 'px';
  document.getElementById('autoSave').checked = settings.autoSave;
  document.getElementById('showTutorial').checked = settings.showTutorial;

  // 添加事件监听器
  document.getElementById('animSpeed').oninput = function() {
    document.getElementById('animSpeedValue').textContent = this.value + 'x';
    saveSettings({ animSpeed: parseFloat(this.value) });
  };

  document.getElementById('fontSize').oninput = function() {
    document.getElementById('fontSizeValue').textContent = this.value + 'px';
    saveSettings({ fontSize: parseInt(this.value) });
    document.documentElement.style.setProperty('--font-size-base', this.value + 'px');
  };

  document.getElementById('autoSave').onchange = function() {
    saveSettings({ autoSave: this.checked });
  };

  document.getElementById('showTutorial').onchange = function() {
    saveSettings({ showTutorial: this.checked });
    if (this.checked) {
      localStorage.removeItem('xiuxian_tutorial_done');
    } else {
      localStorage.setItem('xiuxian_tutorial_done', '1');
    }
  };

  // 存档管理按钮
  document.getElementById('btnExportSave').onclick = exportSave;
  document.getElementById('btnImportSave').onclick = importSave;
  document.getElementById('btnDeleteSave').onclick = deleteSave;
  document.getElementById('btnRebirth').onclick = doRebirth;

  document.getElementById('settingsModal').classList.add('active');
}

function loadSettings() {
  const defaults = {
    animSpeed: 1,
    fontSize: 14,
    autoSave: true,
    showTutorial: true,
  };

  try {
    const saved = localStorage.getItem('xiuxian_settings');
    if (saved) {
      return { ...defaults, ...JSON.parse(saved) };
    }
  } catch (e) {
    console.error('Failed to load settings:', e);
  }

  return defaults;
}

function saveSettings(newSettings) {
  try {
    const current = loadSettings();
    const updated = { ...current, ...newSettings };
    localStorage.setItem('xiuxian_settings', JSON.stringify(updated));
  } catch (e) {
    console.error('Failed to save settings:', e);
  }
}

function exportSave() {
  if (!gameState.character) {
    showToast('没有存档可导出', 'danger');
    return;
  }

  const saveData = JSON.stringify(gameState.character, null, 2);
  const blob = new Blob([saveData], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `xiuxian_save_${gameState.character.name}_${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast('存档已导出', 'success');
}

function importSave() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';

  input.onchange = async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = JSON.parse(text);

      // 验证存档数据
      if (!data.name || !data.realm) {
        showToast('无效的存档文件', 'danger');
        return;
      }

      // 保存到服务器
      const res = await apiPost('/save_character', { character: data });
      if (res.success) {
        gameState.character = data;
        updateUI();
        showToast('存档已导入', 'success');
        closeModal('settingsModal');
      } else {
        showToast('导入失败: ' + (res.message || '未知错误'), 'danger');
      }
    } catch (err) {
      showToast('导入失败: 文件格式错误', 'danger');
    }
  };

  input.click();
}

async function deleteSave() {
  if (!confirm('确定要删除存档吗？此操作不可撤销！')) {
    return;
  }

  const res = await apiPost('/delete_character', {});
  if (res.success) {
    gameState.character = null;
    document.getElementById('gameScreen').classList.remove('active');
    document.getElementById('creationScreen').classList.add('active');
    showToast('存档已删除', 'success');
    closeModal('settingsModal');
  } else {
    showToast('删除失败: ' + (res.message || '未知错误'), 'danger');
  }
}

async function doRebirth() {
  const c = gameState.character;
  if (!c) return;

  if (c.realm_level < 2) {
    showToast('需达到筑基期以上方可转世重生！', 'warning');
    return;
  }

  const confirmMsg = `确定要转世重生吗？\n\n将保留：\n- 所有成就 (${(c.achievements || []).length}个)\n- 怪物图鉴\n- NPC关系（减半）\n\n将重置：\n- 境界回到练气初期\n- 技能、功法、神通\n- 背包物品\n\n基于当前进度，预计获得 ${c.realm_level * 10 + (c.achievements || []).length * 3 + Math.floor((c.kills || 0) / 10)} 转世点数。`;

  if (!confirm(confirmMsg)) return;

  const res = await apiPost('/rebirth', { character: c });
  if (res.success) {
    gameState.character = res.character;
    updateUI();
    closeModal('settingsModal');

    const rp = res.result.rebirth_points;
    showToast(`转世重生成功！获得 ${rp} 转世点数`, 'success');

    // 全屏特效
    playBreakthroughEffect('转世重生');

    addLog(`══════ 转世重生 ══════`);
    addLog(`你选择了转世重生，保留前世记忆重新修炼。`);
    addLog(`获得 ${rp} 转世点数，永久提升基础属性。`);
    addLog(`获得 ${rp * 10} 灵石作为启动资金。`);
    addLog(`══════════════════════`);
  } else {
    showToast(res.message || '转世失败', 'danger');
  }
}

// ============================================================
// 任务系统
// ============================================================
function showQuests() {
  const c = gameState.character;
  if (!c) return;

  const region = gameState.gameData?.regions?.[c.location];
  const npcs = region?.npc || [];

  // 获取当前区域NPC的可用任务
  const availableQuests = [];
  npcs.forEach(npcName => {
    const npcQuests = gameState.gameData?.npcs?.[npcName]?.quests || [];
    npcQuests.forEach(quest => {
      const questId = `${npcName}_${quest.name}`;
      const isActive = (c.active_quests || []).some(q => q.id === questId);
      const isCompleted = (c.completed_quests || []).includes(questId);
      if (!isActive && !isCompleted) {
        availableQuests.push({ ...quest, id: questId, npc: npcName });
      }
    });
  });

  const activeQuests = c.active_quests || [];

  const questList = document.getElementById('questList');
  questList.innerHTML = '';

  // 显示进行中的任务
  if (activeQuests.length > 0) {
    const section = document.createElement('div');
    section.className = 'quest-section';
    section.innerHTML = '<h4 class="quest-section-title">进行中</h4>';

    activeQuests.forEach(quest => {
      const div = document.createElement('div');
      div.className = 'quest-item active';
      const progress = quest.progress || 0;
      const count = quest.count || 1;
      const isComplete = progress >= count;

      div.innerHTML = `
        <div class="quest-header">
          <span class="quest-name">${quest.name}</span>
          <span class="quest-npc">${quest.npc}</span>
        </div>
        <div class="quest-desc">${quest.desc}</div>
        <div class="quest-progress">
          <div class="quest-progress-bar">
            <div class="quest-progress-fill" style="width: ${(progress / count) * 100}%"></div>
          </div>
          <span class="quest-progress-text">${progress}/${count}</span>
        </div>
        ${isComplete ? '<button class="quest-complete-btn" data-quest-id="' + quest.id + '">领取奖励</button>' : ''}
      `;

      if (isComplete) {
        const btn = div.querySelector('.quest-complete-btn');
        btn.addEventListener('click', () => completeQuest(quest.id));
      }

      section.appendChild(div);
    });

    questList.appendChild(section);
  }

  // 显示可接取的任务
  if (availableQuests.length > 0) {
    const section = document.createElement('div');
    section.className = 'quest-section';
    section.innerHTML = '<h4 class="quest-section-title">可接取</h4>';

    availableQuests.forEach(quest => {
      const div = document.createElement('div');
      div.className = 'quest-item available';

      let rewardText = '';
      if (quest.reward) {
        rewardText = Object.entries(quest.reward).map(([item, count]) => `${item}×${count}`).join('、');
      }

      div.innerHTML = `
        <div class="quest-header">
          <span class="quest-name">${quest.name}</span>
          <span class="quest-npc">${quest.npc}</span>
        </div>
        <div class="quest-desc">${quest.desc}</div>
        <div class="quest-reward">奖励: ${rewardText}</div>
        <button class="quest-accept-btn" data-quest-id="${quest.id}">接取任务</button>
      `;

      const btn = div.querySelector('.quest-accept-btn');
      btn.addEventListener('click', () => acceptQuestAction(quest.id));

      section.appendChild(div);
    });

    questList.appendChild(section);
  }

  // 没有任务时显示提示
  if (activeQuests.length === 0 && availableQuests.length === 0) {
    questList.innerHTML = '<div class="quest-empty">当前区域没有可用任务。尝试与其他区域的NPC交谈获取任务。</div>';
  }

  // 设置标签切换
  const tabs = document.querySelectorAll('.quest-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      // 这里可以添加标签切换逻辑
    });
  });

  document.getElementById('questModal').classList.add('active');
}

async function acceptQuestAction(questId) {
  const res = await apiPost('/accept_quest', { character: gameState.character, quest_id: questId });
  if (res.success) {
    addLog(res.result.message, 'success');
    showToast(res.result.message, 'success');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    showQuests();
  } else {
    showToast(res.message || '接取失败', 'danger');
  }
}

async function completeQuest(questId) {
  const res = await apiPost('/complete_quest', { character: gameState.character, quest_id: questId });
  if (res.success) {
    addLog(res.result.message, 'success');
    showToast(res.result.message, 'success');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    showQuests();
  } else {
    showToast(res.message || '完成失败', 'danger');
  }
}

// ============================================================
// 成就系统
// ============================================================
function showAchievements() {
  const c = gameState.character;
  if (!c) return;

  // 从服务器获取成就数据
  apiPost('/get_achievements', { character: c }).then(res => {
    if (!res.success) return;

    const grid = document.getElementById('achievementGrid');
    grid.innerHTML = '';

    const achievements = res.achievements || [];
    const completedCount = achievements.filter(a => a.completed).length;

    // 显示成就统计
    const statsDiv = document.createElement('div');
    statsDiv.className = 'achievement-stats';
    statsDiv.innerHTML = `<span>已解锁: ${completedCount}/${achievements.length}</span>`;
    grid.appendChild(statsDiv);

    // 显示成就列表
    achievements.forEach(ach => {
      const div = document.createElement('div');
      div.className = `achievement-item ${ach.completed ? 'completed' : 'locked'}`;

      let rewardText = '';
      if (ach.reward) {
        rewardText = Object.entries(ach.reward).map(([item, count]) => `${item}×${count}`).join('、');
      }

      div.innerHTML = `
        <div class="achievement-icon">${ach.completed ? '成' : '锁'}</div>
        <div class="achievement-info">
          <div class="achievement-name">${ach.id}</div>
          <div class="achievement-desc">${ach.desc}</div>
          <div class="achievement-reward">奖励: ${rewardText}</div>
        </div>
      `;

      grid.appendChild(div);
    });

    document.getElementById('achievementModal').classList.add('active');
  });
}

// ============================================================
// 怪物图鉴
// ============================================================
function showBestiary() {
  const c = gameState.character;
  if (!c) return;

  const encountered = c.stats?.monsters_encountered || [];
  const grid = document.getElementById('bestiaryGrid');
  grid.innerHTML = '';

  // 统计
  const statsDiv = document.createElement('div');
  statsDiv.style.cssText = 'grid-column:1/-1;text-align:center;font-size:13px;color:var(--text-muted);padding:8px 0;font-family:var(--font-display);letter-spacing:2px;';
  statsDiv.textContent = `已收录: ${encountered.length}/${Object.keys(gameState.gameData?.monsters || {}).length}`;
  grid.appendChild(statsDiv);

  // 获取怪物数据
  const monsters = gameState.gameData?.monsters || {};

  // 怪物图标映射
  const monsterIcons = {
    '野狼': '狼', '灵蛇': '蛇', '石傀儡': '傀', '火焰妖': '焰',
    '水鬼': '鬼', '树妖': '树', '雷兽': '雷', '玄冰蛟': '蛟',
    '金甲虫': '虫', '毒蝎': '蝎', '岩魔': '岩', '冰霜巨狼': '狼',
    '幽魂': '魂', '天机傀儡': '机',
    // 新增怪物
    '野猪': '猪', '山贼': '贼', '竹精': '竹', '蜂群': '蜂',
    '熔岩蜥蜴': '蜥', '火鸦': '鸦', '怨灵': '怨', '蛟龙': '龙',
    '机关兽': '兽', '傀儡将军': '将', '五行灵蝶': '蝶', '噬魂蝠王': '蝠',
    '九尾妖狐': '狐', '上古石魔': '魔',
  };

  Object.entries(monsters).forEach(([name, data]) => {
    const isEncountered = encountered.includes(name);
    const div = document.createElement('div');
    div.className = `bestiary-item ${isEncountered ? 'encountered' : 'unknown'}`;

    if (isEncountered) {
      div.innerHTML = `
        <div class="bestiary-icon">${monsterIcons[name] || '怪'}</div>
        <div class="bestiary-info">
          <div class="bestiary-name">${name}<span class="bestiary-element" data-element="${data.element}">${data.element}</span></div>
          <div class="bestiary-stats">
            <span class="bs-item"><span class="bs-label">气血</span>${data.hp}</span>
            <span class="bs-item"><span class="bs-label">攻击</span>${data.damage || data.attack}</span>
            <span class="bs-item"><span class="bs-label">防御</span>${data.defense}</span>
            <span class="bs-item"><span class="bs-label">经验</span>${data.exp}</span>
          </div>
        </div>
      `;
    } else {
      div.innerHTML = `
        <div class="bestiary-icon">?</div>
        <div class="bestiary-info">
          <div class="bestiary-name">???</div>
          <div class="bestiary-stats"><span class="bs-item">尚未遭遇</span></div>
        </div>
      `;
    }

    grid.appendChild(div);
  });

  document.getElementById('bestiaryModal').classList.add('active');
}

// ============================================================
// 炼丹系统
// ============================================================
function showCrafting() {
  const c = gameState.character;
  if (!c) return;

  apiPost('/get_recipes', { character: c }).then(res => {
    if (!res.success) return;

    const list = document.getElementById('craftList');
    list.innerHTML = '';

    let currentFilter = 'all';

    function renderRecipes(filter) {
      list.innerHTML = '';
      const recipes = res.recipes || [];
      const filtered = filter === 'all' ? recipes : recipes.filter(r => r.type === filter);

      if (filtered.length === 0) {
        list.innerHTML = '<div class="empty-hint">暂无可用配方</div>';
        return;
      }

      filtered.forEach(recipe => {
        const div = document.createElement('div');
        div.className = `craft-item ${recipe.can_craft ? 'available' : 'unavailable'}`;

        const typeLabel = {consumable: '丹药', weapon: '法器', armor: '护甲'}[recipe.type] || '物品';

        let materialsHtml = '';
        Object.entries(recipe.materials).forEach(([mat, count]) => {
          const has = (mat === '灵石') ? (c.inventory?.灵石 || 0) >= count : (c.inventory?.[mat] || 0) >= count;
          const current = (mat === '灵石') ? (c.inventory?.灵石 || 0) : (c.inventory?.[mat] || 0);
          materialsHtml += `<span class="craft-material ${has ? 'has' : 'missing'}">${mat} ${current}/${count}</span>`;
        });

        div.innerHTML = `
          <div class="craft-item-header">
            <span class="craft-item-name">${recipe.name}</span>
            <span class="craft-item-type">${typeLabel}</span>
          </div>
          <div class="craft-item-desc">${recipe.desc}</div>
          <div class="craft-materials">${materialsHtml}</div>
          <button class="craft-btn" ${recipe.can_craft ? '' : 'disabled'} onclick="doCraft('${recipe.name}')">
            ${recipe.can_craft ? '炼制' : '材料不足'}
          </button>
        `;

        list.appendChild(div);
      });
    }

    // Tab切换
    document.querySelectorAll('.craft-tab').forEach(tab => {
      tab.onclick = () => {
        document.querySelectorAll('.craft-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentFilter = tab.dataset.tab;
        renderRecipes(currentFilter);
      };
    });

    renderRecipes('all');
    document.getElementById('craftModal').classList.add('active');
  });
}

window.doCraft = async function(recipeName) {
  const c = gameState.character;
  if (!c) return;

  const res = await apiPost('/craft', { character: c, recipe: recipeName });
  if (res.success) {
    gameState.character = { ...c, ...res.summary };
    // 同步完整数据
    const fullRes = await apiPost('/load_character', {});
    if (fullRes.success) gameState.character = fullRes.character;

    updateUI();
    showToast(res.result.message, 'success');
    addLog(res.result.message, 'reward');
    // 重新打开刷新列表
    showCrafting();
  } else {
    showToast(res.message || '炼制失败', 'danger');
  }
}

function showNPCList() {
  const c = gameState.character;
  if (!c) return;

  const region = gameState.gameData?.regions?.[c.location];
  const npcs = region?.npc || [];

  if (npcs.length === 0) {
    addLog('这里没有可以交流的人。', 'system');
    return;
  }

  if (npcs.length === 1) {
    showNPCDialog(npcs[0]);
  } else {
    const modal = document.getElementById('npcModal');
    document.getElementById('npcModalTitle').textContent = '附近的人';
    const dialogue = document.getElementById('npcDialogue');
    const shop = document.getElementById('npcShop');

    dialogue.innerHTML = '';
    shop.innerHTML = '';

    npcs.forEach(npcName => {
      const npcData = gameState.gameData?.npcs?.[npcName];
      const div = document.createElement('div');
      div.className = 'shop-item';
      div.innerHTML = `
        <span class="shop-name">${npcName}（${npcData?.title || ''}）</span>
        <span class="shop-price">对话</span>
      `;
      div.addEventListener('click', () => showNPCDialog(npcName));
      shop.appendChild(div);
    });

    modal.classList.add('active');
  }
}

async function showNPCDialog(npcName) {
  const res = await apiPost('/npc', { character: gameState.character, npc: npcName });
  if (!res.success) return;

  const r = res.result;
  const modal = document.getElementById('npcModal');
  document.getElementById('npcModalTitle').textContent = npcName;

  const dialogue = document.getElementById('npcDialogue');
  dialogue.innerHTML = `
    <div class="npc-name">${npcName}（${r.title}）</div>
    <div>"${r.dialogue}"</div>
    <div style="margin-top:8px;font-size:12px;color:var(--text-dim);">好感度：${r.relation}</div>
  `;

  const shop = document.getElementById('npcShop');
  shop.innerHTML = '';

  if (r.shop && r.shop.length > 0) {
    r.shop.forEach(item => {
      const itemData = gameState.gameData?.items?.[item] || {};
      const price = itemData.price || 10;
      const div = document.createElement('div');
      div.className = 'shop-item';
      div.innerHTML = `
        <span class="shop-name">${item}（${itemData.desc || ''}）</span>
        <span class="shop-price">灵石 ${price}</span>
      `;
      div.addEventListener('click', () => buyItem(npcName, item));
      shop.appendChild(div);
    });
  }

  // 功法商店
  if (r.technique_shop && r.technique_shop.length > 0) {
    const header = document.createElement('div');
    header.className = 'shop-header';
    header.textContent = '— 功法 —';
    shop.appendChild(header);

    const charElemsTech = Array.isArray(gameState.character?.element) ? gameState.character.element : [gameState.character?.element];
    r.technique_shop.forEach(t => {
      const techData = gameState.gameData?.techniques?.[t] || {};
      const price = techData.price || 0;
      const isLearned = (gameState.character?.techniques || []).includes(t);
      const isLocked = !charElemsTech.includes(techData.element);
      const div = document.createElement('div');
      div.className = `shop-item${isLearned ? ' learned' : ''}${isLocked ? ' locked' : ''}`;
      div.innerHTML = `
        <span class="shop-name">${t}（${techData.desc || ''}）</span>
        <span class="shop-detail">气血+${techData.hp_pct||0}% 灵力+${techData.mp_pct||0}% 攻击+${techData.atk_pct||0}% 防御+${techData.def_pct||0}%</span>
        <span class="shop-price">${isLearned ? '已学会' : isLocked ? `需要${techData.element}灵根` : `灵石 ${price}`}</span>
      `;
      if (!isLearned && !isLocked && price > 0) {
        div.addEventListener('click', () => buyTechnique(npcName, t));
      }
      shop.appendChild(div);
    });
  }

  // 技能商店
  if (r.skill_shop && r.skill_shop.length > 0) {
    const header = document.createElement('div');
    header.className = 'shop-header';
    header.textContent = '— 技能 —';
    shop.appendChild(header);

    const charElems = Array.isArray(gameState.character?.element) ? gameState.character.element : [gameState.character?.element];

    r.skill_shop.forEach(s => {
      const skillData = gameState.gameData?.skills?.[s] || {};
      const price = skillData.price || 0;
      const isLearned = (gameState.character?.skills || []).includes(s);
      const isLocked = !charElems.includes(skillData.element);
      const isSword = skillData.is_sword;
      const dmgDesc = skillData.damage > 0 ? `伤害:${skillData.damage}+${skillData.atk_mult}x` : skillData.damage < 0 ? `回复:${Math.abs(skillData.damage)}生命` : '防御';
      const costDesc = isSword ? '免费(剑法)' : `消耗:${skillData.cost||0}灵力`;
      const div = document.createElement('div');
      div.className = `shop-item${isLearned ? ' learned' : ''}${isLocked ? ' locked' : ''}`;
      div.innerHTML = `
        <span class="shop-name">${s}（${skillData.desc || ''}）</span>
        <span class="shop-detail">${dmgDesc} ${costDesc}</span>
        <span class="shop-price">${isLearned ? '已学会' : isLocked ? `需要${skillData.element}灵根` : price <= 0 ? '免费' : `灵石 ${price}`}</span>
      `;
      if (!isLearned && !isLocked && price > 0) {
        div.addEventListener('click', () => buySkill(npcName, s));
      }
      shop.appendChild(div);
    });
  }

  // 添加交互按钮
  const actions = document.createElement('div');
  actions.className = 'npc-actions';
  actions.innerHTML = `
    <button class="npc-action-btn leave" id="npcLeave">告辞</button>
    <button class="npc-action-btn fight" id="npcFight">切磋</button>
  `;
  shop.appendChild(actions);

  document.getElementById('npcLeave').addEventListener('click', () => {
    closeModal('npcModal');
    addLog(`你与${npcName}告别。`, 'system');
  });

  document.getElementById('npcFight').addEventListener('click', () => {
    closeModal('npcModal');
    startCombat(npcName);
  });

  modal.classList.add('active');
}

async function buyItem(npcName, itemName) {
  const res = await apiPost('/buy', { character: gameState.character, npc: npcName, item: itemName });
  if (res.success) {
    addLog(res.result.message, res.result.success ? 'success' : 'warning');
    await reloadCharacter();
    showNPCDialog(npcName);
  }
}

async function buyTechnique(npcName, techName) {
  const res = await apiPost('/buy_technique', { character: gameState.character, npc: npcName, technique: techName });
  if (res.success) {
    addLog(res.result.message, res.result.success ? 'success' : 'warning');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    showNPCDialog(npcName);
  }
}

async function buySkill(npcName, skillName) {
  const res = await apiPost('/buy_skill', { character: gameState.character, npc: npcName, skill: skillName });
  if (res.success) {
    addLog(res.result.message, res.result.success ? 'success' : 'warning');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    showNPCDialog(npcName);
  }
}

function showMove() {
  const c = gameState.character;
  if (!c || !gameState.gameData) return;

  const modal = document.getElementById('moveModal');
  const list = document.getElementById('regionList');
  list.innerHTML = '';

  Object.entries(gameState.gameData.regions).forEach(([name, region]) => {
    const isCurrent = c.location === name;
    const realmIndex = ['练气','筑基','结丹','元婴','化神'].indexOf(c.realm);
    const isLocked = realmIndex + 1 < region.level;

    const div = document.createElement('div');
    div.className = `region-card${isCurrent ? ' current' : ''}${isLocked ? ' locked' : ''}`;
    div.innerHTML = `
      <div class="region-name">${name} ${isCurrent ? '（当前位置）' : ''}</div>
      <div class="region-level">需要境界：${['练气','筑基','结丹','元婴','化神'][region.level-1]}</div>
      <div class="region-desc">${region.desc}</div>
    `;

    if (!isCurrent && !isLocked) {
      div.addEventListener('click', () => moveTo(name));
    }

    list.appendChild(div);
  });

  modal.classList.add('active');
}

async function moveTo(region) {
  closeModal('moveModal');
  const res = await apiPost('/move', { character: gameState.character, region });
  if (res.success) {
    if (res.result.success) {
      addLog(res.result.message, 'success');
      await reloadCharacter();
    } else {
      addLog(res.result.message, 'warning');
    }
  }
}

async function doRest() {
  if (!gameState.character) return;
  disableActions(true);

  const safetyTimer = setTimeout(() => disableActions(false), 10000);

  try {
    const res = await apiPost('/rest', { character: gameState.character });
    if (res.success) {
      addLog(res.result.message, 'success');
      if (res.summary) updateFromSummary(res.summary);
      flashBar('hp');
      flashBar('mp');
      await reloadCharacter();
    } else {
      addLog(res.message || '休息失败', 'warning');
    }
  } catch (e) {
    console.error('[rest]', e);
  }

  clearTimeout(safetyTimer);
  disableActions(false);
}

async function saveGame() {
  const res = await apiPost('/save_character', { character: gameState.character });
  if (res.success) {
    addLog('存档成功', 'system');
    showToast('存档成功', 'success');
  } else {
    showToast('存档失败: ' + (res.message || '未知错误'), 'danger');
  }
}

// ============================================================
// 战斗系统
// ============================================================
async function startCombat(enemyName) {
  const res = await apiPost('/combat', { character: gameState.character, enemy: enemyName });
  if (res.success) {
    gameState.combat = res.combat;
    showCombat();
  }
}

function showCombat() {
  const combat = gameState.combat;
  if (!combat) return;

  const modal = document.getElementById('combatModal');
  modal.style.display = 'flex';

  const playerElem = combat.player.element?.[0] || '金';
  const enemyName = combat.enemy.name || '妖物';

  document.getElementById('combatPlayerName').textContent = combat.player.name;
  document.getElementById('combatEnemyName').textContent = enemyName;

  // Set element icons
  const elemMap = { '金': 'metal', '木': 'wood', '水': 'water', '火': 'fire', '土': 'earth' };
  const elemChar = { '金': '金', '木': '木', '水': '水', '火': '火', '土': '土' };
  const playerElemIcon = document.getElementById('combatPlayerElement');
  if (playerElemIcon) {
    playerElemIcon.className = `hud-element-icon ${elemMap[playerElem] || 'metal'}`;
    playerElemIcon.textContent = elemChar[playerElem] || '金';
  }
  const enemyElemRaw = combat.enemy.element || '火';
  const enemyElemFirst = Array.isArray(enemyElemRaw) ? enemyElemRaw[0] : (enemyElemRaw[0] || enemyElemRaw);
  const enemyElemIcon = document.getElementById('combatEnemyElement');
  if (enemyElemIcon) {
    enemyElemIcon.className = `hud-element-icon ${elemMap[enemyElemFirst] || 'fire'}`;
    enemyElemIcon.textContent = elemChar[enemyElemFirst] || '火';
  }

  // Set player realm
  const realmEl = document.getElementById('combatPlayerRealm');
  if (realmEl && gameState.character) {
    realmEl.textContent = gameState.character.realm || '';
  }

  // Set enemy info (level + type)
  const enemyInfoEl = document.getElementById('combatEnemyInfo');
  if (enemyInfoEl) {
    const lvl = combat.enemy.level || '';
    const typeLabels = { beast: '妖兽', spirit: '灵体', humanoid: '人形', dragon: '龙族' };
    const type = combat.enemy.type || 'beast';
    const typeLabel = typeLabels[type] || '妖兽';
    enemyInfoEl.innerHTML = `Lv.${lvl} <span class="enemy-type-tag">${typeLabel}</span>`;
  }

  // 重置结果面板
  document.getElementById('combatResult').classList.add('hidden');

  // 显示回合指示
  const turnInd = document.getElementById('turnIndicator');
  turnInd.textContent = '你的回合';
  turnInd.classList.add('show');
  setTimeout(() => turnInd.classList.remove('show'), 1500);

  updateCombatUI();
  document.getElementById('combatLog').innerHTML = '';
  combat.log.forEach(msg => addCombatLog(msg));

  // ── 生成神通卡（最左边） ──
  const abilityCards = document.getElementById('abilityCards');
  abilityCards.innerHTML = '';
  if (combat.player.abilities && combat.player.abilities.length > 0) {
    combat.player.abilities.forEach(a => {
      const abilData = gameState.gameData?.abilities?.[a];
      if (abilData) {
        const card = document.createElement('button');
        card.className = 'combat-card ability-card';
        const dmgDesc = abilData.base_damage > 0 ? `${abilData.base_damage}+${abilData.atk_mult}x` : `回复${Math.abs(abilData.base_damage)}`;
        card.innerHTML = `<span class="card-icon">神</span><span class="card-name">${a}</span><span class="card-cost">${abilData.cost}灵</span>`;
        card.addEventListener('click', () => doCombat('ability', a));
        // Tooltip
        card.addEventListener('mouseenter', (e) => showCardTooltip(e, {
          name: a,
          desc: abilData.desc || '',
          stats: { '伤害': dmgDesc, '消耗': `${abilData.cost}灵力` },
        }));
        card.addEventListener('mouseleave', hideCardTooltip);
        abilityCards.appendChild(card);
      }
    });
  }
  if (abilityCards.children.length === 0) {
    abilityCards.innerHTML = '<span style="color:var(--text-muted);font-size:11px;opacity:0.5;">无神通</span>';
  }

  // ── 生成技能卡（中间） ──
  const skillCards = document.getElementById('skillCards');
  skillCards.innerHTML = '';
  combat.player.skills.forEach(s => {
    const skillData = gameState.gameData?.skills?.[s];
    if (skillData) {
      const card = document.createElement('button');
      card.className = 'combat-card skill-card';
      const isSword = skillData.is_sword;
      const costText = isSword ? '免费' : `${skillData.cost}灵`;
      const icon = isSword ? '剑' : '术';
      const elem = skillData.element || playerElem;
      card.setAttribute('data-element', elem);
      card.innerHTML = `<span class="card-icon">${icon}</span><span class="card-name">${s}</span><span class="card-cost">${costText}</span>`;
      card.addEventListener('click', () => doCombat('skill', s));
      // Tooltip
      card.addEventListener('mouseenter', (e) => showCardTooltip(e, {
        name: s,
        desc: skillData.desc || '',
        stats: {
          '伤害': isSword ? `${skillData.base_damage}+${skillData.atk_mult}x` : `${skillData.base_damage}+${skillData.atk_mult}x`,
          '消耗': costText,
          '元素': elem,
        },
      }));
      card.addEventListener('mouseleave', hideCardTooltip);
      skillCards.appendChild(card);
    }
  });

  // 初始化 Canvas 战斗场景
  combatRenderer.init();
  combatRenderer.setPlayerElement(playerElem);
  const enemyElem = combat.enemy.element || '火';
  const enemyType = combat.enemy.type || 'beast';
  combatRenderer.setEnemyName(enemyName, enemyElem, enemyType);

  // 激活高级战斗特效系统
  initCombatEffects();

  // 启动环境粒子
  spawnCombatParticles(enemyElem);

  // 切换战斗BGM
  if (typeof playBgmForRegion === 'function') playBgmForRegion('battle');
}

function updateCombatUI() {
  const combat = gameState.combat;
  if (!combat) return;

  const p = combat.player;
  const e = combat.enemy;

  const playerHpBar = document.getElementById('combatHpPlayer');
  const enemyHpBar = document.getElementById('combatHpEnemy');

  // 检测HP变化并触发闪光
  const oldPlayerHp = parseInt(document.getElementById('combatHpPlayerVal')?.textContent?.split('/')[0] || '0');
  const oldEnemyHp = parseInt(document.getElementById('combatHpEnemyVal')?.textContent?.split('/')[0] || '0');

  const playerHpPct = Math.max(0, (p.hp / p.max_hp) * 100);
  const enemyHpPct = Math.max(0, (e.hp / e.max_hp) * 100);

  playerHpBar.style.width = `${playerHpPct}%`;
  animateNumber('combatHpPlayerVal', oldPlayerHp, p.hp, p.max_hp, p.hp < oldPlayerHp);
  document.getElementById('combatMpPlayer').style.width = `${Math.max(0, (p.mp / p.max_mp) * 100)}%`;
  const oldPlayerMp = parseInt(document.getElementById('combatMpPlayerVal')?.textContent?.split('/')[0] || '0');
  animateNumber('combatMpPlayerVal', oldPlayerMp, p.mp, p.max_mp, false);

  enemyHpBar.style.width = `${enemyHpPct}%`;
  animateNumber('combatHpEnemyVal', oldEnemyHp, e.hp, e.max_hp, e.hp < oldEnemyHp);

  // 低血量警告脉冲
  if (playerHpPct <= 30) {
    playerHpBar.classList.add('low');
    const scene = document.querySelector('.combat-scene');
    if (scene) scene.classList.add('low-hp-warning');
  } else {
    playerHpBar.classList.remove('low');
    const scene = document.querySelector('.combat-scene');
    if (scene) scene.classList.remove('low-hp-warning');
  }

  // HP变化时闪光
  if (p.hp < oldPlayerHp) {
    playerHpBar.classList.add('flash');
    setTimeout(() => playerHpBar.classList.remove('flash'), 500);
  }
  if (e.hp < oldEnemyHp) {
    enemyHpBar.classList.add('flash');
    setTimeout(() => enemyHpBar.classList.remove('flash'), 500);
  }

  // 更新回合计数
  const turnCounter = document.getElementById('turnCounter');
  if (turnCounter) turnCounter.textContent = `第 ${combat.turn || 1} 回合`;

  // 更新状态效果图标
  updateStatusEffects('playerStatusEffects', p.status_effects || {});
  updateStatusEffects('enemyStatusEffects', e.status_effects || {});
}

// Number scrolling animation
function animateNumber(elementId, from, to, max, isDamage) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const duration = 200;
  const start = performance.now();
  const fromVal = Math.max(0, from);
  const toVal = Math.max(0, to);
  const maxVal = Math.max(1, max);

  // Add tick class for visual feedback
  if (isDamage) {
    el.classList.add('ticking');
    setTimeout(() => el.classList.remove('ticking'), 300);
  } else if (toVal > fromVal) {
    el.classList.add('heal-tick');
    setTimeout(() => el.classList.remove('heal-tick'), 300);
  }

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(1, elapsed / duration);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = Math.round(fromVal + (toVal - fromVal) * eased);
    el.textContent = `${current}/${maxVal}`;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function updateStatusEffects(containerId, effects) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = '';
  const icons = { '中毒': '毒', '灼烧': '火', '冰冻': '冰', '眩晕': '晕', '治愈': '愈', '护盾': '盾' };
  Object.entries(effects).forEach(([name, duration]) => {
    if (duration > 0) {
      const el = document.createElement('span');
      el.className = `status-effect-icon ${name}`;
      el.textContent = icons[name] || name[0];
      el.title = `${name} (${duration}回合)`;
      el.setAttribute('data-duration', duration);
      container.appendChild(el);
    }
  });
}

function addCombatLog(msg) {
  const log = document.getElementById('combatLog');
  const p = document.createElement('p');
  let icon = '';
  if (msg.includes('中毒')) {
    p.className = 'status-effect poison';
    icon = '☠';
  } else if (msg.includes('灼烧')) {
    p.className = 'status-effect burn';
    icon = '🔥';
  } else if (msg.includes('冰冻')) {
    p.className = 'status-effect freeze';
    icon = '❄';
  } else if (msg.includes('眩晕')) {
    p.className = 'status-effect stun';
    icon = '💫';
  } else if (msg.includes('治愈')) {
    p.className = 'status-effect heal';
    icon = '💚';
  } else if (msg.includes('你') || msg.includes('造成') || msg.includes('使用')) {
    p.className = 'player-action';
    if (msg.includes('暴击')) {
      p.classList.add('crit');
      icon = '💥';
    } else if (msg.includes('神通') || msg.includes('技能')) {
      icon = '✨';
    } else {
      icon = '⚔';
    }
  } else if (msg.includes('攻击') || msg.includes('反击') || msg.includes('伤害')) {
    p.className = 'enemy-action';
    icon = '🗡';
  } else if (msg.includes('恢复') || msg.includes('回复') || msg.includes('+')) {
    p.className = 'heal';
    icon = '❤';
  } else if (msg.includes('击败') || msg.includes('胜利')) {
    p.className = 'player-action';
    icon = '🏆';
  } else if (msg.includes('失败') || msg.includes('死亡')) {
    p.className = 'enemy-action';
    icon = '💀';
  } else if (msg.includes('防御') || msg.includes('格挡')) {
    p.className = 'system-msg';
    icon = '🛡';
  } else if (msg.includes('逃跑') || msg.includes('遁走')) {
    p.className = 'system-msg';
    icon = '💨';
  } else {
    p.className = 'system-msg';
    icon = '◆';
  }
  if (icon) {
    const iconSpan = document.createElement('span');
    iconSpan.className = 'log-icon';
    iconSpan.textContent = icon;
    p.appendChild(iconSpan);
  }
  p.appendChild(document.createTextNode(msg));
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

// Card tooltip system
let _tooltipTimer = null;
function showCardTooltip(e, data) {
  clearTimeout(_tooltipTimer);
  _tooltipTimer = setTimeout(() => {
    const tooltip = document.getElementById('cardTooltip');
    const nameEl = document.getElementById('tooltipName');
    const descEl = document.getElementById('tooltipDesc');
    const statsEl = document.getElementById('tooltipStats');
    if (!tooltip) return;

    nameEl.textContent = data.name;
    descEl.textContent = data.desc || '';
    descEl.style.display = data.desc ? 'block' : 'none';

    statsEl.innerHTML = '';
    if (data.stats) {
      Object.entries(data.stats).forEach(([label, value]) => {
        const item = document.createElement('span');
        item.className = 'stat-item';
        item.innerHTML = `<span class="stat-label">${label}:</span><span class="stat-value">${value}</span>`;
        statsEl.appendChild(item);
      });
    }

    tooltip.classList.remove('hidden');
  }, 300);
}

function hideCardTooltip() {
  clearTimeout(_tooltipTimer);
  const tooltip = document.getElementById('cardTooltip');
  if (tooltip) tooltip.classList.add('hidden');
}

// Cooldown tracking
const _cardCooldowns = {};
function startCardCooldown(cardEl, turns) {
  const name = cardEl.querySelector('.card-name')?.textContent;
  if (!name) return;
  _cardCooldowns[name] = turns;
  const overlay = document.createElement('div');
  overlay.className = 'card-cooldown';
  overlay.textContent = turns;
  cardEl.style.position = 'relative';
  cardEl.appendChild(overlay);
  cardEl.disabled = true;
}

function tickCardCooldowns() {
  Object.keys(_cardCooldowns).forEach(name => {
    _cardCooldowns[name]--;
    if (_cardCooldowns[name] <= 0) {
      delete _cardCooldowns[name];
    }
  });
  // Remove expired cooldown overlays
  document.querySelectorAll('.card-cooldown').forEach(el => {
    const cardName = el.parentElement?.querySelector('.card-name')?.textContent;
    if (cardName && !_cardCooldowns[cardName]) {
      el.remove();
      el.parentElement.disabled = false;
    } else if (cardName && _cardCooldowns[cardName]) {
      el.textContent = _cardCooldowns[cardName];
    }
  });
}

window.doCombat = async function(action, skill) {
  const combat = gameState.combat;
  if (!combat || combat.finished) return;

  // 禁用按钮
  const actionBtns = document.querySelectorAll('.combat-card');
  actionBtns.forEach(b => b.disabled = true);

  try {
    const res = await apiPost('/combat', {
      character: gameState.character,
      combat: combat,
      action: action,
      skill: skill,
      enemy: null,
    });

    if (!res.success) {
      showToast(res.message || '操作失败', 'danger');
      return;
    }

    const oldEnemyHp = combat.enemy.hp;
    const oldPlayerHp = combat.player.hp;

    // 播放玩家攻击动画
    let elem = '金';
    let isAbility = false;
    if (action === 'defend') {
      await combatRenderer.playDefendAnim();
    } else if (action === 'flee') {
      await combatRenderer.playFleeAnim();
    } else {
      if (action === 'attack') {
        elem = combat.player.element?.[0] || '金';
      } else if (action === 'skill' && skill) {
        const skillData = gameState.gameData?.skills?.[skill];
        if (skillData) elem = skillData.element;
      } else if (action === 'ability' && skill) {
        const abilData = gameState.gameData?.abilities?.[skill];
        if (abilData) elem = abilData.element;
        isAbility = true;
      }
      await combatRenderer.playAttackAnim(elem, isAbility);
    }

    // 更新数据
    gameState.combat = res.combat;
    updateCombatUI();

    const oldLen = combat.log.length;
    const newLogs = res.combat.log.slice(oldLen);
    newLogs.forEach(msg => addCombatLog(msg));

    // 显示状态效果伤害/治疗浮动数字
    newLogs.forEach(msg => {
      if (msg.includes('中毒') && msg.includes('损失')) {
        const dmg = msg.match(/(\d+)/)?.[1];
        if (dmg) combatRenderer.showDamageFloat(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 80, `-${dmg}`, '#9b59b6', 22, { isStatus: true });
      } else if (msg.includes('灼烧') && msg.includes('损失')) {
        const dmg = msg.match(/(\d+)/)?.[1];
        if (dmg) combatRenderer.showDamageFloat(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 80, `-${dmg}`, '#e74c3c', 22, { isStatus: true });
      } else if (msg.includes('治愈') && msg.includes('恢复')) {
        const heal = msg.match(/(\d+)/)?.[1];
        if (heal) combatRenderer.showDamageFloat(combatRenderer.player.bodyX, combatRenderer.player.bodyY - 80, `+${heal}`, '#2ecc71', 22, { isHeal: true, isStatus: true });
      } else if (msg.includes('冰冻') && msg.includes('跳过')) {
        combatRenderer.showDamageFloat(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 80, '冰冻!', '#3498db', 24, { isStatus: true });
      } else if (msg.includes('眩晕') && msg.includes('跳过')) {
        combatRenderer.showDamageFloat(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 80, '眩晕!', '#f39c12', 24, { isStatus: true });
      }
    });

    // 显示伤害数字 + 高级特效
    if (action !== 'defend' && action !== 'flee') {
      const enemyDmg = oldEnemyHp - res.combat.enemy.hp;
      if (enemyDmg > 0) {
        const lastLogs = res.combat.log.slice(oldLen);
        const isCrit = lastLogs.some(msg => msg.includes('暴击'));
        const dmgColor = isCrit ? '#ffd700' : '#ff4444';
        const dmgSize = isCrit ? 42 : 32;
        const critLabel = isCrit ? ' 暴击!' : '';
        combatRenderer.showDamageFloat(
          combatRenderer.enemy.bodyX,
          combatRenderer.enemy.bodyY - 60,
          `-${enemyDmg}${critLabel}`,
          dmgColor,
          dmgSize,
          { isCrit }
        );
        updateComboCounter(isCrit);

        // 技能/神通：播放光束+冲击波特效
        if (action === 'skill' || action === 'ability') {
          triggerElementBurst(elem, combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY);
          const px = combatRenderer.player.bodyX, py = combatRenderer.player.bodyY - 40;
          const ex = combatRenderer.enemy.bodyX, ey = combatRenderer.enemy.bodyY - 40;
          if (action === 'ability') {
            playAbilityEffect(elem, ex, ey);
          } else {
            playSpellCastEffect(elem, px, py, ex, ey);
          }
          if (typeof playSfx === 'function') playSfx('spell');
        } else {
          if (typeof playSfx === 'function') playSfx('hit');
        }

        // 暴击：冲击波+闪屏
        if (isCrit) {
          playCriticalHitEffect(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 30);
          combatRenderer.emitBurst(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 30, 25, '#ffd700', { speed: 6, r: 4, blend: 'screen', life: 50, spread: 25 });
          combatRenderer.emitBurst(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 20, 15, '#fff', { speed: 4, r: 2, blend: 'screen', life: 30 });
          triggerScreenShake(action === 'ability' ? 'heavy' : 15);
          triggerCriticalFlash();
          if (typeof playSfx === 'function') playSfx('critical');
        }
      } else {
        // MISS 显示
        combatRenderer.showDamageFloat(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY - 60, 'MISS', '#888888', 24, { isMiss: true });
      }
    }

    // 防御音效
    if (action === 'defend' && typeof playSfx === 'function') playSfx('defend');
    if (action === 'flee' && typeof playSfx === 'function') playSfx('flee');

    // 玩家受伤显示
    const playerDmg = oldPlayerHp - res.combat.player.hp;
    if (playerDmg > 0) {
      combatRenderer.showDamageFloat(combatRenderer.player.bodyX, combatRenderer.player.bodyY - 60, `-${playerDmg}`, '#ff6644', 28, {});
      if (playerDmg > 30) triggerScreenShake('heavy');
      else if (playerDmg > 15) triggerScreenShake();
      if (typeof playSfx === 'function') playSfx('hurt');
    }

    // 治疗显示 + 特效
    if (res.combat.player.hp > oldPlayerHp) {
      const heal = res.combat.player.hp - oldPlayerHp;
      combatRenderer.showDamageFloat(combatRenderer.player.bodyX, combatRenderer.player.bodyY - 60, `+${heal}`, '#44ff88', 28, { isHeal: true });
      playHealEffect(combatRenderer.player.bodyX, combatRenderer.player.bodyY - 40);
      if (typeof playSfx === 'function') playSfx('heal');
    }

    // 敌人回合
    if (!res.combat.finished) {
      const turnInd = document.getElementById('turnIndicator');
      turnInd.textContent = '敌方行动';
      turnInd.classList.add('show', 'enemy-turn');
      setTimeout(() => turnInd.classList.remove('show', 'enemy-turn'), 1200);

      await new Promise(r => setTimeout(r, 300));

      // 只在敌人实际造成伤害时播放攻击动画
      if (res.combat.player.hp < oldPlayerHp) {
        await combatRenderer.playEnemyAttackAnim();
      }

      await new Promise(r => setTimeout(r, 200));

      turnInd.textContent = '你的回合';
      turnInd.classList.remove('enemy-turn');
      turnInd.classList.add('show');
      setTimeout(() => turnInd.classList.remove('show'), 1200);

      // Crit flash overlay
      if (res.combat.player.hp < oldPlayerHp) {
        const scene = document.querySelector('.combat-scene');
        if (scene) {
          const flash = document.createElement('div');
          flash.className = 'crit-flash-overlay';
          scene.appendChild(flash);
          setTimeout(() => flash.remove(), 200);
        }
      }
    }

    // 战斗结束
    if (res.combat.finished) {
      await new Promise(r => setTimeout(r, 500));
      if (res.combat.victory === true) {
        combatRenderer.playVictoryAnim();
        showCombatResult(true, res.result);
        checkAchievementsAfterAction();
      } else {
        combatRenderer.playDefeatAnim();
        showCombatResult(false, null);
      }
      await reloadCharacter();
    }

    if (res.summary) {
      gameState.character.hp = res.summary.hp;
      gameState.character.mp = res.summary.mp;
    }
  } catch (err) {
    console.error('Combat error:', err);
    showToast('战斗出错，请重试', 'danger');
  } finally {
    // 无论如何都重新启用按钮
    actionBtns.forEach(b => b.disabled = false);
  }
};

function showCombatResult(isVictory, result) {
  // 清理高级特效
  destroyCombatEffects();
  clearCombatParticles();

  // 战斗结束音效+BGM
  if (typeof playSfx === 'function') playSfx(isVictory ? 'victory' : 'defeat');
  if (typeof playBgmForRegion === 'function') playBgmForRegion(gameState.character?.region || '青云镇');

  const overlay = document.getElementById('combatResult');
  const icon = document.getElementById('resultIcon');
  const text = document.getElementById('resultText');
  const rewards = document.getElementById('resultRewards');
  const btn = document.getElementById('resultBtn');

  overlay.classList.remove('hidden');

  if (isVictory) {
    icon.textContent = '胜';
    icon.className = 'result-icon victory';
    text.textContent = '战斗胜利';
    text.className = 'result-text victory';

    let rewardHtml = '';
    if (result) {
      if (result.exp) rewardHtml += `<span class="reward-item" style="animation-delay:0.1s">修为 +${result.exp}</span>`;
      let dropIdx = 1;
      Object.entries(result.drops || {}).forEach(([item, count]) => {
        rewardHtml += `<span class="reward-item" style="animation-delay:${0.2 + dropIdx * 0.15}s">${item} ×${count}</span>`;
        dropIdx++;
      });
    }
    rewards.innerHTML = rewardHtml || '<span class="reward-item" style="animation-delay:0.1s">无掉落</span>';

    // 胜利特效
    icon.style.animation = 'none';
    void icon.offsetWidth;
    icon.style.animation = 'victoryPulse 0.8s ease-out';

    // 胜利金色光雨
    spawnVictoryParticles();
  } else {
    icon.textContent = '败';
    icon.className = 'result-icon defeat';
    text.textContent = '战斗失败';
    text.className = 'result-text defeat';
    rewards.innerHTML = '<span class="reward-item">需回镇修养</span>';

    // 失败特效
    icon.style.animation = 'none';
    void icon.offsetWidth;
    icon.style.animation = 'defeatShake 0.5s ease-out';

    // 失败屏幕渐暗
    overlay.style.animation = 'defeatDarken 1.5s ease-out forwards';
  }

  btn.onclick = async () => {
    overlay.classList.add('hidden');
    overlay.style.animation = '';
    combatRenderer.stop();
    clearCombatParticles();
    document.getElementById('combatModal').style.display = 'none';
    gameState.combat = null;
    await reloadCharacter();
    addLog(isVictory ? '你赢得了战斗！' : '你被击败了...', isVictory ? 'success' : 'danger');
  };
}

function spawnVictoryParticles() {
  const container = document.getElementById('combatParticles');
  if (!container) return;
  container.innerHTML = '';

  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'combat-particle spirit';
    p.style.left = `${Math.random() * 100}%`;
    p.style.animationDelay = `${Math.random() * 2}s`;
    p.style.animationDuration = `${2 + Math.random() * 3}s`;
    p.style.background = Math.random() > 0.5 ? 'var(--gold-bright)' : 'var(--gold)';
    p.style.width = `${3 + Math.random() * 4}px`;
    p.style.height = p.style.width;
    p.style.boxShadow = `0 0 6px var(--gold-glow)`;
    container.appendChild(p);
  }
}

// ============================================================
// Canvas 战斗渲染系统
// ============================================================
const combatRenderer = {
  canvas: null,
  ctx: null,
  W: 0, H: 0,
  running: false,
  animId: null,
  time: 0,
  particles: [],
  bgParticles: [],
  damageTexts: [],
  playerElem: '金',
  enemyName: '妖',
  enemyElem: '火',

  // 角色状态（anime.js 驱动这些值）
  player: {
    bodyX: 0, bodyY: 0, bodyLean: 0, shakeX: 0,
    scaleX: 1, scaleY: 1, alpha: 1, glowIntensity: 0,
    flashWhite: 0,
  },
  enemy: {
    bodyX: 0, bodyY: 0, bodyLean: 0,
    scaleX: 1, scaleY: 1, alpha: 1, shakeX: 0,
    eyeGlow: 0, flashWhite: 0,
  },

  elemColors: {
    '金': { primary: '#ffd700', glow: 'rgba(255,215,0,0.4)', trail: '#ffec80' },
    '木': { primary: '#5a8a50', glow: 'rgba(90,138,80,0.4)', trail: '#8bc34a' },
    '水': { primary: '#4a7ab0', glow: 'rgba(74,122,176,0.4)', trail: '#80b0e0' },
    '火': { primary: '#ff4500', glow: 'rgba(255,69,0,0.4)', trail: '#ff8c00' },
    '土': { primary: '#8a7050', glow: 'rgba(138,112,80,0.4)', trail: '#b09070' },
  },

  // 当前区域主题色（可动态切换）
  regionTheme: null,

  setRegionTheme(regionName) {
    const themes = typeof REGION_THEMES !== 'undefined' ? REGION_THEMES : {};
    this.regionTheme = themes[regionName] || themes['青云镇'] || null;
  },

  init() {
    this.canvas = document.getElementById('combatCanvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.resize();
    this.initBgParticles();
    this.resetPos();
    this.start();
    this._initSkeletons();
    // 设置区域主题
    const region = gameState.character?.region || '青云镇';
    this.setRegionTheme(region);
    // 移除旧监听器，防止累积
    if (this._resizeHandler) window.removeEventListener('resize', this._resizeHandler);
    this._resizeHandler = () => this.resize();
    window.addEventListener('resize', this._resizeHandler);
  },

  _initSkeletons() {
    // 清理旧骨骼
    this._destroySkeletons();
    const scene = this.canvas.parentElement;
    const colors = this.elemColors[this.playerElem] || this.elemColors['金'];
    const eColors = this.elemColors[this.enemyElem] || this.elemColors['火'];

    // 创建玩家骨骼容器
    this._playerSkelWrap = document.createElement('div');
    this._playerSkelWrap.className = 'skeleton-wrap player-skeleton';
    this._playerSkelWrap.style.cssText = `position:absolute;left:${this.player.bodyX}px;top:${this.player.bodyY}px;width:1px;height:1px;pointer-events:none;`;
    scene.appendChild(this._playerSkelWrap);

    // 创建敌人骨骼容器
    this._enemySkelWrap = document.createElement('div');
    this._enemySkelWrap.className = 'skeleton-wrap enemy-skeleton';
    this._enemySkelWrap.style.cssText = `position:absolute;left:${this.enemy.bodyX}px;top:${this.enemy.bodyY}px;width:1px;height:1px;pointer-events:none;`;
    scene.appendChild(this._enemySkelWrap);

    // 创建骨骼渲染器
    this.playerSkel = new SkeletonRenderer('player', this._playerSkelWrap, '#12101e');
    this.playerSkel.setGlowColor(colors.primary);

    // 根据境界改变玩家外观
    const realm = gameState.character?.realm || '';
    if (realm.includes('化神') || realm.includes('飞升')) {
      this.playerSkel.setColor('#2a1a08');
      this.playerSkel.setGlowColor('#ffd700');
    } else if (realm.includes('元婴')) {
      this.playerSkel.setColor('#1a1520');
      this.playerSkel.setGlowColor('#e0c060');
    } else if (realm.includes('金丹')) {
      this.playerSkel.setColor('#181820');
      this.playerSkel.setGlowColor(colors.secondary);
    }

    // 根据敌人类型选择骨架
    const enemyType = this.enemyType || 'beast';
    const skelType = SkeletonBones[enemyType] ? enemyType : 'enemy';
    this.enemySkel = new SkeletonRenderer(skelType, this._enemySkelWrap, '#10081a');
    this.enemySkel.setGlowColor(eColors.primary);

    // 启动待机动画
    SkeletonAnims.idle(this.playerSkel, 'player');
    SkeletonAnims.idle(this.enemySkel, skelType === 'enemy' ? 'enemy' : skelType);
  },

  _destroySkeletons() {
    if (this.playerSkel) { this.playerSkel.destroy(); this.playerSkel = null; }
    if (this.enemySkel) { this.enemySkel.destroy(); this.enemySkel = null; }
    if (this._playerSkelWrap && this._playerSkelWrap.parentNode) this._playerSkelWrap.parentNode.removeChild(this._playerSkelWrap);
    if (this._enemySkelWrap && this._enemySkelWrap.parentNode) this._enemySkelWrap.parentNode.removeChild(this._enemySkelWrap);
  },

  _updateSkelPositions() {
    if (this._playerSkelWrap) {
      this._playerSkelWrap.style.left = (this.player.bodyX + (this.player.shakeX || 0)) + 'px';
      this._playerSkelWrap.style.top = this.player.bodyY + 'px';
    }
    if (this._enemySkelWrap) {
      this._enemySkelWrap.style.left = (this.enemy.bodyX + (this.enemy.shakeX || 0)) + 'px';
      this._enemySkelWrap.style.top = this.enemy.bodyY + 'px';
    }
  },

  resize() {
    const wrap = this.canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    this.W = wrap.clientWidth;
    this.H = wrap.clientHeight;
    this.canvas.width = this.W * dpr;
    this.canvas.height = this.H * dpr;
    this.canvas.style.width = this.W + 'px';
    this.canvas.style.height = this.H + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.resetPos();
  },

  resetPos() {
    this.player.bodyX = this.W * 0.25;
    this.player.bodyY = this.H * 0.58;
    this.enemy.bodyX = this.W * 0.75;
    this.enemy.bodyY = this.H * 0.52;
  },

  setPlayerElement(elem) { this.playerElem = elem; },
  setEnemyName(name, elem, type) { this.enemyName = name; this.enemyElem = elem || '火'; this.enemyType = type || 'beast'; },

  initBgParticles() {
    this.bgParticles = [];
    for (let i = 0; i < 40; i++) {
      this.bgParticles.push({
        x: Math.random() * (this.W || 800),
        y: Math.random() * (this.H || 500),
        r: Math.random() * 2.5 + 0.8,
        dx: (Math.random() - 0.5) * 0.4,
        dy: -Math.random() * 0.3 - 0.05,
        alpha: Math.random() * 0.4 + 0.08,
        colorIdx: Math.floor(Math.random() * 3),
      });
    }
  },

  start() {
    if (this.running) return;
    this.running = true;
    this.loop();
  },

  stop() {
    this.running = false;
    if (this.animId) { cancelAnimationFrame(this.animId); this.animId = null; }
    this._destroySkeletons();
  },

  loop() {
    if (!this.running) return;
    this.time += 0.016;
    this.draw();
    this.animId = requestAnimationFrame(() => this.loop());
  },

  draw() {
    const { ctx, W, H } = this;
    const dpr = window.devicePixelRatio || 1;
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    // 背景雾气
    this.drawBgParticles();

    // 地面线
    this.drawGround();

    // 元素光环（Canvas 绘制，在骨骼下方）
    this._drawAura(this.player.bodyX, this.player.bodyY - 35, this.playerElem, this.player.glowIntensity);
    this._drawAura(this.enemy.bodyX, this.enemy.bodyY - 20, this.enemyElem, this.enemy.eyeGlow * 0.5);

    // 更新骨骼位置
    this._updateSkelPositions();

    // 粒子特效
    this.drawParticles();

    // 伤害数字
    this.drawDamageTexts();

    // 场景光效
    this.drawSceneGlow();

    ctx.restore();
  },

  _drawAura(x, y, elem, intensity) {
    if (intensity <= 0) return;
    const { ctx } = this;
    const colors = this.elemColors[elem] || this.elemColors['金'];
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    const gr = ctx.createRadialGradient(x, y, 10, x, y, 80 + intensity * 60);
    gr.addColorStop(0, `rgba(${this.hexToRgb(colors.primary)},${intensity * 0.25})`);
    gr.addColorStop(0.5, `rgba(${this.hexToRgb(colors.primary)},${intensity * 0.06})`);
    gr.addColorStop(1, 'transparent');
    ctx.fillStyle = gr;
    ctx.beginPath();
    ctx.arc(x, y, 80 + intensity * 60, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  },

  drawBgParticles() {
    const { ctx } = this;
    const theme = this.regionTheme;
    const colors = theme?.particleColors || ['184,144,62'];
    this.bgParticles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      const c = colors[p.colorIdx % colors.length];
      ctx.fillStyle = `rgba(${c}, ${p.alpha})`;
      ctx.fill();
      p.x += p.dx;
      p.y += p.dy;
      if (p.y < -10) { p.y = this.H + 10; p.x = Math.random() * this.W; }
      if (p.x < -10) p.x = this.W + 10;
      if (p.x > this.W + 10) p.x = -10;
    });
  },

  // Ink-wash mountain silhouettes for atmospheric depth
  drawMountains() {
    const { ctx, W, H } = this;
    const theme = this.regionTheme;
    const lc = theme?.lineColor || '184,144,62';
    const t = this.time;

    // Far mountains (very faint, slow parallax)
    ctx.save();
    ctx.globalAlpha = 0.06;
    ctx.fillStyle = `rgb(${lc})`;
    ctx.beginPath();
    ctx.moveTo(0, H * 0.55);
    ctx.quadraticCurveTo(W * 0.15, H * 0.3 + Math.sin(t * 0.1) * 3, W * 0.25, H * 0.45);
    ctx.quadraticCurveTo(W * 0.35, H * 0.28, W * 0.45, H * 0.42);
    ctx.quadraticCurveTo(W * 0.55, H * 0.25, W * 0.65, H * 0.4);
    ctx.quadraticCurveTo(W * 0.75, H * 0.3, W * 0.85, H * 0.43);
    ctx.quadraticCurveTo(W * 0.95, H * 0.35, W, H * 0.5);
    ctx.lineTo(W, H * 0.78);
    ctx.lineTo(0, H * 0.78);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // Near mountains (slightly more visible)
    ctx.save();
    ctx.globalAlpha = 0.1;
    ctx.fillStyle = `rgb(${lc})`;
    ctx.beginPath();
    ctx.moveTo(0, H * 0.65);
    ctx.quadraticCurveTo(W * 0.1, H * 0.5 + Math.sin(t * 0.15) * 2, W * 0.2, H * 0.6);
    ctx.quadraticCurveTo(W * 0.3, H * 0.48, W * 0.4, H * 0.58);
    ctx.quadraticCurveTo(W * 0.55, H * 0.45, W * 0.7, H * 0.55);
    ctx.quadraticCurveTo(W * 0.85, H * 0.5, W, H * 0.6);
    ctx.lineTo(W, H * 0.78);
    ctx.lineTo(0, H * 0.78);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  },

  drawGround() {
    const { ctx, W, H } = this;
    const gy = H * 0.78;
    const theme = this.regionTheme;
    const lc = theme?.lineColor || '184,144,62';
    const t = this.time;

    // Draw ink-wash mountains behind ground
    this.drawMountains();

    // 地面渐变 (ink wash effect)
    const grad = ctx.createLinearGradient(0, gy - 15, 0, H);
    grad.addColorStop(0, `rgba(${lc},0.15)`);
    grad.addColorStop(0.2, `rgba(${lc},0.08)`);
    grad.addColorStop(0.6, `rgba(${lc},0.03)`);
    grad.addColorStop(1, `rgba(${lc},0)`);
    ctx.fillStyle = grad;
    ctx.fillRect(0, gy - 5, W, H - gy + 5);

    // 主地面线（水墨风格，略微不规则）
    ctx.save();
    ctx.strokeStyle = `rgba(${lc},0.25)`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, gy);
    for (let x = 0; x <= W; x += 20) {
      const wave = Math.sin(x * 0.02 + t * 0.5) * 1.5;
      ctx.lineTo(x, gy + wave);
    }
    ctx.stroke();
    ctx.restore();

    // 地面装饰线（渐远渐淡）
    ctx.lineWidth = 1;
    for (let i = 1; i <= 3; i++) {
      ctx.strokeStyle = `rgba(${lc},${0.08 - i * 0.02})`;
      ctx.beginPath();
      ctx.moveTo(0, gy + i * 12);
      ctx.lineTo(W, gy + i * 12);
      ctx.stroke();
    }

    // 散落的墨点装饰
    ctx.save();
    ctx.globalAlpha = 0.04;
    ctx.fillStyle = `rgb(${lc})`;
    for (let i = 0; i < 5; i++) {
      const dx = (W * (0.15 + i * 0.18) + Math.sin(t * 0.3 + i) * 10) % W;
      const dy = gy + 8 + Math.sin(t * 0.2 + i * 2) * 3;
      ctx.beginPath();
      ctx.arc(dx, dy, 2 + Math.sin(t + i) * 0.5, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  },

  drawSceneGlow() {
    const { ctx, W, H } = this;
    const colors = this.elemColors[this.playerElem] || this.elemColors['金'];
    const t = this.time;
    ctx.save();
    ctx.globalCompositeOperation = 'screen';

    // 玩家侧光环（呼吸效果）
    const breathe = 0.08 + this.player.glowIntensity * 0.15 + Math.sin(t * 1.5) * 0.02;
    const g1 = ctx.createRadialGradient(W * 0.25, H * 0.5, 0, W * 0.25, H * 0.5, 180);
    g1.addColorStop(0, `rgba(${this.hexToRgb(colors.primary)},${breathe})`);
    g1.addColorStop(0.5, `rgba(${this.hexToRgb(colors.primary)},${breathe * 0.4})`);
    g1.addColorStop(1, 'transparent');
    ctx.fillStyle = g1;
    ctx.fillRect(0, 0, W, H);

    // 敌人侧光环（威胁脉动）
    const threat = 0.06 + this.enemy.eyeGlow * 0.1 + Math.sin(t * 2) * 0.015;
    const g2 = ctx.createRadialGradient(W * 0.75, H * 0.5, 0, W * 0.75, H * 0.5, 180);
    g2.addColorStop(0, `rgba(194,59,34,${threat})`);
    g2.addColorStop(0.5, `rgba(194,59,34,${threat * 0.35})`);
    g2.addColorStop(1, 'transparent');
    ctx.fillStyle = g2;
    ctx.fillRect(0, 0, W, H);

    // 中央对峙光（紧张感）
    const tension = 0.03 + Math.sin(t * 0.8) * 0.01;
    const g3 = ctx.createRadialGradient(W * 0.5, H * 0.4, 0, W * 0.5, H * 0.4, 200);
    g3.addColorStop(0, `rgba(184,144,62,${tension})`);
    g3.addColorStop(1, 'transparent');
    ctx.fillStyle = g3;
    ctx.fillRect(0, 0, W, H);

    // 顶部暗角（营造氛围）
    const vignette = ctx.createLinearGradient(0, 0, 0, H * 0.3);
    vignette.addColorStop(0, 'rgba(0,0,0,0.15)');
    vignette.addColorStop(1, 'transparent');
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, W, H * 0.3);

    ctx.restore();
  },

  // ——— 伤害数字渲染 ———
  drawDamageTexts() {
    const { ctx } = this;
    const now = Date.now();

    for (let i = this.damageTexts.length - 1; i >= 0; i--) {
      const dt = this.damageTexts[i];
      const elapsed = now - dt.startTime;
      const progress = elapsed / dt.duration;

      if (progress >= 1) {
        this.damageTexts.splice(i, 1);
        continue;
      }

      const alpha = progress < 0.15 ? progress * 6.67 : 1 - ((progress - 0.15) / 0.85);
      let y = dt.y - elapsed * 0.06;
      let scale = 1;

      if (dt.isCrit) {
        scale = progress < 0.08 ? 0.3 + progress * 8.75 : progress < 0.2 ? 1.3 - (progress - 0.08) * 2.5 : 1;
        y -= Math.sin(progress * Math.PI) * 8;
      } else if (dt.isMiss) {
        scale = progress < 0.1 ? 0.5 + progress * 5 : 1;
      } else if (dt.isHeal) {
        scale = progress < 0.1 ? 0.6 + progress * 4 : 1;
        y -= 10;
      } else if (dt.isStatus) {
        scale = progress < 0.1 ? 0.5 + progress * 5 : 1;
      } else {
        scale = progress < 0.08 ? 0.5 + progress * 6.25 : 1;
      }

      ctx.save();
      ctx.globalAlpha = Math.max(0, alpha);
      const fontSize = Math.round(dt.size * scale);

      if (dt.isCrit) {
        ctx.font = `bold ${fontSize}px 'STKaiti', 'KaiTi', '楷体', cursive`;
      } else if (dt.isMiss) {
        ctx.font = `italic ${fontSize}px 'STKaiti', 'KaiTi', sans-serif`;
      } else if (dt.isStatus) {
        ctx.font = `${fontSize}px 'Noto Serif SC', 'STSong', 'SimSun', serif`;
      } else {
        ctx.font = `bold ${fontSize}px 'STKaiti', 'KaiTi', '楷体', cursive`;
      }

      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      ctx.strokeStyle = dt.isCrit ? 'rgba(139,69,0,0.9)' : 'rgba(0,0,0,0.85)';
      ctx.lineWidth = dt.isCrit ? 4 : 3;
      ctx.strokeText(dt.text, dt.x, y);

      ctx.fillStyle = dt.color;
      ctx.fillText(dt.text, dt.x, y);

      if (dt.isCrit && progress < 0.25) {
        ctx.globalAlpha = (0.25 - progress) * 3;
        ctx.fillStyle = '#fff';
        ctx.fillText(dt.text, dt.x, y);
      }

      ctx.restore();
    }
  },

  showDamageFloat(x, y, text, color = '#ff4444', size = 28, opts = {}) {
    // opts: { isHeal, isCrit, isMiss, isStatus, isBlock }
    this.damageTexts.push({
      x: x + (Math.random() - 0.5) * 20,
      y, text, color, size,
      isHeal: opts.isHeal || false,
      isCrit: opts.isCrit || false,
      isMiss: opts.isMiss || false,
      isStatus: opts.isStatus || false,
      isBlock: opts.isBlock || false,
      startTime: Date.now(),
      duration: opts.isCrit ? 1800 : opts.isStatus ? 1000 : 1200,
    });
  },

  // ——— 玩家精灵渲染：修士黑影剪影 ———
  drawPlayerSprite() {
    const { ctx, player: p, time: t } = this;
    const colors = this.elemColors[this.playerElem] || this.elemColors['金'];
    const breath = Math.sin(t * 1.8) * 3;
    const sway = Math.sin(t * 0.7) * 2;
    const bx = p.bodyX + (p.shakeX || 0);
    const by = p.bodyY + breath;

    ctx.save();
    ctx.globalAlpha = p.alpha;
    ctx.translate(bx, by);
    ctx.rotate(p.bodyLean * Math.PI / 180);
    ctx.scale(p.scaleX || 1, p.scaleY || 1);

    // 地面阴影
    ctx.save();
    ctx.globalAlpha = 0.25 * p.alpha;
    ctx.beginPath();
    ctx.ellipse(0, 68, 40, 8, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#000';
    ctx.fill();
    ctx.restore();

    // 元素光环（背后）
    if (p.glowIntensity > 0) {
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      const gr = ctx.createRadialGradient(0, -20, 10, 0, -20, 100 + p.glowIntensity * 80);
      gr.addColorStop(0, `rgba(${this.hexToRgb(colors.primary)},${p.glowIntensity * 0.3})`);
      gr.addColorStop(0.5, `rgba(${this.hexToRgb(colors.primary)},${p.glowIntensity * 0.08})`);
      gr.addColorStop(1, 'transparent');
      ctx.fillStyle = gr;
      ctx.beginPath();
      ctx.arc(0, -20, 100 + p.glowIntensity * 80, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // ── 修士剪影 ──
    const dark = '#12101e';
    const outline = colors.primary;
    const glowRgb = this.hexToRgb(outline);

    // 白色闪烁（受击）
    const flash = p.flashWhite || 0;

    // ── 长袍下摆（飘逸） ──
    ctx.beginPath();
    ctx.moveTo(-28 + sway * 0.3, 65);
    ctx.quadraticCurveTo(-35 + sway * 0.5, 30, -26 + sway * 0.2, -5);
    ctx.lineTo(26 + sway * 0.2, -5);
    ctx.quadraticCurveTo(35 + sway * 0.5, 30, 28 + sway * 0.3, 65);
    ctx.quadraticCurveTo(15, 70, 0, 68);
    ctx.quadraticCurveTo(-15, 70, -28 + sway * 0.3, 65);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;
    ctx.fill();

    // ── 身体躯干 ──
    ctx.beginPath();
    ctx.moveTo(-18, -8);
    ctx.quadraticCurveTo(-22 + sway * 0.2, 20, -20 + sway * 0.3, 45);
    ctx.lineTo(20 + sway * 0.3, 45);
    ctx.quadraticCurveTo(22 + sway * 0.2, 20, 18, -8);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;
    ctx.fill();

    // ── 交领衣襟 ──
    ctx.beginPath();
    ctx.moveTo(-2, -8);
    ctx.lineTo(-12, 12);
    ctx.lineTo(-2, 30);
    ctx.lineTo(2, 30);
    ctx.lineTo(12, 12);
    ctx.lineTo(2, -8);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.5})` : '#1a1528';
    ctx.fill();

    // ── 腰带 ──
    ctx.beginPath();
    ctx.moveTo(-22 + sway * 0.2, 28);
    ctx.lineTo(22 + sway * 0.2, 28);
    ctx.lineTo(20 + sway * 0.2, 34);
    ctx.lineTo(-20 + sway * 0.2, 34);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.4})` : `rgba(${glowRgb},0.25)`;
    ctx.fill();

    // ── 衣褶线条 ──
    ctx.save();
    ctx.strokeStyle = `rgba(${glowRgb},0.12)`;
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(-8 + sway * 0.2, 35);
    ctx.quadraticCurveTo(-12 + sway * 0.3, 50, -10 + sway * 0.3, 62);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(8 + sway * 0.2, 35);
    ctx.quadraticCurveTo(12 + sway * 0.3, 50, 10 + sway * 0.3, 62);
    ctx.stroke();
    ctx.restore();

    // ── 左臂（抬起施法） ──
    ctx.beginPath();
    ctx.moveTo(-18, -5);
    ctx.quadraticCurveTo(-38, -20, -45 + Math.sin(t * 1.2) * 3, -42);
    ctx.quadraticCurveTo(-48, -50, -42 + Math.sin(t * 1.2) * 3, -52);
    ctx.quadraticCurveTo(-34, -42, -30, -28);
    ctx.quadraticCurveTo(-20, -10, -16, -2);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;
    ctx.fill();

    // ── 右臂（自然下垂，袖袍飘动） ──
    ctx.beginPath();
    ctx.moveTo(18, -5);
    ctx.quadraticCurveTo(32, 5, 36 + sway * 0.4, 25);
    ctx.quadraticCurveTo(38 + sway * 0.6, 40, 30 + sway * 0.5, 48);
    ctx.quadraticCurveTo(24 + sway * 0.3, 42, 26, 28);
    ctx.quadraticCurveTo(28, 10, 20, -2);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;
    ctx.fill();

    // ── 头部 ──
    ctx.beginPath();
    ctx.ellipse(0, -28, 14, 17, 0, 0, Math.PI * 2);
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;
    ctx.fill();

    // ── 发髻（头顶） ──
    ctx.beginPath();
    ctx.ellipse(0, -48, 8, 6, 0, 0, Math.PI * 2);
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.5})` : '#080610';
    ctx.fill();
    // 发簪
    ctx.beginPath();
    ctx.moveTo(-10, -50);
    ctx.lineTo(12, -48);
    ctx.strokeStyle = outline;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // ── 面部特征 ──
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    // 双眼（更亮）
    const eyeBright = 0.6 + Math.sin(t * 2) * 0.2;
    ctx.fillStyle = `rgba(${glowRgb},${eyeBright})`;
    ctx.shadowColor = `rgba(${glowRgb},0.5)`;
    ctx.shadowBlur = 4;
    ctx.beginPath(); ctx.ellipse(-5, -30, 2.5, 1.5, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(5, -30, 2.5, 1.5, 0, 0, Math.PI * 2); ctx.fill();
    ctx.shadowBlur = 0;
    // 眉毛
    ctx.strokeStyle = `rgba(${glowRgb},0.3)`;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(-8, -34); ctx.lineTo(-3, -33); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(8, -34); ctx.lineTo(3, -33); ctx.stroke();
    ctx.restore();

    // ── 元素轮廓光 ──
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    ctx.shadowColor = outline;
    ctx.shadowBlur = 6 + p.glowIntensity * 14;

    // 重绘整体轮廓获取发光效果
    ctx.beginPath();
    ctx.ellipse(0, -28, 14, 17, 0, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(${glowRgb},${0.4 + p.glowIntensity * 0.3})`;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(-28 + sway * 0.3, 65);
    ctx.quadraticCurveTo(-35 + sway * 0.5, 30, -26, -5);
    ctx.lineTo(26, -5);
    ctx.quadraticCurveTo(35 + sway * 0.5, 30, 28 + sway * 0.3, 65);
    ctx.strokeStyle = `rgba(${glowRgb},${0.25 + p.glowIntensity * 0.2})`;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    ctx.restore();

    // 浮动灵气粒子
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (let i = 0; i < 6; i++) {
      const angle = t * 0.8 + i * 1.05;
      const dist = 50 + Math.sin(t * 1.2 + i) * 12;
      const px2 = bx + Math.cos(angle) * dist;
      const py2 = by - 35 + Math.sin(angle * 0.7 + i) * 30;
      const pr = 2 + Math.sin(t * 3 + i * 2) * 1;
      ctx.beginPath();
      ctx.arc(px2, py2, pr, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${glowRgb},${0.3 + Math.sin(t * 2 + i) * 0.15})`;
      ctx.fill();
    }
    ctx.restore();
  },

  // ——— 敌人精灵渲染：妖兽黑影剪影 ———
  drawEnemySprite() {
    const { ctx, enemy: e, time: t } = this;
    const breath = Math.sin(t * 1.3 + 1) * 4;
    const crouch = Math.sin(t * 0.9) * 2;
    const bx = e.bodyX + (e.shakeX || 0);
    const by = e.bodyY + breath;

    ctx.save();
    ctx.globalAlpha = e.alpha;
    ctx.translate(bx, by);
    ctx.rotate(e.bodyLean * Math.PI / 180);
    ctx.scale(e.scaleX || 1, e.scaleY || 1);

    // 地面阴影
    ctx.save();
    ctx.globalAlpha = 0.3 * e.alpha;
    ctx.beginPath();
    ctx.ellipse(0, 65, 55, 10, 0, 0, Math.PI * 2);
    ctx.fillStyle = '#000';
    ctx.fill();
    ctx.restore();

    // 暗影气息
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    for (let i = 0; i < 4; i++) {
      const sx = Math.sin(t * 0.6 + i * 1.8) * 20;
      const sy = -55 - i * 15 - Math.sin(t * 0.8 + i) * 8;
      const sr = 12 + i * 4 + Math.sin(t + i) * 3;
      const grad = ctx.createRadialGradient(sx, sy, 0, sx, sy, sr);
      grad.addColorStop(0, `rgba(194,59,34,${0.04 + e.eyeGlow * 0.03})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(sx, sy, sr, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    // ── 妖兽剪影 ──
    const dark = '#10081a';
    const glowR = `rgba(194,59,34,${0.4 + e.eyeGlow * 0.3})`;
    const flash = e.flashWhite || 0;
    const fill = flash > 0 ? `rgba(255,255,255,${flash * 0.7})` : dark;

    // ── 后腿（左侧） ──
    ctx.beginPath();
    ctx.moveTo(-25, 15 + crouch);
    ctx.quadraticCurveTo(-40, 35, -42, 58);
    ctx.quadraticCurveTo(-44, 65, -35, 65);
    ctx.quadraticCurveTo(-30, 64, -28, 55);
    ctx.quadraticCurveTo(-25, 35, -18, 18 + crouch);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 后腿（右侧） ──
    ctx.beginPath();
    ctx.moveTo(-10, 18 + crouch);
    ctx.quadraticCurveTo(-20, 38, -22, 58);
    ctx.quadraticCurveTo(-24, 65, -15, 65);
    ctx.quadraticCurveTo(-10, 64, -8, 55);
    ctx.quadraticCurveTo(-8, 35, -5, 20 + crouch);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 身体躯干（弓背兽形） ──
    ctx.beginPath();
    ctx.moveTo(-30, -8 + crouch * 0.3);
    ctx.quadraticCurveTo(-40, 5, -30, 20 + crouch);
    ctx.lineTo(-5, 22 + crouch);
    ctx.quadraticCurveTo(10, 20 + crouch, 25, 12 + crouch * 0.5);
    ctx.quadraticCurveTo(35, 2, 30, -12);
    ctx.quadraticCurveTo(20, -18, 0, -16);
    ctx.quadraticCurveTo(-15, -16, -30, -8 + crouch * 0.3);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 前腿（左侧） ──
    ctx.beginPath();
    ctx.moveTo(18, 8 + crouch * 0.5);
    ctx.quadraticCurveTo(22, 28, 20, 55);
    ctx.quadraticCurveTo(18, 65, 25, 65);
    ctx.quadraticCurveTo(32, 64, 32, 58);
    ctx.quadraticCurveTo(34, 35, 28, 10 + crouch * 0.5);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 前腿（右侧） ──
    ctx.beginPath();
    ctx.moveTo(28, 5 + crouch * 0.5);
    ctx.quadraticCurveTo(35, 25, 34, 55);
    ctx.quadraticCurveTo(33, 65, 40, 65);
    ctx.quadraticCurveTo(47, 64, 46, 58);
    ctx.quadraticCurveTo(46, 30, 38, 8 + crouch * 0.5);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 头部（宽大兽头） ──
    ctx.beginPath();
    ctx.moveTo(25, -14);
    ctx.quadraticCurveTo(45, -18, 52, -8);
    ctx.quadraticCurveTo(58, 2, 50, 10);
    ctx.quadraticCurveTo(40, 16, 25, 10 + crouch * 0.3);
    ctx.quadraticCurveTo(20, 2, 25, -14);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 身体纹路 ──
    ctx.save();
    ctx.strokeStyle = `rgba(194,59,34,${0.15 + e.eyeGlow * 0.1})`;
    ctx.lineWidth = 1;
    // 背部脊线
    ctx.beginPath();
    ctx.moveTo(-25, -8 + crouch * 0.3);
    ctx.quadraticCurveTo(-10, -18, 10, -14);
    ctx.quadraticCurveTo(20, -12, 28, -8);
    ctx.stroke();
    // 肋部纹路
    for (let i = 0; i < 3; i++) {
      ctx.beginPath();
      ctx.moveTo(-15 + i * 12, 0 + crouch * 0.3);
      ctx.quadraticCurveTo(-10 + i * 12, 10, -12 + i * 12, 18 + crouch * 0.3);
      ctx.stroke();
    }
    ctx.restore();

    // ── 獠牙 ──
    ctx.beginPath();
    ctx.moveTo(46, 6);
    ctx.lineTo(52, 16);
    ctx.lineTo(48, 10);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.5})` : '#2a1828';
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(42, 8);
    ctx.lineTo(46, 18);
    ctx.lineTo(44, 11);
    ctx.closePath();
    ctx.fillStyle = flash > 0 ? `rgba(255,255,255,${flash * 0.5})` : '#2a1828';
    ctx.fill();

    // ── 左角 ──
    ctx.beginPath();
    ctx.moveTo(30, -14);
    ctx.quadraticCurveTo(25, -35, 18, -42);
    ctx.quadraticCurveTo(22, -38, 28, -18);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 右角 ──
    ctx.beginPath();
    ctx.moveTo(42, -16);
    ctx.quadraticCurveTo(48, -38, 55, -45);
    ctx.quadraticCurveTo(52, -40, 46, -20);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 尾巴（弯曲） ──
    ctx.beginPath();
    ctx.moveTo(-28, 0 + crouch * 0.3);
    ctx.quadraticCurveTo(-50, -10, -58, -25);
    ctx.quadraticCurveTo(-62, -32, -55, -30);
    ctx.quadraticCurveTo(-48, -28, -40, -15);
    ctx.quadraticCurveTo(-30, 0, -25, 5 + crouch * 0.3);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();

    // ── 红色双眼 ──
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    const eyePulse = 0.7 + e.eyeGlow * 0.4 + Math.sin(t * 3) * 0.15;
    ctx.fillStyle = `rgba(255,60,30,${eyePulse})`;
    ctx.shadowColor = `rgba(255,50,30,${0.7 + e.eyeGlow * 0.3})`;
    ctx.shadowBlur = 10 + e.eyeGlow * 12;
    ctx.beginPath(); ctx.ellipse(38, -6, 4.5, 3, -0.15, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(46, -4, 4, 2.5, -0.15, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // ── 红色轮廓光 ──
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    ctx.shadowColor = `rgba(194,59,34,${0.3 + e.eyeGlow * 0.2})`;
    ctx.shadowBlur = 5 + e.eyeGlow * 10;

    // 身体轮廓
    ctx.beginPath();
    ctx.moveTo(-30, -8);
    ctx.quadraticCurveTo(-40, 5, -30, 20);
    ctx.lineTo(25, 12);
    ctx.quadraticCurveTo(35, 2, 30, -12);
    ctx.quadraticCurveTo(20, -18, 0, -16);
    ctx.quadraticCurveTo(-15, -16, -30, -8);
    ctx.strokeStyle = `rgba(194,59,34,${0.2 + e.eyeGlow * 0.15})`;
    ctx.lineWidth = 1;
    ctx.stroke();

    // 头部轮廓
    ctx.beginPath();
    ctx.moveTo(25, -14);
    ctx.quadraticCurveTo(45, -18, 52, -8);
    ctx.quadraticCurveTo(58, 2, 50, 10);
    ctx.quadraticCurveTo(40, 16, 25, 10);
    ctx.quadraticCurveTo(20, 2, 25, -14);
    ctx.stroke();
    ctx.restore();

    ctx.restore();
  },

  // ——— 粒子系统 ———
  drawParticles() {
    const { ctx } = this;
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      ctx.save();
      ctx.globalCompositeOperation = p.blend || 'source-over';

      if (p.type === 'circle') {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.rgb},${p.alpha})`;
        ctx.fill();
      } else if (p.type === 'line') {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x + p.vx * 3, p.y + p.vy * 3);
        ctx.strokeStyle = `rgba(${p.rgb},${p.alpha})`;
        ctx.lineWidth = p.r;
        ctx.lineCap = 'round';
        ctx.stroke();
      } else if (p.type === 'spark') {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.rgb},${p.alpha})`;
        ctx.shadowColor = `rgba(${p.rgb},${p.alpha})`;
        ctx.shadowBlur = 8;
        ctx.fill();
      }

      ctx.restore();

      p.x += p.vx;
      p.y += p.vy;
      p.vy += (p.gravity || 0);
      p.alpha -= p.decay || 0.015;
      p.life--;

      if (p.alpha <= 0 || p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  },

  emitBurst(x, y, count, color, opts = {}) {
    const rgb = this.hexToRgb(color);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = (opts.speed || 3) * (0.5 + Math.random());
      this.particles.push({
        type: opts.type || 'circle',
        x: x + (Math.random() - 0.5) * (opts.spread || 10),
        y: y + (Math.random() - 0.5) * (opts.spread || 10),
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        r: opts.r || (1.5 + Math.random() * 2),
        rgb,
        alpha: opts.alpha || 0.8,
        decay: opts.decay || 0.015,
        life: opts.life || 50,
        gravity: opts.gravity || 0,
        blend: opts.blend || 'source-over',
      });
    }
  },

  emitTrail(x1, y1, x2, y2, count, color) {
    const rgb = this.hexToRgb(color);
    for (let i = 0; i < count; i++) {
      const t = Math.random();
      this.particles.push({
        type: 'circle',
        x: x1 + (x2 - x1) * t + (Math.random() - 0.5) * 15,
        y: y1 + (y2 - y1) * t + (Math.random() - 0.5) * 15,
        vx: (Math.random() - 0.5) * 1,
        vy: (Math.random() - 0.5) * 1,
        r: 1 + Math.random() * 2,
        rgb,
        alpha: 0.6,
        decay: 0.02,
        life: 40,
        gravity: 0,
        blend: 'screen',
      });
    }
  },

  hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r},${g},${b}`;
  },

  // ——— 动画 API（骨骼动画版） ———
  playAttackAnim(skillElement, isAbility, callback) {
    return new Promise(resolve => {
      const colors = this.elemColors[skillElement] || this.elemColors['金'];
      const p = this.player;
      const e = this.enemy;
      const px = this.player.bodyX;
      const py = this.player.bodyY;
      const ex = this.enemy.bodyX;
      const ey = this.enemy.bodyY;

      // 光环脉冲
      anime({ targets: p, glowIntensity: isAbility ? 1 : 0.5, duration: 300 });
      setTimeout(() => anime({ targets: p, glowIntensity: 0, duration: 400 }), 600);

      // 骨骼动画
      const animFn = isAbility ? 'playerAbility' : (skillElement ? 'playerSkill' : 'playerAttack');
      SkeletonAnims[animFn](this.playerSkel, () => {
        SkeletonAnims.idle(this.playerSkel, 'player');
      });

      // 命中时粒子特效（延迟到攻击命中帧）
      setTimeout(() => {
        const hitX = ex - 10;
        const hitY = ey - 10;

        if (skillElement === '火') {
          this.emitBurst(hitX, hitY, 40, '#ff4500', { speed: 6, r: 5, blend: 'screen', gravity: -0.04, spread: 25 });
          this.emitBurst(hitX, hitY, 25, '#ff8c00', { speed: 4, r: 4, blend: 'screen', spread: 18 });
          this.emitBurst(hitX, hitY - 15, 12, '#ffcc00', { speed: 2.5, r: 3, blend: 'screen' });
        } else if (skillElement === '水') {
          this.emitBurst(hitX, hitY, 35, '#4a7ab0', { speed: 5, r: 6, blend: 'screen', spread: 22 });
          this.emitBurst(hitX, hitY, 18, '#80b0e0', { speed: 3, r: 5, blend: 'screen' });
          this.emitBurst(hitX, hitY + 10, 12, '#a0d0ff', { speed: 2, r: 4, blend: 'screen', gravity: 0.05 });
        } else if (skillElement === '木') {
          for (let i = 0; i < 14; i++) {
            const lx = ex - 60 + Math.random() * 60;
            this.emitBurst(lx, ey + 20, 5, '#5a8a50', { speed: 1.5, r: 5, type: 'line', blend: 'screen', life: 60 });
          }
          this.emitBurst(hitX, hitY, 12, '#8bc34a', { speed: 3, r: 4, blend: 'screen' });
        } else if (skillElement === '金') {
          this.emitBurst(hitX, hitY, 15, '#ffd700', { speed: 7, r: 2.5, type: 'spark', blend: 'screen', spread: 18 });
          this.emitTrail(px + 10, py - 40, ex - 10, ey - 10, 20, '#ffd700');
          this.emitBurst(hitX, hitY, 10, '#fff', { speed: 4, r: 2, type: 'spark', blend: 'screen' });
        } else if (skillElement === '土') {
          this.emitBurst(hitX, ey + 15, 25, '#8a7050', { speed: 4, r: 6, gravity: 0.08, blend: 'screen', spread: 28 });
          this.emitBurst(hitX, ey + 8, 12, '#b09070', { speed: 2, r: 4, blend: 'screen' });
        }

        if (isAbility) {
          this.emitBurst(hitX, hitY, 50, '#ffd700', { speed: 8, r: 5, blend: 'screen', life: 70, spread: 35 });
          this.emitBurst(hitX, hitY, 25, '#fff', { speed: 5, r: 3, blend: 'screen', life: 50 });
          this.emitBurst(hitX, hitY, 30, colors.primary, { speed: 6, r: 4, blend: 'screen', life: 60, spread: 40 });
          triggerAbilityFlash();
        }

        // 敌人受击
        this.playerSkel.flash(200);
        SkeletonAnims.enemyHit(this.enemySkel);
        anime({
          targets: e,
          shakeX: [-10, 10, -6, 6, -3, 0],
          duration: 500, easing: 'easeOutElastic',
        });
      }, 350);

      setTimeout(() => { if (callback) callback(); resolve(); }, 900);
    });
  },

  playEnemyAttackAnim(callback) {
    return new Promise(resolve => {
      const p = this.player;
      const e = this.enemy;
      const px = this.player.bodyX;
      const ex = this.enemy.bodyX;
      const colors = this.elemColors[this.enemyElem] || this.elemColors['火'];

      anime({ targets: e, eyeGlow: 1, duration: 300 });
      setTimeout(() => anime({ targets: e, eyeGlow: 0, duration: 400 }), 500);

      SkeletonAnims.enemyAttack(this.enemySkel, () => {
        SkeletonAnims.idle(this.enemySkel, 'enemy');
      });

      setTimeout(() => {
        const hitX = px + 10;
        const hitY = p.bodyY - 30;
        const elem = this.enemyElem;

        if (elem === '火') {
          this.emitBurst(hitX, hitY, 25, '#ff4500', { speed: 5, r: 5, blend: 'screen', spread: 18 });
          this.emitBurst(hitX, hitY, 12, '#ff8c00', { speed: 3, r: 4, blend: 'screen' });
        } else if (elem === '水') {
          this.emitBurst(hitX, hitY, 22, '#4a7ab0', { speed: 4, r: 6, blend: 'screen', spread: 16 });
          this.emitBurst(hitX, hitY, 10, '#80b0e0', { speed: 2.5, r: 4, blend: 'screen', gravity: 0.04 });
        } else if (elem === '木') {
          for (let i = 0; i < 10; i++) {
            const lx = px - 40 + Math.random() * 40;
            this.emitBurst(lx, p.bodyY + 15, 4, '#5a8a50', { speed: 1.2, r: 4, type: 'line', blend: 'screen', life: 50 });
          }
          this.emitBurst(hitX, hitY, 10, '#8bc34a', { speed: 3, r: 3, blend: 'screen' });
        } else if (elem === '金') {
          this.emitBurst(hitX, hitY, 12, '#ffd700', { speed: 6, r: 2, type: 'spark', blend: 'screen', spread: 14 });
          this.emitBurst(hitX, hitY, 8, '#fff', { speed: 3, r: 1.5, type: 'spark', blend: 'screen' });
        } else if (elem === '土') {
          this.emitBurst(hitX, p.bodyY + 10, 18, '#8a7050', { speed: 3, r: 5, gravity: 0.06, blend: 'screen', spread: 20 });
          this.emitBurst(hitX, p.bodyY + 5, 8, '#b09070', { speed: 2, r: 3, blend: 'screen' });
        } else {
          this.emitBurst(hitX, hitY, 20, colors.primary, { speed: 4, r: 4, blend: 'screen', spread: 15 });
        }

        this.playerSkel.flash(300);
        SkeletonAnims.playerHit(this.playerSkel);
        anime({ targets: p, shakeX: [-8, 8, -5, 5, -2, 0], duration: 500, easing: 'easeOutElastic' });
      }, 350);

      setTimeout(() => { if (callback) callback(); resolve(); }, 900);
    });
  },

  playDefendAnim(callback) {
    return new Promise(resolve => {
      const p = this.player;
      const colors = this.elemColors[this.playerElem] || this.elemColors['金'];

      anime({ targets: p, glowIntensity: 0.6, duration: 300 });
      setTimeout(() => anime({ targets: p, glowIntensity: 0, duration: 300 }), 700);

      SkeletonAnims.playerDefend(this.playerSkel, () => {
        SkeletonAnims.idle(this.playerSkel, 'player');
      });

      setTimeout(() => {
        for (let i = 0; i < 20; i++) {
          const angle = (i / 20) * Math.PI * 2;
          const radius = 60;
          const px = p.bodyX + Math.cos(angle) * radius;
          const py = p.bodyY - 20 + Math.sin(angle) * radius;
          this.emitBurst(px, py, 3, colors.primary, { speed: 0.5, r: 3, blend: 'screen', life: 40 });
        }
        this.emitBurst(p.bodyX, p.bodyY - 20, 15, colors.trail, { speed: 2, r: 4, blend: 'screen', life: 50, spread: 20 });
      }, 250);

      setTimeout(() => { if (callback) callback(); resolve(); }, 1000);
    });
  },

  playVictoryAnim() {
    SkeletonAnims.playerVictory(this.playerSkel);
    anime({ targets: this.player, glowIntensity: [0, 1, 0.5], duration: 1500, easing: 'easeInOutSine', loop: true });

    const px = this.player.bodyX;
    const py = this.player.bodyY;
    this.emitBurst(px, py - 40, 35, '#ffd700', { speed: 4, r: 3, blend: 'screen', life: 80, spread: 30 });
    this.emitBurst(px, py - 20, 18, '#fff', { speed: 3, r: 2, blend: 'screen', life: 60 });
    setTimeout(() => {
      this.emitBurst(px, py - 50, 25, '#ffec80', { speed: 5, r: 4, blend: 'screen', life: 70, spread: 40 });
      this.emitBurst(px - 30, py - 30, 15, '#ffd700', { speed: 3, r: 3, blend: 'screen', life: 50 });
      this.emitBurst(px + 30, py - 30, 15, '#ffd700', { speed: 3, r: 3, blend: 'screen', life: 50 });
    }, 500);
    triggerAbilityFlash();
  },

  playDefeatAnim() {
    SkeletonAnims.playerDefeat(this.playerSkel);
    anime({ targets: this.player, alpha: 0.4, duration: 1200, easing: 'easeOutQuad' });
    this.emitBurst(this.player.bodyX, this.player.bodyY - 20, 20, '#666', { speed: 2, r: 2, blend: 'screen', life: 40, spread: 20 });
  },

  playFleeAnim(callback) {
    return new Promise(resolve => {
      const p = this.player;
      SkeletonAnims.playerFlee(this.playerSkel, p.bodyX, () => {
        SkeletonAnims.idle(this.playerSkel, 'player');
      });
      anime({ targets: p, alpha: 0, duration: 500, easing: 'easeInQuad',
        complete: () => { anime({ targets: p, alpha: 1, bodyX: this.W * 0.25, duration: 100 }); } });
      this.emitBurst(p.bodyX, p.bodyY - 20, 15, '#aaa', { speed: 3, r: 2, blend: 'screen', life: 30 });
      setTimeout(() => { if (callback) callback(); resolve(); }, 700);
    });
  },
};

// ============================================================
// SVG 骨骼动画系统（暗影格斗风格）
// ============================================================

const SkeletonBones = {
  player: {
    head:       { path: 'M0,-17 A14,17 0 1,1 0.01,-17 Z', anchor: [0, 0] },
    hair:       { path: 'M-8,-18 A8,7 0 1,1 8,-18 L10,-20 L-10,-20 Z', anchor: [0, -18] },
    torso:      { path: 'M-20,-70 Q-24,-35 -22,0 L22,0 Q24,-35 20,-70 Z', anchor: [0, 0] },
    collar:     { path: 'M-3,-70 L-14,-50 L0,-35 L14,-50 L3,-70 Z', anchor: [0, -55] },
    belt:       { path: 'M-24,-25 L24,-25 L22,-18 L-22,-18 Z', anchor: [0, -22] },
    arm_upper_l:{ path: 'M-4,-22 L4,-22 L6,0 L-6,0 Z', anchor: [0, 0] },
    arm_lower_l:{ path: 'M-3.5,-20 L3.5,-20 L4,0 L-4,0 Z', anchor: [0, 0] },
    arm_upper_r:{ path: 'M-4,-22 L4,-22 L6,0 L-6,0 Z', anchor: [0, 0] },
    arm_lower_r:{ path: 'M-3.5,-20 L3.5,-20 L4,0 L-4,0 Z', anchor: [0, 0] },
    weapon:     { path: 'M-1.5,-45 L1.5,-45 L2,0 L-2,0 Z', anchor: [0, 0] },
    weapon_glow:{ path: 'M-3,-48 Q0,-55 3,-48 L4,2 L-4,2 Z', anchor: [0, 0] },
    leg_upper_l:{ path: 'M-5,-28 L5,-28 L7,0 L-7,0 Z', anchor: [0, 0] },
    leg_lower_l:{ path: 'M-4.5,-26 L4.5,-26 L6,0 L-6,0 Z', anchor: [0, 0] },
    leg_upper_r:{ path: 'M-5,-28 L5,-28 L7,0 L-7,0 Z', anchor: [0, 0] },
    leg_lower_r:{ path: 'M-4.5,-26 L4.5,-26 L6,0 L-6,0 Z', anchor: [0, 0] },
    robe_l:     { path: 'M-8,-30 Q-18,0 -12,30 L-4,30 Q-6,0 0,-30 Z', anchor: [0, 0] },
    robe_r:     { path: 'M0,-30 Q6,0 4,30 L12,30 Q18,0 8,-30 Z', anchor: [0, 0] },
    eye_l:      { path: 'M-2,-1.5 A2,1.5 0 1,1 2,-1.5 A2,1.5 0 1,1 -2,-1.5 Z', anchor: [-5, -5] },
    eye_r:      { path: 'M-2,-1.5 A2,1.5 0 1,1 2,-1.5 A2,1.5 0 1,1 -2,-1.5 Z', anchor: [5, -5] },
  },
  enemy: {
    body:       { path: 'M-35,-40 Q-40,-15 -30,15 L30,15 Q40,-15 35,-40 Q20,-55 0,-50 Q-20,-55 -35,-40 Z', anchor: [0, 15] },
    head:       { path: 'M-22,-18 Q-25,-35 0,-38 Q25,-35 22,-18 Q15,-8 0,-6 Q-15,-8 -22,-18 Z', anchor: [0, 0] },
    horn_l:     { path: 'M-3,0 L-12,-22 L-6,-20 L-1,-5 Z', anchor: [-14, -10] },
    horn_r:     { path: 'M1,0 L12,-22 L6,-20 L3,-5 Z', anchor: [14, -10] },
    jaw:        { path: 'M-14,-2 Q-16,8 0,10 Q16,8 14,-2 L10,-4 Q5,-6 0,-5 Q-5,-6 -10,-4 Z', anchor: [0, -2] },
    fang_l:     { path: 'M-3,-2 L-5,8 L-1,3 Z', anchor: [-6, 0] },
    fang_r:     { path: 'M3,-2 L5,8 L1,3 Z', anchor: [6, 0] },
    leg_front_l:{ path: 'M-5,-20 L5,-20 L6,0 L-6,0 Z', anchor: [0, 0] },
    leg_front_r:{ path: 'M-5,-20 L5,-20 L6,0 L-6,0 Z', anchor: [0, 0] },
    leg_rear_l: { path: 'M-5,-22 L5,-22 L7,0 L-7,0 Z', anchor: [0, 0] },
    leg_rear_r: { path: 'M-5,-22 L5,-22 L7,0 L-7,0 Z', anchor: [0, 0] },
    paw_fl:     { path: 'M-7,-3 L7,-3 L8,3 L-8,3 Z', anchor: [0, 0] },
    paw_fr:     { path: 'M-7,-3 L7,-3 L8,3 L-8,3 Z', anchor: [0, 0] },
    paw_rl:     { path: 'M-8,-3 L8,-3 L9,3 L-9,3 Z', anchor: [0, 0] },
    paw_rr:     { path: 'M-8,-3 L8,-3 L9,3 L-9,3 Z', anchor: [0, 0] },
    tail:       { path: 'M-3,-3 Q-20,-15 -30,-35 Q-28,-38 -22,-30 Q-15,-12 0,0 Z', anchor: [0, 0] },
    eye_l:      { path: 'M-3,-2 A3,2 0 1,1 3,-2 A3,2 0 1,1 -3,-2 Z', anchor: [-10, -15] },
    eye_r:      { path: 'M-3,-2 A3,2 0 1,1 3,-2 A3,2 0 1,1 -3,-2 Z', anchor: [10, -15] },
    spine:      { path: 'M0,-40 L0,10', anchor: [0, 0], isLine: true },
    ribs:       { path: 'M-25,-30 Q-10,-25 0,-28 M0,-28 Q10,-25 25,-30 M-22,-18 Q-8,-13 0,-16 M0,-16 Q8,-13 22,-18', anchor: [0, 0], isLine: true },
  },
  // 灵体 — 核心球 + 飘浮碎片 + 光环
  spirit: {
    core:       { path: 'M0,-20 A20,20 0 1,1 0.01,-20 Z', anchor: [0, -20] },
    fragment_l: { path: 'M-8,-4 L0,-8 L8,-4 L4,4 L-4,4 Z', anchor: [-30, -15] },
    fragment_r: { path: 'M-8,-4 L0,-8 L8,-4 L4,4 L-4,4 Z', anchor: [30, -15] },
    ring:       { path: 'M-35,0 A35,10 0 1,1 35,0 A35,10 0 1,1 -35,0', anchor: [0, 0], isLine: true },
    eye_l:      { path: 'M-4,-2 A4,2 0 1,1 4,-2 A4,2 0 1,1 -4,-2 Z', anchor: [-8, -22] },
    eye_r:      { path: 'M-4,-2 A4,2 0 1,1 4,-2 A4,2 0 1,1 -4,-2 Z', anchor: [8, -22] },
    aura:       { path: 'M-40,-50 Q-50,0 -40,50 Q0,60 40,50 Q50,0 40,-50 Q0,-60 -40,-50 Z', anchor: [0, 0], isLine: true },
    tendril_l:  { path: 'M-20,10 Q-35,25 -30,45 Q-25,50 -20,40 Q-15,25 -10,15', anchor: [0, 0], isLine: true },
    tendril_r:  { path: 'M20,10 Q35,25 30,45 Q25,50 20,40 Q15,25 10,15', anchor: [0, 0], isLine: true },
  },
  // 人形 — 类人战士形态
  humanoid: {
    torso:      { path: 'M-22,-65 Q-26,-30 -24,0 L24,0 Q26,-30 22,-65 Z', anchor: [0, 0] },
    head:       { path: 'M0,-16 A13,16 0 1,1 0.01,-16 Z', anchor: [0, 0] },
    helm:       { path: 'M-14,-16 Q-16,-28 0,-30 Q16,-28 14,-16 L10,-14 Q5,-12 0,-13 Q-5,-12 -10,-14 Z', anchor: [0, -16] },
    arm_upper_l:{ path: 'M-5,-20 L5,-20 L7,0 L-7,0 Z', anchor: [0, 0] },
    arm_lower_l:{ path: 'M-4,-18 L4,-18 L5,0 L-5,0 Z', anchor: [0, 0] },
    arm_upper_r:{ path: 'M-5,-20 L5,-20 L7,0 L-7,0 Z', anchor: [0, 0] },
    arm_lower_r:{ path: 'M-4,-18 L4,-18 L5,0 L-5,0 Z', anchor: [0, 0] },
    weapon:     { path: 'M-2,-40 L2,-40 L3,0 L-3,0 Z', anchor: [0, 0] },
    leg_upper_l:{ path: 'M-6,-26 L6,-26 L8,0 L-8,0 Z', anchor: [0, 0] },
    leg_lower_l:{ path: 'M-5,-24 L5,-24 L7,0 L-7,0 Z', anchor: [0, 0] },
    leg_upper_r:{ path: 'M-6,-26 L6,-26 L8,0 L-8,0 Z', anchor: [0, 0] },
    leg_lower_r:{ path: 'M-5,-24 L5,-24 L7,0 L-7,0 Z', anchor: [0, 0] },
    cape_l:     { path: 'M-6,-65 Q-20,-30 -16,10 Q-10,15 -4,5 Q-2,-30 0,-65 Z', anchor: [0, 0], isLine: true },
    cape_r:     { path: 'M6,-65 Q20,-30 16,10 Q10,15 4,5 Q2,-30 0,-65 Z', anchor: [0, 0], isLine: true },
    eye_l:      { path: 'M-2,-1.5 A2,1.5 0 1,1 2,-1.5 A2,1.5 0 1,1 -2,-1.5 Z', anchor: [-5, -5] },
    eye_r:      { path: 'M-2,-1.5 A2,1.5 0 1,1 2,-1.5 A2,1.5 0 1,1 -2,-1.5 Z', anchor: [5, -5] },
  },
  // 龙族 — 蛇身 + 翅膀 + 龙角
  dragon: {
    body_seg1:  { path: 'M-18,-15 Q-22,0 -18,15 L18,15 Q22,0 18,-15 Z', anchor: [0, 0] },
    body_seg2:  { path: 'M-16,-12 Q-20,0 -16,12 L16,12 Q20,0 16,-12 Z', anchor: [0, 0] },
    body_seg3:  { path: 'M-14,-10 Q-17,0 -14,10 L14,10 Q17,0 14,-10 Z', anchor: [0, 0] },
    head:       { path: 'M-18,-20 Q-22,-35 0,-38 Q22,-35 18,-20 Q12,-8 0,-5 Q-12,-8 -18,-20 Z', anchor: [0, 0] },
    horn_l:     { path: 'M-2,0 L-10,-28 L-5,-25 L0,-5 Z', anchor: [-12, -14] },
    horn_r:     { path: 'M2,0 L10,-28 L5,-25 L0,-5 Z', anchor: [12, -14] },
    jaw:        { path: 'M-12,-2 Q-14,10 0,12 Q14,10 12,-2 L8,-4 Q4,-6 0,-5 Q-4,-6 -8,-4 Z', anchor: [0, -2] },
    wing_l:     { path: 'M0,-10 L-50,-45 L-55,-30 L-45,-15 L-30,-5 L0,0 Z', anchor: [0, -5] },
    wing_r:     { path: 'M0,-10 L50,-45 L55,-30 L45,-15 L30,-5 L0,0 Z', anchor: [0, -5] },
    claw_l:     { path: 'M-5,0 L-8,15 L-3,12 L0,5 L3,12 L8,15 L5,0 Z', anchor: [0, 0] },
    claw_r:     { path: 'M-5,0 L-8,15 L-3,12 L0,5 L3,12 L8,15 L5,0 Z', anchor: [0, 0] },
    tail:       { path: 'M-3,-3 Q-15,-8 -30,-5 Q-40,0 -35,10 Q-30,15 -20,8 Q-10,0 0,0 Z', anchor: [0, 0] },
    tail_tip:   { path: 'M-8,-5 L0,-15 L8,-5 L4,0 L-4,0 Z', anchor: [-25, 5] },
    eye_l:      { path: 'M-3,-2 A3,2 0 1,1 3,-2 A3,2 0 1,1 -3,-2 Z', anchor: [-8, -18] },
    eye_r:      { path: 'M-3,-2 A3,2 0 1,1 3,-2 A3,2 0 1,1 -3,-2 Z', anchor: [8, -18] },
    spine:      { path: 'M0,-15 L0,15 M0,15 L0,40 M0,40 L0,60', anchor: [0, 0], isLine: true },
  },
};

const SkeletonHierarchy = {
  player: {
    torso: ['head', 'collar', 'belt', 'arm_upper_l', 'arm_upper_r', 'leg_upper_l', 'leg_upper_r', 'robe_l', 'robe_r'],
    head: ['hair', 'eye_l', 'eye_r'],
    arm_upper_l: ['arm_lower_l'],
    arm_upper_r: ['arm_lower_r'],
    arm_lower_r: ['weapon', 'weapon_glow'],
    leg_upper_l: ['leg_lower_l'],
    leg_upper_r: ['leg_lower_r'],
  },
  enemy: {
    body: ['head', 'leg_front_l', 'leg_front_r', 'leg_rear_l', 'leg_rear_r', 'tail', 'spine', 'ribs'],
    head: ['horn_l', 'horn_r', 'jaw', 'eye_l', 'eye_r'],
    jaw: ['fang_l', 'fang_r'],
    leg_front_l: ['paw_fl'],
    leg_front_r: ['paw_fr'],
    leg_rear_l: ['paw_rl'],
    leg_rear_r: ['paw_rr'],
  },
  spirit: {
    core: ['fragment_l', 'fragment_r', 'ring', 'eye_l', 'eye_r', 'aura', 'tendril_l', 'tendril_r'],
  },
  humanoid: {
    torso: ['head', 'arm_upper_l', 'arm_upper_r', 'leg_upper_l', 'leg_upper_r', 'cape_l', 'cape_r'],
    head: ['helm', 'eye_l', 'eye_r'],
    arm_upper_l: ['arm_lower_l'],
    arm_upper_r: ['arm_lower_r'],
    arm_lower_r: ['weapon'],
    leg_upper_l: ['leg_lower_l'],
    leg_upper_r: ['leg_lower_r'],
  },
  dragon: {
    body_seg1: ['body_seg2', 'wing_l', 'wing_r', 'claw_l', 'head'],
    body_seg2: ['body_seg3', 'claw_r'],
    body_seg3: ['tail'],
    tail: ['tail_tip'],
    head: ['horn_l', 'horn_r', 'jaw', 'eye_l', 'eye_r'],
  },
};

const SkeletonLayout = {
  player: {
    torso:        { x: 0, y: 0, z: 1 },
    head:         { x: 0, y: -70, z: 5 },
    hair:         { x: 0, y: 0, z: 6 },
    collar:       { x: 0, y: 0, z: 3 },
    belt:         { x: 0, y: 0, z: 3 },
    arm_upper_l:  { x: -22, y: -60, z: 0 },
    arm_lower_l:  { x: 0, y: -22, z: 0 },
    arm_upper_r:  { x: 22, y: -60, z: 4 },
    arm_lower_r:  { x: 0, y: -22, z: 4 },
    weapon:       { x: 0, y: -20, z: 5 },
    weapon_glow:  { x: 0, y: -20, z: 4 },
    leg_upper_l:  { x: -10, y: 0, z: 0 },
    leg_lower_l:  { x: 0, y: -28, z: 0 },
    leg_upper_r:  { x: 10, y: 0, z: 2 },
    leg_lower_r:  { x: 0, y: -28, z: 2 },
    robe_l:       { x: 0, y: 0, z: 2 },
    robe_r:       { x: 0, y: 0, z: 2 },
    eye_l:        { x: 0, y: 0, z: 7 },
    eye_r:        { x: 0, y: 0, z: 7 },
  },
  enemy: {
    body:         { x: 0, y: 0, z: 1 },
    head:         { x: 0, y: -38, z: 5 },
    horn_l:       { x: 0, y: 0, z: 6 },
    horn_r:       { x: 0, y: 0, z: 6 },
    jaw:          { x: 0, y: -6, z: 6 },
    fang_l:       { x: 0, y: 0, z: 7 },
    fang_r:       { x: 0, y: 0, z: 7 },
    leg_front_l:  { x: -22, y: 15, z: 0 },
    leg_front_r:  { x: 22, y: 15, z: 3 },
    leg_rear_l:   { x: -25, y: 15, z: 0 },
    leg_rear_r:   { x: 25, y: 15, z: 3 },
    paw_fl:       { x: 0, y: -20, z: 0 },
    paw_fr:       { x: 0, y: -20, z: 3 },
    paw_rl:       { x: 0, y: -22, z: 0 },
    paw_rr:       { x: 0, y: -22, z: 3 },
    tail:         { x: 30, y: 5, z: 0 },
    eye_l:        { x: 0, y: 0, z: 7 },
    eye_r:        { x: 0, y: 0, z: 7 },
    spine:        { x: 0, y: 0, z: 2 },
    ribs:         { x: 0, y: 0, z: 2 },
  },
  spirit: {
    core:         { x: 0, y: -20, z: 3 },
    fragment_l:   { x: -30, y: -15, z: 1 },
    fragment_r:   { x: 30, y: -15, z: 1 },
    ring:         { x: 0, y: 0, z: 0 },
    eye_l:        { x: 0, y: 0, z: 5 },
    eye_r:        { x: 0, y: 0, z: 5 },
    aura:         { x: 0, y: 0, z: 0 },
    tendril_l:    { x: 0, y: 0, z: 2 },
    tendril_r:    { x: 0, y: 0, z: 2 },
  },
  humanoid: {
    torso:        { x: 0, y: 0, z: 1 },
    head:         { x: 0, y: -65, z: 5 },
    helm:         { x: 0, y: 0, z: 6 },
    arm_upper_l:  { x: -24, y: -55, z: 0 },
    arm_lower_l:  { x: 0, y: -20, z: 0 },
    arm_upper_r:  { x: 24, y: -55, z: 4 },
    arm_lower_r:  { x: 0, y: -20, z: 4 },
    weapon:       { x: 0, y: -18, z: 5 },
    leg_upper_l:  { x: -10, y: 0, z: 0 },
    leg_lower_l:  { x: 0, y: -26, z: 0 },
    leg_upper_r:  { x: 10, y: 0, z: 2 },
    leg_lower_r:  { x: 0, y: -26, z: 2 },
    cape_l:       { x: 0, y: 0, z: 0 },
    cape_r:       { x: 0, y: 0, z: 0 },
    eye_l:        { x: 0, y: 0, z: 7 },
    eye_r:        { x: 0, y: 0, z: 7 },
  },
  dragon: {
    body_seg1:    { x: 0, y: 0, z: 2 },
    body_seg2:    { x: 0, y: 25, z: 1 },
    body_seg3:    { x: 0, y: 25, z: 0 },
    head:         { x: 0, y: -38, z: 5 },
    horn_l:       { x: 0, y: 0, z: 6 },
    horn_r:       { x: 0, y: 0, z: 6 },
    jaw:          { x: 0, y: -5, z: 6 },
    wing_l:       { x: 0, y: -10, z: 3 },
    wing_r:       { x: 0, y: -10, z: 3 },
    claw_l:       { x: -18, y: 15, z: 1 },
    claw_r:       { x: 18, y: 65, z: 0 },
    tail:         { x: 0, y: 10, z: 0 },
    tail_tip:     { x: -25, y: 5, z: 0 },
    eye_l:        { x: 0, y: 0, z: 7 },
    eye_r:        { x: 0, y: 0, z: 7 },
    spine:        { x: 0, y: 0, z: 2 },
  },
};

// ── 骨骼渲染器 ──
class SkeletonRenderer {
  constructor(type, container, color) {
    this.type = type;
    this.container = container;
    this.color = color || '#12101e';
    this.glowColor = '#ffd700';
    this.bones = {};
    this.svg = null;
    this.flashWhite = 0;
    this._idleTl = null;
    this._build();
  }

  _build() {
    const NS = 'http://www.w3.org/2000/svg';
    const bones = SkeletonBones[this.type];
    const layout = SkeletonLayout[this.type];
    const hierarchy = SkeletonHierarchy[this.type];

    this.svg = document.createElementNS(NS, 'svg');
    this.svg.setAttribute('class', 'skeleton-svg');
    this.svg.style.cssText = 'position:absolute;width:100%;height:100%;pointer-events:none;overflow:visible;';
    this.container.appendChild(this.svg);

    // 按 z-index 排序创建骨骼
    const sortedBones = Object.keys(layout).sort((a, b) => (layout[a].z || 0) - (layout[b].z || 0));

    for (const name of sortedBones) {
      const def = bones[name];
      const pos = layout[name];
      if (!def || !pos) continue;

      const g = document.createElementNS(NS, 'g');
      g.setAttribute('data-bone', name);
      g.style.transformOrigin = `${-def.anchor[0]}px ${-def.anchor[1]}px`;

      if (def.isLine) {
        const path = document.createElementNS(NS, 'path');
        path.setAttribute('d', def.path);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', this.color);
        path.setAttribute('stroke-width', '1.5');
        path.setAttribute('stroke-linecap', 'round');
        g.appendChild(path);
      } else {
        const path = document.createElementNS(NS, 'path');
        path.setAttribute('d', def.path);
        path.setAttribute('fill', this.color);
        path.setAttribute('stroke', 'none');
        g.appendChild(path);

        // 眼睛特殊处理
        if (name.startsWith('eye_')) {
          path.setAttribute('fill', this.glowColor);
          path.style.filter = `drop-shadow(0 0 3px ${this.glowColor})`;
          path.style.mixBlendMode = 'screen';
        }
        // 武器发光
        if (name === 'weapon_glow') {
          path.setAttribute('fill', 'none');
          path.setAttribute('stroke', this.glowColor);
          path.setAttribute('stroke-width', '1');
          path.style.filter = `drop-shadow(0 0 4px ${this.glowColor})`;
          path.style.mixBlendMode = 'screen';
          path.style.opacity = '0.4';
        }
      }

      this.bones[name] = { el: g, def, pos, rotation: 0, x: 0, y: 0, scaleX: 1, scaleY: 1, alpha: 1 };
    }

    // 构建父子层级
    this._buildHierarchy(hierarchy);
  }

  _buildHierarchy(hierarchy) {
    for (const [parent, children] of Object.entries(hierarchy)) {
      const parentBone = this.bones[parent];
      if (!parentBone) continue;
      for (const childName of children) {
        const childBone = this.bones[childName];
        if (!childBone) continue;
        parentBone.el.appendChild(childBone.el);
      }
    }
    // 将根骨骼添加到 SVG
    const roots = Object.keys(hierarchy);
    for (const name of Object.keys(this.bones)) {
      if (!roots.includes(name)) continue;
      const bone = this.bones[name];
      const pos = bone.pos;
      bone.el.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);
      this.svg.appendChild(bone.el);
    }
  }

  setBoneTransform(name, { rotation = 0, x = 0, y = 0, scaleX = 1, scaleY = 1, alpha = 1 } = {}) {
    const bone = this.bones[name];
    if (!bone) return;
    bone.rotation = rotation;
    bone.x = x;
    bone.y = y;
    bone.scaleX = scaleX;
    bone.scaleY = scaleY;
    bone.alpha = alpha;
    const pos = bone.pos;
    bone.el.setAttribute('transform',
      `translate(${pos.x + x}, ${pos.y + y}) rotate(${rotation}) scale(${scaleX}, ${scaleY})`);
    if (alpha !== 1) bone.el.style.opacity = alpha;
  }

  resetPose() {
    for (const [name, bone] of Object.entries(this.bones)) {
      this.setBoneTransform(name, {});
      bone.el.style.opacity = '';
    }
  }

  setColor(color) {
    this.color = color;
    for (const [name, bone] of Object.entries(this.bones)) {
      if (name.startsWith('eye_') || name === 'weapon_glow') continue;
      const paths = bone.el.querySelectorAll('path');
      paths.forEach(p => {
        if (p.getAttribute('fill') !== 'none') p.setAttribute('fill', color);
        if (p.getAttribute('stroke') !== 'none' && p.getAttribute('stroke')) p.setAttribute('stroke', color);
      });
    }
  }

  setGlowColor(color) {
    this.glowColor = color;
    for (const name of Object.keys(this.bones)) {
      if (name.startsWith('eye_')) {
        const path = this.bones[name].el.querySelector('path');
        if (path) {
          path.setAttribute('fill', color);
          path.style.filter = `drop-shadow(0 0 3px ${color})`;
        }
      }
      if (name === 'weapon_glow') {
        const path = this.bones[name].el.querySelector('path');
        if (path) {
          path.setAttribute('stroke', color);
          path.style.filter = `drop-shadow(0 0 4px ${color})`;
        }
      }
    }
  }

  flash(duration = 300) {
    for (const bone of Object.values(this.bones)) {
      const paths = bone.el.querySelectorAll('path[fill]:not([fill="none"])');
      paths.forEach(p => {
        if (p.style.mixBlendMode === 'screen') return;
        const orig = p.getAttribute('fill');
        p.setAttribute('fill', '#fff');
        setTimeout(() => p.setAttribute('fill', orig), duration);
      });
    }
  }

  destroy() {
    if (this._idleTl) this._idleTl.pause();
    if (this.svg && this.svg.parentNode) this.svg.parentNode.removeChild(this.svg);
    this.bones = {};
  }
}

// ── 骨骼动画定义 ──
const SkeletonAnims = {
  // 待机呼吸动画
  idle(skeleton, side = 'player') {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ loop: true, autoplay: true });
    if (side === 'player') {
      tl.add({ targets: { v: 0 }, v: [0, -3, 0], duration: 2000, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('torso', { y: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: [0, 5, 0], duration: 2500, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, -3, 0], duration: 2800, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    } else if (side === 'spirit') {
      // 灵体：核心漂浮 + 碎片环绕 + 光环旋转
      tl.add({ targets: { v: 0 }, v: [0, -8, 0], duration: 2500, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('core', { y: -20 + a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: [0, 10, 0], duration: 3000, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('fragment_l', { rotation: a.animations[0].currentValue, y: a.animations[0].currentValue * 0.5 }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, -10, 0], duration: 3200, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('fragment_r', { rotation: a.animations[0].currentValue, y: a.animations[0].currentValue * -0.5 }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, 360, 0], duration: 8000, easing: 'linear',
        update: a => { skeleton.setBoneTransform('ring', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, 3, 0], duration: 2000, easing: 'easeInOutSine',
        update: a => {
          skeleton.setBoneTransform('tendril_l', { rotation: a.animations[0].currentValue });
          skeleton.setBoneTransform('tendril_r', { rotation: -a.animations[0].currentValue });
        } }, 0);
    } else if (side === 'humanoid') {
      // 人形：类似玩家但更沉稳
      tl.add({ targets: { v: 0 }, v: [0, -2, 0], duration: 2200, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('torso', { y: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: [0, 4, 0], duration: 2800, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, -3, 0], duration: 2600, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, 2, 0], duration: 3000, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('cape_l', { rotation: a.animations[0].currentValue }); } }, 0);
    } else if (side === 'dragon') {
      // 龙族：蛇身波动 + 翅膀扇动 + 尾巴甩动
      tl.add({ targets: { v: 0 }, v: [0, -5, 0], duration: 2000, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('body_seg1', { y: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: [0, 4, 0], duration: 2200, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('body_seg2', { y: a.animations[0].currentValue }); } }, 200);
      tl.add({ targets: { v: 0 }, v: [0, 3, 0], duration: 2400, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('body_seg3', { y: a.animations[0].currentValue }); } }, 400);
      tl.add({ targets: { v: 0 }, v: [0, 15, 0], duration: 1800, easing: 'easeInOutSine',
        update: a => {
          skeleton.setBoneTransform('wing_l', { rotation: a.animations[0].currentValue });
          skeleton.setBoneTransform('wing_r', { rotation: -a.animations[0].currentValue });
        } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, 8, 0], duration: 2600, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('tail', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, -3, 0], duration: 2000, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('head', { y: a.animations[0].currentValue }); } }, 0);
    } else {
      // beast (default enemy)
      tl.add({ targets: { v: 0 }, v: [0, -4, 0], duration: 1800, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('body', { y: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: [0, 3, 0], duration: 2200, easing: 'easeInOutSine',
        update: a => { skeleton.setBoneTransform('tail', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, -2, 0], duration: 1600, easing: 'easeInOutSine',
        update: a => {
          skeleton.setBoneTransform('leg_front_l', { rotation: a.animations[0].currentValue });
          skeleton.setBoneTransform('leg_rear_r', { rotation: a.animations[0].currentValue });
        } }, 0);
      tl.add({ targets: { v: 0 }, v: [0, 2, 0], duration: 1600, easing: 'easeInOutSine',
        update: a => {
          skeleton.setBoneTransform('leg_front_r', { rotation: a.animations[0].currentValue * -1 });
          skeleton.setBoneTransform('leg_rear_l', { rotation: a.animations[0].currentValue * -1 });
        } }, 0);
    }
    skeleton._idleTl = tl;
    return tl;
  },

  // 玩家攻击动画
  playerAttack(skeleton, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    // 蓄力：后仰
    tl.add({ targets: { v: 0 }, v: -15, duration: 250,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 0 }, v: -50, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: -30, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, 0);
    // 冲刺挥砍
    tl.add({ targets: { v: -15 }, v: 12, duration: 180, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: -50 }, v: 70, duration: 180, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=180');
    tl.add({ targets: { v: -30 }, v: 20, duration: 180, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, '-=180');
    // 回位
    tl.add({ targets: { v: 12 }, v: 0, duration: 350, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 70 }, v: 0, duration: 350, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=350');
    tl.add({ targets: { v: 20 }, v: 0, duration: 350, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, '-=350');
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 玩家技能动画（手臂高举下劈）
  playerSkill(skeleton, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    // 后仰蓄力 + 手臂高举
    tl.add({ targets: { v: 0 }, v: -12, duration: 300,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 0 }, v: -80, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: -40, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, 0);
    // 前冲下劈
    tl.add({ targets: { v: -12 }, v: 15, duration: 200, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: -80 }, v: 80, duration: 200, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=200');
    tl.add({ targets: { v: -40 }, v: 30, duration: 200, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, '-=200');
    // 回位
    tl.add({ targets: { v: 15 }, v: 0, duration: 400, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 80 }, v: 0, duration: 400, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=400');
    tl.add({ targets: { v: 30 }, v: 0, duration: 400, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, '-=400');
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 玩家神通动画（全身发光 + 双臂挥砍）
  playerAbility(skeleton, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    // 蓄力：后仰 + 双臂展开
    tl.add({ targets: { v: 0 }, v: -18, duration: 400,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 0 }, v: -60, duration: 400,
      update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: -60, duration: 400,
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    // 爆发冲刺
    tl.add({ targets: { v: -18 }, v: 20, duration: 150, easing: 'easeInQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: -60 }, v: 85, duration: 150, easing: 'easeInQuad',
      update: a => {
        skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue });
        skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue });
      } }, '-=150');
    // 回位
    tl.add({ targets: { v: 20 }, v: 0, duration: 500, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 85 }, v: 0, duration: 500, easing: 'easeOutQuad',
      update: a => {
        skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue });
        skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue });
      } }, '-=500');
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 防御动画
  playerDefend(skeleton, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    // 双臂交叉护胸
    tl.add({ targets: { v: 0 }, v: 30, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 0 }, v: -30, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: 40, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_lower_l', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: -40, duration: 250,
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: 0 }, v: 5, duration: 250,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } }, 0);
    // 保持
    tl.add({ targets: { v: 0 }, duration: 400 });
    // 恢复
    tl.add({ targets: { v: 30 }, v: 0, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: -30 }, v: 0, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=300');
    tl.add({ targets: { v: 40 }, v: 0, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_lower_l', { rotation: a.animations[0].currentValue }); } }, '-=300');
    tl.add({ targets: { v: -40 }, v: 0, duration: 300,
      update: a => { skeleton.setBoneTransform('arm_lower_r', { rotation: a.animations[0].currentValue }); } }, '-=300');
    tl.add({ targets: { v: 5 }, v: 0, duration: 300,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } }, '-=300');
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 受击动画
  playerHit(skeleton, callback) {
    const tl = anime.timeline({ easing: 'easeOutElastic' });
    tl.add({ targets: { v: 0 }, v: 20, duration: 150,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 20 }, v: 0, duration: 500, easing: 'easeOutElastic',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 胜利动画
  playerVictory(skeleton) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ loop: true });
    tl.add({ targets: { v: 0 }, v: -70, duration: 400, easing: 'easeOutBack',
      update: a => { skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: 0 }, v: -70, duration: 400, easing: 'easeOutBack',
      update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
    tl.add({ targets: { v: -70 }, v: -50, duration: 300, easing: 'easeInOutSine',
      update: a => {
        skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue });
        skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue });
      } });
    tl.add({ targets: { v: -50 }, v: -70, duration: 300, easing: 'easeInOutSine',
      update: a => {
        skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue });
        skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue });
      } });
    skeleton._idleTl = tl;
  },

  // 失败动画
  playerDefeat(skeleton) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline();
    tl.add({ targets: { v: 0 }, v: 45, duration: 800, easing: 'easeOutQuad',
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue, alpha: 0.4 }); } });
    tl.add({ targets: { v: 0 }, v: 20, duration: 800, easing: 'easeOutQuad',
      update: a => {
        skeleton.setBoneTransform('arm_upper_l', { rotation: a.animations[0].currentValue });
        skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue });
      } }, 0);
  },

  // 逃跑动画
  playerFlee(skeleton, startX, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    tl.add({ targets: { v: 0 }, v: -10, duration: 200,
      update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: startX }, v: startX - 200, duration: 400, easing: 'easeInQuad',
      update: a => {
        const svg = skeleton.svg;
        if (svg) svg.style.transform = `translateX(${a.animations[0].currentValue - startX}px)`;
        if (svg) svg.style.opacity = Math.max(0, 1 - (a.progress / 100));
      } });
    tl.add({ targets: { v: 0 }, duration: 100,
      begin: () => { if (skeleton.svg) { skeleton.svg.style.transform = ''; skeleton.svg.style.opacity = '1'; } } });
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 敌人攻击动画
  enemyAttack(skeleton, callback) {
    if (skeleton._idleTl) skeleton._idleTl.pause();
    const tl = anime.timeline({ easing: 'easeOutExpo' });
    const skelType = skeleton.type || 'enemy';

    if (skelType === 'spirit') {
      // 灵体：核心闪烁 + 冲刺
      tl.add({ targets: { v: 0 }, v: 1.3, duration: 250,
        update: a => { skeleton.setBoneTransform('core', { scaleX: a.animations[0].currentValue, scaleY: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: -20, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('core', { y: -20 + a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 1.3 }, v: 1, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('core', { scaleX: a.animations[0].currentValue, scaleY: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: -20 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('core', { y: -20 + a.animations[0].currentValue }); } }, '-=350');
    } else if (skelType === 'humanoid') {
      // 人形：类似玩家攻击
      tl.add({ targets: { v: 0 }, v: -15, duration: 250,
        update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: -50, duration: 250,
        update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: -15 }, v: 12, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: -50 }, v: 70, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=180');
      tl.add({ targets: { v: 12 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('torso', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 70 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('arm_upper_r', { rotation: a.animations[0].currentValue }); } }, '-=350');
    } else if (skelType === 'dragon') {
      // 龙族：蛇身前冲 + 头部咬击
      tl.add({ targets: { v: 0 }, v: -10, duration: 250,
        update: a => { skeleton.setBoneTransform('body_seg1', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: -20, duration: 250,
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: 0 }, v: -15, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('jaw', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: -10 }, v: 15, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('body_seg1', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: -20 }, v: 20, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, '-=180');
      tl.add({ targets: { v: 15 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('body_seg1', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 20 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, '-=350');
      tl.add({ targets: { v: -15 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('jaw', { rotation: a.animations[0].currentValue }); } }, '-=350');
    } else {
      // beast (default) — 原有四足兽攻击
      tl.add({ targets: { v: 0 }, v: -8, duration: 250,
        update: a => { skeleton.setBoneTransform('body', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 0 }, v: -15, duration: 250,
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, 0);
      tl.add({ targets: { v: -8 }, v: 10, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('body', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: -15 }, v: 15, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, '-=180');
      tl.add({ targets: { v: 0 }, v: -10, duration: 180, easing: 'easeInQuad',
        update: a => { skeleton.setBoneTransform('jaw', { rotation: a.animations[0].currentValue }); } }, '-=180');
      tl.add({ targets: { v: 10 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('body', { rotation: a.animations[0].currentValue }); } });
      tl.add({ targets: { v: 15 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('head', { rotation: a.animations[0].currentValue }); } }, '-=350');
      tl.add({ targets: { v: -10 }, v: 0, duration: 350, easing: 'easeOutQuad',
        update: a => { skeleton.setBoneTransform('jaw', { rotation: a.animations[0].currentValue }); } }, '-=350');
    }
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },

  // 敌人受击动画
  enemyHit(skeleton, callback) {
    const tl = anime.timeline({ easing: 'easeOutElastic' });
    const skelType = skeleton.type || 'enemy';
    const mainBone = skelType === 'spirit' ? 'core' : skelType === 'dragon' ? 'body_seg1' : skelType === 'humanoid' ? 'torso' : 'body';
    tl.add({ targets: { v: 0 }, v: -15, duration: 150,
      update: a => { skeleton.setBoneTransform(mainBone, { rotation: a.animations[0].currentValue }); } });
    tl.add({ targets: { v: -15 }, v: 0, duration: 500, easing: 'easeOutElastic',
      update: a => { skeleton.setBoneTransform(mainBone, { rotation: a.animations[0].currentValue }); } });
    if (callback) tl.finished.then(callback);
    return tl.finished;
  },
};

window.toggleSkillMenu = function() {
  // Cards are now always visible — no-op
};

// ============================================================
// 弹窗管理
// ============================================================
window.closeModal = function(id) {
  document.getElementById(id).classList.remove('active');
};

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal')) {
    e.target.classList.remove('active');
  }
});

// ============================================================
// 工具函数
// ============================================================
async function apiPost(endpoint, data) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    const res = await fetch(`${API}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!res.ok) {
      console.error(`API ${endpoint} HTTP ${res.status}`);
      return { success: false, message: `服务器错误 (${res.status})` };
    }
    return await res.json();
  } catch (e) {
    console.error(`API 错误 ${endpoint}:`, e);
    if (e.name === 'AbortError') return { success: false, message: '请求超时' };
    return { success: false, message: '网络错误' };
  }
}

async function reloadCharacter() {
  try {
    console.log('[reload] fetching...');
    const res = await fetch(`${API}/load_character`);
    const data = await res.json();
    console.log('[reload] response:', data.success, 'exp:', data.character?.exp);
    if (data.success && data.character) {
      gameState.character = data.character;
      updateUI();
      console.log('[reload] UI updated, exp bar:', document.getElementById('expValue')?.textContent);
    } else {
      console.error('[reload] failed:', data.message);
    }
  } catch (e) {
    console.error('[reload] error:', e);
  }
}

function addLog(text, type = '') {
  const log = document.getElementById('gameLog');
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.textContent = text;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight;
}

function shakeInput(el) {
  el.style.animation = 'none';
  el.offsetHeight;
  el.style.animation = 'shake 0.3s ease';
  setTimeout(() => el.style.animation = '', 300);
}

function disableActions(disabled) {
  console.log('[disableActions]', disabled);
  document.querySelectorAll('.seal-btn').forEach(btn => {
    btn.disabled = disabled;
    btn.style.opacity = disabled ? '0.4' : '1';
    btn.style.pointerEvents = disabled ? 'none' : 'auto';
  });
}

function playBreakthroughEffect() {
  // 朱砂金光突破效果
  const flash = document.createElement('div');
  flash.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: radial-gradient(circle, rgba(184,150,62,0.4), rgba(194,59,34,0.2), transparent 70%);
    z-index: 999; pointer-events: none;
    animation: flashAnim 1.2s ease-out forwards;
  `;
  document.body.appendChild(flash);

  // 墨点飞溅
  for (let i = 0; i < 12; i++) {
    const dot = document.createElement('div');
    const angle = (Math.PI * 2 * i) / 12;
    const dist = 80 + Math.random() * 120;
    const size = 3 + Math.random() * 5;
    dot.style.cssText = `
      position: fixed;
      left: 50%; top: 50%;
      width: ${size}px; height: ${size}px;
      background: ${Math.random() > 0.5 ? 'var(--gold-bright)' : 'var(--cinnabar-bright)'};
      border-radius: 50%;
      pointer-events: none;
      z-index: 1000;
      animation: inkDot 0.8s ease-out forwards;
      --dx: ${Math.cos(angle) * dist}px;
      --dy: ${Math.sin(angle) * dist}px;
    `;
    document.body.appendChild(dot);
    setTimeout(() => dot.remove(), 800);
  }

  setTimeout(() => flash.remove(), 1200);
}

// ============================================================
// 墨迹背景画布 — 水墨山水
// ============================================================
// ============================================================
// 地图主题背景系统
// ============================================================
const REGION_THEMES = {
  "青云镇": {
    mountainColor: [200,195,185], mountainAlpha: 0.025,
    particleColors: ['184,150,62','200,195,185'],
    lineColor: '184,150,62', shape: 'gentle',
    special: null, bgTint: 'rgba(10,10,15,0)',
  },
  "翠竹林": {
    mountainColor: [100,160,100], mountainAlpha: 0.03,
    particleColors: ['90,158,143','150,200,150','80,140,80'],
    lineColor: '90,158,143', shape: 'bamboo',
    special: 'leaves', bgTint: 'rgba(20,40,20,0.03)',
  },
  "炎魔谷": {
    mountainColor: [180,80,40], mountainAlpha: 0.035,
    particleColors: ['200,80,30','255,150,50','180,60,20'],
    lineColor: '200,80,30', shape: 'jagged',
    special: 'sparks', bgTint: 'rgba(40,10,5,0.04)',
  },
  "幽冥涧": {
    mountainColor: [60,60,90], mountainAlpha: 0.02,
    particleColors: ['100,80,140','60,80,120','80,60,100'],
    lineColor: '100,80,140', shape: 'deep',
    special: 'wisps', bgTint: 'rgba(10,5,20,0.05)',
  },
  "天机城": {
    mountainColor: [160,140,120], mountainAlpha: 0.025,
    particleColors: ['200,160,80','180,150,100','160,130,80'],
    lineColor: '200,160,80', shape: 'city',
    special: 'lanterns', bgTint: 'rgba(20,15,10,0.02)',
  },
  "万妖山": {
    mountainColor: [140,100,60], mountainAlpha: 0.035,
    particleColors: ['180,120,60','120,80,40','160,100,50'],
    lineColor: '160,100,50', shape: 'jagged',
    special: 'sparks', bgTint: 'rgba(30,20,10,0.04)',
  },
  "星落海": {
    mountainColor: [60,100,160], mountainAlpha: 0.025,
    particleColors: ['80,140,200','100,160,220','60,120,180'],
    lineColor: '80,140,200', shape: 'deep',
    special: 'wisps', bgTint: 'rgba(10,20,40,0.04)',
  },
  "天玄域": {
    mountainColor: [180,160,100], mountainAlpha: 0.03,
    particleColors: ['220,180,60','200,160,80','180,140,60'],
    lineColor: '220,180,60', shape: 'gentle',
    special: 'lanterns', bgTint: 'rgba(20,15,5,0.03)',
  },
  "九幽地府": {
    mountainColor: [50,40,70], mountainAlpha: 0.02,
    particleColors: ['80,60,120','60,50,90','100,80,140'],
    lineColor: '80,60,120', shape: 'deep',
    special: 'wisps', bgTint: 'rgba(15,10,25,0.06)',
  },
  "混沌深渊": {
    mountainColor: [100,40,40], mountainAlpha: 0.03,
    particleColors: ['150,50,50','80,30,30','120,40,60'],
    lineColor: '150,50,50', shape: 'jagged',
    special: 'sparks', bgTint: 'rgba(30,10,10,0.05)',
  },
  "仙灵岛": {
    mountainColor: [80,160,120], mountainAlpha: 0.025,
    particleColors: ['100,200,150','120,180,140','80,160,120'],
    lineColor: '100,200,150', shape: 'bamboo',
    special: 'leaves', bgTint: 'rgba(15,30,20,0.03)',
  },
  "天劫荒原": {
    mountainColor: [140,120,80], mountainAlpha: 0.03,
    particleColors: ['200,180,100','160,140,80','180,160,60'],
    lineColor: '200,180,100', shape: 'jagged',
    special: 'sparks', bgTint: 'rgba(25,20,10,0.04)',
  },
  "飞升台": {
    mountainColor: [200,200,220], mountainAlpha: 0.02,
    particleColors: ['240,240,255','220,220,240','200,200,230'],
    lineColor: '240,240,255', shape: 'gentle',
    special: 'wisps', bgTint: 'rgba(20,20,30,0.02)',
  },
};

let bgAnimId = null;
let currentRegion = null;

function initInkCanvas() {
  drawRegionBackground('青云镇');
}

function drawRegionBackground(regionName) {
  if (currentRegion === regionName && bgAnimId) return;
  currentRegion = regionName;

  if (bgAnimId) { cancelAnimationFrame(bgAnimId); bgAnimId = null; }

  const canvas = document.getElementById('inkCanvas');
  const ctx = canvas.getContext('2d');
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  const theme = REGION_THEMES[regionName] || REGION_THEMES['青云镇'];
  const mc = theme.mountainColor;

  // 山体轮廓
  const mountains = [];
  for (let layer = 0; layer < 3; layer++) {
    const pts = [];
    const segments = theme.shape === 'jagged' ? 12 + layer * 3 : 8 + layer * 4;
    const baseY = h * (0.55 + layer * 0.12);
    for (let i = 0; i <= segments; i++) {
      const x = (w / segments) * i;
      const peakH = (0.15 - layer * 0.03) * h;
      let y;
      if (theme.shape === 'jagged') {
        y = baseY - Math.random() * peakH * 1.3;
      } else if (theme.shape === 'bamboo') {
        y = baseY - Math.random() * peakH * (Math.sin(i * 1.2) * 0.7 + 0.3);
      } else if (theme.shape === 'deep') {
        y = baseY + layer * 20 - Math.random() * peakH * 0.6;
      } else if (theme.shape === 'city') {
        y = baseY - (Math.random() * 0.5 + 0.5) * peakH * 0.5;
      } else {
        y = baseY - Math.random() * peakH * (Math.sin(i * 0.8) * 0.5 + 0.5);
      }
      pts.push({ x, y });
    }
    mountains.push({ pts, alpha: theme.mountainAlpha - layer * 0.006, speed: 0.15 + layer * 0.05 });
  }

  // 粒子
  const particles = [];
  const particleCount = theme.special ? 60 : 50;
  for (let i = 0; i < particleCount; i++) {
    const colorIdx = Math.floor(Math.random() * theme.particleColors.length);
    particles.push({
      x: Math.random() * w, y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.2, vy: (Math.random() - 0.5) * 0.15,
      r: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.08 + 0.01,
      color: theme.particleColors[colorIdx],
    });
  }

  // 特殊粒子
  const specials = [];
  function addSpecial() {
    if (specials.length > 15) return;
    const s = { x: Math.random() * w, y: h * 0.3 + Math.random() * h * 0.5, life: 1 };
    if (theme.special === 'leaves') {
      s.type = 'leaf'; s.vx = -0.3 - Math.random() * 0.5; s.vy = 0.2 + Math.random() * 0.3;
      s.r = 2 + Math.random() * 3; s.rot = Math.random() * Math.PI; s.rotSpeed = 0.02 + Math.random() * 0.03;
    } else if (theme.special === 'sparks') {
      s.type = 'spark'; s.vx = (Math.random() - 0.5) * 0.5; s.vy = -0.5 - Math.random() * 0.8;
      s.r = 1 + Math.random() * 2; s.life = 0.5 + Math.random() * 0.5;
    } else if (theme.special === 'wisps') {
      s.type = 'wisp'; s.vx = (Math.random() - 0.5) * 0.1; s.vy = -0.1 - Math.random() * 0.2;
      s.r = 5 + Math.random() * 10; s.alpha = 0.02 + Math.random() * 0.03;
    } else if (theme.special === 'lanterns') {
      s.type = 'lantern'; s.vx = (Math.random() - 0.5) * 0.05; s.vy = -0.15 - Math.random() * 0.1;
      s.r = 3 + Math.random() * 4; s.glow = 0.03 + Math.random() * 0.04;
    }
    specials.push(s);
  }

  // 墨滴
  const inkDrops = [];
  function addInkDrop() {
    if (inkDrops.length > 5) return;
    inkDrops.push({
      x: Math.random() * w, y: Math.random() * h * 0.6,
      r: 0, maxR: 20 + Math.random() * 40,
      alpha: 0.03 + Math.random() * 0.02, speed: 0.3 + Math.random() * 0.3,
    });
  }

  let frame = 0;
  function draw() {
    ctx.clearRect(0, 0, w, h);
    frame++;

    // 背景色调
    if (theme.bgTint !== 'rgba(10,10,15,0)') {
      ctx.fillStyle = theme.bgTint;
      ctx.fillRect(0, 0, w, h);
    }

    // 山体
    mountains.forEach((m) => {
      ctx.beginPath();
      ctx.moveTo(0, h);
      m.pts.forEach((p, i) => {
        const offsetX = Math.sin(frame * 0.003 * m.speed + i * 0.5) * 2;
        if (i === 0) ctx.lineTo(p.x, p.y + offsetX);
        else {
          const prev = m.pts[i - 1];
          const cpx = (prev.x + p.x) / 2;
          ctx.quadraticCurveTo(prev.x, prev.y + offsetX, cpx, (prev.y + p.y) / 2 + offsetX);
        }
      });
      ctx.lineTo(w, h);
      ctx.closePath();
      ctx.fillStyle = `rgba(${mc[0]},${mc[1]},${mc[2]}, ${m.alpha})`;
      ctx.fill();
    });

    // 普通粒子
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < -10) p.x = w + 10;
      if (p.x > w + 10) p.x = -10;
      if (p.y < -10) p.y = h + 10;
      if (p.y > h + 10) p.y = -10;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color}, ${p.alpha})`;
      ctx.fill();
    });

    // 特殊粒子
    if (theme.special && frame % 60 === 0) addSpecial();
    for (let i = specials.length - 1; i >= 0; i--) {
      const s = specials[i];
      s.x += s.vx; s.y += s.vy;
      s.life -= 0.003;
      if (s.life <= 0 || s.x < -20 || s.x > w + 20 || s.y < -20 || s.y > h + 20) {
        specials.splice(i, 1); continue;
      }
      if (s.type === 'leaf') {
        s.rot += s.rotSpeed;
        ctx.save();
        ctx.translate(s.x, s.y);
        ctx.rotate(s.rot);
        ctx.fillStyle = `rgba(80,150,60, ${s.life * 0.15})`;
        ctx.beginPath();
        ctx.ellipse(0, 0, s.r * 2, s.r * 0.6, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      } else if (s.type === 'spark') {
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * s.life, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,180,50, ${s.life * 0.4})`;
        ctx.fill();
      } else if (s.type === 'wisp') {
        const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r);
        grad.addColorStop(0, `rgba(120,100,180, ${s.alpha * s.life})`);
        grad.addColorStop(1, 'rgba(120,100,180, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      } else if (s.type === 'lantern') {
        const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3);
        grad.addColorStop(0, `rgba(255,180,60, ${s.glow * s.life})`);
        grad.addColorStop(1, 'rgba(255,180,60, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,200,80, ${s.life * 0.3})`;
        ctx.fill();
      }
    }

    // 墨滴
    if (frame % 300 === 0) addInkDrop();
    for (let i = inkDrops.length - 1; i >= 0; i--) {
      const d = inkDrops[i];
      d.r += d.speed;
      if (d.r > d.maxR) { d.alpha -= 0.001; if (d.alpha <= 0) { inkDrops.splice(i, 1); continue; } }
      ctx.beginPath();
      ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${mc[0]},${mc[1]},${mc[2]}, ${d.alpha})`;
      ctx.fill();
    }

    // 连线
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(${theme.lineColor}, ${0.02 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.3;
          ctx.stroke();
        }
      }
    }

    bgAnimId = requestAnimationFrame(draw);
  }

  draw();
}

// ============================================================
// CSS 动画注入
// ============================================================
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-8px); }
    75% { transform: translateX(8px); }
  }
  @keyframes flashAnim {
    0% { opacity: 1; }
    100% { opacity: 0; }
  }
  @keyframes inkDot {
    0% { transform: translate(0, 0) scale(1); opacity: 1; }
    100% { transform: translate(var(--dx), var(--dy)) scale(0); opacity: 0; }
  }
  @keyframes inkSplashAnim {
    0% { transform: scale(0); opacity: 1; }
    100% { transform: scale(1); opacity: 0; }
  }
  @keyframes screenFadeIn {
    0% { opacity: 0; }
    100% { opacity: 1; }
  }
  @keyframes scrollRoll {
    0% { opacity: 1; transform: translateY(0) scale(1); }
    100% { opacity: 0; transform: translateY(-30px) scale(0.95); }
  }
  .pulse {
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(122,90,138,0.3); }
    50% { box-shadow: 0 0 16px 4px rgba(122,90,138,0.15); }
  }
`;
document.head.appendChild(style);

// 初始化创建界面预览
updateCreationPreview();

// ============================================================
// Toast 通知系统
// ============================================================
// ============================================================
// 视觉特效函数
// ============================================================
function triggerScreenShake(intensity = 1) {
  // Use canvas-based shake when combat renderer is active (smoother, no CSS reflow)
  if (combatFx && combatFx.running) {
    const shakeVal = intensity === 'heavy' ? 20 : (typeof intensity === 'number' ? intensity : 10);
    combatFx.triggerShake(shakeVal);
    return;
  }
  // Fallback to CSS shake
  const scene = document.querySelector('.combat-scene');
  if (!scene) return;

  if (intensity === 'heavy') {
    scene.classList.add('screen-shake-heavy');
    setTimeout(() => scene.classList.remove('screen-shake-heavy'), 600);
  } else {
    scene.classList.add('screen-shake');
    setTimeout(() => scene.classList.remove('screen-shake'), 500);
  }
}

function triggerCameraZoom(mode = 'normal') {
  const canvas = document.getElementById('combatCanvas');
  if (!canvas) return;

  if (mode === 'heavy') {
    canvas.classList.add('camera-zoom-heavy');
    setTimeout(() => canvas.classList.remove('camera-zoom-heavy'), 500);
  } else {
    canvas.classList.add('camera-zoom-in');
    setTimeout(() => canvas.classList.remove('camera-zoom-in'), 300);
  }
}

function triggerAchievementFlash() {
  const gameScreen = document.getElementById('gameScreen');
  if (!gameScreen) return;

  gameScreen.classList.add('achievement-flash');
  setTimeout(() => gameScreen.classList.remove('achievement-flash'), 1000);
}

function flashStatBar(barId) {
  const bar = document.getElementById(barId);
  if (!bar) return;

  bar.classList.add('bar-flash');
  setTimeout(() => bar.classList.remove('bar-flash'), 600);
}

function triggerElementBurst(element, x, y) {
  const container = document.getElementById('elementBurstContainer');
  if (!container) return;

  const elemMap = { '金': 'metal', '木': 'wood', '水': 'water', '火': 'fire', '土': 'earth' };
  const burst = document.createElement('div');
  burst.className = `element-burst ${elemMap[element] || 'fire'}`;
  burst.style.left = `${x - 100}px`;
  burst.style.top = `${y - 100}px`;
  container.appendChild(burst);
  setTimeout(() => burst.remove(), 800);
}

function triggerCriticalFlash() {
  const scene = document.querySelector('.combat-scene');
  if (!scene) return;
  const flash = document.createElement('div');
  flash.className = 'crit-flash-overlay';
  scene.appendChild(flash);
  setTimeout(() => flash.remove(), 200);
}

function triggerAbilityFlash() {
  const scene = document.querySelector('.combat-scene');
  if (!scene) return;

  // 多层闪光效果
  scene.style.filter = 'brightness(2.5) saturate(1.5)';
  scene.style.transition = 'filter 0.05s';

  // 添加闪光叠加层
  const flash = document.createElement('div');
  flash.style.cssText = `
    position: absolute; inset: 0; z-index: 10;
    background: radial-gradient(circle at 60% 45%, rgba(255,215,0,0.6) 0%, rgba(255,180,0,0.3) 30%, transparent 70%);
    animation: abilityFlashBurst 0.6s ease-out forwards;
    pointer-events: none;
  `;
  scene.appendChild(flash);

  // 镜头缩放效果
  const canvas = document.getElementById('combatCanvas');
  if (canvas) {
    canvas.style.transition = 'transform 0.15s ease-out';
    canvas.style.transform = 'scale(1.08)';
    setTimeout(() => {
      canvas.style.transform = 'scale(1.02)';
    }, 150);
    setTimeout(() => {
      canvas.style.transform = 'scale(1)';
    }, 400);
  }

  setTimeout(() => {
    scene.style.filter = 'brightness(1.8) saturate(1.2)';
  }, 80);
  setTimeout(() => {
    scene.style.filter = 'brightness(1.2)';
  }, 200);
  setTimeout(() => {
    scene.style.filter = '';
    scene.style.transition = '';
    flash.remove();
  }, 600);
}

function updateComboCounter(isCrit) {
  const now = Date.now();
  const counter = document.getElementById('comboCounter');
  if (!counter) return 1;

  if (now - gameState.combatLastHitTime < 2000) {
    gameState.combatCombo++;
  } else {
    gameState.combatCombo = 1;
  }
  gameState.combatLastHitTime = now;

  const combo = gameState.combatCombo;
  let comboText = `${combo} 连击`;
  let dmgMult = 1.0;

  // 连击奖励
  if (combo >= 10) {
    dmgMult = 1.5;
    comboText += ' 天崩地裂！';
    triggerScreenShake('heavy');
    if (combatFx) {
      combatFx.shockwave(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY, 200, '#ffd700');
      combatFx.emitParticles(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY, 60, {
        color: '#ffd700', glow: '#ffffff', speed: 6, decay: 0.01, size: 7, shape: 'star', glowSize: 12,
      });
    }
  } else if (combo >= 5) {
    dmgMult = 1.25;
    comboText += ' 势如破竹！';
    triggerScreenShake();
    if (combatFx) {
      combatFx.emitParticles(combatRenderer.enemy.bodyX, combatRenderer.enemy.bodyY, 30, {
        color: '#ff8c00', glow: '#ffd700', speed: 4, decay: 0.015, size: 5, shape: 'star',
      });
    }
  } else if (combo >= 3) {
    dmgMult = 1.1;
    comboText += ' 连击加成！';
  }

  counter.textContent = comboText;
  counter.classList.remove('show', 'critical');
  void counter.offsetWidth;
  counter.classList.add('show');
  if (isCrit) counter.classList.add('critical');
  if (combo >= 5) counter.style.color = '#ffd700';
  else if (combo >= 3) counter.style.color = '#ff8c00';
  else counter.style.color = '';

  clearTimeout(gameState.comboTimer);
  gameState.comboTimer = setTimeout(() => {
    counter.classList.remove('show', 'critical');
    counter.style.color = '';
    if (gameState.combatCombo >= 3) {
      combatRenderer.showDamageFloat(combatRenderer.player.bodyX, combatRenderer.player.bodyY - 90, `最终连击: ${gameState.combatCombo}`, '#ffd700', 20, {});
    }
    gameState.combatCombo = 0;
  }, 2000);

  return dmgMult;
}

// ── 环境粒子系统 ──
function spawnCombatParticles(element) {
  const container = document.getElementById('combatParticles');
  if (!container) return;
  container.innerHTML = '';

  const elemClassMap = {
    '金': 'spirit', '木': 'spirit', '水': 'frost', '火': 'ember', '土': 'spirit'
  };
  const particleClass = elemClassMap[element] || 'spirit';

  for (let i = 0; i < 15; i++) {
    const p = document.createElement('div');
    p.className = `combat-particle ${particleClass}`;
    p.style.left = `${Math.random() * 100}%`;
    p.style.animationDelay = `${Math.random() * 5}s`;
    p.style.animationDuration = `${3 + Math.random() * 4}s`;
    container.appendChild(p);
  }
}

function clearCombatParticles() {
  const container = document.getElementById('combatParticles');
  if (container) container.innerHTML = '';
}

// ============================================================
// 高级战斗Canvas特效系统
// ============================================================
class CombatEffectsRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.spellEffects = [];
    this.impactEffects = [];
    this.trailEffects = [];
    this.shockwaves = [];
    this.running = false;
    this.frame = 0;
    this.dpr = window.devicePixelRatio || 1;
    // Particle pool for GC optimization
    this._particlePool = [];
    this.PARTICLE_CAP = 200;
    // Screen shake state
    this.shakeX = 0;
    this.shakeY = 0;
    this.shakeIntensity = 0;
    this.shakeDecay = 0.9;
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * this.dpr;
    this.canvas.height = rect.height * this.dpr;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';
    this.ctx.scale(this.dpr, this.dpr);
    this.W = rect.width;
    this.H = rect.height;
  }

  // Object pool: reuse dead particles instead of GC
  _getParticle() {
    return this._particlePool.pop() || {};
  }
  _recycleParticle(p) {
    if (this._particlePool.length < 100) this._particlePool.push(p);
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.resize();
    this.animate();
  }

  stop() {
    this.running = false;
    this.particles = [];
    this.spellEffects = [];
    this.impactEffects = [];
    this.trailEffects = [];
    this.shockwaves = [];
  }

  animate() {
    if (!this.running) return;
    this.frame++;
    const ctx = this.ctx;
    ctx.save();
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    ctx.clearRect(0, 0, this.W, this.H);

    // Screen shake with decay
    if (this.shakeIntensity > 0.5) {
      this.shakeX = (Math.random() - 0.5) * this.shakeIntensity;
      this.shakeY = (Math.random() - 0.5) * this.shakeIntensity;
      ctx.translate(this.shakeX, this.shakeY);
      this.shakeIntensity *= this.shakeDecay;
    } else {
      this.shakeIntensity = 0;
      this.shakeX = 0;
      this.shakeY = 0;
    }

    // Update and draw particles
    this.updateParticles(ctx);
    this.updateSpellEffects(ctx);
    this.updateImpactEffects(ctx);
    this.updateTrailEffects(ctx);
    this.updateShockwaves(ctx);

    ctx.restore();
    requestAnimationFrame(() => this.animate());
  }

  triggerShake(intensity) {
    this.shakeIntensity = Math.max(this.shakeIntensity, intensity);
  }

  updateParticles(ctx) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;
      p.vy += p.gravity || 0;

      if (p.life <= 0) {
        this._recycleParticle(this.particles[i]);
        this.particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.shadowColor = p.glow || p.color;
      ctx.shadowBlur = p.glowSize || 5;

      if (p.shape === 'circle') {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
        ctx.fill();
      } else if (p.shape === 'star') {
        this.drawStar(ctx, p.x, p.y, p.size * p.life, 5);
      } else if (p.shape === 'diamond') {
        this.drawDiamond(ctx, p.x, p.y, p.size * p.life);
      } else if (p.shape === 'trail') {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
        // Trail
        for (let t = 1; t <= 3; t++) {
          ctx.globalAlpha = p.life * (1 - t * 0.3);
          ctx.beginPath();
          ctx.arc(p.x - p.vx * t * 2, p.y - p.vy * t * 2, p.size * (1 - t * 0.2), 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.restore();
    }
  }

  drawStar(ctx, x, y, r, points) {
    ctx.beginPath();
    for (let i = 0; i < points * 2; i++) {
      const radius = i % 2 === 0 ? r : r * 0.4;
      const angle = (i * Math.PI) / points - Math.PI / 2;
      const px = x + Math.cos(angle) * radius;
      const py = y + Math.sin(angle) * radius;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
  }

  drawDiamond(ctx, x, y, r) {
    ctx.beginPath();
    ctx.moveTo(x, y - r);
    ctx.lineTo(x + r * 0.6, y);
    ctx.lineTo(x, y + r);
    ctx.lineTo(x - r * 0.6, y);
    ctx.closePath();
    ctx.fill();
  }

  updateSpellEffects(ctx) {
    for (let i = this.spellEffects.length - 1; i >= 0; i--) {
      const e = this.spellEffects[i];
      e.progress += e.speed;

      if (e.progress >= 1) {
        this.spellEffects.splice(i, 1);
        continue;
      }

      ctx.save();

      if (e.type === 'beam') {
        // Energy beam
        const gradient = ctx.createLinearGradient(e.x1, e.y1, e.x2, e.y2);
        gradient.addColorStop(0, e.color + '00');
        gradient.addColorStop(0.3, e.color);
        gradient.addColorStop(0.7, e.color);
        gradient.addColorStop(1, e.color + '00');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = e.width * (1 - e.progress * 0.5);
        ctx.shadowColor = e.color;
        ctx.shadowBlur = 20;
        ctx.globalAlpha = 1 - e.progress;

        ctx.beginPath();
        ctx.moveTo(e.x1, e.y1);
        ctx.lineTo(e.x2, e.y2);
        ctx.stroke();

        // Core
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = e.width * 0.3 * (1 - e.progress * 0.5);
        ctx.stroke();

      } else if (e.type === 'circle') {
        // Expanding circle
        const r = e.radius * e.progress;
        ctx.strokeStyle = e.color;
        ctx.lineWidth = 3 * (1 - e.progress);
        ctx.shadowColor = e.color;
        ctx.shadowBlur = 15;
        ctx.globalAlpha = 1 - e.progress;

        ctx.beginPath();
        ctx.arc(e.cx, e.cy, r, 0, Math.PI * 2);
        ctx.stroke();

        // Inner glow
        const gradient = ctx.createRadialGradient(e.cx, e.cy, 0, e.cx, e.cy, r);
        gradient.addColorStop(0, e.color + '40');
        gradient.addColorStop(1, e.color + '00');
        ctx.fillStyle = gradient;
        ctx.fill();

      } else if (e.type === 'vortex') {
        // Spinning vortex
        ctx.translate(e.cx, e.cy);
        ctx.rotate(e.progress * Math.PI * 4);

        for (let arm = 0; arm < 3; arm++) {
          const angle = (arm * Math.PI * 2) / 3;
          ctx.strokeStyle = e.color;
          ctx.lineWidth = 2 * (1 - e.progress);
          ctx.globalAlpha = (1 - e.progress) * 0.8;

          ctx.beginPath();
          for (let t = 0; t < 1; t += 0.05) {
            const r = e.radius * t * e.progress;
            const a = angle + t * Math.PI * 2;
            const x = Math.cos(a) * r;
            const y = Math.sin(a) * r;
            if (t === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.stroke();
        }

      } else if (e.type === 'rain') {
        // Particle rain
        for (let j = 0; j < 20; j++) {
          const x = e.x + (Math.random() - 0.5) * e.width;
          const y = e.y + Math.random() * e.height * e.progress;
          const size = 1 + Math.random() * 2;

          ctx.fillStyle = e.color;
          ctx.globalAlpha = (1 - e.progress) * (0.5 + Math.random() * 0.5);
          ctx.shadowColor = e.color;
          ctx.shadowBlur = 5;
          ctx.fillRect(x, y, size, size * 3);
        }
      }

      ctx.restore();
    }
  }

  updateImpactEffects(ctx) {
    for (let i = this.impactEffects.length - 1; i >= 0; i--) {
      const e = this.impactEffects[i];
      e.progress += 0.03;

      if (e.progress >= 1) {
        this.impactEffects.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = 1 - e.progress;

      if (e.type === 'slash') {
        // Slash marks
        for (let s = 0; s < 3; s++) {
          const offset = (s - 1) * 15;
          const len = 60 * e.progress;

          ctx.strokeStyle = e.color;
          ctx.lineWidth = 3 * (1 - e.progress);
          ctx.shadowColor = e.color;
          ctx.shadowBlur = 10;

          ctx.beginPath();
          ctx.moveTo(e.x + offset - len, e.y + offset - len * 0.5);
          ctx.lineTo(e.x + offset + len, e.y + offset + len * 0.5);
          ctx.stroke();
        }

      } else if (e.type === 'explosion') {
        // Explosion burst
        const r = 50 * e.progress;
        const gradient = ctx.createRadialGradient(e.x, e.y, 0, e.x, e.y, r);
        gradient.addColorStop(0, '#ffffff');
        gradient.addColorStop(0.3, e.color);
        gradient.addColorStop(1, e.color + '00');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(e.x, e.y, r, 0, Math.PI * 2);
        ctx.fill();

        // Debris particles
        for (let d = 0; d < 8; d++) {
          const angle = (d * Math.PI * 2) / 8;
          const dist = r * 1.5;
          const dx = e.x + Math.cos(angle) * dist;
          const dy = e.y + Math.sin(angle) * dist;

          ctx.fillStyle = e.color;
          ctx.beginPath();
          ctx.arc(dx, dy, 2 * (1 - e.progress), 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.restore();
    }
  }

  updateTrailEffects(ctx) {
    for (let i = this.trailEffects.length - 1; i >= 0; i--) {
      const t = this.trailEffects[i];
      t.life -= 0.02;

      if (t.life <= 0) {
        this.trailEffects.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = t.life * 0.5;
      ctx.fillStyle = t.color;
      ctx.shadowColor = t.color;
      ctx.shadowBlur = 8;

      for (let j = 0; j < t.points.length; j++) {
        const p = t.points[j];
        const size = t.size * (j / t.points.length) * t.life;
        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    }
  }

  updateShockwaves(ctx) {
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const s = this.shockwaves[i];
      s.progress += 0.02;

      if (s.progress >= 1) {
        this.shockwaves.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = (1 - s.progress) * 0.6;
      ctx.strokeStyle = s.color;
      ctx.lineWidth = 4 * (1 - s.progress);
      ctx.shadowColor = s.color;
      ctx.shadowBlur = 15;

      const r = s.radius * s.progress;
      ctx.beginPath();
      ctx.arc(s.x, s.y, r, 0, Math.PI * 2);
      ctx.stroke();

      // Secondary ring
      if (s.progress > 0.2) {
        ctx.globalAlpha = (1 - s.progress) * 0.3;
        ctx.lineWidth = 2 * (1 - s.progress);
        ctx.beginPath();
        ctx.arc(s.x, s.y, r * 0.7, 0, Math.PI * 2);
        ctx.stroke();
      }

      ctx.restore();
    }
  }

  // Public API
  emitParticles(x, y, count, config) {
    for (let i = 0; i < count; i++) {
      // Enforce particle cap for 60fps
      if (this.particles.length >= this.PARTICLE_CAP) break;

      const angle = config.angle !== undefined ? config.angle + (Math.random() - 0.5) * (config.spread || 0.5) : Math.random() * Math.PI * 2;
      const speed = (config.speed || 2) * (0.5 + Math.random() * 0.5);

      const p = this._getParticle();
      p.x = x + (Math.random() - 0.5) * (config.scatter || 10);
      p.y = y + (Math.random() - 0.5) * (config.scatter || 10);
      p.vx = Math.cos(angle) * speed;
      p.vy = Math.sin(angle) * speed;
      p.size = config.size || 3;
      p.life = 1;
      p.decay = config.decay || 0.02;
      p.color = config.color || '#f0d060';
      p.glow = config.glow || config.color;
      p.glowSize = config.glowSize || 5;
      p.shape = config.shape || 'circle';
      p.gravity = config.gravity || 0;
      this.particles.push(p);
    }
  }

  castSpell(type, config) {
    this.spellEffects.push({ type, ...config, progress: 0, speed: config.speed || 0.02 });
  }

  impact(type, x, y, config) {
    this.impactEffects.push({ type, x, y, ...config, progress: 0 });
  }

  shockwave(x, y, radius, color) {
    this.shockwaves.push({ x, y, radius, color, progress: 0 });
  }

  addTrail(points, color, size) {
    this.trailEffects.push({ points, color, size, life: 1 });
  }
}

// Global combat effects renderer
let combatFx = null;

function initCombatEffects() {
  const canvas = document.getElementById('combatCanvas');
  if (!canvas) return;
  combatFx = new CombatEffectsRenderer(canvas);
  combatFx.start();
}

function destroyCombatEffects() {
  if (combatFx) {
    combatFx.stop();
    combatFx = null;
  }
}

// Spell casting effects by element — each element has unique visual
function playSpellCastEffect(element, casterX, casterY, targetX, targetY) {
  if (!combatFx) return;

  const elementColors = {
    '金': { primary: '#d4b060', secondary: '#f0e0a0', glow: '#f0d060' },
    '木': { primary: '#7ec4b0', secondary: '#a0e8c0', glow: '#90d8b0' },
    '水': { primary: '#7ab0d8', secondary: '#a0d0f0', glow: '#80c0e8' },
    '火': { primary: '#e08060', secondary: '#f0a080', glow: '#f09070' },
    '土': { primary: '#b8a870', secondary: '#d0c890', glow: '#c0b080' },
  };

  const colors = elementColors[element] || elementColors['金'];

  switch (element) {
    case '金':
      // Metal: golden beam → metal debris (diamond particles) → metallic shockwave
      combatFx.emitParticles(casterX, casterY, 15, {
        color: colors.primary, glow: colors.glow, speed: 1.5, decay: 0.03, size: 4, shape: 'star', scatter: 20,
      });
      setTimeout(() => {
        if (!combatFx) return;
        combatFx.castSpell('beam', { x1: casterX, y1: casterY, x2: targetX, y2: targetY, color: colors.primary, width: 10, speed: 0.05 });
        setTimeout(() => {
          if (!combatFx) return;
          combatFx.impact('explosion', targetX, targetY, { color: colors.secondary });
          combatFx.shockwave(targetX, targetY, 90, '#d4b060');
          // Metal debris — sharp diamond shards
          combatFx.emitParticles(targetX, targetY, 35, { color: '#f0e0a0', glow: '#f0d060', speed: 5, decay: 0.015, size: 5, shape: 'diamond', gravity: 0.08, scatter: 30 });
          combatFx.emitParticles(targetX, targetY, 15, { color: '#fff', speed: 3, decay: 0.03, size: 2, shape: 'star', scatter: 20 });
        }, 250);
      }, 200);
      break;

    case '木':
      // Wood: green energy gather → vine trail curve → leaf burst
      combatFx.emitParticles(casterX, casterY, 20, {
        color: '#40c080', glow: '#60e0a0', speed: 1, decay: 0.02, size: 3, shape: 'star', scatter: 15,
      });
      setTimeout(() => {
        if (!combatFx) return;
        // Vine trail — curved path via multiple short beams
        const midX = (casterX + targetX) / 2 + (Math.random() - 0.5) * 60;
        const midY = (casterY + targetY) / 2 - 40;
        combatFx.castSpell('beam', { x1: casterX, y1: casterY, x2: midX, y2: midY, color: '#50b880', width: 6, speed: 0.06 });
        setTimeout(() => {
          if (!combatFx) return;
          combatFx.castSpell('beam', { x1: midX, y1: midY, x2: targetX, y2: targetY, color: '#60c890', width: 6, speed: 0.06 });
          setTimeout(() => {
            if (!combatFx) return;
            // Leaf burst — circle expanding + green particles
            combatFx.castSpell('circle', { x: targetX, y: targetY, radius: 60, color: '#70d8a0', width: 3, speed: 0.05 });
            combatFx.emitParticles(targetX, targetY, 30, { color: '#80e0b0', glow: '#60d090', speed: 2.5, decay: 0.02, size: 4, shape: 'diamond', gravity: -0.02, scatter: 25 });
          }, 200);
        }, 200);
      }, 200);
      break;

    case '水':
      // Water: water column (rain downward) → splash (circle expanding)
      combatFx.emitParticles(casterX, casterY, 10, {
        color: '#5090d0', glow: '#70b0e0', speed: 1, decay: 0.03, size: 3, shape: 'circle', scatter: 10,
      });
      setTimeout(() => {
        if (!combatFx) return;
        // Water column — rain effect over target area
        combatFx.castSpell('rain', { x: targetX, y: targetY - 80, width: 100, height: 120, color: '#60a8e0', count: 25, speed: 4 });
        setTimeout(() => {
          if (!combatFx) return;
          // Splash — expanding circles
          combatFx.castSpell('circle', { x: targetX, y: targetY, radius: 50, color: '#80c0f0', width: 4, speed: 0.06 });
          setTimeout(() => {
            if (!combatFx) return;
            combatFx.castSpell('circle', { x: targetX, y: targetY, radius: 70, color: '#a0d8ff', width: 2, speed: 0.04 });
          }, 100);
          combatFx.emitParticles(targetX, targetY, 25, { color: '#90d0ff', glow: '#60a8e0', speed: 3, decay: 0.025, size: 3, shape: 'circle', gravity: 0.06, scatter: 20 });
          combatFx.shockwave(targetX, targetY, 60, '#60a8e0');
        }, 350);
      }, 200);
      break;

    case '火':
      // Fire: fireball projectile → explosion flame + upward particles
      combatFx.emitParticles(casterX, casterY, 15, {
        color: '#f06030', glow: '#ff8040', speed: 1, decay: 0.03, size: 3, shape: 'star', scatter: 15,
      });
      setTimeout(() => {
        if (!combatFx) return;
        // Fireball trail
        combatFx.addTrail([
          { x: casterX, y: casterY },
          { x: (casterX + targetX) / 2, y: Math.min(casterY, targetY) - 30 },
          { x: targetX, y: targetY },
        ], '#f06030', 6);
        combatFx.castSpell('beam', { x1: casterX, y1: casterY, x2: targetX, y2: targetY, color: '#f06030', width: 12, speed: 0.06 });
        setTimeout(() => {
          if (!combatFx) return;
          // Explosion
          combatFx.impact('explosion', targetX, targetY, { color: '#f08040' });
          combatFx.shockwave(targetX, targetY, 100, '#e06030');
          // Flame particles — upward
          combatFx.emitParticles(targetX, targetY, 40, { color: '#ff6030', glow: '#ffaa40', speed: 4, decay: 0.015, size: 4, shape: 'star', gravity: -0.08, scatter: 25 });
          combatFx.emitParticles(targetX, targetY, 20, { color: '#ffcc40', speed: 2, decay: 0.02, size: 2, shape: 'circle', gravity: -0.05, scatter: 15 });
        }, 250);
      }, 200);
      break;

    case '土':
      // Earth: ground crack (slash lines) → rock debris (large diamonds)
      combatFx.emitParticles(casterX, casterY + 20, 15, {
        color: '#a09060', glow: '#c0b080', speed: 1, decay: 0.03, size: 3, shape: 'diamond', scatter: 15,
      });
      setTimeout(() => {
        if (!combatFx) return;
        // Ground crack — multiple slash marks
        combatFx.impact('slash', targetX - 20, targetY + 10, { color: '#b0a070' });
        setTimeout(() => {
          if (!combatFx) return;
          combatFx.impact('slash', targetX + 15, targetY - 5, { color: '#a09060' });
        }, 100);
        setTimeout(() => {
          if (!combatFx) return;
          // Rock debris — large diamond particles
          combatFx.emitParticles(targetX, targetY, 30, { color: '#c0b080', glow: '#d0c890', speed: 4, decay: 0.012, size: 6, shape: 'diamond', gravity: 0.12, scatter: 30 });
          combatFx.shockwave(targetX, targetY, 70, '#a09060');
          combatFx.emitParticles(targetX, targetY + 10, 15, { color: '#807050', speed: 2, decay: 0.02, size: 3, shape: 'circle', gravity: 0.1, scatter: 20 });
        }, 250);
      }, 200);
      break;

    default:
      // Fallback: generic beam + explosion
      combatFx.emitParticles(casterX, casterY, 20, {
        color: colors.primary, glow: colors.glow, speed: 1.5, decay: 0.03, size: 4, shape: 'star', scatter: 20,
      });
      setTimeout(() => {
        if (!combatFx) return;
        combatFx.castSpell('beam', { x1: casterX, y1: casterY, x2: targetX, y2: targetY, color: colors.primary, width: 8, speed: 0.04 });
        setTimeout(() => {
          if (!combatFx) return;
          combatFx.impact('explosion', targetX, targetY, { color: colors.secondary });
          combatFx.shockwave(targetX, targetY, 80, colors.primary);
          combatFx.emitParticles(targetX, targetY, 30, { color: colors.glow, speed: 3, decay: 0.02, size: 3, shape: 'diamond', gravity: 0.05 });
        }, 300);
      }, 200);
  }
}

// Critical hit effect — enhanced with larger shockwave and more particles
function playCriticalHitEffect(x, y) {
  if (!combatFx) return;

  // Double slash marks
  combatFx.impact('slash', x, y, { color: '#f0d060' });
  setTimeout(() => {
    if (!combatFx) return;
    combatFx.impact('slash', x + 10, y - 8, { color: '#fff' });
  }, 80);

  // Large shockwave (150 instead of 120)
  combatFx.shockwave(x, y, 150, '#f0d060');

  // Star burst
  combatFx.emitParticles(x, y, 50, {
    color: '#f0d060',
    glow: '#ffffff',
    speed: 5,
    decay: 0.012,
    size: 6,
    shape: 'star',
    glowSize: 12,
    scatter: 30,
  });

  // Secondary white sparks
  combatFx.emitParticles(x, y, 20, {
    color: '#ffffff',
    speed: 3,
    decay: 0.02,
    size: 2,
    shape: 'circle',
    scatter: 20,
  });
}

// Healing effect — enhanced with beam from above and spiral particles
function playHealEffect(x, y) {
  if (!combatFx) return;

  // Green beam from above (heavenly light)
  combatFx.castSpell('beam', {
    x1: x, y1: y - 200,
    x2: x, y2: y,
    color: '#60d890',
    width: 15,
    speed: 0.08,
  });

  // Expanding green circles
  setTimeout(() => {
    if (!combatFx) return;
    combatFx.castSpell('circle', { cx: x, cy: y, radius: 50, color: '#7ec4b0', speed: 0.04 });
    setTimeout(() => {
      if (!combatFx) return;
      combatFx.castSpell('circle', { cx: x, cy: y, radius: 80, color: '#a0e8c0', speed: 0.03 });
    }, 150);
  }, 200);

  // Upward spiral particles
  combatFx.emitParticles(x, y, 30, {
    color: '#7ec4b0',
    glow: '#a0e8c0',
    speed: 1.5,
    decay: 0.01,
    size: 4,
    shape: 'diamond',
    gravity: -0.06,
    angle: -Math.PI / 2,
    spread: Math.PI * 0.8,
  });

  // Green sparkles
  combatFx.emitParticles(x, y - 20, 15, {
    color: '#c0f0d0',
    speed: 0.8,
    decay: 0.008,
    size: 3,
    shape: 'star',
    gravity: -0.04,
    scatter: 30,
  });
}

// Ability (神通) effect
function playAbilityEffect(element, x, y) {
  if (!combatFx) return;

  const elementColors = {
    '金': '#f0d060', '木': '#90d8b0', '水': '#80c0e8', '火': '#f09070', '土': '#c0b080',
  };
  const color = elementColors[element] || '#f0d060';

  // Vortex
  combatFx.castSpell('vortex', {
    cx: x, cy: y,
    radius: 100,
    color: color,
    speed: 0.015,
  });

  // Massive particle burst
  combatFx.emitParticles(x, y, 50, {
    color: color,
    glow: '#ffffff',
    speed: 5,
    decay: 0.01,
    size: 6,
    shape: 'star',
    glowSize: 12,
  });

  // Shockwave
  combatFx.shockwave(x, y, 150, color);
}

// Victory celebration
function playVictoryEffect() {
  if (!combatFx) return;

  const canvas = combatFx.canvas;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  for (let i = 0; i < 5; i++) {
    setTimeout(() => {
      const x = cx + (Math.random() - 0.5) * canvas.width * 0.6;
      const y = cy + (Math.random() - 0.5) * canvas.height * 0.4;

      combatFx.emitParticles(x, y, 30, {
        color: ['#f0d060', '#7ec4b0', '#e08060', '#7ab0d8', '#c8a0e8'][Math.floor(Math.random() * 5)],
        speed: 3,
        decay: 0.008,
        size: 5,
        shape: 'star',
        gravity: 0.03,
        glowSize: 8,
      });
    }, i * 300);
  }
}

function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ============================================================
// 新手引导系统
// ============================================================
const TUTORIAL_STEPS = [
  {
    target: '.xuan-paper',
    text: '欢迎来到鬼谷修仙录！这是你的修炼日志，所有事件都会记录在这里。',
    position: 'left',
  },
  {
    target: '#btnCultivate',
    text: '点击「修炼」可以提升修为，修为满了就能突破境界。多灵根修炼更快！',
    position: 'top',
  },
  {
    target: '#btnExplore',
    text: '点击「探索」可以在当前区域冒险，遇到怪物、发现宝物、偶遇NPC。',
    position: 'top',
  },
  {
    target: '#btnBreakthrough',
    text: '修为足够时，这里会出现突破按钮。突破成功可以提升境界，变强！',
    position: 'top',
  },
  {
    target: '#btnNPC',
    text: '点击「交谈」可以和NPC对话，购买丹药、功法和技能。',
    position: 'top',
  },
  {
    target: '#btnMove',
    text: '点击「移动」可以前往其他区域，更强的区域有更强的敌人和更好的奖励。',
    position: 'top',
  },
  {
    target: '.bamboo-panel',
    text: '左侧是你的属性面板，灵根、属性、装备、技能都在这里查看。',
    position: 'right',
  },
  {
    target: null,
    text: '引导完成！开始你的修仙之旅吧。记住：先修炼，再探索，积累实力后突破！',
    position: 'center',
  },
];

let tutorialStep = 0;
let tutorialActive = false;

function startTutorial() {
  tutorialStep = 0;
  tutorialActive = true;
  const overlay = document.getElementById('tutorialOverlay');
  overlay.style.display = 'block';
  showTutorialStep();
}

function showTutorialStep() {
  const step = TUTORIAL_STEPS[tutorialStep];
  const highlight = document.getElementById('tutorialHighlight');
  const tooltip = document.getElementById('tutorialTooltip');
  const text = document.getElementById('tutorialText');
  const indicator = document.getElementById('tutorialStepIndicator');
  const nextBtn = document.getElementById('tutorialNext');

  // 步骤指示器
  indicator.innerHTML = TUTORIAL_STEPS.map((_, i) =>
    `<span class="dot${i === tutorialStep ? ' active' : i < tutorialStep ? ' done' : ''}"></span>`
  ).join('');

  text.textContent = step.text;
  nextBtn.textContent = tutorialStep === TUTORIAL_STEPS.length - 1 ? '开始修仙' : '下一步';

  if (step.target) {
    const el = document.querySelector(step.target);
    if (el) {
      const rect = el.getBoundingClientRect();
      const pad = 8;
      highlight.style.display = 'block';
      highlight.style.top = (rect.top - pad) + 'px';
      highlight.style.left = (rect.left - pad) + 'px';
      highlight.style.width = (rect.width + pad * 2) + 'px';
      highlight.style.height = (rect.height + pad * 2) + 'px';

      // 定位 tooltip
      const tooltipPad = 16;
      if (step.position === 'left') {
        tooltip.style.top = rect.top + 'px';
        tooltip.style.right = (window.innerWidth - rect.left + tooltipPad) + 'px';
        tooltip.style.left = 'auto';
      } else if (step.position === 'right') {
        tooltip.style.top = rect.top + 'px';
        tooltip.style.left = (rect.right + tooltipPad) + 'px';
        tooltip.style.right = 'auto';
      } else if (step.position === 'top') {
        tooltip.style.bottom = (window.innerHeight - rect.top + tooltipPad) + 'px';
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = 'auto';
      }
    }
  } else {
    highlight.style.display = 'none';
    tooltip.style.top = '50%';
    tooltip.style.left = '50%';
    tooltip.style.transform = 'translate(-50%, -50%)';
    tooltip.style.right = 'auto';
  }
}

function endTutorial() {
  tutorialActive = false;
  document.getElementById('tutorialOverlay').style.display = 'none';
  localStorage.setItem('xiuxian_tutorial_done', '1');
  showToast('引导完成，开始修仙！', 'success');
}

document.getElementById('tutorialNext').addEventListener('click', () => {
  tutorialStep++;
  if (tutorialStep >= TUTORIAL_STEPS.length) {
    endTutorial();
  } else {
    showTutorialStep();
  }
});

document.getElementById('tutorialSkip').addEventListener('click', endTutorial);

// ============================================================
// 战斗动画系统
// ============================================================
// ============================================================
// 全局互动UI增强
// ============================================================

// 按钮波纹效果
function addRipple(btn, e) {
  const ripple = document.createElement('span');
  ripple.className = 'ripple-effect';
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
  ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

// 给所有印章按钮添加波纹
document.querySelectorAll('.seal-btn').forEach(btn => {
  btn.addEventListener('click', (e) => addRipple(btn, e));
});

// 墨溅效果（使用第一个定义，append到body的全屏版本）

// 属性变化动画
function animateStatChange(elementId, isUp) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.classList.remove('stat-change-up', 'stat-change-down');
  void el.offsetWidth; // 触发重绘
  el.classList.add(isUp ? 'stat-change-up' : 'stat-change-down');
  setTimeout(() => el.classList.remove('stat-change-up', 'stat-change-down'), 500);
}

// 境界提升全屏特效
function playBreakthroughEffect(realmName) {
  const overlay = document.createElement('div');
  overlay.className = 'breakthrough-overlay';

  const text = document.createElement('div');
  text.className = 'breakthrough-text';
  text.textContent = realmName;
  overlay.appendChild(text);

  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 2500);
}

// 探索发现闪光
function playDiscoveryFlash() {
  const flash = document.createElement('div');
  flash.className = 'discovery-flash';
  document.body.appendChild(flash);
  setTimeout(() => flash.remove(), 800);
}

// 修炼发光效果
function playCultivateGlow() {
  const paper = document.querySelector('.xuan-paper');
  if (paper) {
    paper.classList.add('cultivate-glow');
    setTimeout(() => paper.classList.remove('cultivate-glow'), 1000);
  }
}

// ============================================================
// 增强后的游戏操作（集成动画）
// ============================================================

const _originalDoCultivate = doCultivate;
doCultivate = async function() {
  playCultivateGlow();
  await _originalDoCultivate();
};

const _originalDoExplore = doExplore;
doExplore = async function() {
  playDiscoveryFlash();
  await _originalDoExplore();
};

// 拦截突破结果添加特效
const _originalShowBreakthrough = showBreakthrough;
showBreakthrough = async function() {
  await _originalShowBreakthrough();
};

// 增强 updateUI 添加属性变化检测
const _originalUpdateUI = updateUI;
let _lastStats = null;
updateUI = function() {
  const c = gameState.character;
  if (c && _lastStats) {
    if (c.stats.根骨 > _lastStats.gengu) animateStatChange('statGengu', true);
    if (c.stats.悟性 > _lastStats.wuxing) animateStatChange('statWuxing', true);
    if (c.stats.气运 > _lastStats.qiyun) animateStatChange('statQiyun', true);
    if (c.stats.魅力 > _lastStats.meili) animateStatChange('statMeili', true);
  }
  if (c) _lastStats = { gengu: c.stats.根骨, wuxing: c.stats.悟性, qiyun: c.stats.气运, meili: c.stats.魅力 };
  _originalUpdateUI();
};

// 检查是否需要启动教程
const _originalEnterGame = enterGame;
enterGame = function() {
  _originalEnterGame();
  if (!localStorage.getItem('xiuxian_tutorial_done')) {
    setTimeout(startTutorial, 800);
  }
};

// ============================================================
// 音频系统集成
// ============================================================
let audioInitialized = false;

async function initAudio() {
  if (audioInitialized) return;
  if (typeof audioManager !== 'undefined') {
    await audioManager.init();
    audioInitialized = true;
  }
}

// 用户交互时初始化音频
document.addEventListener('click', function initAudioOnClick() {
  initAudio();
  document.removeEventListener('click', initAudioOnClick);
}, { once: true });

// 音频控制按钮
function createAudioToggle() {
  const btn = document.createElement('button');
  btn.className = 'audio-toggle';
  btn.id = 'audioToggle';
  btn.innerHTML = '♪';
  btn.title = '开关音乐';
  btn.addEventListener('click', () => {
    if (typeof audioManager !== 'undefined') {
      audioManager.toggleMute();
      btn.classList.toggle('muted', audioManager.muted);
      btn.innerHTML = audioManager.muted ? '♪̸' : '♪';
    }
  });
  document.body.appendChild(btn);
}

// 在游戏操作中播放音效
function playSfx(name) {
  if (typeof audioManager !== 'undefined' && audioInitialized) {
    audioManager.playSfx(name);
  }
}

function playBgmForRegion(regionType) {
  if (typeof audioManager === 'undefined' || !audioInitialized) return;
  const bgmMap = {
    '和平': 'bgm_peaceful', 'peaceful': 'bgm_peaceful',
    '战斗': 'bgm_battle', 'battle': 'bgm_battle',
    '幽暗': 'bgm_dark', 'dark': 'bgm_dark',
    '庄严': 'bgm_majestic', 'majestic': 'bgm_majestic',
    '空灵': 'bgm_ethereal', 'ethereal': 'bgm_ethereal',
  };
  const bgm = bgmMap[regionType] || 'bgm_peaceful';
  audioManager.playBgm(bgm);
}

// ============================================================
// 宗门系统
// ============================================================
document.getElementById('btnSect').addEventListener('click', showSect);

async function showSect() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('sectModal').classList.add('active');
  document.getElementById('sectDetail').style.display = 'none';
  document.getElementById('sectInfo').style.display = 'block';
  await loadSectList();
}

async function loadSectList() {
  const res = await apiPost('/sect/list', { character: gameState.character });
  const listEl = document.getElementById('sectList');
  if (!res.success) {
    listEl.innerHTML = '<p class="empty-hint">加载失败</p>';
    return;
  }

  // Check if player is already in a sect
  const infoRes = await apiPost('/sect/info', { character: gameState.character });
  if (infoRes.success && infoRes.sect) {
    showSectDetail(infoRes.sect);
    return;
  }

  const sectIcons = { '天剑宗': '⚔️', '青木门': '🌿', '玄水宫': '🌊', '烈焰门': '🔥', '厚土宗': '🪨' };
  listEl.innerHTML = (res.sects || []).map(s => `
    <div class="sect-card" onclick="joinSect('${s.name}')">
      <div class="sect-card-icon">${sectIcons[s.name] || '🏯'}</div>
      <div class="sect-card-name">${s.name}</div>
      <div class="sect-card-desc">${s.desc || ''}</div>
    </div>
  `).join('');
}

async function joinSect(name) {
  const res = await apiPost('/sect/join', { character: gameState.character, sect_name: name });
  if (res.success) {
    addLog(`加入${name}！`, 'success');
    playSfx('sfx_item');
    showToast(`成功加入${name}`, 'success');
    await reloadCharacter();
    await loadSectList();
  } else {
    addLog(res.message || '加入失败', 'danger');
    showToast(res.message || '加入失败', 'danger');
  }
}

function showSectDetail(sect) {
  document.getElementById('sectInfo').style.display = 'none';
  document.getElementById('sectDetail').style.display = 'block';
  document.getElementById('sectName').textContent = sect.name;
  document.getElementById('sectRank').textContent = sect.rank || '外门弟子';
  document.getElementById('sectDesc').textContent = sect.desc || '';
  document.getElementById('sectStats').innerHTML = `
    <div class="sect-stat"><span class="sect-stat-label">等级</span><span class="sect-stat-val">${sect.level || 1}</span></div>
    <div class="sect-stat"><span class="sect-stat-label">成员</span><span class="sect-stat-val">${sect.member_count || 1}</span></div>
    <div class="sect-stat"><span class="sect-stat-label">贡献</span><span class="sect-stat-val">${sect.contribution || 0}</span></div>
  `;
  if (sect.members && sect.members.length) {
    document.getElementById('sectMembers').innerHTML = '<h4 style="color:var(--gold-dim);margin-bottom:8px;">成员</h4>' +
      sect.members.map(m => `<div class="sect-member"><span>${m.name}</span><span>${m.rank}</span></div>`).join('');
  }
  if (sect.tasks && sect.tasks.length) {
    document.getElementById('sectTasks').innerHTML = '<h4 style="color:var(--gold-dim);margin-bottom:8px;">宗门任务</h4>' +
      sect.tasks.map(t => `<div class="sect-task-item"><div class="sect-task-name">${t.name}</div><div class="sect-task-desc">${t.desc}</div></div>`).join('');
  }
}

document.getElementById('btnLeaveSect').addEventListener('click', async () => {
  if (!confirm('确定要退出宗门吗？')) return;
  const res = await apiPost('/sect/leave', { character: gameState.character });
  if (res.success) {
    addLog('已退出宗门', 'system');
    showToast('已退出宗门', 'info');
    await reloadCharacter();
    document.getElementById('sectDetail').style.display = 'none';
    document.getElementById('sectInfo').style.display = 'block';
    await loadSectList();
  }
});

document.getElementById('btnSectTask').addEventListener('click', async () => {
  const res = await apiPost('/sect/task', { character: gameState.character });
  if (res.success) {
    addLog(`接取宗门任务：${res.task_name}`, 'success');
    showToast(`接取任务：${res.task_name}`, 'success');
  } else {
    showToast(res.message || '接取失败', 'danger');
  }
});

// ============================================================
// 灵宠系统
// ============================================================
document.getElementById('btnPet').addEventListener('click', showPet);

async function showPet() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('petModal').classList.add('active');
  document.getElementById('petDetail').style.display = 'none';
  document.getElementById('petCatchArea').style.display = 'none';
  await loadPetList();
}

// Pet tab switching
document.querySelectorAll('.pet-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.pet-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    if (tab.dataset.tab === 'list') {
      document.getElementById('petList').style.display = 'grid';
      document.getElementById('petCatchArea').style.display = 'none';
      document.getElementById('petDetail').style.display = 'none';
      loadPetList();
    } else {
      document.getElementById('petList').style.display = 'none';
      document.getElementById('petCatchArea').style.display = 'block';
      document.getElementById('petDetail').style.display = 'none';
      showWildPet();
    }
  });
});

async function loadPetList() {
  const res = await apiPost('/pet/list', { character: gameState.character });
  const listEl = document.getElementById('petList');
  if (!res.success || !res.pets || res.pets.length === 0) {
    listEl.innerHTML = '<p class="empty-hint">还没有灵宠，去捕获一只吧！</p>';
    return;
  }
  const petIcons = { '灵狐': '🦊', '仙鹤': '🦢', '雷兽': '⚡', '火凤': '🔥', '玄龟': '🐢', '玉兔': '🐰', '金翅鹏': '🦅', '墨龙': '🐉' };
  listEl.innerHTML = res.pets.map((p, i) => `
    <div class="pet-card" onclick="showPetDetail(${i})">
      <div class="pet-card-icon">${petIcons[p.species] || '🐾'}</div>
      <div class="pet-card-name">${p.name}</div>
      <div class="pet-card-level">Lv.${p.level || 1} ${p.species || ''}</div>
    </div>
  `).join('');
}

let currentPets = [];
async function showPetDetail(index) {
  const res = await apiPost('/pet/list', { character: gameState.character });
  if (!res.success || !res.pets || !res.pets[index]) return;
  const pet = res.pets[index];
  currentPets = res.pets;

  document.getElementById('petList').style.display = 'none';
  document.getElementById('petDetail').style.display = 'block';

  const petIcons = { '灵狐': '🦊', '仙鹤': '🦢', '雷兽': '⚡', '火凤': '🔥', '玄龟': '🐢', '玉兔': '🐰', '金翅鹏': '🦅', '墨龙': '🐉' };
  document.getElementById('petAvatar').textContent = petIcons[pet.species] || '🐾';
  document.getElementById('petInfo').innerHTML = `
    <div class="pet-info-row"><span>名字</span><span>${pet.name}</span></div>
    <div class="pet-info-row"><span>种类</span><span>${pet.species || '未知'}</span></div>
    <div class="pet-info-row"><span>等级</span><span>Lv.${pet.level || 1}</span></div>
    <div class="pet-info-row"><span>亲密度</span><span>${pet.affinity || 0}</span></div>
    <div class="pet-info-row"><span>攻击</span><span>${pet.attack || 0}</span></div>
    <div class="pet-info-row"><span>防御</span><span>${pet.defense || 0}</span></div>
  `;
  if (pet.skills && pet.skills.length) {
    document.getElementById('petSkills').innerHTML = pet.skills.map(s => `<span class="pet-skill-tag">${s}</span>`).join('');
  }
}

document.getElementById('btnFeedPet').addEventListener('click', async () => {
  if (!currentPets.length) return;
  const pet = currentPets[0]; // Feed the first pet for simplicity
  const res = await apiPost('/pet/feed', { character: gameState.character, pet_name: pet.name });
  if (res.success) {
    addLog(`喂养${pet.name}成功，亲密度+${res.affinity_gain || 1}`, 'success');
    playSfx('sfx_item');
    showToast(`喂养成功`, 'success');
    await showPetDetail(0);
  } else {
    showToast(res.message || '喂养失败', 'danger');
  }
});

document.getElementById('btnEvolvePet').addEventListener('click', async () => {
  if (!currentPets.length) return;
  const pet = currentPets[0];
  const res = await apiPost('/pet/evolve', { character: gameState.character, pet_name: pet.name });
  if (res.success) {
    addLog(`${pet.name}进化成功！`, 'success');
    playSfx('sfx_breakthrough');
    showToast(`${pet.name}进化成功！`, 'success');
    await showPetDetail(0);
  } else {
    showToast(res.message || '进化失败', 'danger');
  }
});

document.getElementById('btnPetBattle').addEventListener('click', async () => {
  if (!currentPets.length) return;
  showToast('已设为出战灵宠', 'success');
});

async function showWildPet() {
  const wildPets = ['灵狐', '仙鹤', '雷兽', '火凤', '玄龟', '玉兔'];
  const randomPet = wildPets[Math.floor(Math.random() * wildPets.length)];
  const petIcons = { '灵狐': '🦊', '仙鹤': '🦢', '雷兽': '⚡', '火凤': '🔥', '玄龟': '🐢', '玉兔': '🐰' };
  document.getElementById('petWild').textContent = petIcons[randomPet] || '🐾';
  document.getElementById('petWild').dataset.petName = randomPet;
}

document.getElementById('btnCatchPet').addEventListener('click', async () => {
  const petName = document.getElementById('petWild').dataset.petName;
  if (!petName) return;
  playSfx('sfx_pet_catch');
  const res = await apiPost('/pet/catch', { character: gameState.character, pet_name: petName });
  if (res.success) {
    addLog(`成功捕获${petName}！`, 'success');
    showToast(`捕获${petName}成功！`, 'success');
    // Show a new wild pet
    showWildPet();
  } else {
    addLog(`${petName}逃脱了...`, 'system');
    showToast(`${petName}逃脱了`, 'warning');
    showWildPet();
  }
});

// ============================================================
// 秘境副本
// ============================================================
document.getElementById('btnDungeon').addEventListener('click', showDungeon);

async function showDungeon() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('dungeonModal').classList.add('active');
  document.getElementById('dungeonProgress').style.display = 'none';
  await loadDungeonList();
}

async function loadDungeonList() {
  const res = await apiPost('/dungeon/list', { character: gameState.character });
  const listEl = document.getElementById('dungeonList');
  if (!res.success || !res.dungeons || res.dungeons.length === 0) {
    listEl.innerHTML = '<p class="empty-hint">暂无可用秘境</p>';
    return;
  }
  const dungeonIcons = ['🌀', '⛩️', '🏔️', '🌊', '🔥'];
  listEl.innerHTML = res.dungeons.map((d, i) => `
    <div class="dungeon-card" onclick="enterDungeon('${d.name}')">
      <div class="dungeon-card-icon">${dungeonIcons[i % dungeonIcons.length]}</div>
      <div class="dungeon-card-name">${d.name}</div>
      <div class="dungeon-card-info">
        推荐境界：${d.min_realm || '练气'}<br>
        层数：${d.floors || '?'}层<br>
        ${d.desc || ''}
      </div>
    </div>
  `).join('');
}

async function enterDungeon(name) {
  playSfx('sfx_dungeon_enter');
  const res = await apiPost('/dungeon/enter', { character: gameState.character, dungeon_name: name });
  if (res.success) {
    addLog(`进入秘境：${name}`, 'event');
    showToast(`进入${name}`, 'info');
    document.getElementById('dungeonList').style.display = 'none';
    document.getElementById('dungeonProgress').style.display = 'block';
    document.getElementById('dungeonFloor').textContent = res.floor || 1;
    if (res.hp_percent !== undefined) {
      document.getElementById('dungeonHpFill').style.width = res.hp_percent + '%';
    }
  } else {
    showToast(res.message || '进入失败', 'danger');
  }
}

document.getElementById('btnDungeonNext').addEventListener('click', async () => {
  const res = await apiPost('/dungeon/battle', { character: gameState.character });
  if (res.success) {
    addLog(`秘境战斗：${res.battle_desc || '遭遇敌人'}`, 'event');
    if (res.victory) {
      playSfx('sfx_victory');
      document.getElementById('dungeonFloor').textContent = res.floor || 1;
      if (res.hp_percent !== undefined) {
        document.getElementById('dungeonHpFill').style.width = res.hp_percent + '%';
      }
    } else {
      playSfx('sfx_defeat');
      addLog('秘境挑战失败...', 'danger');
    }
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
  } else {
    showToast(res.message || '战斗失败', 'danger');
  }
});

document.getElementById('btnDungeonReward').addEventListener('click', async () => {
  const res = await apiPost('/dungeon/reward', { character: gameState.character });
  if (res.success) {
    addLog(`获得秘境奖励：${res.rewards || '丰厚奖励'}`, 'success');
    playSfx('sfx_item');
    showToast('领取奖励成功', 'success');
    document.getElementById('dungeonProgress').style.display = 'none';
    document.getElementById('dungeonList').style.display = 'grid';
    await loadDungeonList();
    await reloadCharacter();
  } else {
    showToast(res.message || '领取失败', 'danger');
  }
});

document.getElementById('btnDungeonLeave').addEventListener('click', () => {
  document.getElementById('dungeonProgress').style.display = 'none';
  document.getElementById('dungeonList').style.display = 'grid';
  addLog('离开了秘境', 'system');
});

// ============================================================
// 世界BOSS
// ============================================================
document.getElementById('btnWorldBoss').addEventListener('click', showWorldBoss);

async function showWorldBoss() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('worldBossModal').classList.add('active');
  await loadWorldBoss();
}

async function loadWorldBoss() {
  const res = await apiPost('/world_boss/info', { character: gameState.character });
  if (res.success && res.boss) {
    document.getElementById('bossInfo').style.display = 'block';
    document.getElementById('bossEmpty').style.display = 'none';
    const bossIcons = { '天魔': '👹', '妖皇': '🐲', '混沌老祖': '👿' };
    document.getElementById('bossAvatar').textContent = bossIcons[res.boss.name] || '👹';
    document.getElementById('bossName').textContent = res.boss.name;
    const hpPct = res.boss.hp_percent || 100;
    document.getElementById('bossHpFill').style.width = hpPct + '%';
    document.getElementById('bossHpText').textContent = `${res.boss.current_hp || '?'}/${res.boss.max_hp || '?'}`;
    document.getElementById('bossDesc').textContent = res.boss.desc || '';
    if (res.rankings && res.rankings.length) {
      document.getElementById('bossRankings').innerHTML = '<div class="boss-rank-title">伤害排行</div>' +
        res.rankings.map((r, i) => `<div class="boss-rank-item"><span>${i+1}. ${r.name}</span><span>${r.damage}</span></div>`).join('');
    }
  } else {
    document.getElementById('bossInfo').style.display = 'none';
    document.getElementById('bossEmpty').style.display = 'block';
  }
}

document.getElementById('btnAttackBoss').addEventListener('click', async () => {
  playSfx('sfx_attack');
  const res = await apiPost('/world_boss/attack', { character: gameState.character });
  if (res.success) {
    addLog(`对BOSS造成${res.damage || 0}伤害！`, 'event');
    if (res.killed) {
      playSfx('sfx_victory');
      addLog('BOSS已被击杀！', 'success');
      showToast('BOSS击杀成功！', 'success');
    }
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    await loadWorldBoss();
  } else {
    showToast(res.message || '挑战失败', 'danger');
  }
});

// ============================================================
// 装备强化
// ============================================================
document.getElementById('btnEnhance').addEventListener('click', showEnhance);

async function showEnhance() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('enhanceModal').classList.add('active');
  document.getElementById('enhancePanel').style.display = 'none';
  document.getElementById('gemPanel').style.display = 'none';
  await loadEnhanceEquipList();
}

// Enhance tab switching
document.querySelectorAll('.enhance-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.enhance-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    if (tab.dataset.tab === 'enhance') {
      document.getElementById('enhanceEquipSelect').style.display = 'block';
      document.getElementById('enhancePanel').style.display = 'none';
      document.getElementById('gemPanel').style.display = 'none';
      loadEnhanceEquipList();
    } else {
      document.getElementById('enhanceEquipSelect').style.display = 'none';
      document.getElementById('enhancePanel').style.display = 'none';
      document.getElementById('gemPanel').style.display = 'block';
      loadGemPanel();
    }
  });
});

async function loadEnhanceEquipList() {
  const charRes = await apiPost('/load_character', {});
  const char = charRes.character || gameState.character;
  const equipped = char.equipped || {};
  const items = [];
  if (equipped.weapon) items.push({ slot: 'weapon', name: equipped.weapon, icon: '⚔️' });
  if (equipped.armor) items.push({ slot: 'armor', name: equipped.armor, icon: '🛡️' });
  if (equipped.accessory) items.push({ slot: 'accessory', name: equipped.accessory, icon: '💍' });

  const listEl = document.getElementById('enhanceEquipList');
  if (items.length === 0) {
    listEl.innerHTML = '<p class="empty-hint">没有可强化的装备</p>';
    return;
  }
  listEl.innerHTML = items.map(it => `
    <div class="enhance-equip-card" onclick="selectEnhanceEquip('${it.slot}', '${it.name}')">
      <div style="font-size:24px;margin-bottom:6px;">${it.icon}</div>
      <div class="enhance-equip-name">${it.name}</div>
      <div class="enhance-equip-level">${it.slot === 'weapon' ? '武器' : it.slot === 'armor' ? '护甲' : '饰品'}</div>
    </div>
  `).join('');
}

async function selectEnhanceEquip(slot, name) {
  document.getElementById('enhanceEquipSelect').style.display = 'none';
  document.getElementById('enhancePanel').style.display = 'block';
  document.getElementById('enhancePreview').innerHTML = `
    <div class="enhance-preview-name">${name}</div>
    <div class="enhance-preview-stats">点击强化提升装备属性</div>
  `;
  document.getElementById('enhanceCost').textContent = '消耗灵石进行强化';
}

document.getElementById('btnDoEnhance').addEventListener('click', async () => {
  playSfx('sfx_enhance');
  const res = await apiPost('/enhance/equip', { character: gameState.character });
  if (res.success) {
    addLog(`强化成功！${res.message || ''}`, 'success');
    playSfx('sfx_breakthrough');
    showToast('强化成功！', 'success');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
  } else {
    playSfx('sfx_enhance_fail');
    addLog(res.message || '强化失败', 'danger');
    showToast(res.message || '强化失败', 'danger');
  }
});

async function loadGemPanel() {
  const gemIcons = { '攻击宝石': '🔴', '防御宝石': '🔵', '生命宝石': '🟢', '灵力宝石': '🟣', '暴击宝石': '🟡' };
  const listEl = document.getElementById('gemList');
  listEl.innerHTML = Object.entries(gemIcons).map(([name, icon]) => `
    <div class="gem-item" onclick="selectGem('${name}')">
      <span class="gem-icon">${icon}</span>
      <span class="gem-name">${name}</span>
    </div>
  `).join('');

  document.getElementById('gemSocket').innerHTML = `
    <div class="gem-slot">⚔️</div>
    <div class="gem-slot">🛡️</div>
    <div class="gem-slot">💍</div>
  `;
}

let selectedGem = null;
function selectGem(name) {
  selectedGem = name;
  document.querySelectorAll('.gem-item').forEach(el => el.classList.remove('selected'));
  event.currentTarget.classList.add('selected');
}

document.getElementById('btnEmbedGem').addEventListener('click', async () => {
  if (!selectedGem) { showToast('请先选择宝石', 'warning'); return; }
  const res = await apiPost('/enhance/gem', { character: gameState.character, gem_name: selectedGem });
  if (res.success) {
    playSfx('sfx_enhance');
    addLog(`镶嵌${selectedGem}成功！`, 'success');
    showToast('镶嵌成功', 'success');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
  } else {
    showToast(res.message || '镶嵌失败', 'danger');
  }
});

// ============================================================
// 拍卖行
// ============================================================
document.getElementById('btnAuction').addEventListener('click', showAuction);

async function showAuction() {
  if (!gameState.character) { addLog('请先创建角色', 'danger'); return; }
  playSfx('sfx_open');
  document.getElementById('auctionModal').classList.add('active');
  await loadAuctionList();
}

// Auction tab switching
document.querySelectorAll('.auction-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auction-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    if (tab.dataset.tab === 'browse') {
      document.getElementById('auctionBrowse').style.display = 'block';
      document.getElementById('auctionSell').style.display = 'none';
      loadAuctionList();
    } else {
      document.getElementById('auctionBrowse').style.display = 'none';
      document.getElementById('auctionSell').style.display = 'block';
      loadAuctionSellList();
    }
  });
});

async function loadAuctionList() {
  const res = await apiPost('/auction/list', { character: gameState.character });
  const listEl = document.getElementById('auctionList');
  if (!res.success || !res.items || res.items.length === 0) {
    listEl.innerHTML = '<p class="empty-hint">拍卖行暂无物品</p>';
    return;
  }
  listEl.innerHTML = res.items.map((item, i) => `
    <div class="auction-item">
      <div class="auction-item-name">${item.name}</div>
      <div class="auction-item-price">起拍价：<span class="price-val">${item.price} 灵石</span></div>
      <button class="auction-item-btn" onclick="buyAuction(${i}, '${item.name}', ${item.price})">竞拍</button>
    </div>
  `).join('');
}

async function buyAuction(index, name, price) {
  const res = await apiPost('/auction/buy', { character: gameState.character, item_index: index });
  if (res.success) {
    addLog(`拍得${name}！`, 'success');
    playSfx('sfx_item');
    showToast(`成功拍得${name}`, 'success');
    if (res.summary) updateFromSummary(res.summary);
    await reloadCharacter();
    await loadAuctionList();
  } else {
    showToast(res.message || '竞拍失败', 'danger');
  }
}

document.getElementById('btnRefreshAuction').addEventListener('click', async () => {
  playSfx('sfx_click');
  await loadAuctionList();
  showToast('拍品已刷新', 'info');
});

async function loadAuctionSellList() {
  const charRes = await apiPost('/load_character', {});
  const char = charRes.character || gameState.character;
  const inv = char.inventory || [];
  const listEl = document.getElementById('auctionSellList');
  if (inv.length === 0) {
    listEl.innerHTML = '<p class="empty-hint">背包空空如也</p>';
    return;
  }
  listEl.innerHTML = inv.map((item, i) => `
    <div class="auction-sell-item" onclick="sellAuction(${i}, '${item}')">
      <div style="font-size:20px;margin-bottom:4px;">📦</div>
      <div style="font-size:12px;color:var(--text-body);">${item}</div>
    </div>
  `).join('');
}

async function sellAuction(index, name) {
  const price = prompt(`设置${name}的售价（灵石）：`, '100');
  if (!price || isNaN(price)) return;
  const res = await apiPost('/auction/sell', { character: gameState.character, item_index: index, price: parseInt(price) });
  if (res.success) {
    addLog(`上架${name}，售价${price}灵石`, 'success');
    showToast('上架成功', 'success');
    await loadAuctionSellList();
  } else {
    showToast(res.message || '上架失败', 'danger');
  }
}

// ============================================================
// 音频集成到游戏操作
// ============================================================
const _origDoCultivate2 = doCultivate;
doCultivate = async function() {
  playSfx('sfx_click');
  await _origDoCultivate2();
};

const _origDoExplore2 = doExplore;
doExplore = async function() {
  playSfx('sfx_click');
  await _origDoExplore2();
};

const _origShowBreakthrough2 = showBreakthrough;
showBreakthrough = async function() {
  playSfx('sfx_open');
  await _origShowBreakthrough2();
};

const _origDoBreakthrough = typeof doBreakthrough !== 'undefined' ? doBreakthrough : null;
if (_origDoBreakthrough) {
  window.doBreakthrough = async function() {
    const result = await _origDoBreakthrough();
    // breakthrough sound is handled in the result display
    return result;
  };
}

// Initialize audio toggle button
createAudioToggle();
