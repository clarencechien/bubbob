# bubbob — 強化版泡泡龍「蓄能引爆」手感原型

單一 HTML（vanilla JS + Canvas 2D，零相依、零 build），直接用瀏覽器打開 `public/index.html` 即玩。
規格見 [SPEC.md](SPEC.md)（v0.3）。

## 部署（Cloudflare Workers）

已附 `wrangler.jsonc`（assets-only，靜態上傳 `public/`）。Workers Builds 的
deploy 指令維持 `npx wrangler versions upload` 就會動；本機手動部署則是
`npx wrangler deploy`。沒有 Worker 程式碼、沒有 build step。

## 玩法

**五關關卡制**：每關擊殺配額 10→20→40→80→160，殺滿過關（補滿血），越後面怪越快、生得越密、場上越擠。死亡即結束，`R` 重來。

- `←→` / `A D` 移動，`空白` / `↑` / `W` 跳
- `J` / 滑鼠左鍵：**點按**吐普通泡泡；**按住集氣、放開**射出強力泡（集滿約 0.8 秒）
  - 強力泡困住的敵人**很難掙脫**：鎖定期間不擲掙脫骰（秒數由 `powerLock` 旋鈕控制；簡單難度＝永不掙脫，最難難度只鎖 3 秒）
- **身體碰到敵泡泡＝引爆**，鄰近泡泡 BFS 連鎖
- 泡泡越熟價值越高、掙脫機率也越高：綠 ×1 → 黃 ×2 → 橙 ×3.5 → 紅閃 ×6
- 引爆獎勵依 Tier：綠＝分數（簡單難度還會補血）、黃＝補血、橙＝雙泡能力、紅＝無敵星（碰敵自動困成泡泡）
- 被敵人碰到扣 1 血（預設 5 血，可調），歸零即崩盤結束
- 頭上雙 bar：狀態 bar（★無敵星／2雙泡，倒數縮短）＋集氣 bar
- 調整面板預設隱藏：右上 ⚙ 或 `O` 鍵開啟（難易度一鍵預設＋13 顆即時滑桿）
  - `maxEnemies` 生敵上限：場上（含被困）最多幾隻；設 **-1 = 場上不設限**

## 素材

玩家小龍與敵人是**本專案自繪的 32×32 原創像素圖**（依概念參考圖重繪；`tools/pixelart.py` 產生，原檔在 `assets/`，可自由取用）：
側面行走兩幀（走路交替、空中用跨步幀、靜止併攏）、翻面即反向；暴走型態為手繪紅色調色盤置換（強度色），
不再用程式紅染（僅使用者上傳單張素材時退回紅染）。
UI 與地形（心心、太陽、泡泡外框、草地、磚牆）取自 [KAPLAY](https://github.com/kaplayjs/kaplay) crew sprites（MIT License, © KAPLAY Team）。全部 base64 內嵌。

### 自行更換素材（OpenGameArt 等）

面板右下的**素材槽**可直接上傳 PNG 即時替換（玩家／敵人／暴走敵／泡泡）。
squash & stretch、Tier 著色、暴走紅染、閃爍等效果照常套用。建議規格：

- 透明背景 PNG、單張立繪（不用 sprite sheet），約 16–64px 見方
- 玩家與敵人**面向右**（上傳的素材預設視為朝右，會自動翻面）
- 泡泡素材：圓形外框、內部盡量透明（程式會依 Tier 著色 + 塞敵人進去）

推薦的免費像素素材（請確認各頁授權標示）：

| 用途 | 連結 | 授權 |
|------|------|------|
| 主角＋敵人 | [Classic hero and baddies pack（GrafxKid）](https://opengameart.org/content/classic-hero-and-baddies-pack) | CC0 |
| 敵人 | [Platformer Baddies](https://opengameart.org/content/platformer-baddies) | 見頁面 |
| 敵人／角色 | [Enemies and characters (Pixel Art)](https://opengameart.org/content/enemies-and-characters-pixel-art) | 見頁面 |
| 泡泡 | [Pink Bubble Popping Animation 16x16](https://opengameart.org/content/pink-bubble-popping-animation-16x16) | CC0 |
| 小龍主角＋磚塊 | [Pixel Art Platformer Asset Pack](https://opengameart.org/content/pixel-art-platformer-asset-pack) | CC0 |
| 整包備選 | [Kenney — Pixel Platformer](https://kenney.nl/assets/pixel-platformer) | CC0 |
| 作者頁（大量同風格） | [GrafxKid 全部作品](https://opengameart.org/users/grafxkid) | 多為 CC0 |
| 總目錄 | [OpenGameArt CC0 資源清單](https://opengameart.org/content/cc0-resources) | — |

> 之後想把素材固定進檔案：把 PNG 轉 base64 塞進 `index.html` 的 `EMBED` 表即可（鍵名見 `EMBED_SLOTS`）。
